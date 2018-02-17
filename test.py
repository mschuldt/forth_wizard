#!/usr/bin/env python3

from test_helpers import *

def runtests():
    assert forthwiz.solve_stacks([1,2],[1,2,2]) == ['dup']
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
    #test return stack
    a=['a','b','c','h','i']
    out_vars = ['a', 'h', 'i']
    out_top=['a','h']
    test(a, out_top, ['2swap', '2drop', '-rot'],out_vars=out_vars, use_rstack=False, out_rstack=[])
    test(a, out_top, ['>r', 'nip', 'nip'], out_vars=out_vars, use_rstack=True, out_rstack=['i'])
    test([0], [0,1], ['r>'], in_rstack=[2,1], out_vars=[0,1,2], use_rstack=True, out_rstack=[2])
    # test multiple solutions
    test(['a', 'b'], ['a', 'b', 'b'], [['dup'],
                                       ['2dup', 'nip'],
                                       ['tuck', 'rot'],
                                       ['swap', 'over', 'rot'],
                                       ['over', 'over', 'nip'],
                                       ['>r', 'r@', 'r>']])

if __name__ == '__main__':

    remove_old_cache_files()
    runtests()
    remove_cache_files()

    print("ok")
