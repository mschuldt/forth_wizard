import chuckmoore as wizard
from .ops import *
from os import path

version = '2.2' # also change in setup.py

def convert_code(code):
    if code is None: return code
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
    def __init__(self, code, stack, rstack, use_pick):
        self.code, self.stack, self.rstack, self.use_pick \
            = code, stack, rstack, use_pick
        self.unconverted_code = code

class Wizard:
    def __init__(self):
        self.reset()

    def reset(self):
        self.n_ops = 0 # ops added to solver
        self.symbols = {}
        self.symbol_counter = 0
        self.cache = Cache()
        self.solution_counter = 0
        self.op_map = {} # maps numbers used by solver to op names

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

    def solve_next(self):
        if self.n_ops == 0:
            self.add_all_ops()
        code = wizard.solve()
        if code is None:
            return []
        if code == -1:
            return None
        return [ self.op_map[ op ] for op in code ]

    def add_ops(self, x):
        for o in x:
            if o not in ops:
                raise Exception("Unsupported op '{}'".format(o))
            n = self.n_ops
            self.op_map[n] = o
            self.n_ops = n + 1
            wizard.add_op(ops.index(o))

    def add_pick_ops(self):      self.add_ops(pick_ops)
    def add_none_pick_ops(self): self.add_ops(not_pick_ops)
    def add_all_ops(self):       self.add_ops(ops)

    def find_solution(self):
        # find solution without pick
        wizard.reset_ops()
        wizard.save_state(0)
        self.add_ops(self.ops_without_pick)
        without_pick = self.solve_next()
        #TODO: need to revisit which state to restore to when maybe using pick
        wizard.save_state(1)
        c_without_pick = convert_code(without_pick)
        if not self.ops_with_pick:
            return c_without_pick, without_pick
        # find solution with pick
        wizard.restore_state(0)
        self.add_ops(self.ops_with_pick)
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

    def setup(self, in_stack, out_stack, use_cache=True, use_pick=True,
              cache_file=None, convert=True, target=None, ops=None,
              in_rstack=None, out_vars=None, use_rstack=False):
        """
        Setup the solver state and options.
        parameters:
        in_stack - Initial data stack state.
        out_stack - The vars that must be on the top of ending data stack.
        use_cache - If False don't use the cache. Default True.
        use_pick - If False don't use the pick instruction. Default True
        cache_file - optionally specify the cache filename.
        target - set the forth op collection to use when solving.
                 supported targets are 'gforth' and 'amforth'
        ops - a list of ops the solver may use when finding a solution.
              Specify the op "N pick" with "Npick",
              currently supported for N=[2,5].
        in_rstack - specify the initial state of the return stack.
        out_vars - the vars that must be on the data or return stack.
                   If set the in_stack represents the top of the stack.
                   vars that are in in_stack but not in out_stack can
                   will be left at the bottom of the data stack in any order.
        use_rstack - when True variables in out_vars that are not in
                     out_stack may be left on the return stack instead
                     of at the bottom of the data stack. Default False.

        vars listed in in_stack, out_stack, in_rstack, and out_vars
        can be of any hashable type.
        All vars referenced by out_stack and out_vars must be present
        in in_stack or in_rstack.
        """
        self.reset()
        if use_rstack:
            assert out_vars, "setting use_rstack without specifying out_vars"
        self.n_ops = 0
        if out_vars is None:
            out_vars = list(set(out_stack))
        use_ops = self.setup_ops(use_pick, target=target, op_list=ops)
        self._setup_cache(use_cache, cache_file, use_ops)

        s_in, r_in, s_out, v_out = \
            self.convert_stacks(in_stack, in_rstack, out_stack, out_vars)
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
        """
        Find the next solution. Returns type forthwiz.Solution
        """
        self.solution_counter += 1
        if self.use_cache:
            key = make_cache_key(self.s_in, self.r_in, self.s_out, self.v_out,
                                 self.use_pick, self.use_rstack,
                                 self.solution_counter)
            solution = self.get_cached_solution(key, self.convert)
            if solution:
                #setup solver state for next call
                #as if it had found the solution
                wizard.reset_ops()
                self.add_ops(self.ops_with_pick
                             if solution.use_pick
                             else self.ops_without_pick)
                wizard.set_next_code([ops.index(o)
                                      for o in solution.unconverted_code])
                return solution

        code, cache_code = self.find_solution()
        solution_stack = wizard.get_stack()
        solution_rstack = wizard.get_return_stack()
        c_stacks = self.convert_stacks_back(solution_stack, solution_rstack)
        if not code or not self.use_cache:
            ret_code = code if self.convert else cache_code
            return Solution(ret_code, c_stacks[0], c_stacks[1], self.use_pick)

        if self.use_cache:
            self.cache.save(key, cache_code, solution_stack, solution_rstack)
        ret_code = code if self.convert else cache_code
        return Solution(ret_code, c_stacks[0], c_stacks[1], self.use_pick)

    def solve_many(self, n, max_solutions=None):
        """
        Find all solutions with length N.
        MAX_SOLUTIONS can be used to limit the number of solutions found
        """
        solutions = []
        count = 0
        while True:
            s = self.solve()
            if s.code is None or len(s.code) > n:
                return solutions
            solutions.append(s)
            if max_solutions and count == max_solutions:
                return solutions

    def solutions(self):
        """
        Find all solutions with the minimal code length.
        """
        s = self.solve()
        if not s.code:
            return None
        n = len(s.code)
        return [s] + self.solve_many(n)

    def get_cached_solution(self, key, convert):
        solution = self.cache.get(key)
        if solution:
            solution.stack = self.convert_stacks_back(solution.stack)[0]
            solution.rstack = self.convert_stacks_back(solution.rstack)[0]
            if convert:
                solution.code = convert_code(solution.code)
                return solution
        return None

    def setup_ops(self, use_pick, target=None, op_list=None):
        if target:
            use_ops = target_ops.get(target)
            if not use_ops:
                raise Exception("Unknown target:" + str(target))
            if not use_pick:
                # remove pick ops
                use_ops = [o for o in use_ops if o not in pick_ops]
        elif op_list:
            use_ops = op_list
        else:
            # if no target is specified, default to all ops
            use_ops = ops if use_pick else not_pick_ops

        ops_with_pick, ops_without_pick = [], []
        for o in use_ops:
            (ops_with_pick if o in pick_ops else ops_without_pick).append(o)
        self.ops_with_pick = ops_with_pick
        self.ops_without_pick = ops_without_pick
        return use_ops


def make_cache_key(s_in, r_in, s_out, v_out, use_pick, use_rstack, counter):
    sep = -1
    k = [-2 if use_pick else -3]
    use_r = [1 if use_rstack else 0]
    for x in [s_in, r_in, s_out, v_out, use_r, [counter]]:
        k.append(sep)
        if x:
            k.extend(x)
    return tuple(k)

def get_cache_filename(used_ops):
    base = 'wizard_cache_{}_{}.txt'
    v_str = version.replace(".", "_")
    op_str = "".join([ '1' if op in used_ops else '0' for op in used_ops])
    return base.format(v_str, hex(int('0b1'+op_str,2))[2:])

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
                use_pick = True if k.split('-1')[0] == -2 else False
                s = Solution(code.split(), read_elts(stack),
                             read_elts(rstack), use_pick)
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

def solve_stacks(in_stack, out_stack, use_cache=True, use_pick=True,
                 cache_file=None, convert=True, target=None):
    """Helper function that solves a simple data stack transformation"""
    wiz = Wizard()
    wiz.setup(in_stack, out_stack, use_cache=use_cache, use_pick=use_pick,
              cache_file=cache_file, convert=convert, target=target)
    solution = wiz.solve()
    return solution.code
