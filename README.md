# codon
Write native python byte code and learn about python instructions

Example

```python
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
```
