FUNCTION = 67
GENERATOR = 99

LINE_GENERATOR = ('''
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
''', (
    ('name', 'line'),
    ('stacksize', 2),
    ('argcount', 2),
    ('localcount', 1),
    ('varnames', ('slope', 'offset', 'x')),
    ('constants', (0, 1)),
    ('flags', GENERATOR),
))


SQUARER = ('''
    loop:
        YIELD_VALUE
        DUP_TOP
        BINARY_MULTIPLY
        YIELD_VALUE
    JUMP_ABSOLUTE loop
''', (
    ('name', 'analog'),
    ('stacksize', 2),
    ('argcount', 0),
    ('localcount', 0),
    ('constants', (2,)),
    ('flags', GENERATOR),
))


STEPWISE_LINE = ('''
    LOAD_FAST 0
    LOAD_CONST 1
    COMPARE_OP 0
    POP_JUMP_IF_FALSE onfalse
        LOAD_FAST 0
        RETURN_VALUE
    onfalse:
        LOAD_CONST 2
        LOAD_FAST 0
        BINARY_MULTIPLY
        LOAD_CONST 3
        BINARY_ADD
        RETURN_VALUE
''', (
    ('name', 'x_or_2xplus3'),
    ('argcount', 1),
    ('localcount', 1),
    ('flags', FUNCTION),
    ('constants', (None, 10, 2, 3)),
    ('varnames', ('x',))
))
