#!/usr/bin/env python3

import forthwiz as wiz

wiz.init()
wiz.set_stack_in([1,2,3,4,5])
wiz.set_stack_out([5,1,5,3,4])
print("solutions:")
for i in range(10):
    print(wiz.solve())

