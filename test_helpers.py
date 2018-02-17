
import forthwiz
import os

test_cache_file_base = "__TEST_CACHE_FILE__"
cache_files = set()

def make_cache_filename(target):
    return test_cache_file_base + target

def cache_filename(target):
    n = make_cache_filename(target)
    cache_files.add(n)
    return n

def check_solution(note, result, expected, in_stack, out_stack, out_rstack):
    if out_rstack is not None or True: # then result is type Solution
        # in this case out_stack represents the top items that
        # we expect on result.stack, so trimp the rsult stack to size
        assert(len(result.stack) >= len(out_stack))
        result_stack_top = result.stack[-len(out_stack):]
        if (result.code != expected
             or result_stack_top != out_stack
             or result.rstack != out_rstack):
            in_rstack=None #TODO
            print( 'FAILED: {}, {} -> {}, {}'
                   .format( in_stack, in_rstack, out_stack, out_rstack ))
            print( 'note:', note)
            if result.code != expected:
                print('  want code: ', expected)
                print('   got code: ', result.code)
            if result_stack_top != out_stack:
                print('  want stack: ', out_stack)
                print('   got stack: ', result_stack_top)
            if result.rstack != out_rstack:
                print('  want rstack: ', out_rstack)
                print('   got rstack: ', result.rstack)
            exit(1)
    elif result != expected:
        print('FAILED: in: {}, out: {}'.format( in_stack, out_stack ))
        print('note:', note)
        print(' want: ', expected)
        print('  got: ', result)
        exit(1)

def nth(i, lst):
    if lst:
        return lst[i]
    return []

def check(note, wiz, expected, in_stack, out_stack, out_rstack):
    if len(expected) > 0 and type(expected[0]) is list:
        for i, exp in enumerate(expected):
            result = wiz.solve()
            out_r = nth(i, out_rstack)
            check_solution(note + ", result {}".format(i), result, exp, in_stack, out_stack, out_r)
    else:
        check_solution(note, wiz.solve(), expected, in_stack, out_stack, out_rstack)

def test(in_stack, out_stack, expected, use_pick=True, target=None, in_rstack=None,
         out_rstack=[], out_vars=None, use_rstack=False):

    target = target or ""
    cache_name = cache_filename(target)
    wiz = forthwiz.Wizard()
    wiz.setup( in_stack, out_stack, use_cache=False, use_pick=use_pick,
               in_rstack=in_rstack, target=target, out_vars=out_vars,
               use_rstack=use_rstack )
    check('no cache', wiz, expected, in_stack, out_stack, out_rstack)
    wiz.setup( in_stack, out_stack, use_cache=True, use_pick=use_pick,
               cache_file=cache_name, target=target, in_rstack=in_rstack,
               out_vars=out_vars, use_rstack=use_rstack)
    check('with cache, 1st', wiz,  expected, in_stack, out_stack, out_rstack)
    wiz.setup( in_stack, out_stack, use_cache=True, use_pick=use_pick,
               cache_file=cache_name, target=target, in_rstack=in_rstack,
               out_vars=out_vars, use_rstack=use_rstack)
    check('with cache, 2st', wiz, expected, in_stack, out_stack, out_rstack)

def remove_old_cache_files():
    # remove cache files that may be present from a previous run
    for target in list(forthwiz.target_ops.keys())+[""]:
        name = make_cache_filename(target)
        if os.path.exists(target):
            os.remove(target)

def remove_cache_files():
    # check expected cache files where created and move them
    for name in cache_files:
        assert os.path.exists(name), "cache file was not created: " + name
        os.remove(name)

