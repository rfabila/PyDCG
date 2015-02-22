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
    //The C++ function prototype is: int turn(const punto&, const punto&, const punto&);
    PyObject* py_p;
    PyObject* py_q;
    PyObject* py_r;

    punto p, q, r;

    static const char *kwlist[] = {"p", "q", "r", NULL};


    //The arguments must be: 3 lists representing 3 points (each point is a list of two or three integers)
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!O!:turn", (char**)kwlist, &PyList_Type, &py_p, &PyList_Type, &py_q, &PyList_Type, &py_r))
        return NULL;

    if (pyPointCPoint(py_p, p) == FAIL || pyPointCPoint(py_q, q) == FAIL || pyPointCPoint(py_q, q) == FAIL)
        return (PyObject*)NULL;

    return Py_BuildValue("i", turn(p,q,r));
}

/*static const char* sort_around_point_doc =
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
    //void sort_around_point(long p[2], long pts[][2], int n);
	PyObject* py_pts;
	PyObject* py_p;
	PyObject* py_join = NULL;

	static const char *kwlist[] = {"p", "points", "join", NULL}; //TODO: This function doesn't really recieve "join". Unify the different sort_around_point functions that currently exist

	//The arguments must be: a list representing a point (a list of two or three integers)
	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!|O!:sort_around_point", (char**)kwlist, &PyList_Type, &py_p, &PyList_Type, &py_pts, &PyBool_Type, &py_join))
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

	delete c_pts;

	return res;
} //TODO: This function was moved to crossing for the moment since it relies on a global variable 'pivot'
*/
PyMethodDef geometricbasicsCppMethods[] =
{
    {"turn", (PyCFunction)turn_wrapper, METH_VARARGS | METH_KEYWORDS, turn_doc},
    //{"sort_around_point", (PyCFunction)sort_around_point_wrapper, METH_VARARGS | METH_KEYWORDS, sort_around_point_doc},
    {NULL, NULL, 0, NULL}
};

extern "C" PyMODINIT_FUNC
initgeometricbasicsCpp(void)
{
    (void) Py_InitModule3("geometricbasicsCpp", geometricbasicsCppMethods,
                          "Extension written in C++ with basic geometric functions.");
}
