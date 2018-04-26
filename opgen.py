"""Op generator."""

import dis
import random

unary_ops = (
    'UNARY_CONVERT', 'UNARY_INVERT', 'UNARY_NEGATIVE',
    'UNARY_NOT', 'UNARY_POSITIVE',
)

binary_ops = (
    'BINARY_ADD', 'BINARY_AND', 'BINARY_FLOOR_DIVIDE',
    'BINARY_FLOOR_DIVIDE', 'BINARY_LSHIFT',
    'BINARY_MODULO', 'BINARY_MULTIPLY',
    'BINARY_OR', 'BINARY_POWER',
    'BINARY_RSHIFT', 'BINARY_SUBSCR',
    'BINARY_SUBTRACT', 'BINARY_TRUE_DIVIDE',
    'BINARY_XOR',
)

math_ops = unary_ops + binary_ops

load_ops = (
    'LOAD_ATTR', 'LOAD_CONST',
    'LOAD_FAST', 'LOAD_GLOBAL',
    'LOAD_NAME', 'LOAD_CLOSURE',
)

store_ops = (
    'STORE_ATTR', 'STORE_FAST', 'STORE_GLOBAL',
    'STORE_MAP', 'STORE_NAME', 'STORE_SLICE+0',
    'STORE_SLICE+1', 'STORE_SLICE+2', 'STORE_SLICE+3',
    'STORE_SUBSCR'
)

call_ops = ('CALL_FUNCTION', )

return_ops = (
    'YIELD_VALUE', 'RETURN_VALUE'
)


class OpGenerator(object):

    _opcount = len(dis.opname)

    def __init__(self, localcount=None, constantcount=None):
        self.stacked = 0
        self.emitted = 0
        self.finished = 0
        self.localcount = localcount
        self.constantcount = constantcount
        self.last_op = 'NOP'
        self.ophistory = []
        self.weights = {}
        self.reset()

    def reset(self, weights=None):
        """Reset the generator."""
        self.stacked = 0
        self.finished = False
        self.emitted = False
        self.last_op = 'NOP'
        self.weights = weights or {op: self.init_weight() for op in dis.opmap}
        self.ophistory = []

    def init_weight(self):
        return random.random() * 0.8 + 0.2

    def opening(self):
        return (op for op in ())

    def closing(self):
        return (op for op in ())

    def arg(self, op):
        if op == 'LOAD_FAST':
            return random.randrange(self.localcount)
        elif op == 'LOAD_CONST':
            return random.randrange(self.constantcount)
        elif op in dis.hasjrel:
            return random.random() * 2 * 5
        elif op in dis.hasjabs:
            return random.random() * 2 * 10
        else:
            return 0

    def pre_update(self):
        last_op = self.last_op
        if last_op in load_ops:
            self.stacked += 1
        elif last_op in binary_ops:
            self.stacked -= 1
        elif last_op in return_ops:
            self.finished = True

    def __iter__(self):
        yield from self.opening()
        while not self.finished:
            self.pre_update()
            if self.finished:
                return
            chosen = False
            while not chosen:
                op = self.select_op(
                    self.get_opgroups()
                )
                weight = self.weights[op]
                if random.random() > weight:
                    continue
                self.ophistory.append(op)
                chosen = True
            yield op, self.arg(op)
            self.last_op = op
            self.emitted += 1
        yield from self.closing()

    def get_opgroups(self):
        return (
            self.valid_load_ops(),
            self.valid_math_ops(),
            self.valid_return_ops(),
            self.valid_call_ops(),
        )

    def select_op(self, opgroups):
        if not any(opgroups):
            self.finished = True
            return 'NOP'
        ops = random.choice(list(filter(None, opgroups)))
        return random.choice(ops)

    def update_stack(self):
        if self.last_op in load_ops:
            self.stacked += 1
        elif self.last_op in binary_ops:
            self.stacked -= 1

    def valid_call_ops(self):
        """Call functions when stacked."""
        if self.stacked and self.last_op in load_ops:
            if 'CALL_FUNCTION' in self.ophistory:
                return ()  # XXX
            return call_ops
        return ()

    def valid_load_ops(self):
        """Load anything any time."""
        if self.stacked >= 2 or self.emitted > 64:
            return ()  # Don't overuse the stack
        return load_ops

    def valid_return_ops(self):
        """Return a value at the end."""
        if self.stacked == 1:
            return ('RETURN_VALUE',)

    def valid_math_ops(self):
        """Unary and/or binary math where possible."""
        # Now yield valid ops
        if self.stacked >= 2:
            return math_ops
        elif self.stacked == 1:
            return unary_ops
        else:
            return ()


import vm
import logging
import math
# logging.basicConfig(level='DEBUG')
# vm.enable_debug_tracing()

def test(f, programmer):
    low = -4.1
    high = 4.1
    output = []
    assert 'CALL_FUNCTION' in programmer.ophistory
    for x in range(-10, 10):
        val = f(x)
        assert low < val and val < high
        output.append(val)
    print(output)

programmer = OpGenerator(1, 3)
context = (
    ('name', 'func'),
    ('stacksize', 2),
    ('argcount', 1),
    ('localcount', 4),
    ('constants', (None, math.sin, math.cos, math.tan, math.sqrt, 0.5, 1.0, 2.0, 4.0, 8.0)),
    ('flags', 67),
)

attempts = 2000
num_runs = 50
best_run = 0
best_weights = None
best_programs = None

while best_run < 1:
    valids = []
    for p in range(attempts):
        programmer.reset()
        try:
            code = '\n'.join(
                '{} {}'.format(*pair)
                for pair in programmer
            )
            func = vm.assemble(code, context)
            if p % 100 == 0:
                print(code + "\n\n")
            # print("====")
            # dis.dis(func)
            test(func, programmer)
        except Exception as excp:
            import traceback
            # if p % 10 == 0:
            #     print(traceback.format_exc())
            continue
        else:
            valids.append(func)
            # if len(valids) == 3:
            #     break
    score = len(valids)
    if score > best_run:
        best_run = score
        best_weights = programmer.weights.copy()
        best_programs = valids
        print(score)

print(best_run)
if best_programs:
    for idx, p in enumerate(best_programs):
        print("== {}".format(idx))
        dis.dis(p)
        print("====")
    import pdb; pdb.set_trace()
