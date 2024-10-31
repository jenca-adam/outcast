#define PY_SSIZE_T_CLEAN
// INCLUDES
#include <Python.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
// MACROS
#define CCORE_NEW_VEC3 (Vec3Object *)(&Vec3Type)->tp_alloc(&Vec3Type, 0);
#define CCORE_MK_MATRIX_OBJ(ma, r, c, varn)                                    \
  MatrixObject *varn =                                                         \
      (MatrixObject *)(&MatrixType)->tp_alloc(&MatrixType, 0);                 \
  varn->rows = r;                                                              \
  varn->cols = c;                                                              \
  varn->m = ma;
#define CCORE_RETURN_MATRIX_OBJ(ma, r, c)                                      \
  CCORE_MK_MATRIX_OBJ(ma, r, c, ret)                                           \
  return ret;
#define CCORE_RETURN_MATRIX(ma, r, c)                                          \
  CCORE_MK_MATRIX_OBJ(ma, r, c, ret)                                           \
  return (PyObject *)ret;
#define CCORE_MATRIX_ASSERT_SQUARE(self, s)                                    \
  if (self->rows != s || self->cols != s) {                                    \
    char *errmsg;                                                              \
    asprintf(&errmsg, "matrix not a %d*%d square", s, s);                      \
    PyErr_SetString(PyExc_ValueError, errmsg);                                 \
    free(errmsg);                                                              \
    return NULL;                                                               \
  }
#define VEC3_ALLZEROS cCore_mk_vec3_obj(0, 0, 0)
#define VEC3_ALLONES cCore_mk_vec3_obj(1, 1, 1)
#define VEC3_ZBACK cCore_mk_vec3_obj(0, 0, -1)
#define CCORE_PHONG_1_(c)                                                      \
  cCore_calcphong_1_(ambient_coeff, diffuse_coeff, specular_coeff, diff, spec, \
                     c);
#ifdef Py_LIMITED_API
#error "can't compile with limited api"
#endif
#define EPSILON 0.00000001
#define VIEWPORT_DEPTH 255
/* FORWARD */

static PyTypeObject Vec3Type, MatrixType, TextureType;
static PyModuleDef ccoremodule;

typedef struct {
  PyObject_HEAD double x;
  double y;
  double z;
} Vec3Object;
typedef struct {
  PyObject_HEAD double **m;
  Py_ssize_t cols;
  Py_ssize_t rows;
} MatrixObject;
typedef struct {
  Vec3Object *a;
  Vec3Object *b;
} Vec3_pair;
typedef struct {
  Vec3Object *v0;
  Vec3Object *v1;
  Vec3Object *v2;
} Triangle;
typedef struct {
  PyObject_HEAD Vec3Object ***m;
  Py_ssize_t width;
  Py_ssize_t height;
} TextureObject;

typedef enum { PHONG, GOURAUD, NONE, DEPTH } Lighting;
static double Vec3_get_length_obj_(Vec3Object *self_);
static MatrixObject *Matrix__matmul__obj(MatrixObject *self_,
                                         MatrixObject *other_);
static Vec3Object *cCore_mk_vec3_obj(double x, double y, double z);
/* formerly vec3.py: */

double cCore_linear_to_gamma(double linear) {
  double retval;
  if (linear < 0) {
    retval = 0;
  } else {
    retval = sqrt(linear);
  }
  return retval;
}

//// VEC3 ////

// Define the Vec3Obje/ct structure
// INIT
static void Vec3_dealloc(Vec3Object *self) {
  Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *Vec3_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
  Vec3Object *self;
  self = (Vec3Object *)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->x = 0.0;
    self->y = 0.0;
    self->z = 0.0;
  }
  return (PyObject *)self;
}

static int Vec3_init(Vec3Object *self, PyObject *args, PyObject *kwds) {
  if (!PyArg_ParseTuple(args, "|ddd", &self->x, &self->y, &self->z))
    return -1;
  return 0;
}

// MATH
static Vec3Object *Vec3__add__obj_(Vec3Object *self_, Vec3Object *other_) {
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = self_->x + other_->x;
  obj->y = self_->y + other_->y;
  obj->z = self_->z + other_->z;

  return obj;
}
static PyObject *Vec3__add__(PyObject *self, PyObject *other) {
  if (!PyObject_TypeCheck(other, &Vec3Type)) {
    PyErr_SetString(PyExc_TypeError, "+ operand can only be a Vec3");
    return NULL;
  }
  Vec3Object *self_ = (Vec3Object *)self;
  Vec3Object *other_ = (Vec3Object *)other;

  return (PyObject *)(Vec3__add__obj_(self_, other_));
}
static Vec3Object *Vec3__sub__obj_(Vec3Object *self_, Vec3Object *other_) {
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = self_->x - other_->x;
  obj->y = self_->y - other_->y;
  obj->z = self_->z - other_->z;

  return obj;
}
static PyObject *Vec3__sub__(PyObject *self, PyObject *other) {
  if (!PyObject_TypeCheck(other, &Vec3Type)) {
    PyErr_SetString(PyExc_TypeError, "- operand can only be a Vec3");
    return NULL;
  }
  Vec3Object *self_ = (Vec3Object *)self;
  Vec3Object *other_ = (Vec3Object *)other;
  return (PyObject *)Vec3__sub__obj_(self_, other_);
}
static Vec3Object *Vec3__mul__obj_(Vec3Object *self_, double other_double) {
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = self_->x * other_double;
  obj->y = self_->y * other_double;
  obj->z = self_->z * other_double;

  return obj;
}

static PyObject *Vec3__mul__(PyObject *self, PyObject *other) {
  PyObject *other_pyfloat = PyNumber_Float(other);
  if (!other_pyfloat || !PyNumber_Check(other)) {
    PyErr_SetString(PyExc_TypeError, "* operand can only be a real number");
    return NULL;
  }
  double other_double = PyFloat_AsDouble(other_pyfloat);
  Vec3Object *self_ = ((Vec3Object *)self);
  return (PyObject *)Vec3__mul__obj_(self_, other_double);
}
static Vec3Object *Vec3__truediv__obj_(Vec3Object *self_, double other_double) {
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = self_->x / other_double;
  obj->y = self_->y / other_double;
  obj->z = self_->z / other_double;
  return obj;
}

static PyObject *Vec3__truediv__(PyObject *self, PyObject *other) {
  PyObject *other_pyfloat = PyNumber_Float(other);
  if (!other_pyfloat || !PyNumber_Check(other)) {
    PyErr_SetString(PyExc_TypeError, "/ operand can only be a real number");
    return NULL;
  }
  double other_double = PyFloat_AsDouble(other_pyfloat);
  if (other_double == 0) {
    PyErr_SetString(PyExc_ZeroDivisionError, "divide vec3 by 0");
    return NULL;
  }
  Vec3Object *self_ = (Vec3Object *)self;
  return (PyObject *)Vec3__truediv__obj_(self_, other_double);
}

static PyObject *Vec3__floordiv__(PyObject *self, PyObject *other) {
  PyObject *other_pyfloat = PyNumber_Float(other);
  if (!other_pyfloat || !PyNumber_Check(other)) {
    PyErr_SetString(PyExc_TypeError, "// operand can only be a real number");
    return NULL;
  }
  double other_double = PyFloat_AsDouble(other_pyfloat);
  if (other_double == 0) {
    PyErr_SetString(PyExc_ZeroDivisionError, "divide vec3 by 0");
    return NULL;
  }
  Vec3Object *self_ = (Vec3Object *)self;
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = floor(self_->x / other_double);
  obj->y = floor(self_->y / other_double);
  obj->z = floor(self_->z / other_double);
  return (PyObject *)obj;
}
static Vec3Object *Vec3__neg__obj_(Vec3Object *self_) {
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = -self_->x;
  obj->y = -self_->y;
  obj->z = -self_->z;
  return obj;
}
static PyObject *Vec3__neg__(PyObject *self) {
  return (PyObject *)Vec3__neg__obj_((Vec3Object *)self);
}

static PyObject *Vec3_asrgb(PyObject *self, PyObject *_) {
  Vec3Object *self_ = (Vec3Object *)self;
  if (!((0 <= self_->x && self_->x <= 1) && (0 <= self_->y && self_->y <= 1) &&
        (0 <= self_->z && self_->z <= 1))) {
    PyErr_SetString(PyExc_ValueError, "can't make RGB: overflow");
    return NULL;
  }
  return Vec3__floordiv__(Vec3__mul__(self, PyLong_FromLong(256)),
                          PyLong_FromLong(1)); // fancy
}
static double Vec3_dot_obj_(Vec3Object *self_, Vec3Object *other_) {
  return (self_->x * other_->x + self_->y * other_->y + self_->z * other_->z);
}

static PyObject *Vec3_dot(PyObject *self, PyObject *other) {
  if (!PyObject_TypeCheck(other, &Vec3Type)) {
    PyErr_SetString(PyExc_TypeError, "can only dot() with Vec3");
    return NULL;
  }
  Vec3Object *self_ = (Vec3Object *)self;
  Vec3Object *other_ = (Vec3Object *)other;
  return PyFloat_FromDouble(Vec3_dot_obj_(self_, other_));
}
static PyObject *Vec3__abs__(PyObject *self) {
  Vec3Object *self_ = (Vec3Object *)self;
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = fabs(self_->x);
  obj->y = fabs(self_->y);
  obj->z = fabs(self_->z);
  return (PyObject *)obj;
}
static PyObject *Vec3_item_mul(PyObject *self, PyObject *other) {
  if (!PyObject_TypeCheck(other, &Vec3Type)) {
    PyErr_SetString(PyExc_TypeError, "can only item_mul() with Vec3");
    return NULL;
  }
  Vec3Object *self_ = (Vec3Object *)self;
  Vec3Object *other_ = (Vec3Object *)other;
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = self_->x * other_->x;
  obj->y = self_->y * other_->y;
  obj->z = self_->z * other_->z;
  return (PyObject *)obj;
}
static PyObject *Vec3_near_zero(PyObject *self, PyObject *_) {
  Vec3Object *self_ = (Vec3Object *)self;
  return PyBool_FromLong((fabs(self_->x) < EPSILON) &&
                         (fabs(self_->y) < EPSILON) &&
                         (fabs(self_->z) < EPSILON));
}
static PyObject *Vec3_gamma_corrected(PyObject *self, PyObject *_) {
  Vec3Object *self_ = (Vec3Object *)self;
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = cCore_linear_to_gamma(self_->x);
  obj->y = cCore_linear_to_gamma(self_->y);
  obj->z = cCore_linear_to_gamma(self_->z);
  return (PyObject *)obj;
}
static Vec3Object *Vec3_normalized_obj_(Vec3Object *self_) {
  double length = Vec3_get_length_obj_(self_);
  if (length == 0) {
    return CCORE_NEW_VEC3;
  }
  return Vec3__truediv__obj_(self_, length);
}
static PyObject *Vec3_normalized(PyObject *self, PyObject *_) {
  PyObject *length_obj = PyObject_GetAttrString(self, "length");
  if (PyFloat_AsDouble(length_obj) == 0) {
    return (PyObject *)CCORE_NEW_VEC3;
  }
  return PyNumber_TrueDivide(self, length_obj);
}
static Vec3Object *Vec3_cross_obj_(Vec3Object *self_, Vec3Object *other_) {
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = self_->y * other_->z - self_->z * other_->y;
  obj->y = self_->z * other_->x - self_->x * other_->z;
  obj->z = self_->x * other_->y - self_->y * other_->x;
  return obj;
}
static PyObject *Vec3_cross(PyObject *self, PyObject *other) {
  if (!PyObject_TypeCheck(other, &Vec3Type)) {
    PyErr_SetString(PyExc_TypeError, "can only cross() with Vec3");
    return NULL;
  }
  Vec3Object *self_ = (Vec3Object *)self;
  Vec3Object *other_ = (Vec3Object *)other;
  return (PyObject *)Vec3_cross_obj_(self_, other_);
}
// PROPERTIES
static PyObject *Vec3_get_length_squared(PyObject *self, void *_) {
  Vec3Object *self_ = (Vec3Object *)self;
  return PyFloat_FromDouble(pow((self_->x), 2) + pow((self_->y), 2) +
                            pow((self_->z), 2));
}
static double Vec3_get_length_obj_(Vec3Object *self_) {
  return sqrt(pow((self_->x), 2) + pow((self_->y), 2) + pow((self_->z), 2));
}
static PyObject *Vec3_get_length(PyObject *self, void *_) {
  Vec3Object *self_ = (Vec3Object *)self;
  return PyFloat_FromDouble(Vec3_get_length_obj_(self_));
}
// MISCELLANEOUS
static Py_ssize_t Vec3__len__(PyObject *self) { return 3; }
static PyObject *Vec3__repr__(PyObject *self) {
  Vec3Object *self_ = (Vec3Object *)self;
  PyObject *x = PyFloat_FromDouble(self_->x);
  PyObject *y = PyFloat_FromDouble(self_->y);
  PyObject *z = PyFloat_FromDouble(self_->z);
  return PyUnicode_FromFormat("Vec3(%R, %R, %R)", x, y, z);
}
static PyObject *Vec3__getitem__(PyObject *self, Py_ssize_t index) {
  Vec3Object *self_ = (Vec3Object *)self;
  PyObject *retval;
  switch (index) {
  case 0:
    retval = PyFloat_FromDouble(self_->x);
    break;
  case 1:
    retval = PyFloat_FromDouble(self_->y);
    break;
  case 2:
    retval = PyFloat_FromDouble(self_->z);
    break;
  default:
    PyErr_SetString(PyExc_IndexError, "");
    retval = NULL;
  }
  return retval;
}
static PyObject *Vec3__iter__(PyObject *self) {
  Vec3Object *self_ = (Vec3Object *)self;
  PyObject *iterargs =
      PyTuple_Pack(3, PyFloat_FromDouble(self_->x),
                   PyFloat_FromDouble(self_->y), PyFloat_FromDouble(self_->z));
  PyObject *iterator = PyObject_GetIter(iterargs);

  Py_DECREF(iterargs);
  return iterator;
}
// CLASSMETHODS

static PyObject *Vec3_from_matrix(PyObject *cls, PyObject *other) {
  if (!PyObject_TypeCheck(other, &MatrixType)) {
    PyErr_SetString(PyExc_TypeError, "can only call from_matrix with a matrix");
    return NULL;
  }
  MatrixObject *other_ = (MatrixObject *)other;
  if (other_->rows < 4) {
    PyErr_SetString(PyExc_ValueError,
                    "Matrix too small, try using from_matrix3 instead");
    return NULL;
  }
  double **m = (other_)->m;

  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = floor(m[0][0] / m[3][0]);
  obj->y = floor(m[1][0] / m[3][0]);
  obj->z = floor(-m[2][0] / m[3][0]);
  return (PyObject *)obj;
}
static PyObject *Vec3_from_matrix3(PyObject *cls, PyObject *other) {
  if (!PyObject_TypeCheck(other, &MatrixType)) {
    PyErr_SetString(PyExc_TypeError, "can only call from_matrix with a matrix");
    return NULL;
  }
  double **m = ((MatrixObject *)other)->m;
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = m[0][0];
  obj->y = m[1][0];
  obj->z = m[2][0];
  return (PyObject *)obj;
}
// STRUCTS
static PyNumberMethods Vec3_num = {
    .nb_add = &Vec3__add__,
    .nb_subtract = &Vec3__sub__,
    .nb_multiply = &Vec3__mul__,
    .nb_true_divide = &Vec3__truediv__,
    .nb_floor_divide = &Vec3__floordiv__,
    .nb_negative = &Vec3__neg__,
    .nb_absolute = &Vec3__abs__,
};
static PySequenceMethods Vec3_seq = {
    .sq_length = Vec3__len__,
    .sq_item = Vec3__getitem__,
};
static PyGetSetDef Vec3_properties[] = {
    {"length_squared", Vec3_get_length_squared, NULL, "|v|^2"},
    {"length", Vec3_get_length, NULL, "|v|"},
    {NULL} /* sentinel */
};

static PyMemberDef Vec3_members[] = {
    {"x", Py_T_DOUBLE, offsetof(Vec3Object, x), 0, "X coordinate"},
    {"y", Py_T_DOUBLE, offsetof(Vec3Object, y), 0, "Y coordinate"},
    {"z", Py_T_DOUBLE, offsetof(Vec3Object, z), 0, "Z coordinate"},
    {NULL} /* Sentinel */
};

static PyMethodDef Vec3_methods[] = {
    {"asrgb", &Vec3_asrgb, METH_NOARGS, "Convert to RGB"},
    {"dot", &Vec3_dot, METH_O, "Dot product"},
    {"item_mul", &Vec3_item_mul, METH_O, "Multiplication item by item"},
    {"near_zero", &Vec3_near_zero, METH_NOARGS, "True if vector is near zero"},
    {"gamma_corrected", &Vec3_gamma_corrected, METH_NOARGS, "Gamma corrects"},
    {"normalized", &Vec3_normalized, METH_NOARGS, "Divides by length"},
    {"cross", &Vec3_cross, METH_O, "Cross product"},
    {"from_matrix", &Vec3_from_matrix, METH_CLASS | METH_O,
     "Makes a vector from a matrix"},
    {"from_matrix3", &Vec3_from_matrix3, METH_CLASS | METH_O,
     "Makes a vector from a matrix ignoring the 4th row"},
    {NULL} /* Sentinel */
};

static PyTypeObject Vec3Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "cCore.Vec3",
    .tp_doc = "A Vec3 class",
    .tp_basicsize = sizeof(Vec3Object),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Vec3_new,
    .tp_init = (initproc)Vec3_init,
    .tp_dealloc = (destructor)Vec3_dealloc,
    .tp_members = Vec3_members,
    .tp_methods = Vec3_methods,
    .tp_as_number = &Vec3_num,
    .tp_getset = Vec3_properties,
    .tp_as_sequence = &Vec3_seq,
    .tp_repr = Vec3__repr__,
    .tp_iter = Vec3__iter__,
};

//// MATRIX ////

// UTILS
double **cCore_mk_empty_matrix(Py_ssize_t rows, Py_ssize_t cols) {
  double **m = (double **)malloc(rows * sizeof(double *));
  for (Py_ssize_t i = 0; i < rows; i++) {
    double *r = calloc(cols, sizeof(double));
    for (Py_ssize_t j = 0; j < cols; j++) {
      r[j] = 0;
    }
    m[i] = r;
  }
  return m;
}
double **cCore_mk_id_matrix(Py_ssize_t size) {
  double **m = (double **)malloc(size * sizeof(double *));
  for (Py_ssize_t i = 0; i < size; i++) {
    double *r = calloc(size, sizeof(double));
    for (Py_ssize_t j = 0; j < size; j++) {
      if (i == j) {
        r[j] = 1;
      } else {
        r[j] = 0;
      }
    }
    m[i] = r;
  }
  return m;
}

// INIT

static PyObject *Matrix_new(PyTypeObject *type, PyObject *args,
                            PyObject *kwds) {
  MatrixObject *self;
  self = (MatrixObject *)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->cols = 0;
    self->rows = 0;
    self->m = NULL;
  }
  return (PyObject *)self;
}
static int Matrix_init(MatrixObject *self, PyObject *args, PyObject *kwds) {
  PyObject *ma = NULL;
  if (!PyArg_ParseTuple(args, "O", &ma)) {
    return -1;
  }
  if (!PySequence_Check(ma)) {
    PyErr_SetString(PyExc_TypeError, "Matrix() arg must be a sequence");
    return -1;
  }
  self->rows = PySequence_Length(ma);

  if (self->rows && !PySequence_Check(PySequence_GetItem(ma, 0))) {
    PyErr_SetString(PyExc_ValueError, "Matrix() arg must be 2D");
    return -1;
  }
  if (self->rows) {
    self->cols = PySequence_Length(PySequence_GetItem(ma, 0));
  }
  self->m = (double **)malloc(self->rows * sizeof(double *));
  for (Py_ssize_t i = 0; i < self->rows; i++) {
    double *mr = calloc(self->cols, sizeof(double));
    for (Py_ssize_t j = 0; j < self->cols; j++) {
      mr[j] =
          PyFloat_AsDouble(PySequence_GetItem(PySequence_GetItem(ma, i), j));
    }
    self->m[i] = mr;
  }
  if (PyErr_Occurred()) {
    return -1;
  }
  return 0;
}
static void Matrix_dealloc(MatrixObject *self) {
  if (self->m != NULL) {
    for (Py_ssize_t i = 0; i < self->rows; i++) {
      free(self->m[i]);
    }
    free(self->m);
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}
// CONSTRUCTORS
static PyObject *Matrix_empty(PyObject *cls, PyObject *args) {
  Py_ssize_t rows, cols;
  if (!PyArg_ParseTuple(args, "nn", &rows, &cols)) {
    return NULL;
  }
  double **m = cCore_mk_empty_matrix(rows, cols);
  CCORE_RETURN_MATRIX(m, rows, cols);
}

static PyObject *Matrix_identity(PyObject *cls, PyObject *args) {
  Py_ssize_t size;
  if (!PyArg_ParseTuple(args, "n", &size)) {
    return NULL;
  }
  double **m = cCore_mk_id_matrix(size);
  CCORE_RETURN_MATRIX(m, size, size);
}
static PyObject *Matrix_viewport(PyObject *cls, PyObject *args) {
  double x, y, w, h;
  if (!PyArg_ParseTuple(args, "dddd", &x, &y, &w, &h)) {
    return NULL;
  }
  double **m = cCore_mk_id_matrix(4);
  m[0][3] = x + w / 2.;
  m[1][3] = y + h / 2.;
  m[2][3] = m[2][2] = VIEWPORT_DEPTH / 2.;
  m[0][0] = w / 2.;
  m[1][1] = h / 2.;
  CCORE_RETURN_MATRIX(m, 4, 4);
}
static PyObject *Matrix_projection(PyObject *cls, PyObject *o) {
  if (!PyNumber_Check(o)) {
    return NULL;
  }
  double camz = PyFloat_AsDouble(o);
  double **m = cCore_mk_id_matrix(4);
  m[3][2] = 1. / camz;
  CCORE_RETURN_MATRIX(m, 4, 4);
}
static PyObject *Matrix_rotz(PyObject *cls, PyObject *args) {
  double theta;
  if (!PyArg_ParseTuple(args, "d", &theta)) {
    return NULL;
  }
  double **m = cCore_mk_id_matrix(3);
  m[0][0] = cos(theta);
  m[0][1] = -sin(theta);
  m[1][0] = sin(theta);
  m[1][1] = cos(theta);
  CCORE_RETURN_MATRIX(m, 3, 3);
}
static PyObject *Matrix_roty(PyObject *cls, PyObject *args) {
  double theta;
  if (!PyArg_ParseTuple(args, "d", &theta)) {
    return NULL;
  }
  double **m = cCore_mk_id_matrix(3);
  m[0][0] = cos(theta);
  m[2][0] = -sin(theta);
  m[0][2] = sin(theta);
  m[2][2] = cos(theta);
  CCORE_RETURN_MATRIX(m, 3, 3);
}
static PyObject *Matrix_rotx(PyObject *cls, PyObject *args) {
  double theta;
  if (!PyArg_ParseTuple(args, "d", &theta)) {
    return NULL;
  }
  double **m = cCore_mk_id_matrix(3);
  m[1][1] = cos(theta);
  m[1][2] = -sin(theta);
  m[2][1] = sin(theta);
  m[2][2] = cos(theta);
  CCORE_RETURN_MATRIX(m, 3, 3);
}
static MatrixObject *Matrix_from_vector_obj(Vec3Object *ve_) {
  double **m = cCore_mk_empty_matrix(4, 1);
  m[0][0] = ve_->x;
  m[1][0] = ve_->y;
  m[2][0] = ve_->z;
  m[3][0] = 1;
  CCORE_RETURN_MATRIX_OBJ(m, 4, 1);
}
static PyObject *Matrix_from_vector(PyObject *cls, PyObject *ve) {
  if (!PyObject_TypeCheck(ve, &Vec3Type)) {
    PyErr_SetString(PyExc_TypeError, "can only call from_vector() with a Vec3");
    return NULL;
  }
  return (PyObject *)Matrix_from_vector_obj((Vec3Object *)ve);
}
static MatrixObject *Matrix_lookat_obj(Vec3Object *eye, Vec3Object *center,
                                       Vec3Object *up) {
  Vec3Object *z = Vec3_normalized_obj_(Vec3__sub__obj_(eye, center));
  Vec3Object *x = Vec3_normalized_obj_(Vec3_cross_obj_(up, z));
  Vec3Object *y = Vec3_normalized_obj_(Vec3_cross_obj_(z, x));
  double **minv = cCore_mk_id_matrix(4);
  double **tr = cCore_mk_id_matrix(4);
  minv[0][0] = x->x;
  minv[0][1] = x->y;
  minv[0][2] = x->z;
  minv[1][0] = y->x;
  minv[1][1] = y->y;
  minv[1][2] = y->z;
  minv[2][0] = z->x;
  minv[2][1] = z->y;
  minv[2][2] = z->z;
  tr[0][3] = -eye->x;
  tr[1][3] = -eye->y;
  tr[2][3] = -eye->z;
  CCORE_MK_MATRIX_OBJ(minv, 4, 4, minvm);
  CCORE_MK_MATRIX_OBJ(tr, 4, 4, trm);
  return Matrix__matmul__obj(minvm, trm);
}
static PyObject *Matrix_lookat(PyObject *cls, PyObject *args) {
  PyObject *eye, *center, *up;
  if (!PyArg_ParseTuple(args, "O!O!O!", &Vec3Type, &eye, &Vec3Type, &center,
                        &Vec3Type, &up)) {
    return NULL;
  }
  return (PyObject *)Matrix_lookat_obj((Vec3Object *)eye, (Vec3Object *)center,
                                       (Vec3Object *)up);
}
// MATH
double _Matrix_determinant_asdouble(PyObject *self) {
  MatrixObject *self_ = (MatrixObject *)self;
  double **m = self_->m;
  double result = m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
                  m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
                  m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
  return result;
}
static PyObject *Matrix_determinant(PyObject *self, PyObject *_) {
  MatrixObject *self_ = (MatrixObject *)self;
  CCORE_MATRIX_ASSERT_SQUARE(self_, 3);
  return PyFloat_FromDouble(_Matrix_determinant_asdouble(self));
}

static MatrixObject *Matrix__matmul__obj(MatrixObject *self_,
                                         MatrixObject *other_) {

  double **m = cCore_mk_empty_matrix(self_->rows, other_->cols);
  for (Py_ssize_t i = 0; i < self_->rows; i++) {
    for (Py_ssize_t j = 0; j < other_->cols; j++) {
      for (Py_ssize_t k = 0; k < self_->cols; k++) {
        m[i][j] += self_->m[i][k] * other_->m[k][j];
      }
    }
  }
  CCORE_RETURN_MATRIX_OBJ(m, self_->rows, other_->cols);
}
static Vec3Object *Matrix__matmul__obj_2vec3(MatrixObject *self_,
                                             MatrixObject *ma) {
  MatrixObject *re = Matrix__matmul__obj(self_, ma);
  Vec3Object *rev = CCORE_NEW_VEC3;
  rev->x = re->m[0][0];
  rev->y = re->m[1][0];
  rev->z = re->m[2][0];
  return rev;
}
static Vec3Object *Matrix_apply_to_vec3(MatrixObject *self_, Vec3Object *ve) {
  return Matrix__matmul__obj_2vec3(self_, Matrix_from_vector_obj(ve));
}
static PyObject *Matrix__matmul__(PyObject *self, PyObject *other) {
  /*
   * If the argument is a vec3, convert it to a matrix and return the result as
   * a vector otherwise mmul
   */
  bool is_vec3 = false;
  if (!PyObject_TypeCheck(self, &MatrixType)) {
    return Matrix__matmul__(other, self);
  }
  if (PyObject_TypeCheck(other, &Vec3Type)) {
    is_vec3 = true;
    other = Matrix_from_vector(self, other);
  } else if (!PyObject_TypeCheck(other, &MatrixType)) {
    PyErr_SetString(PyExc_TypeError, "@ operator must be a Matrix");
    return NULL;
  }
  MatrixObject *self_ = (MatrixObject *)self;
  MatrixObject *other_ = (MatrixObject *)other;
  MatrixObject *result = Matrix__matmul__obj(self_, other_);
  if (!is_vec3) {
    return (PyObject *)result;
  } else {

    Vec3Object *res = CCORE_NEW_VEC3;
    if (result->rows == 4) {
      res->x = floor(result->m[0][0] / result->m[3][0]);
      res->y = floor(result->m[1][0] / result->m[3][0]);
      res->z = floor(-result->m[2][0] / result->m[3][0]);
    } else {
      res->x = result->m[0][0];
      res->y = result->m[1][0];
      res->z = result->m[2][0];
    }
    return (PyObject *)res;
  }
}
static MatrixObject *Matrix_inverse_obj(MatrixObject *self_) {
  CCORE_MATRIX_ASSERT_SQUARE(self_, 3);
  double det = _Matrix_determinant_asdouble((PyObject *)self_);
  if (det == 0) {
    PyErr_SetString(PyExc_ValueError,
                    "Non invertible Matrix (determinant is 0)");
    return NULL;
  }
  double inv_det = 1. / det;
  double **inv = cCore_mk_empty_matrix(3, 3);
  double **m = self_->m;
  inv[0][0] = (m[1][1] * m[2][2] - m[1][2] * m[2][1]) * inv_det;
  inv[0][1] = -(m[0][1] * m[2][2] - m[0][2] * m[2][1]) * inv_det;
  inv[0][2] = (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * inv_det;
  inv[1][0] = -(m[1][0] * m[2][2] - m[1][2] * m[2][0]) * inv_det;
  inv[1][1] = (m[0][0] * m[2][2] - m[0][2] * m[2][0]) * inv_det;
  inv[1][2] = -(m[0][0] * m[1][2] - m[0][2] * m[1][0]) * inv_det;
  inv[2][0] = (m[1][0] * m[2][1] - m[1][1] * m[2][0]) * inv_det;
  inv[2][1] = -(m[0][0] * m[2][1] - m[0][1] * m[2][0]) * inv_det;
  inv[2][2] = (m[0][0] * m[1][1] - m[0][1] * m[1][0]) * inv_det;
  CCORE_RETURN_MATRIX_OBJ(inv, 3, 3);
}
static PyObject *Matrix_inverse(PyObject *self, PyObject *_) {
  MatrixObject *self_ = (MatrixObject *)self;
  return (PyObject *)Matrix_inverse_obj(self_);
}
double _Matrix_determinant4x4_asdouble(PyObject *self) {
  MatrixObject *self_ = (MatrixObject *)self;
  double **m = self_->m;

  double det = m[0][0] * (m[1][1] * (m[2][2] * m[3][3] - m[2][3] * m[3][2]) -
                          m[1][2] * (m[2][1] * m[3][3] - m[2][3] * m[3][1]) +
                          m[1][3] * (m[2][1] * m[3][2] - m[2][2] * m[3][1])) -
               m[0][1] * (m[1][0] * (m[2][2] * m[3][3] - m[2][3] * m[3][2]) -
                          m[1][2] * (m[2][0] * m[3][3] - m[2][3] * m[3][0]) +
                          m[1][3] * (m[2][0] * m[3][2] - m[2][2] * m[3][0])) +
               m[0][2] * (m[1][0] * (m[2][1] * m[3][3] - m[2][3] * m[3][1]) -
                          m[1][1] * (m[2][0] * m[3][3] - m[2][3] * m[3][0]) +
                          m[1][3] * (m[2][0] * m[3][1] - m[2][1] * m[3][0])) -
               m[0][3] * (m[1][0] * (m[2][1] * m[3][2] - m[2][2] * m[3][1]) -
                          m[1][1] * (m[2][0] * m[3][2] - m[2][2] * m[3][0]) +
                          m[1][2] * (m[2][0] * m[3][1] - m[2][1] * m[3][0]));

  return det;
}
static PyObject *Matrix_determinant4x4(PyObject *self, PyObject *_) {
  MatrixObject *self_ = (MatrixObject *)self;
  CCORE_MATRIX_ASSERT_SQUARE(self_, 4);
  return PyFloat_FromDouble(_Matrix_determinant4x4_asdouble(self));
}
static MatrixObject *Matrix_inverse4x4_obj(MatrixObject *self_) {
  CCORE_MATRIX_ASSERT_SQUARE(self_, 4);

  double det = _Matrix_determinant4x4_asdouble((PyObject *)self_);
  if (det == 0) {
    PyErr_SetString(PyExc_ValueError,
                    "Non-invertible Matrix (determinant is 0)");
    return NULL;
  }

  double inv_det = 1.0 / det;
  double **inv = cCore_mk_empty_matrix(4, 4);
  double **m = self_->m;

  inv[0][0] = (m[1][1] * (m[2][2] * m[3][3] - m[2][3] * m[3][2]) -
               m[1][2] * (m[2][1] * m[3][3] - m[2][3] * m[3][1]) +
               m[1][3] * (m[2][1] * m[3][2] - m[2][2] * m[3][1])) *
              inv_det;

  inv[0][1] = -(m[0][1] * (m[2][2] * m[3][3] - m[2][3] * m[3][2]) -
                m[0][2] * (m[2][1] * m[3][3] - m[2][3] * m[3][1]) +
                m[0][3] * (m[2][1] * m[3][2] - m[2][2] * m[3][1])) *
              inv_det;

  inv[0][2] = (m[0][1] * (m[1][2] * m[3][3] - m[1][3] * m[3][2]) -
               m[0][2] * (m[1][1] * m[3][3] - m[1][3] * m[3][1]) +
               m[0][3] * (m[1][1] * m[3][2] - m[1][2] * m[3][1])) *
              inv_det;

  inv[0][3] = -(m[0][1] * (m[1][2] * m[2][3] - m[1][3] * m[2][2]) -
                m[0][2] * (m[1][1] * m[2][3] - m[1][3] * m[2][1]) +
                m[0][3] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])) *
              inv_det;

  inv[1][0] = -(m[1][0] * (m[2][2] * m[3][3] - m[2][3] * m[3][2]) -
                m[1][2] * (m[2][0] * m[3][3] - m[2][3] * m[3][0]) +
                m[1][3] * (m[2][0] * m[3][2] - m[2][2] * m[3][0])) *
              inv_det;

  inv[1][1] = (m[0][0] * (m[2][2] * m[3][3] - m[2][3] * m[3][2]) -
               m[0][2] * (m[2][0] * m[3][3] - m[2][3] * m[3][0]) +
               m[0][3] * (m[2][0] * m[3][2] - m[2][2] * m[3][0])) *
              inv_det;

  inv[1][2] = -(m[0][0] * (m[1][2] * m[3][3] - m[1][3] * m[3][2]) -
                m[0][2] * (m[1][0] * m[3][3] - m[1][3] * m[3][0]) +
                m[0][3] * (m[1][0] * m[3][2] - m[1][2] * m[3][0])) *
              inv_det;

  inv[1][3] = (m[0][0] * (m[1][2] * m[2][3] - m[1][3] * m[2][2]) -
               m[0][2] * (m[1][0] * m[2][3] - m[1][3] * m[2][0]) +
               m[0][3] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])) *
              inv_det;

  inv[2][0] = (m[1][0] * (m[2][1] * m[3][3] - m[2][3] * m[3][1]) -
               m[1][1] * (m[2][0] * m[3][3] - m[2][3] * m[3][0]) +
               m[1][3] * (m[2][0] * m[3][1] - m[2][1] * m[3][0])) *
              inv_det;

  inv[2][1] = -(m[0][0] * (m[2][1] * m[3][3] - m[2][3] * m[3][1]) -
                m[0][1] * (m[2][0] * m[3][3] - m[2][3] * m[3][0]) +
                m[0][3] * (m[2][0] * m[3][1] - m[2][1] * m[3][0])) *
              inv_det;

  inv[2][2] = (m[0][0] * (m[1][1] * m[3][3] - m[1][3] * m[3][1]) -
               m[0][1] * (m[1][0] * m[3][3] - m[1][3] * m[3][0]) +
               m[0][3] * (m[1][0] * m[3][1] - m[1][1] * m[3][0])) *
              inv_det;

  inv[2][3] = -(m[0][0] * (m[1][1] * m[2][3] - m[1][3] * m[2][1]) -
                m[0][1] * (m[1][0] * m[2][3] - m[1][3] * m[2][0]) +
                m[0][3] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])) *
              inv_det;

  inv[3][0] = -(m[1][0] * (m[2][1] * m[3][2] - m[2][2] * m[3][1]) -
                m[1][1] * (m[2][0] * m[3][2] - m[2][2] * m[3][0]) +
                m[1][2] * (m[2][0] * m[3][1] - m[2][1] * m[3][0])) *
              inv_det;

  inv[3][1] = (m[0][0] * (m[2][1] * m[3][2] - m[2][2] * m[3][1]) -
               m[0][1] * (m[2][0] * m[3][2] - m[2][2] * m[3][0]) +
               m[0][2] * (m[2][0] * m[3][1] - m[2][1] * m[3][0])) *
              inv_det;

  inv[3][2] = -(m[0][0] * (m[1][1] * m[3][2] - m[1][2] * m[3][1]) -
                m[0][1] * (m[1][0] * m[3][2] - m[1][2] * m[3][0]) +
                m[0][2] * (m[1][0] * m[3][1] - m[1][1] * m[3][0])) *
              inv_det;

  inv[3][3] = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
               m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
               m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])) *
              inv_det;

  CCORE_RETURN_MATRIX_OBJ(inv, 4, 4);
}
static PyObject *Matrix_inverse4x4(PyObject *self, PyObject *_) {
  MatrixObject *self_ = (MatrixObject *)self;
  return (PyObject *)Matrix_inverse4x4_obj(self_);
}
static MatrixObject *Matrix_inverse_projection_obj(double cam_z) {
  double **m = cCore_mk_id_matrix(4);
  m[3][2] = -1. / cam_z;
  CCORE_RETURN_MATRIX_OBJ(m, 4, 4);
}

static PyObject *Matrix_inverse_projection(PyObject *cls, PyObject *o) {
  if (!PyNumber_Check(o)) {
    return NULL;
  }
  double camz = PyFloat_AsDouble(o);
  return (PyObject *)Matrix_inverse_projection_obj(camz);
}
static MatrixObject *Matrix_inverse_viewport_obj(double x, double y, double w,
                                                 double h) {
  double **m = cCore_mk_id_matrix(4);
  m[0][0] = 2. / w;
  m[1][1] = 2. / h;
  m[2][2] = 1. / (VIEWPORT_DEPTH / 2.);
  m[0][3] = -(2. * x / w) - 1.;
  m[1][3] = -(2. * y / h) - 1.;
  m[2][3] = -1;
  CCORE_RETURN_MATRIX_OBJ(m, 4, 4);
}
static PyObject *Matrix_inverse_viewport(PyObject *cls, PyObject *args) {
  double x, y, w, h;
  if (!PyArg_ParseTuple(args, "dddd", &x, &y, &w, &h)) {
    return NULL;
  };
  return (PyObject *)Matrix_inverse_viewport_obj(x, y, w, h);
}
// MISC

static PyObject *Matrix__getitem__(PyObject *self, PyObject *idx) {
  if (PyLong_Check(idx)) {
    MatrixObject *self_ = (MatrixObject *)self;
    long index = PyLong_AsLong(idx);
    if (PyErr_Occurred()) {
      return NULL;
    }
    if (index >= self_->rows) {
      PyErr_SetString(PyExc_IndexError, "Matrix index out of range");
      return NULL;
    }
    PyObject *item = PyList_New(self_->cols);

    for (Py_ssize_t i = 0; i < self_->cols; i++) {
      PyList_SetItem(item, i, PyFloat_FromDouble(self_->m[index][i]));
    }
    return item;
  } else if (PyTuple_Check(idx)) {
    int i, j;
    if (!PyArg_ParseTuple(idx, "ii", &i, &j)) {
      PyErr_SetString(PyExc_TypeError, "Bad index");
      return NULL;
    }

    return PyFloat_FromDouble(((MatrixObject *)self)->m[i][j]);
  }
  PyErr_SetString(PyExc_TypeError, "Matrix index must be an int or a tuple");
  return NULL;
}
static PyObject *Matrix__repr__(PyObject *self) {
  MatrixObject *self_ = (MatrixObject *)self;
  PyObject *m = PyList_New(0);

  for (Py_ssize_t i = 0; i < self_->rows; i++) {
    PyList_Append(m, Matrix__getitem__(self, PyLong_FromSsize_t(i)));
  }
  return PyUnicode_FromFormat("Matrix(%R)", m);
}
// STRUCTS
static PyMemberDef Matrix_members[] = {
    //{"m", Py_T_OBJECT_EX, offsetof(MatrixObject, m), 0, "Matrix as sequence"},
    {"rows", Py_T_PYSSIZET, offsetof(MatrixObject, rows), 0,
     "Number of rows in the matrix"},
    {"cols", Py_T_PYSSIZET, offsetof(MatrixObject, cols), 0,
     "Number of columns in the matrix"},
    {NULL},
};
static PyMethodDef Matrix_methods[] = {
    {"empty", &Matrix_empty, METH_VARARGS | METH_CLASS,
     "Creates an N*M empty matrix"},
    {"identity", &Matrix_identity, METH_VARARGS | METH_CLASS,
     "Creates an M*M identity transformation matrix"},
    {"rotx", &Matrix_rotx, METH_VARARGS | METH_CLASS,
     "Creates a 3D x rotation matrix by theta"},
    {"roty", &Matrix_roty, METH_VARARGS | METH_CLASS,
     "Creates a 3D y rotation matrix by theta"},
    {"rotz", &Matrix_rotz, METH_VARARGS | METH_CLASS,
     "Creates a 3D z rotation matrix by theta"},
    {"viewport", &Matrix_viewport, METH_VARARGS | METH_CLASS,
     "Creates a viewport matrix"},
    {"lookat", &Matrix_lookat, METH_VARARGS | METH_CLASS},
    {"projection", &Matrix_projection, METH_O | METH_CLASS,
     "Creates a projection matrix"},
    {"from_vector", &Matrix_from_vector, METH_O | METH_CLASS,
     "Creates a matrix from a vec3"},
    {"determinant", &Matrix_determinant, METH_NOARGS,
     "Returns the 3*3 matrix determinant"},
    {"inverse", &Matrix_inverse, METH_NOARGS, "Returns the 3x3 inverse matrix"},
    {"determinant4x4", &Matrix_determinant4x4, METH_NOARGS,
     "Returns the 4*4 matrix determinant"},
    {"inverse4x4", &Matrix_inverse4x4, METH_NOARGS,
     "Returns the 4x4 inverse matrix"},
    {"inverse_viewport", &Matrix_inverse_viewport, METH_VARARGS | METH_CLASS,
     "Creates an inverse viewport matrix"},
    {"inverse_projection", &Matrix_inverse_projection, METH_O | METH_CLASS,
     "Creates an inverse projection matrix"},

    {NULL},
};
static PyMappingMethods Matrix_mapping = {
    .mp_subscript = &Matrix__getitem__,
};
static PyNumberMethods Matrix_number = {
    .nb_matrix_multiply = Matrix__matmul__,
};
static PyTypeObject MatrixType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "cCore.Matrix",
    .tp_doc = "A Matrix class",
    .tp_basicsize = sizeof(MatrixObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Matrix_new,
    .tp_init = (initproc)Matrix_init,
    .tp_dealloc = (destructor)Matrix_dealloc,
    .tp_members = Matrix_members,
    .tp_methods = Matrix_methods,
    .tp_as_mapping = &Matrix_mapping,
    .tp_as_number = &Matrix_number,
    .tp_repr = Matrix__repr__

};
static PyObject *Texture_new(PyTypeObject *type, PyObject *args,
                             PyObject *kwds) {
  TextureObject *self;
  self = (TextureObject *)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->width = 0;
    self->height = 0;
    self->m = NULL;
  }
  return (PyObject *)self;
}
static void Texture_dealloc(TextureObject *self) {
  if (self->m != NULL) {
    for (Py_ssize_t i = 0; i < self->height; i++) {
      for (Py_ssize_t j = 0; j < self->width; j++) {

        Vec3_dealloc(self->m[i][j]);
      }
      free(self->m[i]);
    }
    free(self->m);
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}
static int Texture_init(TextureObject *self, PyObject *args, PyObject *kwds) {
  Py_ssize_t width = 0, height = 0;
  PyObject *pycolor = NULL;
  Vec3Object *color = NULL;
  static char *kwlist[] = {"width", "height", "color", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "nn|O!", kwlist, &width, &height,
                                   &Vec3Type, &pycolor)) {
    return -1;
  }
  if (!pycolor) {
    color = VEC3_ALLZEROS;
  } else {
    color = (Vec3Object *)pycolor;
  }
  self->width = width;
  self->height = height;
  self->m = malloc(width * height * sizeof(Vec3Object *));
  if (self->m == NULL) {
    PyErr_SetString(PyExc_MemoryError, "malloc fail");
    return -1;
  }
  for (Py_ssize_t i = 0; i < self->height; i++) {
    self->m[i] = calloc(width, sizeof(Vec3Object *));
    for (Py_ssize_t j = 0; j < self->width; j++) {
      self->m[i][j] = color;
    }
  }
  return 0;
}
static PyObject *Texture_from_ppm(PyObject *cls, PyObject *args) {
  char *fn;
  Py_ssize_t width, height;
  int maxn;
  if (!PyArg_ParseTuple(args, "s", &fn)) {
    return NULL;
  }
  FILE *fp = fopen(fn, "r");
  if (!fp) {
    PyErr_SetString(PyExc_OSError, "fopen fail");
    return NULL;
  }
  char mode[3];
  if (!fgets(mode, sizeof(mode), fp)) {
    PyErr_SetString(PyExc_OSError, "ppm format error");
    return NULL;
  }
  if (strcmp(mode, "P6")) {
    PyErr_SetString(PyExc_OSError, "ppm format error");
    return NULL;
  }
  if (fscanf(fp, "%ld %ld %d", &width, &height, &maxn) != 3) {
    PyErr_SetString(PyExc_OSError, "ppm format error");
    return NULL;
  }
  if (maxn != 255) {
    char *es;
    asprintf(&es, "ppm not in 24-bit format: %s", fn);
    PyErr_SetString(PyExc_NotImplementedError, es);
    return NULL;
  }
  Vec3Object ***m = malloc(width * height * sizeof(Vec3Object *));
  int i = 0, j = 0;
  fgetc(fp);
  while (!feof(fp) && i < height) {
    if (j == 0)
      m[i] = calloc(width, sizeof(Vec3Object *));
    unsigned char r = fgetc(fp);
    unsigned char g = fgetc(fp);
    unsigned char b = fgetc(fp);

    /*if (r == EOF || g == EOF || b == EOF) {
      PyErr_SetString(PyExc_EOFError, "eof while reading color");
      return NULL;
    }*/
    Vec3Object *color = cCore_mk_vec3_obj((double)r, (double)g, (double)b);
    m[i][j] = color;
    if (++j == width) {
      i++;
      j = 0;
    }
  }
  TextureObject *texture =
      (TextureObject *)(&TextureType)->tp_alloc(&TextureType, 0);
  texture->width = width;
  texture->height = height;
  texture->m = m;
  return (PyObject *)texture;
}
// MISC
static PyObject *Texture__getitem__(PyObject *self, PyObject *xy) {
  if (!PyTuple_Check(xy)) {
    PyErr_SetString(PyExc_TypeError, "can only index textures with tuples");
    return NULL;
  }

  Py_ssize_t x = 0, y = 0;
  if (!PyArg_ParseTuple(xy, "nn", &x, &y)) {
    PyErr_Clear();
    PyErr_SetString(PyExc_ValueError, "invalid texture index");
    return NULL;
  }
  printf("%ld %ld\n", x, y);
  TextureObject *self_ = (TextureObject *)self;
  if (!(0 <= x && x < self_->width) || !(0 <= y && y < self_->height)) {
    PyErr_SetString(PyExc_IndexError, "texture index out of range");
    return NULL;
  }
  return (PyObject *)self_->m[y][x];
}
static PyMappingMethods Texture_mapping = {.mp_subscript = &Texture__getitem__};
static PyMemberDef Texture_members[] = {
    {"width", Py_T_PYSSIZET, offsetof(TextureObject, width), 0,
     "Texture width in px"},
    {"height", Py_T_PYSSIZET, offsetof(TextureObject, height), 0,
     "Texture height in px"},
    {NULL},
};
static PyMethodDef Texture_methods[] = {
    {"from_ppm", Texture_from_ppm, METH_VARARGS | METH_CLASS,
     "loads the texture froma ppm file"},
    {NULL, NULL, 0, NULL},
};
static PyTypeObject TextureType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "cCore.Texture",
    .tp_doc = "Texture",
    .tp_basicsize = sizeof(TextureObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_members = Texture_members,
    .tp_new = Texture_new,
    .tp_methods = Texture_methods,
    .tp_init = (initproc)Texture_init,
    .tp_dealloc = (destructor)Texture_dealloc,
    .tp_as_mapping = &Texture_mapping,
};
//// formerly core.py
static MatrixObject *
cCore_mk_matrix_from_vec3_obj(Vec3Object *v0, Vec3Object *v1, Vec3Object *v2) {
  double **m = malloc(9 * sizeof(double));
  m[0] = calloc(3, sizeof(double));
  m[1] = calloc(3, sizeof(double));
  m[2] = calloc(3, sizeof(double));
  m[0][0] = v0->x;
  m[0][1] = v0->y;
  m[0][2] = v0->z;
  m[1][0] = v1->x;
  m[1][1] = v1->y;
  m[1][2] = v1->z;
  m[2][0] = v2->x;
  m[2][1] = v2->y;
  m[2][2] = v2->z;
  CCORE_RETURN_MATRIX_OBJ(m, 3, 3);
}
static Vec3Object *cCore_mk_vec3_obj(double x, double y, double z) {
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = x;
  obj->y = y;
  obj->z = z;
  return obj;
}
static PyObject *cCore_mk_vec3(double x, double y, double z) {
  Vec3Object *obj = cCore_mk_vec3_obj(x, y, z);
  return (PyObject *)obj;
}
static Vec3Object *cCore_barymetric_(Vec3Object *v0, Vec3Object *v1,
                                     Vec3Object *v2, double x, double y) {

  Vec3Object *u = (Vec3Object *)Vec3_cross(
      cCore_mk_vec3(v2->x - v0->x, v1->x - v0->x, v0->x - x),
      cCore_mk_vec3(v2->y - v0->y, v1->y - v0->y, v0->y - y));
  double uz = u->z;
  if (fabs(uz) < 1) {
    return cCore_mk_vec3_obj(-1, 1, 1);
  }
  return cCore_mk_vec3_obj(1 - (u->x + u->y) / uz, u->y / uz, u->x / uz);
}
static double cCore_calcphong_1_(double ambient_coeff, double diffuse_coeff,
                                 double specular_coeff, double diff,
                                 double spec, double c) {
  return fmin(
      ambient_coeff + c * (diffuse_coeff * diff + specular_coeff * spec), 255);
}
static Vec3Object *cCore_calcphong_(Vec3Object *normal, Vec3Object *lightdir,
                                    Vec3Object *specular, double ambient_coeff,
                                    double diffuse_coeff, double specular_coeff,
                                    Vec3Object *color) {
  double ndl = Vec3_dot_obj_(normal, lightdir);
  Vec3Object *r = Vec3_normalized_obj_(Vec3__neg__obj_(
      Vec3__sub__obj_(Vec3__mul__obj_(normal, ndl * 2), lightdir)));
  double spec = pow(fmax(r->z, 0), specular->x);
  double diff = fmax(ndl, 0);
  Vec3Object *obj = CCORE_NEW_VEC3;
  obj->x = CCORE_PHONG_1_(color->x);
  obj->y = CCORE_PHONG_1_(color->y);
  obj->z = CCORE_PHONG_1_(color->z);

  return obj;
}

static Vec3_pair *cCore_compute_tangent_space_basis_(
    Vec3Object *v0, Vec3Object *v1, Vec3Object *v2, Vec3Object *uv0,
    Vec3Object *uv1, Vec3Object *uv2, Vec3Object *bn) {
  if (bn == NULL) {
    PyErr_SetString(
        PyExc_ValueError,
        "can't get normals from tangent space without vertex normals");
    return NULL;
  }

  Vec3_pair *dp = (Vec3_pair *)malloc(sizeof(Vec3_pair));
  Vec3Object *d1 = Vec3__sub__obj_(v1, v0);
  Vec3Object *d2 = Vec3__sub__obj_(v2, v0);
  MatrixObject *a = cCore_mk_matrix_from_vec3_obj(d1, d2, bn);
  MatrixObject *ai = Matrix_inverse_obj(a);

  if (PyErr_Occurred()) {
    PyErr_Clear();
    Vec3_dealloc(d1);
    Vec3_dealloc(d2);
    Matrix_dealloc(a);
    dp->a = VEC3_ALLZEROS;
    dp->b = VEC3_ALLZEROS;
    return dp;
  }
  double **mmi = cCore_mk_empty_matrix(4, 1);
  mmi[0][0] = uv1->x - uv0->x;
  mmi[1][0] = uv2->x - uv0->x;
  mmi[2][0] = 0;
  mmi[3][0] = 1;
  CCORE_MK_MATRIX_OBJ(mmi, 4, 1, mi);
  double **mmj = cCore_mk_empty_matrix(4, 1);
  mmj[0][0] = uv1->y - uv0->y;
  mmj[1][0] = uv2->y - uv0->y;
  mmj[2][0] = 0;
  mmj[3][0] = 1;
  CCORE_MK_MATRIX_OBJ(mmj, 4, 1, mj);
  Vec3Object *vi = Vec3_normalized_obj_(Matrix__matmul__obj_2vec3(ai, mi));
  Vec3Object *vj = Vec3_normalized_obj_(Matrix__matmul__obj_2vec3(ai, mj));

  dp->a = vi;
  dp->b = vj;
  return dp;
}
static PyObject *cCore_zero(PyObject *self, PyObject *args) {
  return (PyObject *)VEC3_ALLZEROS;
}
static Vec3Object *cCore_getuv_(TextureObject *texture, Vec3Object *uv) {
  long u = (fabs(uv->x * (texture->width - 1)));
  long v = (fabs(texture->height - uv->y * (texture->height - 1)));
  return texture->m[v % texture->height][u % texture->width];
}
static void cCore_set_pixel_(PyObject *img, double x, double y,
                             Vec3Object *color) {
  PyObject *x_coord = PyFloat_FromDouble(x);
  PyObject *y_coord = PyFloat_FromDouble(y);
  PyObject *coords = PyTuple_Pack(2, x_coord, y_coord);
  PyObject *pycolor = (PyObject *)color;
  PyObject_SetItem(img, coords, pycolor);
  Py_DECREF(pycolor);
  Py_DECREF(coords);
  Py_DECREF(x_coord);
  Py_DECREF(y_coord);
}
static bool cCore_draw_triangle_(
    PyObject *img, double width, double height, Vec3Object *v0, Vec3Object *v1,
    Vec3Object *v2, TextureObject *color_or_texture, MatrixObject *zbuffer,
    Lighting lighting, Triangle *texture_coords, Triangle *vertex_normals,
    TextureObject *normal_map, TextureObject *specular_map,
    Vec3Object *light_dir, double ambient_coeff, double diffuse_coeff,
    double specular_coeff, Vec3Object *rotation, int tangent_space,
    double mindepth) {
  if (zbuffer->rows <= height || zbuffer->cols <= width) {
    PyErr_SetString(PyExc_ValueError, "zbuffer too small");
    return false;
  }
  double minx = fmax(0, fmin(fmin(v0->x, v1->x), v2->x));
  double miny = fmax(0, fmin(fmin(v0->y, v1->y), v2->y));
  double maxx = fmin(width, fmax(fmax(v0->x, v1->x), v2->x));
  double maxy = fmin(height, fmax(fmax(v0->y, v1->y), v2->y));
  if (light_dir == NULL) {
    light_dir = VEC3_ZBACK;
  }
  for (int x = minx; x <= maxx + 1; x++) {
    for (int y = miny; y <= maxy + 1; y++) {

      double u, v, w;
      double gouraud_scale = 1;
      Vec3Object *phong;
      Vec3Object *col;
      Vec3Object *ta, *tb, *tc;
      // printf("bary\n");
      Vec3Object *uv = cCore_barymetric_(v0, v1, v2, x, y);
      u = uv->x;
      v = uv->y;
      w = uv->z;
      if (u >= 0 && v >= 0 && w >= 0 && 0 <= x && x <= width && 0 <= y &&
          y <= height) {
        double z = v0->z * u + v1->z * v + v2->z * w;
        double zbuffer_z = zbuffer->m[y][x];
        if (!zbuffer_z || zbuffer_z < z) {
          zbuffer->m[y][x] = z;
          if (lighting == DEPTH) {
            cCore_set_pixel_(
                img, x, y,
                Vec3__mul__obj_(
                    VEC3_ALLONES,
                    fmin(255, fmax(0, 255 * (mindepth + z) / (mindepth * 2)))));
            continue;
          }
          Vec3Object *interpolated_uv_normal = NULL, *uv_normal = NULL;
          if (vertex_normals != NULL) {
            Vec3Object *na = vertex_normals->v0;
            Vec3Object *nb = vertex_normals->v1;
            Vec3Object *nc = vertex_normals->v2;
            interpolated_uv_normal = Vec3__add__obj_(
                Vec3__add__obj_(Vec3__mul__obj_(na, u), Vec3__mul__obj_(nb, v)),
                Vec3__mul__obj_(nc, w));
            uv_normal = interpolated_uv_normal;
          }
          if (texture_coords == NULL) {
            col = color_or_texture->m[0][0];
            if (lighting == PHONG) {
              PyErr_SetString(PyExc_ValueError,
                              "can't phong without texture coords");
              return false;
            } else if (lighting == GOURAUD) {
              if (interpolated_uv_normal != NULL) {
                gouraud_scale =
                    fmax(0, -Vec3_dot_obj_(interpolated_uv_normal, light_dir));
              }
            }
          } else {

            ta = texture_coords->v0;
            tb = texture_coords->v1;
            tc = texture_coords->v2;

            Vec3Object *tp = Vec3__add__obj_(
                Vec3__add__obj_(Vec3__mul__obj_(ta, u), Vec3__mul__obj_(tb, v)),
                Vec3__mul__obj_(tc, w));
            col = cCore_getuv_(color_or_texture, tp);
            if (lighting == NONE) {
              cCore_set_pixel_(img, x, y, Vec3__mul__obj_(col, 1));
              if (PyErr_Occurred()) {
                return NULL;
              }
              continue;
            }

            if (normal_map != NULL) {
              Vec3Object *sampled_normal = cCore_getuv_(normal_map, tp);
              if (!sampled_normal) {
                return false;
              }
              uv_normal = Vec3_normalized_obj_(Vec3__sub__obj_(
                  Vec3__mul__obj_(sampled_normal, 2. / 255.), VEC3_ALLONES));
              if (tangent_space) {
                Vec3_pair *ij = cCore_compute_tangent_space_basis_(
                    v0, v1, v2, ta, tb, tc, interpolated_uv_normal);
                Vec3Object *i = ij->a;
                Vec3Object *j = ij->b;
                MatrixObject *tbn_matrix =
                    cCore_mk_matrix_from_vec3_obj(i, j, interpolated_uv_normal);
                uv_normal = Vec3_normalized_obj_(
                    Matrix_apply_to_vec3(tbn_matrix, uv_normal));
              }
            }
            if (uv_normal == NULL) {
              gouraud_scale = 1;
              phong = col;
            } else {
              if (lighting == GOURAUD) {
                gouraud_scale = fmax(0, -Vec3_dot_obj_(uv_normal, light_dir));

              } else if (lighting == PHONG) {
                Vec3Object *specular_uv = VEC3_ALLONES;
                if (specular_map != NULL) {
                  specular_uv = cCore_getuv_(specular_map, tp);
                }
                phong = cCore_calcphong_(Vec3__neg__obj_(uv_normal), light_dir,
                                         specular_uv, ambient_coeff,
                                         diffuse_coeff, specular_coeff, col);
              }
            }
          }
          if (lighting == GOURAUD) {
            cCore_set_pixel_(img, x, y, Vec3__mul__obj_(col, gouraud_scale));

          } else if (lighting == PHONG) {
            cCore_set_pixel_(img, x, y, phong);
          }
        }
      }
    }
  }
  return true;
}
static Triangle *cCore_sequence_to_triangle(PyObject *seq) {
  if (seq == Py_None) {
    return NULL;
  }
  PyObject *v0p = PySequence_GetItem(seq, 0);

  PyObject *v1p = PySequence_GetItem(seq, 1);
  PyObject *v2p = PySequence_GetItem(seq, 2);
  if (!(PyObject_TypeCheck(v0p, &Vec3Type) &&
        PyObject_TypeCheck(v1p, &Vec3Type) &&
        PyObject_TypeCheck(v2p, &Vec3Type))) {
    PyErr_SetString(PyExc_TypeError, ("all triangle vertices must be vec3s"));
    return NULL;
  }
  Triangle *tr = malloc(sizeof(Triangle));
  tr->v0 = (Vec3Object *)v0p;
  tr->v1 = (Vec3Object *)v1p;
  tr->v2 = (Vec3Object *)v2p;
  return tr;
}
static PyObject *cCore_draw_triangle(PyObject *self, PyObject *args,
                                     PyObject *kwargs) {
  PyObject *img, *v0, *v1, *v2, *color_or_texture,
      *zbuffer = PyDict_New(), *texture_coords = Py_None,
      *vertex_normals = Py_None, *specular_map = NULL, *normal_map = NULL,
      *light_dir = Py_None, *rotation = Py_None;
  double width, height, mindepth = 300;
  double ambient_coeff = 0.6, diffuse_coeff = 1, specular_coeff = 0.7;
  bool tangent_space;
  const char *lighting = "phong";
  static char *kwlist[] = {"img",
                           "width",
                           "height",
                           "v0",
                           "v1",
                           "v2",
                           "color_or_texture",
                           "zbuffer",
                           "lighting",
                           "texture_coords",
                           "vertex_normals",
                           "specular_map",
                           "normal_map",
                           "light_dir",
                           "ambient_coeff",
                           "diffuse_coeff",
                           "specular_coeff",
                           "rotation",
                           "tangent_space",
                           "mindepth",
                           NULL};
  if (!PyArg_ParseTupleAndKeywords(
          args, kwargs, "OddO!O!O!O!|O!sOOO!O!O!dddO!pd", kwlist, &img, &width,
          &height, &Vec3Type, &v0, &Vec3Type, &v1, &Vec3Type, &v2, &TextureType,
          &color_or_texture, &MatrixType, &zbuffer, &lighting, &texture_coords,
          &vertex_normals, &TextureType, &specular_map, &TextureType,
          &normal_map, &Vec3Type, &light_dir, &ambient_coeff, &diffuse_coeff,
          &specular_coeff, &Vec3Type, &rotation, &tangent_space, &mindepth)) {
    return NULL;
  }
  // printf("load ok\n");
  Lighting lght;
  if (!strcmp(lighting, "phong")) {
    lght = PHONG;
  } else if (!strcmp(lighting, "gouraud")) {
    lght = GOURAUD;
  } else if (!strcmp(lighting, "none")) {
    lght = NONE;
  } else if (!strcmp(lighting, "depth")) {
    lght = DEPTH;
  } else {
    PyErr_SetString(PyExc_ValueError, "unknown lighting mode");
    return NULL;
  }
  // printf("light ok\n");
  Triangle *texture_coords_tri = cCore_sequence_to_triangle(texture_coords);
  Triangle *vertex_normals_tri = cCore_sequence_to_triangle(vertex_normals);
  // printf("triangles ok\n");
  if (!cCore_draw_triangle_(
          img, width, height, (Vec3Object *)v0, (Vec3Object *)v1,
          (Vec3Object *)v2, (TextureObject *)color_or_texture,
          (MatrixObject *)zbuffer, lght, texture_coords_tri, vertex_normals_tri,
          (TextureObject *)normal_map, (TextureObject *)specular_map,
          (Vec3Object *)light_dir, ambient_coeff, diffuse_coeff, specular_coeff,
          (Vec3Object *)rotation, tangent_space, mindepth)) {
    return NULL;
  }
  free(texture_coords_tri);
  free(vertex_normals_tri);
  return Py_None; // TODO
}
static PyObject *cCore_compute_tangent_space_basis(PyObject *self,
                                                   PyObject *args) {
  PyObject *v0, *v1, *v2, *uv0, *uv1, *uv2, *bn;
  if (!PyArg_ParseTuple(args, "OOOOOOO", &v0, &v1, &v2, &bn, &uv0, &uv1,
                        &uv2)) {
    return NULL;
  }
  if (!(PyObject_TypeCheck(v0, &Vec3Type) &&
        PyObject_TypeCheck(v1, &Vec3Type) &&
        PyObject_TypeCheck(v2, &Vec3Type) &&
        PyObject_TypeCheck(uv0, &Vec3Type) &&
        PyObject_TypeCheck(uv1, &Vec3Type) &&
        PyObject_TypeCheck(uv2, &Vec3Type) &&
        PyObject_TypeCheck(bn, &Vec3Type))) {
    PyErr_SetString(PyExc_TypeError, "all args must be vec3s");
    return NULL;
  }
  Vec3_pair *dp = cCore_compute_tangent_space_basis_(
      (Vec3Object *)v0, (Vec3Object *)v1, (Vec3Object *)v2, (Vec3Object *)uv0,
      (Vec3Object *)uv1, (Vec3Object *)uv2, (Vec3Object *)bn);
  if (!dp) {
    return NULL;
  }
  return PyTuple_Pack(2, (PyObject *)dp->a, (PyObject *)dp->b);
}
static PyObject *cCore_calcphong(PyObject *self, PyObject *args) {
  PyObject *normal, *lightdir, *specular, *color;
  double ac, dc, sc;
  if (!PyArg_ParseTuple(args, "OOOdddO", &normal, &lightdir, &specular, &ac,
                        &dc, &sc, &color)) {
    return NULL;
  }
  if (!(PyObject_TypeCheck(normal, &Vec3Type) &&
        PyObject_TypeCheck(lightdir, &Vec3Type) &&
        PyObject_TypeCheck(specular, &Vec3Type) &&
        PyObject_TypeCheck(color, &Vec3Type))) {
    PyErr_SetString(PyExc_TypeError, "args 0, 1, 2, 6 must be vec3s");
    return NULL;
  }
  return (PyObject *)cCore_calcphong_(
      (Vec3Object *)normal, (Vec3Object *)lightdir, (Vec3Object *)specular, ac,
      dc, sc, (Vec3Object *)color);
}
static PyObject *cCore_barymetric(PyObject *self, PyObject *args) {
  PyObject *v0, *v1, *v2;
  double x, y;
  if (!PyArg_ParseTuple(args, "OOOdd", &v0, &v1, &v2, &x, &y)) {
    return NULL;
  }
  if (!(PyObject_TypeCheck(v0, &Vec3Type) &&
        PyObject_TypeCheck(v1, &Vec3Type) &&
        PyObject_TypeCheck(v2, &Vec3Type))) {
    PyErr_SetString(PyExc_TypeError, "args 0, 1, 2 must be vec3s");
    return NULL;
  }
  return (PyObject *)cCore_barymetric_((Vec3Object *)v0, (Vec3Object *)v1,
                                       (Vec3Object *)v2, x, y);
}
////INIT
static PyMethodDef cCore_methods[] = {
    {"barymetric", cCore_barymetric, METH_VARARGS, "barymetric coords"},
    {"calc_phong", cCore_calcphong, METH_VARARGS, "phong shading calculation"},

    {"compute_tangent_space_basis", cCore_compute_tangent_space_basis,
     METH_VARARGS, "tangent space basis"},
    {"draw_triangle", (PyCFunction)(void (*)(void))cCore_draw_triangle,
     METH_VARARGS | METH_KEYWORDS, "draws a triangle"},
    {"zero", cCore_zero, METH_NOARGS, "A"},
    {NULL, NULL, 0, NULL},
};
static PyModuleDef ccoremodule = {PyModuleDef_HEAD_INIT,
                                  "cCore",
                                  "Core C math module",
                                  -1,
                                  cCore_methods,
                                  NULL,
                                  NULL,
                                  NULL,
                                  NULL};

PyMODINIT_FUNC PyInit_cCore(void) {
  PyObject *m;
  /*VEC3_ALLZEROS = cCore_mk_vec3_obj(0, 0, 0);
  VEC3_ALLONES = cCore_mk_vec3_obj(1, 1, 1);
  VEC3_ZBACK = cCore_mk_vec3_obj(0, 0, -1);*/
  if (PyType_Ready(&Vec3Type) < 0)
    return NULL;
  if (PyType_Ready(&MatrixType) < 0)
    return NULL;
  if (PyType_Ready(&TextureType) < 0)
    return NULL;
  m = PyModule_Create(&ccoremodule);
  if (m == NULL)
    return NULL;

  Py_INCREF(&Vec3Type);
  if (PyModule_AddObject(m, "Vec3", (PyObject *)&Vec3Type) < 0) {
    Py_DECREF(&Vec3Type);
    Py_DECREF(m);
    return NULL;
  }
  Py_INCREF(&MatrixType);
  if (PyModule_AddObject(m, "Matrix", (PyObject *)&MatrixType) < 0) {
    Py_DECREF(&MatrixType);
    Py_DECREF(m);
    return NULL;
  }
  Py_INCREF(&TextureType);
  if (PyModule_AddObject(m, "Texture", (PyObject *)&TextureType) < 0) {
    Py_DECREF(&TextureType);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
