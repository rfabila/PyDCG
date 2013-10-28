#include <Python.h>
#include "count_crossing.h"

using std::vector;

static const long long max_val = (1 << 30);

static const char* crossing_doc =
"count_convex_rholes(points, r, mono = True)\n\
    \n\
    Counts the r-holes in a point set.\n\
    \n\
    This function counts how many convex `r`-holes are in `points` (the \n\
    point set may be colored). It is an implementation of the algorithm \n\
    presented in \"Searching for Empty Convex Polygons\" [1]_\n\
    \n\
    Parameters\n\
    ----------\n\
    points : list\n\
        This list represents the point set, each point is represented as a\n\
        list of 3 integers: the first two are the coordinates of the point,\n\
        the third one is the color. The color is optional.\n\
    r : int\n\
        The number of sides of the holes we want to fint in the point set.\n\
    mono : boolean\n\
        Determines wheter to look for monochromatic `r`-holes or not.\n\
    \n\
    Returns\n\
    -------\n\
    h : int\n\
        The number of `r`-holes in `points`.\n\
    \n\
    Notes\n\
    -----\n\
    The coordinates of the points should be less than or equal to :math:`2^{30}` to\n\
    prevent overflow on the C++ side.\n\
    \n\
    Examples\n\
    --------\n\
    The first call counts the empty quadrilaterals, disregarding the color\n\
    of the points. The second call counts only monochromatic quadrilaterals.\n\
    \n\
    >>> import holesCpp as holes\n\
    >>> points=[[0,2,0], [1,0,1], [2,4,0], [4,1,0], [4,3,0]]\n\
    >>> holes.count_convex_rholes(points, 4)\n\
    5\n\
    >>> holes.count_convex_rholes(points, 4, True)\n\
    1\n";

extern "C" PyObject* crossing_wrapper(PyObject* self, PyObject* args)
{
    //The C++ function prototype is: long crossing(long pts[][2], int n);
    PyObject* py_pts;

    //The arguments must be: a list with the points (each point is a list of two integers),
    if (!PyArg_ParseTuple(args, "O!:crossing", &PyList_Type, &py_pts))
        return NULL;

    Py_ssize_t points_size = PyList_Size(py_pts);
    //Py_ssize_t can be bigger than an 2^32, but we don't expect
    //to work with that many points.
    long (*pts)[2] = new long [points_size][2];

    for(Py_ssize_t i=0; i < points_size; i++)
    {
        PyObject *point = PyList_GetItem(py_pts, i); //Borrowed Reference
        Py_ssize_t n_coords = PyList_Size(point);
        long x, y;

        if(n_coords > 3 || n_coords < 2)
        {
            PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
            return NULL;
        }

        x = PyInt_AsLong(PyList_GetItem(point, 0)); //Borrowed References
        y = PyInt_AsLong(PyList_GetItem(point, 1));

        if(x > max_val || y > max_val || x < -max_val || y < -max_val)
        {
            PyErr_SetString(PyExc_ValueError, "The coordinates of each point must less than or equal to 2^30 in absolute value.");
            return NULL;
        }

        pts[i][0] = x;
        pts[i][1] = y;
    }
    int res = crossing(pts, points_size);
    delete[] pts;
    return Py_BuildValue("i", res);
}

extern "C" PyMethodDef crossingCppMethods[] =
{
    {"crossing", crossing_wrapper, METH_VARARGS, crossing_doc},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initcrossingCpp(void)
{
    (void) Py_InitModule3("crossingCpp", crossingCppMethods,
                          "Extension written in C++ intended to help finding sets with few r-holes.");
}
