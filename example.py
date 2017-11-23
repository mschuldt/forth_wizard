#!/usr/bin/env python3

import forthwiz as wiz
import time

wiz.set_stacks( in_stack=[1,2,3,4,5],
                out_stack=[5,1,5,3,4] )

print("solutions:")
t0 = time.time()

for i in range(10):
    print(" ".join( wiz.solve_next() ) )

print("time: ", time.time() - t0)
