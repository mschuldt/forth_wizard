ops = [ 'dup',
        'drop',
        'swap',
        'over',
        'rot',
        '>r',
        'r>',
        '2dup',
        '2drop',
        '2swap',
        '2over',
        '2rot',
        'nip',
        'tuck',
        '-rot',
        'r@',
        '2>r',
        '2r>',
        '2r@',
        '3dup',
]

pick_ops =  [ '2pick',
              '3pick',
              '4pick',
              '5pick',
]

not_pick_ops = [o for o in ops if o not in pick_ops]

ops.extend(pick_ops)

code_map = { "2pick" : ["2", "pick"],
             "3pick" : ["3", "pick"],
             "4pick" : ["4", "pick"],
             "5pick" : ["5", "pick"]
}

def _ops_except(*except_ops):
    ret = list(ops)
    for o in except_ops:
        ret.remove(o)
    return ret

gforth_ops = _ops_except(
    '3dup',
)

amforth_ops = _ops_except(
    '2over',
    '2rot',
    'tuck',
    '-rot',
    '3dup',
)

target_ops = { "gforth" : gforth_ops,
               "amforth" : amforth_ops,
}
