#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <assert.h>

#define N_CODE_REGS 3

typedef struct Slice {
  char *data;
  int len;
  int cap;
} Slice;

typedef struct Op {
  bool (*fn)(void);
  char* name;
} Op;

Slice *stack;
Slice *rstack;
Slice *stack_in;
Slice *rstack_in;
Slice *stack_out;
Slice *vars_out;
Slice **stack_history;
Slice **rstack_history;

Slice *code;
Slice **code_regs;
Slice *solution;

int max_code_length = 15;
int stack_size = 30;

int max_ops;
bool use_rstack;

Slice* new_slice(int cap) {
  Slice* stack = (Slice*)calloc(sizeof(Slice), 1);
  stack->data = (char*)calloc(sizeof(char), cap);
  stack->cap = cap;
  stack->len = 0;
  return stack;
}

int slice_equal(Slice *in, Slice *out) {
  int len = in->len;
  if (len != out->len){
    return false;
  }
  int i;
  for (i=0; i<len; i++){
    if (in->data[i] != out->data[i]){
      return false;
    }
  }
  return true;
}

int slice_post_equal(Slice *slice, Slice *post) {
  // test that the n items from Slice POST match
  // the last n items from Slice SLICE
  int post_end = post->len - 1;
  int slice_end = slice->len - 1;
  if (post_end < 0){
    return true;
  }
  if (post_end > slice_end){
    return false;
  }
  int i;
  for (i=post_end; i>=0; i--){
    if (slice->data[slice_end-i] != post->data[post_end-i]){
      return false;
    }
  }
  return true;
}

Slice* slice_clone(Slice *in) {
  Slice *s = new_slice(in->cap);
  int len = in->len;
  int i;
  for(i = 0; i < len; i++){
    s->data[i] = in->data[i];
  }
  s->len = len;
  return s;
}

void slice_copy(Slice *to, Slice *from) {
  assert( from->len <= to->cap && "destination slice is too small" );
  int len = from->len;
  to->len = len;
  int i;
  for(i = 0; i < len; i++){
    to->data[i] = from->data[i];
  }
}

void slice_clear(Slice *slice) {
  slice->len = 0;
}

static inline void slice_push(Slice* s, char v) {
  assert(s->len < s->cap && "stack overflow");
  s->data[ s->len ] = v;
  s->len++;
}

static inline char slice_pop(Slice* s) {
  assert(s->len >= 0 && "stack underflow");
  int len = s->len - 1;
  char ret = s->data[len];
  s->len = len;
  return ret;
}

static inline int pick(int i) { return stack->data[stack->len - i ]; }
static inline int rpick(int i) { return rstack->data[rstack->len - i ]; }

static inline void push(int v) { slice_push(stack, v); }
static inline void rpush(int v) { slice_push(rstack, v); }

static inline int pop(void) { return slice_pop(stack); }
static inline int rpop(void) { return slice_pop(rstack); }

bool member(char *s, unsigned int len, char n) {
  int i;
  for(i = 0; i < len; i++) {
    if( s[i] == n) {
      return true;
    }
  }
  return false;
}

static inline bool slice_member(Slice* s, char n) {
  return member(s->data, s->len, n);
}

void unshift( Slice *s, char v ) {
  assert( s->len < s->cap && "unshift: no room");
  int i;
  for(i=s->len-1; i >= 0; i--) {
    s->data[i+1] = s->data[i];
  }
  s->data[0] = v;
  s->len++;
}

void slice_print( Slice *s ) {
  int i;
  for (i=0; i < s->len; i ++){
    printf("%d ", s->data[i]);
  }
  printf("\n");
}

bool check_symbols(void);

#define CHECK_SYMS if (!check_symbols()) return false

#define CHECK_STACK_1 if (stack->len < 1) return false
#define CHECK_STACK_2 if (stack->len < 2) return false
#define CHECK_STACK_3 if (stack->len < 3) return false
#define CHECK_STACK_4 if (stack->len < 4) return false
#define CHECK_STACK_5 if (stack->len < 5) return false
#define CHECK_STACK_6 if (stack->len < 6) return false

#define CHECK_RSTACK_1 if (rstack->len < 1) return false
#define CHECK_RSTACK_2 if (rstack->len < 2) return false

////////////////////////////////////////////////////////////////////////////////
// forth ops

bool dup_(void) {
  CHECK_STACK_1;
  push(pick(1));
  return true;
}

bool drop(void) {
  CHECK_STACK_1;
  pop();
  CHECK_SYMS;
  return true;
}

bool swap(void) {
  CHECK_STACK_2;
  char n1 = pop();
  char n2 = pop();
  push(n1);
  push(n2);
  return true;
}

bool over(void) {
  CHECK_STACK_2;
  push(pick(2));
  return true;
}

bool rot(void) {
  CHECK_STACK_3;
  char n1 = pop();
  char n2 = pop();
  char n3 = pop();
  push(n2);
  push(n1);
  push(n3);
  return true;
}

bool tor(void) {
  CHECK_STACK_1;
  rpush(pop());
  return true;
}

bool rfrom(void) {
  CHECK_RSTACK_1;
  push(rpop());
  return true;
}

bool dup2_(void) {
  CHECK_STACK_2;
  push(pick(2));
  push(pick(2));
  return true;
}

bool dup3(void) {
  CHECK_STACK_3;
  push(pick(3));
  push(pick(3));
  push(pick(3));
  return true;
}

bool drop2(void) {
  CHECK_STACK_2;
  stack->len -= 2;
  CHECK_SYMS;
  return true;
}

bool swap2(void) {
  CHECK_STACK_4;
  char n1 = pop();
  char n2 = pop();
  char n3 = pop();
  char n4 = pop();
  push(n2);
  push(n1);
  push(n4);
  push(n3);
  return true;
}

bool over2(void) {
  CHECK_STACK_4;
  push(pick(4));
  push(pick(4));
  return true;
}

bool rot2(void) {
  CHECK_STACK_6;
  char n1 = pop();
  char n2 = pop();
  char n3 = pop();
  char n4 = pop();
  char n5 = pop();
  char n6 = pop();
  push(n4);
  push(n3);
  push(n2);
  push(n1);
  push(n6);
  push(n5);
  return true;
}

bool nip(void) {
  CHECK_STACK_2;
  char n = pop();
  pop();
  push(n);
  CHECK_SYMS;
  return true;
}

bool tuck(void) {
  CHECK_STACK_2;
  char n1 = pop();
  char n2 = pop();
  push(n1);
  push(n2);
  push(n1);
  return true;
}

bool mrot(void) {
  CHECK_STACK_3;
  char n1 = pop();
  char n2 = pop();
  char n3 = pop();
  push(n1);
  push(n3);
  push(n2);
  return true;
}

bool rfetch(void) {
  CHECK_RSTACK_1;
  push(rpick(1));
  return true;
}

bool tor2(void) {
  CHECK_STACK_2;
  char n1 = pop();
  char n2 = pop();
  rpush(n2);
  rpush(n1);
  return true;
}

bool rfrom2(void) {
  CHECK_RSTACK_2;
  char n1 = rpop();
  char n2 = rpop();
  push(n2);
  push(n1);
  return true;
}

bool rfetch2(void) {
  CHECK_RSTACK_2;
  push(rpick(2));
  push(rpick(1));
  return true;
}

bool pick2(void) {
  CHECK_STACK_3;
  push(pick(3));
  return true;
}

bool pick3(void) {
  CHECK_STACK_4;
  push(pick(4));
  return true;
}

bool pick4(void) {
  CHECK_STACK_5;
  push(pick(5));
  return true;
}

bool pick5(void) {
  CHECK_STACK_6;
  push(pick(6));
  return true;
}

// Note: remember to update corresponding list in forthwiz/ops.py
Op ops[] = { { dup_, "dup" },
             { drop, "drop" },
             { swap, "swap" },
             { over, "over" },
             { rot, "rot" },
             { tor, ">r" },
             { rfrom, "r>" },
             { dup2_, "2dup" },
             { drop2, "2drop" },
             { swap2, "2swap" },
             { over2, "2over" },
             { rot2, "2rot" },
             { nip, "nip" },
             { tuck, "tuck" },
             { mrot, "-rot" },
             { rfetch, "r@" },
             { tor2, "2>r" },
             { rfrom2, "2r>" },
             { rfetch2, "2r@" },
             { dup3, "3dup"},
             { pick2, "2pick" },
             { pick3, "3pick" },
             { pick4, "4pick" },
             { pick5, "5pick" },
             { NULL, NULL }};

typedef bool (*op_fn_t)(void);
op_fn_t *_ops;

int n_ops_used;

bool add_op(int op) {
  if (op > max_ops) {
    printf("Error: invalid op: %d\n", op);
    exit(1);
  }
  _ops[n_ops_used++] = ops[op].fn;
  return true;
}
////////////////////////////////////////////////////////////////////////////////

void next(void) {
  int i = code->len - 1;
  int max = n_ops_used - 1;

  code->data[i]++;

  while (code->data[i] > max) {
    code->data[i] = 0;
    if (i == 0) {
      unshift(code, 0);
    } else {
      code->data[--i]++;
    }
  }
}

void skip_code(int n) {
  int max = n_ops_used - 1;
  int i;
  for (i=n+1; i < code->len; i++) {
    code->data[i] = max;
  }
}

void validate_stacks(void) {
  int i;
  for(i = 0; i < stack_out->len; i++ ) {
    if ( !slice_member(stack_in, stack_out->data[i] )
         || !slice_member(rstack_in, stack_out->data[i] )) {
      printf("ERROR: output stack value not present in input stacks\n");
      exit(1);
    }
  }
}

// check that all symbols are present in at least one of the stacks
bool check_symbols()
{
  int i;
  for (i = 0; i < vars_out->len; i++) {
    if(!slice_member(stack, vars_out->data[i])
       && !slice_member(rstack, vars_out->data[i]))
      return false;
  }
  return true;
}

bool noop(int n) {
  if(slice_equal(stack, stack_in) && slice_equal(rstack, rstack_in)){
    return true;
  }
  int i;
  for (i=0; i < n; i++ ){
    if(slice_equal(stack_history[i], stack) && slice_equal(rstack_history[i], rstack))
      return true;
  }
  return false;
}

static inline bool
check_stack_repeats(void){
  // check that symbols below stack_out values are not repeats
  // of values in stack_out
  int end = stack_out->len;
  int len = stack->len;
  int i, j;
  for (i = 0; i < end; i++){ // for item in bottom portion
    int sym = stack->data[i];
    for (j=end; j<len; j++ ){ // for item in top portion
      if (sym == stack->data[j]){
        return false;
      }
    }
  }
  return true;
}

static inline bool
check_extra_vars(void){
  // check that only values present in vars_out
  // are present in the stacks
  int i;
  for (i=0; i<stack->len; i++){
    if (!slice_member(vars_out, stack->data[i])){
      return false;
    }
  }
  for (i=0; i<rstack->len; i++){
    if (!slice_member(vars_out, rstack->data[i])){
      return false;
    }
  }
  return true;
}

static inline bool
check_rstack_repeats(void){
  // check that all symbols present in the rstack are
  // not repeated on the data stack
  int len = rstack->len;
  if( !use_rstack && len != 0 ) {
    return false;
  }
  int i;
  for(i=0; i<len; i++){
    if (slice_member(stack, rstack->data[i])){
      return false;
    }
  }
  return true;
}

bool verify_code(void) {
  slice_copy(stack, stack_in);
  slice_copy(rstack, rstack_in);
  int i;
  for(i = 0; i < code->len; i++) {
    if( !_ops[(int)(code->data[i])]()
        || noop(i) ){
      skip_code(i);
      return false;
    }
    slice_copy(stack_history[i], stack);
    slice_copy(rstack_history[i], rstack);
  }
  if (slice_post_equal(stack, stack_out) // check that top of the stack matches
      && check_stack_repeats()
      && check_extra_vars()
      && check_rstack_repeats()){
    return true;
  }
  return false;
}

void add_all_ops(void) {
  int op=0;
  while (ops[op].fn != NULL) {
    add_op(op++);
  }
}

void print_solution(void) {
  int i;
  for(i=0; i< solution->len; i++){
    printf("%s ", ops[(int)(solution->data[i])].name);
  }
  printf("\n");
}

bool solve_next(void) {
  if (!n_ops_used){
    printf("Error: calling solve before adding ops\n");
    exit(1);
  }
  // case for when in and out states are the same
  if (slice_equal(stack_in, stack_out)
      && rstack_in->len == 0){
    slice_copy(stack, stack_in);
    slice_clear(code);
    slice_clear(rstack);
    return true;
  }
  while( code->len <= max_code_length ) {
    if( verify_code() ) {
      return true;
    }
    next();
  }
  return false;
}

void count_ops(void) {
  max_ops=0;
  while (ops[max_ops].fn != NULL) {
    max_ops++;
  }
}

void set_stack_size(int n){
  stack_size = n;
}

void set_stack_in( int *values, int len ) {
  int i;
  for (i = 0; i < len; i++) {
    slice_push(stack_in, values[i]);
  }
  //printf("in stack\n");
  //slice_print(stack_in);
}

void set_rstack_in( int *values, int len ) {
  int i;
  for (i = 0; i < len; i++) {
    slice_push(rstack_in, values[i]);
  }
}

void set_stack_out( int *values, int len ) {
  int i;
  for (i = 0; i < len; i++) {
    slice_push(stack_out, values[i]);
  }
  validate_stacks();
  //printf("out stack\n");
  //slice_print(stack_out);
}

bool initialized = false;

void reset_ops(void) {
  n_ops_used = 0;
}

void reset_solver(void) {
     slice_clear(code);
     slice_push(code,0);
     slice_clear(solution);
}

void reset(void) {
  reset_solver();
  slice_clear(stack_in);
  slice_clear(rstack_in);
  slice_clear(stack_out);
  reset_ops();
  use_rstack = false;
}

void save_state(unsigned int i){
  assert(i < N_CODE_REGS);
  slice_copy(code_regs[i], code);
}

void restore_state(unsigned int i){
  assert(i < N_CODE_REGS);
  slice_copy(code, code_regs[i]);
}

void init(void) {
  if ( initialized ) {
    reset();
    return;
  }
  stack_size=23;
  max_code_length = 10;
  stack_in = new_slice(stack_size);
  rstack_in = new_slice(stack_size);
  stack_out = new_slice(stack_size);
  stack = new_slice(stack_size);
  rstack = new_slice(stack_size);
  vars_out = new_slice(stack_size);
  stack_history = (Slice**)calloc(sizeof(Slice*), max_code_length);
  rstack_history = (Slice**)calloc(sizeof(Slice*), max_code_length);
  int i;
  for(i = 0; i < max_code_length; i++) {
      stack_history[i] = new_slice(stack_size);
      rstack_history[i] = new_slice(stack_size);
  }

  count_ops(); //sets max_ops
  _ops = (op_fn_t*)calloc(sizeof(bool (*)(void)), max_ops);
  n_ops_used = 0;

  code = new_slice(max_code_length);
  code_regs = (Slice**)calloc(sizeof(Slice*), N_CODE_REGS);
  for(i = 0; i < N_CODE_REGS; i++) {
    code_regs[i] = new_slice(max_code_length);
  }
  solution = new_slice(max_code_length);
  slice_push(code,0);
  initialized = true;
  use_rstack = false;
}

bool solve(void) {
  if (!solve_next()) {
    return false;
  }
  slice_copy(solution, code);
  if( code->len > 0 ) {
    next();
  }
  return true;
}
