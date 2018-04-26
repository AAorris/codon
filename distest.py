import dis
import vm
import multiprocessing as cpu


asm = vm.assemble('''
    LOAD_CONST 2
    DUP_TOP
    BINARY_MULTIPLY
    LOAD_CONST 2
    BINARY_MULTIPLY
    RETURN_VALUE
''', {'argcount': 0, 'constants': (None, 0, 1)})

vm.delete(asm)
