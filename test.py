#!/usr/bin/env python3

import forthwiz as wiz

def test(in_stack, out_stack, expected):
    result = wiz.solve( in_stack, out_stack, use_cache=False )
    if result != expected:
        print( 'FAILED: in: {}, out: {}'.format( in_stack, out_stack ))
        print( ' want: ', expected)
        print( '  got: ', result)
        exit(1)

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
    test( ['a', 'b'],['a', 'b', 'a', 'b'], ['2dup'] )
    #test(['x', 'y'], ['x','error', 'y'], ['swap', 'dup'])

if __name__ == '__main__':
    runtests()
    print("ok")
