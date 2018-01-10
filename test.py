#!/usr/bin/env python3

import forthwiz as wiz
import os

test_cache_file_base = "__TEST_CACHE_FILE__"
cache_files = set()

def make_cache_filename(target):
    return test_cache_file_base + target

def cache_filename(target):
    n = make_cache_filename(target)
    cache_files.add(n)
    return n

def check(note, result, expected, in_stack, out_stack):
    if result != expected:
        print( 'FAILED: in: {}, out: {}'.format( in_stack, out_stack ))
        print( 'note:', note)
        print( ' want: ', expected)
        print( '  got: ', result)
        exit(1)

def test(in_stack, out_stack, expected, use_pick=True, target=None, in_rstack=None):
    target = target or ""
    cache_name = cache_filename(target)
    result = wiz.solve( in_stack, out_stack, use_cache=False, use_pick=use_pick,
                        in_rstack=in_rstack, target=target )
    check('no cache', result, expected, in_stack, out_stack)
    result = wiz.solve( in_stack, out_stack, use_cache=True, use_pick=use_pick,
                        cache_file=cache_name, target=target, in_rstack=in_rstack )
    check('with cache, 1st', result, expected, in_stack, out_stack)
    result = wiz.solve( in_stack, out_stack, use_cache=True, use_pick=use_pick,
                        cache_file=cache_name, target=target, in_rstack=in_rstack )
    check('with cache, 2st', result, expected, in_stack, out_stack)

def remove_old_cache_files():
    # remove cache files that may be present from a previous run
    for target in list(wiz.target_ops.keys())+[""]:
        name = make_cache_filename(target)
        if os.path.exists(target):
            os.remove(target)

def remove_cache_files():
    # check expected cache files where created and move them
    for name in cache_files:
        assert os.path.exists(name), "cache file was not created: " + name
        os.remove(name)

def runtests():
    test(['a', 'b'], ['a', 'b', 'b'], ['dup'])
    test(['t1', 't2'], ['t1'], ['drop'])
    test([1, 2], [ 2, 1], ['swap'])
    test([1, 2], [ 1, 2, 1], ['over'])
    test([1, 2, 3], [ 2, 3, 1], ['rot'])
    test([1, 2, 3, 4], [1, 2, 3, 4, 3, 4], ['2dup'])
    test([1, 2, 3], [1], ['2drop'])
    test([1, 2, 3, 4], [3, 4, 1, 2], ['2swap'])
    test([1, 2, 3, 4], [1,2,3,4,1,2], ['2over'])
    test([1, 2, 3, 4, 5, 6, 7], [1, 4, 5, 6, 7, 2, 3] , ['2rot'])
    test([1, 2, 3], [1, 3] , ['nip'])
    test([1, 2, 3], [1, 3, 2, 3] , ['tuck'])
    test([1, 2, 3, 4], [1, 4, 2, 3] , ['-rot'])
    #TODO: >r, r>, 2>r, 2r>, rfetch2, rfetch
    test(['a', 'b'], ['a', 'b'], [])
    test(['a', '+_arg1'], ['+_arg1', 'a', 'a'], ['swap', 'dup'])
    test(['a', 'b'],['a', 'b', 'a', 'b'], ['2dup'] )
    test([0,1,2], [0,1,2,0], ['2', 'pick'])
    test([0,1,2,3], [0,1,2,3,0], ['3', 'pick'])
    test([0,1,2,3,4], [0,1,2,3,4,0], ['4', 'pick'])
    test([0,1,2,3,4,5], [0,1,2,3,4,5,0], ['5', 'pick'])
    a=[0, 1, 2, 3, 4, 5, 6]
    b=[0, 1, 2, 3, 4, 5, 6, 3]
    test(a, b, ['3', 'pick'], use_pick=True)
    test(a, b, ['2over', 'drop'], use_pick=False)
    a=[0, 1, 2]
    b=[0, 2, 0, 1]
    test(a,b, ['2', 'pick', 'rot'])
    test(a,b, ['swap', '>r', 'over', 'r>'], use_pick=False, target='gforth')
    test(a,b, ['3dup', '2drop', 'rot'], use_pick=False)
    a=[0, 1, 2, 3]
    b=[0, 1, 2, 3, 1]
    test(a, b, ['2', 'pick'])
    test(a, b, ['2over', 'nip'], use_pick=False)
    a=[0, 1, 2, 3, 4, 5]
    b=[0, 1, 2, 3, 4, 5, 1]
    test(a, b, ['4', 'pick'])
    test(a, b, ['>r', '2over', 'drop', '>r', '2r>'], use_pick=False)
    test([0,1,2,3], [0,1,2,3,1,2,3], ['3dup'])
    #test(['x', 'y'], ['x','error', 'y'], ['swap', 'dup'])
    test([], [0], ['r>'], in_rstack=[0])
    test([], [0, 1], ['2r>'], in_rstack=[0, 1])
    test([0], [0], ['r>', 'drop'], in_rstack=[1])
    test([0], [1, 0], ['>r', '2r>'], in_rstack=[1])
    test([], [0, 1], ['r>', 'r>'], in_rstack=[1, 0])

if __name__ == '__main__':

    remove_old_cache_files()
    runtests()
    remove_cache_files()

    print("ok")
