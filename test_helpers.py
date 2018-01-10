
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

