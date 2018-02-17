import chuckmoore as wizard
from .ops import *
from .version import version
from os import path

def convert_code(code):
    ret = []
    for x in code:
        c = code_map.get(x)
        ret.extend(c) if c else ret.append(x)
    return ret

def count_drop_nip(code):
    s = 0
    for o in ['drop', '2drop', 'nip']:
        s += code.count(o)
    return s

class Solution:
    def __init__(self, code, stack, rstack):
        self.code, self.stack, self.rstack = code, stack, rstack

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

class Wizard:
    def __init__(self):
        self.n_ops = 0 # ops added to solver
        self.symbols = {}
        self.symbol_counter = 0
        self.cache = Cache()

    def convert_stacks(self, *stacks):
        self.symbols.clear()
        self.symbol_counter = 0
        def convert(symbol):
            if symbol not in self.symbols:
                self.symbols[ symbol ] = self.symbol_counter
                self.symbol_counter += 1
            return self.symbols[ symbol ]
        ret = []
        for i, stack in enumerate(stacks):
            if stack:
                ret.append([convert(s) for s in stack])
            else:
                ret.append([])
        return ret

    def convert_stacks_back(self, *stacks):
        mapping = {v:k for k,v in self.symbols.items()}
        ret = []
        for stack in stacks:
            if stack:
                ret.append([mapping[v] for v in stack])
            else:
                ret.append([])
        return ret

    def set_stacks(self, in_stack, out_stack):
        s_in, s_out = self.convert_stacks(in_stack, out_stack)
        wizard.init()
        wizard.set_stack_in(s_in)
        wizard.set_stack_out(s_out)

    def solve_next(self):
        if self.n_ops == 0:
            self.add_all_ops()
        code = wizard.solve()
        if code is None:
            return []
        if code == -1:
            return None
        return [ ops[ op ] for op in code ]

    def add_ops(self, x):
        self.n_ops += len(x)
        for o in x:
            if o not in x:
                raise Exception("Unsupported op '{}'".format(o))
            wizard.add_op(ops.index(o))

    def add_pick_ops(self):      self.add_ops(pick_ops)
    def add_none_pick_ops(self): self.add_ops(not_pick_ops)
    def add_all_ops(self):       self.add_ops(ops)


    def find_solution(self, ops):
        ops_with_pick, ops_without_pick = [], []
        for o in ops:
            (ops_with_pick if o in pick_ops else ops_without_pick).append(o)
        # find solution without pick
        wizard.reset_ops()
        wizard.save_state(0)
        self.add_ops(ops_without_pick)
        without_pick = self.solve_next()
        wizard.save_state(1) #TODO: need to revisit which state to restore to when maybe using pick
        c_without_pick = convert_code(without_pick)
        if not ops_with_pick or True:
            return c_without_pick, without_pick
        # find solution with pick
        wizard.restore_state(0)
        self.add_ops(ops_with_pick)
        with_pick = self.solve_next()
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
        wizard.restore_state(1)
        return c_without_pick, without_pick

    def _setup_cache(self, use_cache, cache_file, ops):
        cache = self.cache
        if cache_file:
            cache.cache_filename = cache_file
            if cache.cache_filename != cache.current_cache_filename:
                cache.clear()
            cache.read()
        elif not cache.cache and use_cache:
            cache.cache_filename = get_cache_filename(ops)
            cache.read()

    def solve1(self, in_stack, out_stack, use_cache=True, use_pick=True,
               cache_file=None, convert=True, target=None,
               in_rstack=None, out_vars=None, use_rstack=False):
        """setup and solve solve for 1 solution"""
        self.setup(in_stack, out_stack, use_cache=use_cache, use_pick=use_pick,
                   cache_file=cache_file, convert=convert, target=target,
                   in_rstack=in_rstack, out_vars=out_vars, use_rstack=use_rstack)
        solution = self._solve()
        if out_vars is None:
            return solution.code
        return solution

    def setup(self, in_stack, out_stack, use_cache=True, use_pick=True,
               cache_file=None, convert=True, target=None,
               in_rstack=None, out_vars=None, use_rstack=False):
        if use_rstack:
            assert out_vars, "setting use_rstack without specifying out_vars"
        self.n_ops = 0
        if out_vars is None:
            out_vars = list(set(out_stack))
        self.use_ops = _choose_ops(use_pick, target)
        self._setup_cache(use_cache, cache_file, self.use_ops)

        s_in, r_in, s_out, v_out = self.convert_stacks(in_stack, in_rstack, out_stack, out_vars)
        self.s_in = s_in
        self.r_in = r_in
        self.s_out = s_out
        self.v_out = v_out
        self.use_pick = use_pick
        self.use_rstack = use_rstack
        self.use_cache = use_cache
        self.convert = convert
        wizard.init()
        wizard.set_stack_in(s_in)
        wizard.set_rstack_in(r_in)
        wizard.set_stack_out(s_out)
        wizard.set_vars_out(v_out)
        wizard.use_rstack(use_rstack)

    def solve(self):

        if self.use_cache:
            key = make_cache_key(self.s_in, self.r_in, self.s_out, self.v_out,
                                 self.use_pick, self.use_rstack)
            solution = self.get_cached_solution(key, self.convert)
            if solution:
                self.s_in = solution.stack
                self.r_in = solution.rstack
                return solution

        code, cache_code = self.find_solution(self.use_ops)
        solution_stack = wizard.get_stack()
        solution_rstack = wizard.get_return_stack()
        c_stacks = self.convert_stacks_back(solution_stack, solution_rstack)
        if not code or not self.use_cache:
            ret_code = code if self.convert else cache_code
            return Solution(ret_code, c_stacks[0], c_stacks[1])

        self.s_in = solution_stack
        self.r_in = solution_rstack

        if self.use_cache:
            self.cache.save(key, cache_code, solution_stack, solution_rstack)
        ret_code = code if self.convert else cache_code
        return Solution(ret_code, c_stacks[0], c_stacks[1])

    def get_cached_solution(self, key, convert):
        solution = self.cache.get(key)
        if solution:
            solution.stack = self.convert_stacks_back(solution.stack)[0]
            solution.rstack = self.convert_stacks_back(solution.rstack)[0]
            if convert:
                solution.code = convert_code(solution.code)
                return solution
        return None

def make_cache_key(s_in, r_in, s_out, v_out, use_pick, use_rstack):
    sep = -1
    k = [-2 if use_pick else -3]
    use_r = [1 if use_rstack else 0]
    for x in [s_in, r_in, s_out, v_out, use_r]:
        k.append(sep)
        k.extend(x or [0])
    return tuple(k)

def get_cache_filename(used_ops):
    base = 'wizard_cache_{}_{}.txt'
    v_str = version.replace(".", "_")
    op_str = "".join([ '1' if op in used_ops else '0' for op in used_ops])
    return base.format(v_str, hex(int('0b'+op_str,2))[2:])

class Cache:
    def __init__(self):
        self.cache = {}
        self.cache_filename = None
        self.current_cache_filename = None

    def read(self):
        def read_elts(x):
            return list(map(int,x.split()))
        if not path.exists(self.cache_filename):
            return
        with open(self.cache_filename,'r') as f:
            for line in f.readlines():
                k,v = line.split('=')
                code, stack, rstack = v.split('&')
                s = Solution(code.split(), read_elts(stack), read_elts(rstack))
                self.cache[tuple(map(int, k.split()))] = s
        self.current_cache_filename = self.cache_filename

    def save(self, key_, code_, stack_, rstack_):
        def join(lst):
            if not lst:
                return ''
            return ' '.join([str(x) for x in lst])
        value="&".join([join(code_), join(stack_), join(rstack_)])
        key = join(key_)
        self.cache[key] = value
        flag = 'a' if path.exists(self.cache_filename) else 'w'
        with open(self.cache_filename,flag) as f:
            f.write('{}={}\n'.format(key, value))

    def get(self, key):
        return self.cache.get(key)

    def clear(self):
        self.cache.clear()
