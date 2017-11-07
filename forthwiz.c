#include "wiz.c"
#include <Python.h>

static PyObject* wiz_set_stack_size(PyObject* self, PyObject* size) {
  stack_size = PyLong_AsLong( size);
  return Py_BuildValue("i", stack_size);
}

int* get_stack(PyObject *tuple, long len) {

  int *stack = (int*)calloc(sizeof(int), len);

  for(int i = 0; i < len; i++){
    stack[i] = PyLong_AsLong(PyList_GetItem(tuple, i));
  }
  return stack;
}

static PyObject* wiz_set_stack_in(PyObject* self, PyObject* args) {
  PyObject * tuple;

  if (! PyArg_ParseTuple( args, "O", &tuple)) {
    return NULL;
  }

  long len = PyList_Size(tuple);
  int *in_stack = get_stack(tuple, len);
  set_stack_in(in_stack, len);
  free(in_stack);
  return Py_BuildValue("i", 1);
}

static PyObject* wiz_set_stack_out(PyObject* self, PyObject* args) {
  PyObject * tuple;

  if (! PyArg_ParseTuple( args, "O", &tuple)) {
    return NULL;
  }

  long len = PyList_Size(tuple);
  int *out_stack = get_stack(tuple, len);
  set_stack_out(out_stack, len);
  free(out_stack);
  return Py_BuildValue("i", 1);
}

static PyObject* wiz_solve(PyObject* self) {
  int* d = code->data;
  if (solve()){
    switch(code->len) {
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
    default:
      printf("solution size >9 unimplemented");
      exit(1);
    }
  }
  return Py_BuildValue("i", -1);
}

static PyObject* wiz_init(PyObject* self) {
  init();
  return Py_BuildValue("i", 0);
}

static char todo_docs[] = "TODO\n";

static PyMethodDef wiz_methods[] = {{"init", (PyCFunction)wiz_init, METH_NOARGS, todo_docs},
                                    {"set_stack_in", (PyCFunction)wiz_set_stack_in, METH_VARARGS, todo_docs},
                                    {"set_stack_out", (PyCFunction)wiz_set_stack_out, METH_VARARGS, todo_docs},
                                    {"solve", (PyCFunction)wiz_solve, METH_NOARGS, todo_docs},
                                    {"set_stack_size", (PyCFunction)wiz_set_stack_size, METH_O, todo_docs},

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
