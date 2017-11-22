import chuckmoore as wizard
from os import path

cache_filename = 'forth_wizard_cache.txt'

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
        '2r@' ]

def convert_stacks(in_stack, out_stack):
    symbols = {}
    counter = 0
    def convert(symbol):
        nonlocal counter
        if symbol not in symbols:
            symbols[ symbol ] = counter
            counter += 1
        return symbols[ symbol ]
    s_in = [convert(s) for s in in_stack]
    s_out = [convert(s) for s in out_stack]
    # normalize stacks
    for i, n in enumerate(s_out):
        if s_out[i] != i: break
        if s_out.count(n) != 1:
            s_in = [x - n for x in s_in[n:]]
            s_out = [x - n for x in s_out[n:]]
            break
    return s_in, s_out

def set_stacks(in_stack, out_stack):
    s_in, s_out = convert_stacks(in_stack, out_stack)
    wizard.init()
    wizard.set_stack_in(s_in)
    wizard.set_stack_out(s_out)

def solve_next():
    code = wizard.solve()
    if code is None:
        return []
    if code == -1:
        return None
    return [ ops[ op ] for op in code ]

def solve(in_stack, out_stack, use_cache=True):
    if not cache and use_cache:
        cache_read()
    s_in, s_out = convert_stacks(in_stack, out_stack)
    key = tuple(s_in + [-1] + s_out)
    if use_cache:
        code = cache.get(key)
        if code:
            return code
    wizard.init()
    wizard.set_stack_in(s_in)
    wizard.set_stack_out(s_out)
    code = solve_next()
    if code and use_cache:
        cache_save(key, code)
    return code

cache = {}

def cache_read():
    if not path.exists(cache_filename):
        return
    with open(cache_filename,'r') as f:
        for line in f.readlines():
            k,v = line.split('=')
            cache[tuple(map(int, k.split()))] = v.split()

def cache_save(key, value):
    cache[key] = value
    k=' '.join([str(x) for x in key])
    v=' '.join([str(x) for x in value])
    flag = 'a' if path.exists(cache_filename) else 'w'
    with open(cache_filename,flag) as f:
        f.write('{}={}\n'.format(k,v))
