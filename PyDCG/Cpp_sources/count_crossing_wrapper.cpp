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

#include <Python.h>
#include "count_crossing.h"

using std::vector;

#ifdef INT32
static const long long max_val = (1L << 30);
const char max_val_error[] = "The coordinates of each point must less than or equal to 2^30 in absolute value.";
#else
static const long long max_val = (1L << 62);
const char max_val_error[] = "The coordinates of each point must less than or equal to 2^62 in absolute value.";
#endif

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
        return (PyObject*)NULL;

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
            return (PyObject*)NULL;
        }

        x = PyInt_AsLong(PyList_GetItem(point, 0)); //Borrowed References
        if(PyErr_Occurred() != NULL)
            return (PyObject*)NULL;
        y = PyInt_AsLong(PyList_GetItem(point, 1));
        if(PyErr_Occurred() != NULL)
            return (PyObject*)NULL;

        if(x > max_val || y > max_val || x < -max_val || y < -max_val)
        {
            PyErr_SetString(PyExc_OverflowError, max_val_error);
            return (PyObject*)NULL;
        }

        pts[i][0] = x;
        pts[i][1] = y;
    }
    int res = crossing(pts, points_size);
    delete[] pts;
    return Py_BuildValue("i", res);
}
//TODO: Añadir docstring de count_crossings_candidate_list
//TODO: Añadir una función para pasar listas d epython a vectores/arreglos de C++
extern "C" PyObject* count_crossings_candidate_list_wrapper(PyObject* self, PyObject* args)
{
    //The C++ function prototype is: vector<int> count_crossings_candidate_list(int point_index, vector<punto> &candidate_list, vector<punto> &puntos)
    PyObject* py_candidate_list = NULL;
    PyObject* py_points = NULL;

    int index;

    //The arguments must be: an integer and two lists with points (each point is a list of two integers)
    if (!PyArg_ParseTuple(args, "iO!O!:count_crossings_candidate_list", &index, &PyList_Type, &py_candidate_list, &PyList_Type, &py_points))
        return (PyObject*)NULL;

    Py_ssize_t points_size = PyList_Size(py_points);
    Py_ssize_t candidates_size = PyList_Size(py_candidate_list);

    vector<Punto> pts;
    vector<Punto> candidates;
    //Py_ssize_t can be bigger than an 2^32, but we don't expect
    //to work with that many points.
    pts.reserve(int(points_size));
    candidates.reserve(int(candidates_size));

    for(Py_ssize_t i=0; i < points_size; i++)
    {
        PyObject *punto = PyList_GetItem(py_points, i); //Borrowed Reference
        Py_ssize_t n_coords = PyList_Size(punto);
        long long x, y;

        if(n_coords > 3 || n_coords < 2)
        {
            PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
            return (PyObject*)NULL;
        }

        x = PyInt_AsLong(PyList_GetItem(punto, 0)); //Borrowed References
        if(PyErr_Occurred() != NULL)
            return (PyObject*)NULL;
        y = PyInt_AsLong(PyList_GetItem(punto, 1));
        if(PyErr_Occurred() != NULL)
            return (PyObject*)NULL;

        if(x > max_val || y > max_val || x < -max_val || y < -max_val)
        {
            PyErr_SetString(PyExc_OverflowError, max_val_error);
            return (PyObject*)NULL;
        }


        pts.emplace_back(x, y);
    }

    for(Py_ssize_t i=0; i < candidates_size; i++)
    {
        PyObject *punto = PyList_GetItem(py_candidate_list, i); //Borrowed Reference
        Py_ssize_t n_coords = PyList_Size(punto);
        long long x, y;

        if(n_coords > 3 || n_coords < 2)
        {
            PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
            return (PyObject*)NULL;
        }

        x = PyInt_AsLong(PyList_GetItem(punto, 0)); //Borrowed References
        if(PyErr_Occurred() != NULL)
            return (PyObject*)NULL;
        y = PyInt_AsLong(PyList_GetItem(punto, 1));
        if(PyErr_Occurred() != NULL)
            return (PyObject*)NULL;

        if(x > max_val || y > max_val || x < -max_val || y < -max_val)
        {
            PyErr_SetString(PyExc_OverflowError, max_val_error);
            return (PyObject*)NULL;
        }

        candidates.emplace_back(x, y);
    }

    vector<int> res = count_crossings_candidate_list(index, candidates, pts);

    PyObject* py_res = PyList_New(0);

    for(auto &crossings : res)
    {
        PyObject* py_crossings = PyInt_FromLong(crossings);
        if(PyList_Append(py_res, py_crossings) == -1) //Append increases reference count
            return (PyObject*)NULL;
        Py_DECREF(py_crossings);
    }

    return py_res;
}

extern "C" PyMethodDef crossingCppMethods[] =
{
    {"crossing", crossing_wrapper, METH_VARARGS, crossing_doc},
    {"count_crossings_candidate_list", count_crossings_candidate_list_wrapper, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initcrossingCpp(void)
{
    (void) Py_InitModule3("crossingCpp", crossingCppMethods,
                          "Extension written in C++ intended to help finding sets with few r-holes.");
}
