"""A "High level Virtual Machine" implementation.

Write debuggable assembly level code using the python instruction set.

Example:
    LOAD_CONST 0
    LOAD_CONST 1
    BINARY_ADD
    RETURN_VALUE
"""

import ast
import atexit
import dis
import logging
import os
import re
import tempfile
import types
import inspect
import signal
import sys


FLAGS = {
    'function': (
        inspect.CO_OPTIMIZED |
        inspect.CO_NEWLOCALS |
        inspect.CO_NOFREE
    ),
    'generator': (
        inspect.CO_OPTIMIZED |
        inspect.CO_NEWLOCALS |
        inspect.CO_NOFREE |
        inspect.CO_GENERATOR
    )
}
"""dict: containing common flags for compiled functions."""

TEMPSOURCES = []
"""list: temporary files with assembled source for debugging."""

LOGGER = logging.getLogger('bytecode')
LOGGER.addHandler(logging.NullHandler())


def remove_temp_sources():
    for source in TEMPSOURCES:
        os.remove(source.name)

atexit.register(remove_temp_sources)


def assemble(code, context=None):
    """Build asm code into a function."""
    if isinstance(context, tuple):
        context = dict(context)
    return _assemble_function(*_get_program_context(code, context))


def _get_program_context(code, context=None):
    """Build a program and context object.

    Args:
        code (str): The assembly-like program.
            It should use instructions from
            dis.opmap.

            It may include comments which set metadata
            in context, like `# varnames = ('ctx', )`
            which are used for function definition.

        context (dict, optional): default metadata.
            This can be passed instead of defining
            context within the program.

    Returns:
        tuple: (program: bytecode, context: dict)

        The program is the parsed instructions from "code",
        and the context contains a dictionary of variables
        parsed out of comment style strings and labels.

    """
    # Setup context
    context = context or {}
    context.setdefault('labels', {})
    context.setdefault('save', False)
    program = []  # bytecode
    lnotab = [0, 1]  # source line number table
    LOGGER.debug('Compiling')
    save = context['save']
    if save:
        fileno = tempfile.NamedTemporaryFile(delete=False)  # stack trace
        fileno.write(b'# <bytecode>\n')
        TEMPSOURCES.append(fileno)
    location = 0
    # Get lines without extra indentation
    lines = inspect.cleandoc(code).split('\n')

    LOGGER.debug("Collecting labels")
    for line in (item.strip() for item in lines):
        if ':' in line:
            label = line.strip(':')
            LOGGER.debug("%s @ %d", label, location)
            context['labels'][label] = location
            continue
        elif not line or line.startswith('#'):
            continue
        location += 2
    location = 0

    LOGGER.debug("Building program")
    for line in (item.strip() for item in lines):
        LOGGER.debug("Parsing: %s", line)
        if line.startswith('#'):
            LOGGER.debug(" - comment")
            continue  # comment
        if ':' in line:
            LOGGER.debug(" - label")
            continue  # label
        if not line:
            LOGGER.debug(" - empty")
            continue  # empty
        # with argument
        # (anything after is implied as a comment)
        args = line.split(' ')
        op, arg = args[0], '0'
        opcode = dis.opmap[op]
        if opcode >= dis.HAVE_ARGUMENT:
            arg = args[1]
        if opcode in dis.hasjabs and not arg.isdigit():
            # Allow absolute jumping to labels
            arg = context['labels'][arg]
        elif not arg.isdigit():
            arg = '0'  # comment, etc... w/ no arg
        LOGGER.debug("- %s %s", opcode, arg)
        location += 2
        program.append(opcode)
        program.append(int(arg))
        lnotab.extend([2, 1])  # increment 1 line
        if save:
            fileno.write(bytes('{}\n'.format(line), 'utf-8'))
    LOGGER.debug("Completing build.")
    context['lnotab'] = bytes(lnotab)
    if save:
        context['filename'] = fileno.name
        fileno.close()
    return program, context


def _assemble_function(program, context):
    """Build an assembled function.

    Args:
        program (list[int]): of bytecode operations
        context (dict): of arguments for function creation

       Returns:
           FunctionType: initialized function object

    """
    nargs = len(context.get('varnames', ('x',)))
    context.setdefault('stacksize', 2)
    context.setdefault('argcount', nargs)
    context.setdefault('kwcount', 0)
    context.setdefault('localcount', 0)
    context.setdefault('flags', FLAGS['function'])
    context.setdefault('constants', ())
    context.setdefault('names', ())
    context.setdefault('filename', '<filename>')
    context.setdefault('name', '<name>')
    context.setdefault('firstlineno', 1)
    context.setdefault('lnotab', b'')
    context.setdefault('freevars', ())
    context.setdefault('cellvars', ())
    context.setdefault(
        'totallocals',
        (
            context.get('argcount', 0) +
            context.get('kwcount', 0) +
            context.get('localcount', 0)
        )
    )
    context.setdefault(
        'varnames',
        tuple((chr(ord('a') + x) for x in range(nargs)))
    )
    LOGGER.debug("Creating Code Object with %s", context)
    try:
        code = types.CodeType(
            context['argcount'],
            context['kwcount'],
            context['totallocals'],
            context['stacksize'],
            context['flags'],
            bytes(program),
            context['constants'],
            context['names'],
            context['varnames'],
            context['filename'],
            context['name'],
            context['firstlineno'],
            context['lnotab'],
            context['freevars'],
            context['cellvars']
        )
    except TypeError as excp:
        raise TypeError(
            '\n{}\nCould not compile: {}'
            .format(context, excp)
        )
    _verify_assembly(code)
    func = types.FunctionType(
        code,
        context.get('globals', globals())
    )
    if context['save']:
        func.fileno = next(
            source for source in TEMPSOURCES
            if source.name == context['filename']
        )
    return func


def _verify_assembly(code):
    instructions = dis.Bytecode(code)
    jumps = []
    max_offset = 0
    for instruction in instructions:
        if instruction.opcode in dis.hasjabs:
            jumps.append(instruction.argval)
        max_offset = instruction.offset
    missed_jumps = set()
    for jump in jumps:
        if jump >= max_offset:
            missed_jumps.add(jump)
    if missed_jumps:
        raise ValueError('Missed Jumps: {}'.format(missed_jumps))


def delete(assembled):
    fileno = TEMPSOURCES.pop(TEMPSOURCES.index(assembled.fileno))
    os.remove(assembled.fileno.name)
    del assembled


def disassemble(function):
    instructions = dis.Bytecode(function)
    for instruction in instructions:
        opname = instruction.opname
        arg = instruction.arg
        if arg is None:
            arg = 0
        jtarg = '<<' if instruction.is_jump_target else ''
        argval = instruction.argval or ''
        comment = ' '.join(map(str, filter(None, [jtarg, argval])))
        comment = f' # {comment}' if comment else ''
        yield f'{opname} {arg} {comment}'


def _custom_trace(frame, event, arg):
    LOGGER.debug("%s %s", event, arg)
    if tempfile.gettempdir() not in frame.f_code.co_filename:
        return _custom_trace
    with open(frame.f_code.co_filename) as fd:
        for idx, line in enumerate(fd, 0):
            if idx != frame.f_lineno:
                continue
            LOGGER.debug(line.strip())
            sys.stderr.flush()
    return _custom_trace


def enable_debug_tracing():
    """Enable debug tracing."""
    if not LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.setLevel('DEBUG')
    sys.settrace(_custom_trace)
    LOGGER.debug('[debug enabled]')


if __name__ == '__main__':
    """Assemble a function.

    Below:
        a generator that calculates a line
        based on an input dict (ctx) with
        keys 'm', 'x', and 'b'.

    """
    import sys
    logging.basicConfig()
    enable_debug_tracing()
    line = assemble('''
        LOAD_CONST 0  # load 0
        STORE_FAST 2  # store 0 in x

        loop:
            LOAD_FAST 2  # x
            LOAD_CONST 1  # 1
            INPLACE_ADD  # (x + 1)
            STORE_FAST 2  # x

            # yield slope * x + offset
            LOAD_FAST 0  # slope
            LOAD_FAST 2  # x
            BINARY_MULTIPLY  # (slope * x)
            LOAD_FAST 1  # offset
            BINARY_ADD  # (+ offset)
            YIELD_VALUE  # y = mx + b
            POP_TOP  # pop y
        JUMP_ABSOLUTE loop
    ''', {
        'name': 'line',
        'stacksize': 2,
        'argcount': 2,
        'localcount': 1,
        'varnames': ('slope', 'offset', 'x'),
        'constants': (0, 1),
        'flags': FLAGS['generator']
    })
    print(dis.dis(line))
    print(dis.show_code(line))
    path = line(2, 5)
    y = next(path)
    print(y)
