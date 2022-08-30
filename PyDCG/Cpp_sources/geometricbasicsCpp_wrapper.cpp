/*    PyDCG

   A Python library for Discrete and Combinatorial Geometry.

   Copyright (C) 2015 Ruy Fabila Monroy

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation version 2.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/

#include "utilities.cpp"

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

PyObject* turn_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    //The C++ function prototype is: int turn(const Punto&, const Punto&, const Punto&);
    PyObject* py_p;
    PyObject* py_q;
    PyObject* py_r;

    long long p[2], q[2], r[2];

    static const char *kwlist[] = {"p", "q", "r", NULL};

    //The arguments must be: 3 lists representing 3 points (each point is a list of two or three integers)
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!O!:turn", (char**)kwlist, &PyList_Type, &py_p, &PyList_Type, &py_q, &PyList_Type, &py_r))
        return NULL;

    p[0] = PyLong_AsLong(PyList_GetItem(py_p, 0));
	p[1] = PyLong_AsLong(PyList_GetItem(py_p, 1));
	q[0] = PyLong_AsLong(PyList_GetItem(py_q, 0));
	q[1] = PyLong_AsLong(PyList_GetItem(py_q, 1));
	r[0] = PyLong_AsLong(PyList_GetItem(py_r, 0));
	r[1] = PyLong_AsLong(PyList_GetItem(py_r, 1));

    if(PyErr_Occurred() != NULL)
        return (PyObject*)NULL;

    if(abs(p[0]) > max_val || abs(p[1]) > max_val || abs(q[0]) > max_val || abs(q[1]) > max_val || abs(r[0]) > max_val || abs(r[1]) > max_val)
    {
        PyErr_SetString(PyExc_OverflowError, max_val_error);
        return (PyObject*)NULL;
    }

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

PyObject* sort_around_point_wrapper(PyObject* self, PyObject* args, PyObject *keywds) //check this. Thereś another sort_around_point version in holesCpp
{
    //The C function prototype is:
    //void sort_around_point(const long long* p, long long** const pts, int n);
	PyObject *py_pts, *py_p;

	static const char *kwlist[] = {"p", "points", NULL};

	//The arguments must be: a list representing a point (a list of two or three integers)
	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!:sort_around_point", (char**)kwlist, &PyList_Type, &py_p, &PyList_Type, &py_pts))
		return NULL;

	Py_ssize_t pts_size = PyList_Size(py_pts);

	long long **c_pts = new long long* [pts_size];
	for(int i=0; i<pts_size; i++)
        c_pts[i] = new long long[2];
	long long p[2];

	p[0] = PyLong_AsLong(PyList_GetItem(py_p, 0));
	p[1] = PyLong_AsLong(PyList_GetItem(py_p, 1));

	if(abs(p[0]) > max_val || abs(p[1]) > max_val)
    {
        PyErr_SetString(PyExc_OverflowError, max_val_error);
        return (PyObject*)NULL;
    }

	for(int i=0; i<pts_size; i++)
	{
		PyObject* temp = PyList_GetItem(py_pts, i); //Borrowed Reference
		c_pts[i][0] = PyLong_AsLong(PyList_GetItem(temp, 0)); //Borrowed References
		c_pts[i][1] = PyLong_AsLong(PyList_GetItem(temp, 1)); //Borrowed References
		if(abs(c_pts[i][0]) > max_val || abs(c_pts[i][1]) > max_val)
        {
            PyErr_SetString(PyExc_OverflowError, max_val_error);
            return (PyObject*)NULL;
        }
	}
    sort_around_point(p, c_pts, pts_size);

    if(PyErr_Occurred() != NULL)
        {
            return (PyObject*)NULL;
        }

	PyObject* res = PyList_New(pts_size);

	for(int i=0; i<pts_size; i++)
	{
		PyObject* temp = PyList_New(2); //New Reference
		PyList_SetItem(temp, 0, PyLong_FromLong(c_pts[i][0])); //Steals Reference
		PyList_SetItem(temp, 1, PyLong_FromLong(c_pts[i][1]));
		PyList_SetItem(res, i, temp);
	}

    for(int i=0; i<pts_size; i++)
        {
            delete[] c_pts[i];
        }

	delete[] c_pts;

	return res;
}

PyMethodDef geometricbasicsCppMethods[] =
{
    {"turn", (PyCFunction)turn_wrapper, METH_VARARGS | METH_KEYWORDS, turn_doc},
    {"sort_around_point", (PyCFunction)sort_around_point_wrapper, METH_VARARGS | METH_KEYWORDS, sort_around_point_doc},
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3
    static struct PyModuleDef moduledef3 = {
        PyModuleDef_HEAD_INIT,
        "geometricbasicsCpp",     /* m_name */
        "Extension written in C++ with basic geometric functions.",  /* m_doc */
        -1,                  /* m_size */
        geometricbasicsCppMethods,    /* m_methods */
        NULL,                /* m_reload */
        NULL,                /* m_traverse */
        NULL,                /* m_clear */
        NULL,                /* m_free */
    };

    //extern "C" PyMODINIT_FUNC initgeometricbasicsCpp(void
    extern "C" PyMODINIT_FUNC PyInit_geometricbasicsCpp(void)
    {
        //(void) PyModule_Create(&moduledef3);
        return PyModule_Create(&moduledef3);
    }
#else
    extern "C" PyMODINIT_FUNC
    initgeometricbasicsCpp(void)
    {
        (void) Py_InitModule3("geometricbasicsCpp", geometricbasicsCppMethods,
                              "Extension written in C++ with basic geometric functions.");
    }
#endif
