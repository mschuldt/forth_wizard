#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

void assert(bool x, char *msg){
  if(x){
    //printf("OK: assertion: %s\n", msg);
    return;
  }
  printf("failed assertion: %s\n", msg);
  exit(1);
}

typedef struct List {
  int *data;
  int len;
  int size;
} List;

typedef struct Op {
  bool (*fn)(void);
  char* name;
} Op;

List *stack;
List *rstack;
List *stack_in;
List *stack_out;
//List *rstack_in;
List **stack_history;
List **rstack_history;

List *code;
List *solution;
List *unique_symbols;

int max_code_length = 15;
int stack_size = 30;

int n_ops;

List* new_list(int size) {
  List* stack = (List*)calloc(sizeof(List), 1);
  stack->data = (int*)calloc(sizeof(int), size);
  stack->size = size;
  stack->len = 0;
  return stack;
}

int list_equal(List *in, List *out) {
  int len = in->len;
  if (len != out->len){
    return false;
  }
  for (int i=0; i<len; i++){
    if (in->data[i] != out->data[i]){
      return false;
    }
  }
  return true;
}

List* list_clone(List *in) {
  List *s = new_list(in->size);
  int len = in->len;
  for(int i = 0; i < len; i++){
    s->data[i] = in->data[i];
  }
  s->len = len;
  return s;
}

void list_copy(List *to, List *from) {
  assert( from->len <= to->size, "destination list is too small" );
  int len = from->len;
  to->len = len;
  for(int i = 0; i < len; i++){
    to->data[i] = from->data[i];
  }
}

void list_clear(List *list) {
  list->len = 0;
}

static inline void _push(List* s, int v) {
  assert(s->len < s->size, "stack overflow");
  s->data[ s->len ] = v;
  s->len++;
}

static inline int _pop(List* s) {
  assert(s->len >= 0, "stack underflow");
  int len = s->len - 1;
  int ret = s->data[len];
  s->len = len;
  return ret;
}

static inline int pick(int i) { return stack->data[stack->len - i ]; }
static inline int rpick(int i) { return rstack->data[rstack->len - i ]; }

static inline void push(int v) { _push(stack, v); }
static inline void rpush(int v) { _push(rstack, v); }

static inline int pop() { return _pop(stack); }
static inline int rpop() { return _pop(rstack); }

bool member(unsigned int *s, unsigned int len, int n) {
  for(int i = 0; i < len; i++) {
    if( s[i] == n) {
      return true;
    }
  }
  return false;
}

static inline bool stack_member(List* s, int n) {
  return member(s->data, s->len, n);
}

void unshift( List *s, int v ) {
  assert( s->len < s->size, "unshift: no room");
  for( int i=s->len-1; i >= 0; i--) {
    s->data[i+1] = s->data[i];
  }
  s->data[0] = v;
  s->len++;
}

void list_print( List *s ) {
  for (int i=0; i < s->len; i ++){
    printf("%d ", s->data[i]);
  }
  printf("\n");
}

bool check_symbols();

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
  int n1 = pop();
  int n2 = pop();
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
  int n1 = pop();
  int n2 = pop();
  int n3 = pop();
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

bool drop2(void) {
  CHECK_STACK_2;
  stack->len -= 2;
  CHECK_SYMS;
  return true;
}

bool swap2(void) {
  CHECK_STACK_4;
  int n1 = pop();
  int n2 = pop();
  int n3 = pop();
  int n4 = pop();
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
  int n1 = pop();
  int n2 = pop();
  int n3 = pop();
  int n4 = pop();
  int n5 = pop();
  int n6 = pop();
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
  int n = pop();
  pop();
  push(n);
  CHECK_SYMS;
  return true;
}

bool tuck(void) {
  CHECK_STACK_2;
  int n1 = pop();
  int n2 = pop();
  push(n1);
  push(n2);
  push(n1);
  return true;
}

bool mrot(void) {
  CHECK_STACK_3;
  int n1 = pop();
  int n2 = pop();
  int n3 = pop();
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
  int n1 = pop();
  int n2 = pop();
  rpush(n2);
  rpush(n1);
  return true;
}

bool rfrom2(void) {
  CHECK_RSTACK_2;
  int n1 = rpop();
  int n2 = rpop();
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

// Note: remember to update corresponding list in forthwiz/__init__.py
Op ops[] = { { dup_, "dup" },
             { drop, "drop" },
             { swap, "swap" },
             { over, "over" },
             { rot, "rot" },
             { tor, ">r" },
             { rfrom, "r>" },
             { dup2_, "dup2" },
             { drop2, "drop2" },
             { swap2, "2swap" },
             { over2, "over2" },
             { rot2, "rot2" },
             { nip, "nip" },
             { tuck, "tuck" },
             { mrot, "-rot" },
             { rfetch, "rfetch" },
             { tor2, "2>r" },
             { rfrom2, "2r>" },
             { rfetch2, "rfetch2" },
             { NULL, NULL }};

////////////////////////////////////////////////////////////////////////////////

void next() {
  int i = code->len - 1;
  int max = n_ops - 1;

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
  int max = n_ops - 1;

  for (int i=n+1; i < code->len; i++) {
    code->data[i] = max;
  }
}

void collect_unique_symbols() {
  int len = stack_out->len;
  unique_symbols = new_list(len);

  for(int i = 0; i < len; i++) {
    if( !stack_member(unique_symbols, stack_out->data[i])) {
      _push(unique_symbols, stack_out->data[i]);
    }
  }
}

void validate_stacks() {
  for(int i = 0; i < stack_out->len; i++ ) {
    if ( !stack_member(stack_in, stack_out->data[i] ) ) {
      printf("ERROR: output stack value not present in input stack\n");
      exit(1);
    }
  }
}

// check that all symbols are present in at least one of the stacks
bool check_symbols()
{
  for (int i = 0; i < unique_symbols->len; i++) {
    if(!stack_member(stack, unique_symbols->data[i])
       && !stack_member(rstack, unique_symbols->data[i]))
      return false;
  }
  return true;
}

bool noop(int n) {
  if(!rstack->len && list_equal(stack, stack_in)){
    return true;
  }
  for ( int i=0; i < n; i++ ){
    if(list_equal(stack_history[i], stack) && list_equal(rstack_history[i], rstack))
      return true;
  }
  return false;
}

bool verify_code() {
  stack = list_clone(stack_in);
  rstack = new_list(10);

  for(int i = 0; i < code->len; i++) {
    if( !ops[(int)code->data[i]].fn()
        || noop(i) ){
      skip_code(i);
      return false;
    }
    stack_history[i] = list_clone(stack);
    rstack_history[i] = list_clone(rstack);
  }
  return ( rstack->len == 0 ) && list_equal(stack, stack_out);
}

void print_solution() {
  for( int i=0; i< code->len; i++){
    printf("%s ", ops[(int)code->data[i]].name);
  }
  printf("\n");
}

bool solve_next() {
  if (list_equal(stack_in, stack_out)){
    list_clear(code);
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

void count_ops() {
  n_ops=0;
  while (ops[n_ops].fn != NULL) {
    n_ops++;
  }
}

void set_stack_size(int n){
  stack_size = n;
}

void set_stack_in( int *values, int len ) {

  for (int i = 0; i < len; i++) {
    _push(stack_in, values[i]);
  }
  //printf("in stack\n");
  //list_print(stack_in);
}

void set_stack_out( int *values, int len ) {

  for (int i = 0; i < len; i++) {
    _push(stack_out, values[i]);
  }
  collect_unique_symbols();
  validate_stacks();
  //printf("out stack\n");
  //list_print(stack_out);
}

bool initialized = false;

void init() {
  if ( initialized ) {
    list_clear(code);
    _push(code,0);
    list_clear(stack_in);
    list_clear(stack_out);
    list_clear(solution);
    return;
  }
  stack_size=23;
  max_code_length = 10;
  stack_in = new_list(stack_size);
  stack_out = new_list(stack_size);
  stack_history = (List**)calloc(sizeof(List*), max_code_length);
  rstack_history = (List**)calloc(sizeof(List*), max_code_length);
  count_ops();

  code = new_list(max_code_length);
  solution = new_list(max_code_length);
  _push(code,0);
  initialized = true;
}

bool solve() {
  if (!solve_next()) {
    return false;
  }
  list_copy(solution, code);
  if( code->len > 0 ) {
    next();
  }
  return true;
}
