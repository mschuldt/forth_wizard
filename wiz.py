#!/usr/bin/env python3

import forthwiz
from sys import argv

from os import path

cache_filename = 'forth_wizard_cache.txt'

def cache_read():
    if not path.exists(cache_filename):
        return
    with open(cache_filename,'r') as f:
        for line in f.readlines():
            k,v = line.split('=')
            cache[tuple(map(int, k.split()))] = v.split()

def cache_save(key, value):
    return
    cache[key] = value
    k=' '.join([str(x) for x in key])
    v=' '.join([str(x) for x in value])
    flag = 'a' if path.exists(cache_filename) else 'w'
    with open(cache_filename,flag) as f:
        f.write('{}={}\n'.format(k,v))


def fix_cache():
    # recomputes all values in the cache
    # used to verify cache entries, remove duplicates, and update cache after wizard changes
    # verify cache entries and re-write cache to remove duplicates
    cache.clear()
    cache_read()
    cache_copy = cache.copy()
    cache.clear()
    for k,v in cache.items():
        i = k.find(-1)
        s_in = k[:i-1]
        s_out = k[i:]
        result = solve(s_in, s_out, use_cache=False)
        if result == v:
            #cache_save(k, result) #TODO: don't open/close the cache file for every write
            pass
        else:
            print("dropping bad cache value in_stack={}, out_stack={}, expected={}, got={}"
                  .format(s_in, s_out, v, result))


if "--fix-cache" in argv:
    print("fixing cache...")
    #forthwiz.fix_cache()
    fix_cache()
    exit(0)

exit(0)
#argv[1:].
