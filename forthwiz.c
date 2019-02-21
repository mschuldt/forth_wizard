#include "solver.c"
#include <Python.h>

static PyObject* wiz_set_stack_size(PyObject* self, PyObject* size) {
  stack_size = PyLong_AsLong( size);
  return Py_BuildValue("i", stack_size);
}

static void copy_to_slice(PyObject *tuple, Slice *slice) {
  long len = PyList_Size(tuple);
  slice_clear(slice);
  int i;
  for(i = 0; i < len; i++){
    slice_push(slice, (char) PyLong_AsLong(PyList_GetItem(tuple, i)));
  }
}

static PyObject* wiz_set_stack_in(PyObject* self, PyObject* args) {
  PyObject * tuple;

  if (! PyArg_ParseTuple( args, "O", &tuple)) {
    return NULL;
  }
  copy_to_slice(tuple, stack_in);
  return Py_BuildValue("i", 1);
}

static PyObject* wiz_set_rstack_in(PyObject* self, PyObject* args) {
  PyObject * tuple;

  if (! PyArg_ParseTuple( args, "O", &tuple)) {
    return NULL;
  }
  copy_to_slice(tuple, rstack_in);
  return Py_BuildValue("i", 1);
}

static PyObject* wiz_set_stack_out(PyObject* self, PyObject* args) {
  PyObject * tuple;

  if (! PyArg_ParseTuple( args, "O", &tuple)) {
    return NULL;
  }
  copy_to_slice(tuple, stack_out);
  return Py_BuildValue("i", 1);
}
static PyObject* wiz_set_vars_out(PyObject* self, PyObject* args) {
  PyObject * tuple;

  if (! PyArg_ParseTuple( args, "O", &tuple)) {
    return NULL;
  }
  copy_to_slice(tuple, vars_out);
  return Py_BuildValue("i", 1);
}

static PyObject* wiz_set_code(PyObject* self, PyObject* args) {
  PyObject * tuple;

  if (! PyArg_ParseTuple( args, "O", &tuple)) {
    return NULL;
  }
  copy_to_slice(tuple, code);
  return Py_BuildValue("i", 1);
}

static PyObject* wiz_set_next_code(PyObject* self, PyObject* args) {
  PyObject * tuple;

  if (! PyArg_ParseTuple( args, "O", &tuple)) {
    return NULL;
  }

  long len = PyList_Size(tuple);
  copy_to_slice(tuple, code);
  if (len > 0) {
    next();
  }
  return Py_BuildValue("i", 1);
}

static PyObject* build_tuple(char *d, int len) {
  switch(len) {
    //TODO: how to construct a variable sized tuple
  case 0: return Py_BuildValue("");
  case 1: return Py_BuildValue("(i)", d[0]);
  case 2: return Py_BuildValue("(i,i)", d[0], d[1]);
  case 3: return Py_BuildValue("(i,i,i)", d[0], d[1], d[2]);
  case 4: return Py_BuildValue("(i,i,i,i)", d[0], d[1], d[2], d[3]);
  case 5: return Py_BuildValue("(i,i,i,i,i)", d[0], d[1], d[2], d[3], d[4]);
  case 6: return Py_BuildValue("(i,i,i,i,i,i)", d[0], d[1], d[2], d[3], d[4], d[5]);
  case 7: return Py_BuildValue("(i,i,i,i,i,i,i)", d[0], d[1], d[2], d[3], d[4], d[5], d[6]);
  case 8: return Py_BuildValue("(i,i,i,i,i,i,i,i)", d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7]);
  case 9: return Py_BuildValue("(i,i,i,i,i,i,i,i,i)", d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8]);
  case 10: return Py_BuildValue("(i,i,i,i,i,i,i,i,i,i)", d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9]);
  case 11: return Py_BuildValue("(i,i,i,i,i,i,i,i,i,i,i)", d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], d[10]);
  case 12: return Py_BuildValue("(i,i,i,i,i,i,i,i,i,i,i,i)", d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], d[10], d[11]);
  default:
    printf("stack size >13 unimplemented");
    exit(1);
  }
}

static PyObject* wiz_solve(PyObject* self) {
  if (solve()) {
    return build_tuple(solution->data, solution->len);
  }
  return Py_BuildValue("i", -1);
}

static PyObject* wiz_get_return_stack(PyObject* self)  {
  return build_tuple(rstack->data, rstack->len);
}

static PyObject* wiz_get_stack(PyObject* self)  {
  return build_tuple(stack->data, stack->len);
}

static PyObject* wiz_init(PyObject* self) {
  init();
  return Py_BuildValue("i", 0);
}

static PyObject* wiz_add_op(PyObject* self, PyObject* op) {
  char o = PyLong_AsLong(op);
  return Py_BuildValue("i", add_op(o));
}

static PyObject* wiz_reset(PyObject* self) {
  reset();
  return Py_BuildValue("i", 0);
}

static PyObject* wiz_reset_solver(PyObject* self) {
  reset_solver();
  return Py_BuildValue("i", 0);
}

static PyObject* wiz_reset_ops(PyObject* self) {
  reset_ops();
  return Py_BuildValue("i", 0);
}

static PyObject* wiz_save_state(PyObject* self, PyObject* reg) {
  int n = PyLong_AsLong(reg);
  save_state(n);
  return Py_BuildValue("i", 0);
}

static PyObject* wiz_restore_state(PyObject* self, PyObject* reg) {
  int n = PyLong_AsLong(reg);
  restore_state(n);
  return Py_BuildValue("i", 0);
}

static PyObject* wiz_verify(PyObject* self) {
  bool ok = verify_code();
  return Py_BuildValue("i", ok);
}

static PyObject* wiz_use_rstack(PyObject* self, PyObject* size) {
  use_rstack = PyLong_AsLong(size) ? true : false;
  return Py_BuildValue("i", use_rstack);
}

static char todo_docs[] = "TODO\n";

static PyMethodDef wiz_methods[] = {{"init", (PyCFunction)wiz_init, METH_NOARGS, todo_docs},
                                    {"set_stack_in", (PyCFunction)wiz_set_stack_in, METH_VARARGS, todo_docs},
                                    {"set_rstack_in", (PyCFunction)wiz_set_rstack_in, METH_VARARGS, todo_docs},
                                    {"set_stack_out", (PyCFunction)wiz_set_stack_out, METH_VARARGS, todo_docs},
                                    {"set_vars_out", (PyCFunction)wiz_set_vars_out, METH_VARARGS, todo_docs},
                                    {"set_code", (PyCFunction)wiz_set_code, METH_VARARGS, todo_docs},
                                    {"set_next_code", (PyCFunction)wiz_set_next_code, METH_VARARGS, todo_docs},
                                    {"solve", (PyCFunction)wiz_solve, METH_NOARGS, todo_docs},
                                    {"set_stack_size", (PyCFunction)wiz_set_stack_size, METH_O, todo_docs},
                                    {"get_stack", (PyCFunction)wiz_get_stack, METH_NOARGS, todo_docs},
                                    {"get_return_stack", (PyCFunction)wiz_get_return_stack, METH_NOARGS, todo_docs},
                                    {"add_op", (PyCFunction)wiz_add_op, METH_O, todo_docs},
                                    {"reset", (PyCFunction)wiz_reset, METH_NOARGS, todo_docs},
                                    {"reset_solver", (PyCFunction)wiz_reset_solver, METH_NOARGS, todo_docs},
                                    {"reset_ops", (PyCFunction)wiz_reset_ops, METH_NOARGS, todo_docs},
                                    {"verify", (PyCFunction)wiz_verify, METH_NOARGS, todo_docs},
                                    {"use_rstack", (PyCFunction)wiz_use_rstack, METH_O, todo_docs},
                                    {"save_state", (PyCFunction)wiz_save_state, METH_O, todo_docs},
                                    {"restore_state", (PyCFunction)wiz_restore_state, METH_O, todo_docs},
                                    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef forthwizmodule =
  {
   PyModuleDef_HEAD_INIT,
   "chuckmoore",
   "usage: TODO\n",
   -1,
   wiz_methods
  };

PyMODINIT_FUNC PyInit_chuckmoore(void)
{
  return PyModule_Create(&forthwizmodule);
}
