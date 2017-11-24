// gcc example.c -g -O3 -o example

#include "solver.c"

void next_solution() {
  if (solve()) {
    print_solution();
  } else {
    printf("no solution");
    exit(0);
  }
}

int test () {
  list_push(stack_in, 1);
  list_push(stack_in, 2);
  list_push(stack_in, 3);
  list_push(stack_in, 4);
  list_push(stack_in, 5);

  list_push(stack_out, 5);
  list_push(stack_out, 1);
  list_push(stack_out, 5);
  list_push(stack_out, 3);
  list_push(stack_out, 4);

  collect_unique_symbols();

  for(int i = 0; i < 10; i ++ ) {
    next_solution();
  }
}

int main(int argc, char **argv) {
  init();
  add_all_ops();
  test();   // 0.877 secs
            // 2.937 secs with pick ops ({3-6} pick)
}
