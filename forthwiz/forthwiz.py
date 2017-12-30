import chuckmoore as wizard
from .ops import *
from os import path

cache_filename = 'forth_wizard_cache.txt'
current_cache_filename = None
n_ops = 0 # ops added to solver

def normalize_stacks(in_stack, out_stack):
    for i, n in enumerate(out_stack):
        if out_stack[i] != i: break
        if out_stack.count(n) != 1:
            in_stack = [x - n for x in in_stack[i:]]
            out_stack = [x - n for x in out_stack[i:]]
            break
    return in_stack, out_stack

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
    return s_in, s_out

def set_stacks(in_stack, out_stack):
    s_in, s_out = convert_stacks(in_stack, out_stack)
    wizard.init()
    wizard.set_stack_in(s_in)
    wizard.set_stack_out(s_out)

def solve_next():
    if n_ops == 0:
        add_all_ops()
    code = wizard.solve()
    if code is None:
        return []
    if code == -1:
        return None
    return [ ops[ op ] for op in code ]

def convert_code(code):
    ret = []
    for x in code:
        c = code_map.get(x)
        ret.extend(c) if c else ret.append(x)
    return ret

def add_ops(x):
    global n_ops
    n_ops += len(x)
    for o in x:
        if o not in x:
            raise Exception("Unsupported op '{}'".format(o))
        wizard.add_op(ops.index(o))

def add_pick_ops():      add_ops(pick_ops)
def add_none_pick_ops(): add_ops(not_pick_ops)
def add_all_ops():       add_ops(ops)

def find_solution(ops):
    ops_with_pick, ops_without_pick = [], []
    for o in ops:
        (ops_with_pick if o in pick_ops else ops_without_pick).append(o)
    # find solution without pick
    add_ops(ops_without_pick)
    without_pick = solve_next()
    c_without_pick = convert_code(without_pick)
    if not ops_with_pick:
        return c_without_pick, without_pick
    # find solution with pick
    wizard.reset_solver()
    add_ops(ops_with_pick)
    with_pick = solve_next()
    c_with_pick = convert_code(with_pick)
    # Attempt to choose the 'best' solution
    # When does it become preferable to use pick?
    len_with = len(c_with_pick)
    len_without = len(c_without_pick)
    if len_with < len_without:
        # using pick made the solution shorter
        return c_with_pick, with_pick
    if len_with == len_without:
        # if there are at least as many 'drop's as 'pick's, prefer 'pick'
        if ( ( c_without_pick.count('drop') + c_without_pick.count('nip') )
             >= c_with_pick.count('pick') ):
            return c_with_pick, with_pick
        # otherwise solutions are tied, don't use pick
    return c_without_pick, without_pick


# Stack normalization does not always result in the same answer.
# for example:
#
#  in stack: [0,1,2,3]
# out stack: [0,1,2,3,1]
#   => 2over nip
#
# after normalization:
#  in stack: [0,1,2]
# out stack:[0,1,2,0]
#  => dup 2over drop nip
#
# The normalized form is preferred as it de-duplicates a lot of input
# leading to greater cache utilization, but it cannot be done in situations
# where the deeper stack depth is used to produce shorter code sequence.
#
# Generate the solution using the original stacks, then verify that the
# solution is still unchanged with normalized stacks, if it is then cache the
# result using the normalized stacks, otherwise cache using the original stacks.

def make_cache_key(s_in, s_out, use_pick):
    return tuple([-2 if use_pick else -3 ] + s_in + [-1] + s_out)

def solve(in_stack, out_stack, use_cache=True, use_pick=True,
          cache_file=None, convert=True):
    if cache_file:
        global cache_filename
        cache_filename = cache_file
        if cache_filename != current_cache_filename:
            cache.clear()
    if not cache and use_cache:
        cache_read()
    s_in, s_out = convert_stacks(in_stack, out_stack)

    key = make_cache_key(s_in, s_out, use_pick)
    n_in, n_out = normalize_stacks(s_in, s_out)
    n_key = make_cache_key(n_in, n_out, use_pick)
    if use_cache:
        code = cache.get(key)
        if code:
            return convert_code(code) if convert else code
        code = cache.get(n_key)
        if code:
            return convert_code(code) if convert else code
    # find solution using the original stacks
    wizard.init()
    wizard.set_stack_in(s_in)
    wizard.set_stack_out(s_out)
    use_ops = ops if use_pick else not_pick_ops
    code, cache_code = find_solution(use_ops)
    if not code or not use_cache:
        return code if convert else cache_code
    # check that solution is valid with normalized stacks
    if n_in != s_in or n_out != s_out:
        wizard.reset_solver()
        wizard.set_stack_in(n_in)
        wizard.set_stack_out(n_out)
        wizard.set_code([ops.index(c) for c in cache_code])
        if wizard.verify():
            key = n_key
    cache_save(key, cache_code)
    return code if convert else cache_code

cache = {}

def cache_read():
    if not path.exists(cache_filename):
        return
    with open(cache_filename,'r') as f:
        for line in f.readlines():
            k,v = line.split('=')
            cache[tuple(map(int, k.split()))] = v.split()
    global current_cache_filename
    current_cache_filename = cache_filename

def cache_save(key, value):
    cache[key] = value
    k=' '.join([str(x) for x in key])
    v=' '.join([str(x) for x in value])
    flag = 'a' if path.exists(cache_filename) else 'w'
    with open(cache_filename,flag) as f:
        f.write('{}={}\n'.format(k,v))
