import chuckmoore as wizard

ops = [ "dup",
        "drop",
        "swap",
        "over",
        "rot",
        ">r",
        "r>",
        "dup2",
        "drop2",
        "2swap",
        "over2",
        "rot2",
        "nip",
        "tuck",
        "-rot",
        "rfetch",
        "2>r",
        "2r>",
        "rfetch2" ]

def set_stacks(in_stack, out_stack):
    symbols = {}
    counter = 0
    def convert(symbol):
        nonlocal counter
        if symbol not in symbols:
            symbols[ symbol ] = counter
            counter += 1
        return symbols[ symbol ]
    wizard.init()
    wizard.set_stack_in([convert(s) for s in in_stack])
    wizard.set_stack_out([convert(s) for s in out_stack])

def solve_next():
    code = wizard.solve()
    if code is None:
        return []
    if code == -1:
        return None
    return [ ops[ op-1 ] for op in code ]

def solve(in_stack, out_stack):
    set_stacks(in_stack, out_stack)
    return solve_next()
