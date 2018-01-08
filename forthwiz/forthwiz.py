import chuckmoore as wizard
from .ops import *
from .version import version
from os import path

cache_filename = None
current_cache_filename = None
n_ops = 0 # ops added to solver

def normalize_stacks(in_stack, in_rstack, out_stack, vars_out):
    for i, n in enumerate(out_stack):
        if out_stack[i] != i: break
        if out_stack.count(n) != 1:
            in_stack = [x - n for x in in_stack[i:]]
            in_rstack = [x - n for x in in_rstack[i:]]
            out_stack = [x - n for x in out_stack[i:]]
            vars_out = [x - n for x in vars_out[i:]]
            break
    return in_stack, in_rstack, out_stack, vars_out

def convert_stacks(*stacks):
    symbols = {}
    counter = 0
    def convert(symbol):
        nonlocal counter
        if symbol not in symbols:
            symbols[ symbol ] = counter
            counter += 1
        return symbols[ symbol ]
    ret = []
    for i, stack in enumerate(stacks):
        if stack:
            ret.append([convert(s) for s in stack])
        else:
            ret.append([])
    return ret

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

def count_drop_nip( code ):
    s = 0
    for o in ['drop', '2drop', 'nip']:
        s += code.count(o)
    return s

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
        if count_drop_nip( c_without_pick ) >= c_with_pick.count('pick'):
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

def _choose_ops(use_pick, target):
    if target:
        use_ops = target_ops.get(target)
        if not use_ops:
            raise Exception("Unknown target:" + str(target))
        if not use_pick:
            # remove pick ops
            use_ops = [o for o in use_ops if o not in pick_ops]
    else:
        # if no target is specified, default to all ops
        use_ops = ops if use_pick else not_pick_ops
    return use_ops

def _handle_cache(use_cache, cache_file, ops):
    global cache_filename
    if cache_file:
        cache_filename = cache_file
        if cache_filename != current_cache_filename:
            cache.clear()
        cache_read()
    elif not cache and use_cache:
        cache_filename = get_cache_filename(ops)
        cache_read()

def solve(in_stack, out_stack, use_cache=True, use_pick=True,
          cache_file=None, convert=True, target=None,
          in_rstack=None, out_vars=None):
    global n_ops
    n_ops = 0
    if out_vars is None:
        return_full = False
        out_vars = list(set(out_stack))
    else:
        return_full = True
    use_ops = _choose_ops(use_pick, target)
    _handle_cache(use_cache, cache_file, use_ops)
    s_in, r_in, s_out, v_out = convert_stacks(in_stack, in_rstack, out_stack, out_vars)

    key = make_cache_key(s_in, r_in, s_out, v_out, use_pick, return_full)
    n_in, rn_in, n_out, vn_out = normalize_stacks(s_in, r_in, s_out, v_out)
    n_key = make_cache_key(n_in, r_in, n_out, vn_out, use_pick, return_full)
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
    wizard.set_rstack_in(r_in)
    wizard.set_stack_out(s_out)
    wizard.set_vars_out(v_out)
    code, cache_code = find_solution(use_ops)
    if not code or not use_cache:
        return code if convert else cache_code
    # check that the solution is valid with normalized stacks
    if n_in != s_in or r_in != rn_in or n_out != s_out:
        wizard.reset_solver()
        wizard.set_stack_in(n_in)
        wizard.set_rstack_in(rn_in)
        wizard.set_stack_out(n_out)
        wizard.set_vars_out(vn_out)
        wizard.set_code([ops.index(c) for c in cache_code])
        if wizard.verify():
            key = n_key
    cache_save(key, cache_code)
    return code if convert else cache_code

cache = {}

def make_cache_key(s_in, r_in, s_out, v_out, use_pick, ret_full):
    sep = -1
    if not ret_full:
        # if ret_full is False then the v_out was set from s_out
        # so does not need to be included
        v_out = []
    k = [-2 if use_pick else -3]
    for x in [s_in, r_in, s_out, v_out]:
        k.append(sep)
        k.extend(x)
    return tuple(k)

def get_cache_filename(used_ops):
    base = 'wizard_cache_{}_{}.txt'
    v_str = version.replace(".", "_")
    op_str = "".join([ '1' if op in used_ops else '0' for op in used_ops])
    return base.format(v_str, hex(int('0b'+op_str,2))[2:])

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
