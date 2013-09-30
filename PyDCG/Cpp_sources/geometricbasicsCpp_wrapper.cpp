#include <Python.h>
#include "geometricbasicsCpp.h"
#include <iostream>

static const char* turn_doc =
"turn(p, q, r)\n\
    \n\
    Determines whether `p`, `q` and `r` are collinear or form a left or \n\
	right turn.\n\
    \n\
    This function counts how many convex `r`-holes are in `points` (the \n\
    point set may be colored). It is an implementation of the algorithm \n\
    presented in \"Searching for Empty Convex Polygons\" [1]_\n\
    \n\
    Parameters\n\
    ----------\n\
    p : list\n\
        A point is represented as a list of 3 integers: the \n\
		first two are the coordinates of the point, the third\n\
        one is the color. The color is optional.\n\
    q : Analogous to `p`\n\
	r : Analogous to `p`\n\
    \n\
    Returns\n\
    -------\n\
    t : int\n\
        -1 if `p`, `q` and `r` form a left turn,\n\
        -0 if `p`, `q` and `r` are collinear,\n\
		 1 if `p`, `q` and `r` form a right turn,\n\
    \n\
    Notes\n\
    -----\n\
    The coordinates of the points should be less than or equal to :math:`2^{30}` to\n\
    prevent overflow on the C++ side.\n\
    \n\
    Examples\n\
    --------\n\
    >>> import geometricbasicsCpp as gb\n\
    >>> p=[0,0]\n\
	>>> q=[1,0]\n\
	>>> p=[1,1]\n\
    >>> gb.turn(p, q, r)\n\
    -1\n";

extern "C" PyObject* turn_wrapper(PyObject* self, PyObject* args)
{
    //The C++ function prototype is: int turn(const punto&, const punto&, const punto&);
    PyObject* py_p;
    PyObject* py_q;
    PyObject* py_r;

    //The arguments must be: 3 lists representing 3 points (each point is a list of two or three integers)
    if (!PyArg_ParseTuple(args, "O!O!O!:turn", &PyList_Type, &py_p, &PyList_Type, &py_q, &PyList_Type, &py_r))
        return NULL;
        
    if (PyList_Size(py_p) < 2 || PyList_Size(py_q) < 2 || PyList_Size(py_r) < 2)
    {
    	PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
    	return NULL;
    }

    punto p(PyLong_AsLong(PyList_GetItem(py_p, 0)), PyLong_AsLong(PyList_GetItem(py_p, 1)));
    punto q(PyLong_AsLong(PyList_GetItem(py_q, 0)), PyLong_AsLong(PyList_GetItem(py_q, 1)));
    punto r(PyLong_AsLong(PyList_GetItem(py_q, 0)), PyLong_AsLong(PyList_GetItem(py_r, 1)));

    return Py_BuildValue("i", turn(p,q,r));
}

static const char* sort_around_point_doc =
"sort_around_point(p, pts)\n\
    \n\
    Sorts the points in `pts` around point `p`.\n\
    \n\
    This function counts how many convex `r`-holes are in `points` (the \n\
    point set may be colored). It is an implementation of the algorithm \n\
    presented in \"Searching for Empty Convex Polygons\" [1]_\n\
    \n\
    Parameters\n\
    ----------\n\
    p : list\n\
        A point is represented as a list of 3 integers: the \n\
		first two are the coordinates of the point, the third\n\
        one is the color. The color is optional.\n\
    pts : list\n\
        A list containing points, each point in the format described \n\
		above.\n\
    \n\
    Returns\n\
    -------\n\
    s_points : list\n\
        A list with the points in `pts` sorted by angle around `p`\n\
    \n\
    Notes\n\
    -----\n\
    The coordinates of the points should be less than or equal to :math:`2^{30}` to\n\
    prevent overflow on the C++ side.\n\
    \n\
    Examples\n\
    --------\n\
    >>> import geometricbasicsCpp as gb\n\
    >>> p=[0,0]\n\
	>>> q=[1,0]\n\
	>>> p=[1,1]\n\
    >>> gb.turn(p, q, r)\n\
    -1\n";

extern "C" PyObject* sort_around_point_wrapper(PyObject* self, PyObject* args)
{
    //The C function prototype is:
    //void sort_around_point(long p[2], long pts[][2], int n);
	PyObject* py_pts;
	PyObject* py_p;

	//The arguments must be: a list representing a point (a list of two or three integers)
	if (!PyArg_ParseTuple(args, "O!O!:sort_around_point", &PyList_Type, &py_p, &PyList_Type, &py_pts))
		return NULL;

	Py_ssize_t pts_size = PyList_Size(py_pts);
	long (*c_pts)[2] = new long [pts_size] [2];
	long p[2];

	p[0] = PyInt_AsLong(PyList_GetItem(py_p, 0));
	p[1] = PyInt_AsLong(PyList_GetItem(py_p, 1));

	for(int i=0; i<pts_size; i++)
	{
		PyObject* temp = PyList_GetItem(py_pts, i); //Borrowed Reference
		c_pts[i][0] = PyInt_AsLong(PyList_GetItem(temp, 0)); //Borrowed References
		c_pts[i][1] = PyInt_AsLong(PyList_GetItem(temp, 1)); //Borrowed References
	}

	sort_around_point(p, c_pts, pts_size);

	PyObject* res = PyList_New(pts_size);

	for(int i=0; i<pts_size; i++)
	{
		PyObject* temp = PyList_New(2); //New Reference
		PyList_SetItem(temp, 0, PyInt_FromLong(c_pts[i][0])); //Steals Reference
		PyList_SetItem(temp, 1, PyInt_FromLong(c_pts[i][1]));
		PyList_SetItem(res, i, temp);
	}

	return res;
}

extern "C" PyMethodDef geometricbasicsCppMethods[] =
{
    {"turn", turn_wrapper, METH_VARARGS, turn_doc},
    {"sort_around_point", sort_around_point_wrapper, METH_VARARGS, sort_around_point_doc},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initgeometricbasicsCpp(void)
{
    (void) Py_InitModule3("geometricbasicsCpp", geometricbasicsCppMethods,
                          "Extension written in C++ with basic geometric functions.");
}
