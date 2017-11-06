#include "wiz.c"

void next_solution() {
  if (solve()) {
    print_solution();
  } else {
    printf("no solution");
    exit(0);
  }
}

int test () {
  _push(stack_in, 1);
  _push(stack_in, 2);
  _push(stack_in, 3);
  _push(stack_in, 4);
  _push(stack_in, 5);

  _push(stack_out, 5);
  _push(stack_out, 1);
  _push(stack_out, 5);
  _push(stack_out, 3);
  _push(stack_out, 4);

  collect_unique_symbols();

  for(int i = 0; i < 10; i ++ ) {
    next_solution();
  }
}

int main(int argc, char **argv) {
  init();
  test();   // 5.721 secs
}
