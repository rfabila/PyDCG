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
#include "holesCPP.h"

static const char* count_convex_rholes_doc =
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

PyObject* count_convex_rholes_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    //The C++ function prototype is: int count_convex_rholes(const std::vector<Punto>&, int, bool=false);
    PyObject* py_pts;
    PyObject* py_mono = NULL;

    int r;
    bool mono = false;
    vector<Punto> pts;

    static const char *kwlist[] = {"points", "r", "mono", NULL};

    //The arguments must be: a list with the points (each point is a list of two integers),
    //an integer (r) and a boolean (mono). The boolean is optional.
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!i|O!:count_convex_rholes", (char**)kwlist, &PyList_Type, &py_pts, &r, &PyBool_Type, &py_mono))
        return (PyObject*)NULL;                                                     //This cast ^ is stupid. I just put to avoid the annoying warnings that appear if
                                                                         //kwlist isn't declared const
    if(py_mono == Py_True)
        mono = true;

    if(pyPointset_CPointset(py_pts, pts) == FAIL)
        return (PyObject*)NULL;

    return Py_BuildValue("i", count_convex_rholes(pts, r, mono));
}

static const char* report_convex_rholes_doc =
"report_convex_rholes(points, r, mono = True)\n\
    \n\
    Reports the r-holes in a point set.\n\
    \n\
    This function reports how many convex `r`-holes are in `points` (the \n\
    point set may be colored). It is an implementation of the algorithm \n\
    presented in \"Searching for Empty Convex Polygons\"\n\
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
        Determines wheter to look for monochromatic `r`-holes or not\n\
    \n\
    Returns\n\
    -------\n\
    H : int\n\
        A list containing the `r`-holes in `points`. Each `r`-hole is repre-\n\
        sented as a list of points, in counterclockwise order. Each point is\n\
        stored in the same way explained for the parameter `points`.\n\
    \n\
    Notes\n\
    -----\n\
    The coordinates of the points should be less than or equal to 2^30 to\n\
    prevent overflow on the C++ side.";

extern "C" PyObject* report_convex_rholes_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    //The C++ function prototype is:
    //std::deque<std::vector<Punto> > report_convex_rholes(const std::vector<Punto>&, int, bool=false);
    PyObject* py_pts;
    PyObject* py_mono = NULL;

    int r;
    bool mono = false;
    vector<Punto> pts;

    static const char *kwlist[] = {"points", "r", "mono", NULL};

    //The arguments must be: a list with the points (each point is a list of two integers),
    //an integer (r) and a boolean (mono). The boolean is optional.
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!i|O!:count_convex_rholes", (char**)kwlist, &PyList_Type, &py_pts, &r, &PyBool_Type, &py_mono))
        return (PyObject*)NULL;                                                            //See comment in count_convex_rholes_p_wrapper about this cast.

    if(py_mono == Py_True)
        mono = true;

    if(pyPointset_CPointset(py_pts, pts) == FAIL)
        return (PyObject*)NULL;

    auto res = report_convex_rholes(pts, r, mono);

    PyObject* py_res = PyList_New(0);

    for (auto poli : res)
    {
        PyObject* py_poli = CPointset_PyPointset(poli);
        if(py_poli == NULL)
            return (PyObject*)NULL;

        if(PyList_Append(py_res, py_poli) == -1) //Append increases reference count
            return (PyObject*)NULL;
        Py_DECREF(py_poli);
    }
    return py_res;
}

static const char* count_convex_rholes_p_doc =
"count_convex_rholes_p(p, points, r, mono = True)\n\
    \n\
    Counts the r-holes in a point set with certain point as vertex and the\n\
    r-gons with only that point inside them.\n\
    \n\
    This function counts how many convex `r`-holes in `points` have `p`\n\
    as a vertex and how many convex `r`-gons in `points` have only `p` \n\
    inside them. The point set may be colored. Point `p` must not\n\
    be contained in `points`.\n\
    \n\
    Parameters\n\
    ----------\n\
    p : list\n\
        A list with 3 integers, representing a point in the plane. The\n\
        first two are the coordinates of the point, the third one is the\n\
        color. The color is optional\n\
    points : list\n\
        This list represents the point set, each point is represented in the\n\
        same way as p.\n\
    r : int\n\
        The number of sides of the holes we want to fint in the point set.\n\
    mono : boolean\n\
        Determines wheter to look for monochromatic `r`-holes or not\n\
    \n\
    Returns\n\
    -------\n\
    (a, b) : tuple\n\
        `a` is the number of convex `r`-holes in `points` that have `p` as\n\
        a vertex and `b` the number of convex `r`-gons in `points` have only\n\
        `p` inside them.\n\
    \n\
    Notes\n\
    -----\n\
    The coordinates of the points should be less than or equal to 2^30 to\n\
    prevent overflow on the C++ side. The point `p` must not be included\n\
    in points.";

extern "C" PyObject* count_convex_rholes_p_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    //The C++ function prototype is:
    //void count_convex_rholes_p(Punto, const std::vector<Punto>&, int, int&, int&, bool=false);
    PyObject* py_pts;
    PyObject* py_p;
    PyObject* py_mono = NULL;

    int r;
    bool mono = false;
    Punto p;
    vector<Punto> pts;

    static const char *kwlist[] = {"p", "points", "r", "mono", NULL};

    //The arguments must be: a point (each point is a list of two or three integers),
    //a list with the points, an integer (r) and a boolean (mono). The boolean is optional.
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!i|O!:count_convex_rholes", (char**)kwlist, &PyList_Type, &py_p, &PyList_Type, &py_pts, &r, &PyBool_Type, &py_mono))
        return (PyObject*)NULL;                                                               //See comment in count_convex_rholes_p_wrapper about this cast.

    if(py_mono == Py_True)
        mono = true;

    if(pyPointset_CPointset(py_pts, pts) == FAIL)
        return (PyObject*)NULL;

    if(pyPoint_CPoint(py_p, p) == FAIL)
        return (PyObject*)NULL;

    int A, B;
    count_convex_rholes_p(p, pts, r, A, B, mono);

    return Py_BuildValue("ii", A, B);
}

extern "C" PyObject* countEmptyTriangs_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    PyObject* py_pts;

    vector<Punto> pts;

    static const char *kwlist[] = {"points", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!:countEmptyTriangs", (char**)kwlist, &PyList_Type, &py_pts))
        return NULL;

    if(pyPointset_CPointset(py_pts, pts) == FAIL)
        return (PyObject*)NULL;

    return Py_BuildValue("i", countEmptyTriangs(pts));
}

extern "C" PyObject* report_empty_triangles_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    //The C++ function prototype is:
    //std::vector<std::vector<Punto> > report_empty_triangles(const std::vector<Punto>&);
    PyObject* py_pts;

    vector<Punto> pts;

    static const char *kwlist[] = {"points", NULL};

    //The argument must be a list with the points (each point is a list of two integers)
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!:report_empty_triangles", (char**)kwlist, &PyList_Type, &py_pts))
        return NULL;                                                 //See comment in count_convex_rholes_p_wrapper about this cast.


    if(pyPointset_CPointset(py_pts, pts) == FAIL)
        return (PyObject*)NULL;

    auto res = report_empty_triangles(pts);

    PyObject* py_res = PyList_New(0);

    for (auto triang : res)
    {
        PyObject* py_poli = CPointset_PyPointset(triang);
        if(py_poli == NULL)
            return (PyObject*)NULL;

        if(PyList_Append(py_res, py_poli) == -1)
            return (PyObject*)NULL;
        Py_DECREF(py_poli);
    }

    return py_res;
}

extern "C" PyObject* count_empty_triangles_p_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    PyObject* py_pts;
    PyObject* py_p;

    vector<Punto> pts;
    Punto p;

    static const char *kwlist[] = {"p", "points", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!:count_convex_rholes", (char**)kwlist, &PyList_Type, &py_p, &PyList_Type, &py_pts))
        return (PyObject*)NULL;

    if (pyPoint_CPoint(py_p, p) == FAIL)
        return (PyObject*)NULL;

    if(pyPointset_CPointset(py_pts, pts) == FAIL)
        return (PyObject*)NULL;

    int A, B;
    count_empty_triangles_p(p, pts, A, B);

    return Py_BuildValue("ii", A, B);
}

extern "C" PyObject* report_empty_triangles_p_wrapper(PyObject* self, PyObject* args, PyObject *keywds) //TODO: Update this one
{
    //The C++ function prototype is:
    //pair<list<triangulo>, std::unordered_set<triangulo> > report_empty_triangles_p(Punto, const vector<Punto>&);
	PyObject* py_pts;
	PyObject* py_p;

	static const char *kwlist[] = {"p", "points", NULL};

	vector<Punto> pts;
	Punto p;

	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!:report_empty_triangles_p", (char**)kwlist, &PyList_Type, &py_p, &PyList_Type, &py_pts))
		return NULL;

    if(pyPointset_CPointset(py_pts, pts) == FAIL)
        return (PyObject*)NULL;

    if (pyPoint_CPoint(py_p, p) == FAIL)
        return (PyObject*)NULL;

    vector<vector<Punto> > A, B;

    report_empty_triangles_p(p, pts, A, B);

    PyObject* py_A = PyList_New(A.size());
    PyObject* py_B = PyList_New(B.size());

    int i = 0;

    for (auto triang : A)
    {
        PyObject* py_triang = CPointset_PyPointset(triang);
        if(py_triang == NULL)
            return (PyObject*)NULL;

        if(PyList_SetItem(py_A, i++, py_triang) == -1)
            return (PyObject*)NULL;
    }

    i = 0;

    for (auto triang : B)
    {
        PyObject* py_triang = CPointset_PyPointset(triang);
        if(py_triang == NULL)
            return (PyObject*)NULL;

        if(PyList_SetItem(py_B, i++, py_triang) == -1)
            return (PyObject*)NULL;
    }

	return Py_BuildValue("NN", py_A, py_B);
}

extern "C" PyObject* general_position_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    //The C++ function prototype is: general_position(vector<Punto>& points)
    PyObject* py_points;

    static const char *kwlist[] = {"points", NULL};

    vector<Punto> points;

    //The arguments must be: a list with the point (a list of two integers),
    //and a list of 3 points representing the triangle
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!:general_position", (char**)kwlist, &PyList_Type, &py_points))
        return NULL;

    if(pyPointset_CPointset(py_points, points) == FAIL)
        return (PyObject*)NULL;

    return Py_BuildValue("i", general_position(points));
}

PyMethodDef holesCppMethods[] =
{
    {"count_convex_rholes", (PyCFunction)count_convex_rholes_wrapper, METH_VARARGS | METH_KEYWORDS, count_convex_rholes_doc},
    {"report_convex_rholes", (PyCFunction)report_convex_rholes_wrapper, METH_VARARGS | METH_KEYWORDS, report_convex_rholes_doc},
    {"count_convex_rholes_p", (PyCFunction)count_convex_rholes_p_wrapper, METH_VARARGS | METH_KEYWORDS, count_convex_rholes_p_doc},
    {"countEmptyTriangs", (PyCFunction)countEmptyTriangs_wrapper, METH_VARARGS | METH_KEYWORDS,
        "Counts the number of empty triangles in points."},
    {"report_empty_triangles", (PyCFunction)report_empty_triangles_wrapper, METH_VARARGS | METH_KEYWORDS,
         "Report the number of empty triangles in points."},
    {"count_empty_triangles_p", (PyCFunction)count_empty_triangles_p_wrapper, METH_VARARGS | METH_KEYWORDS,
        "Returns (A_p, B_p), the number of empty triangles with p as a vertex and the number of triangles with only p inside. points must not contain p."},
	{"report_empty_triangles_p", (PyCFunction)report_empty_triangles_p_wrapper, METH_VARARGS | METH_KEYWORDS,
			 "Report the the empty triangles in points that have p as a vertex and the triangles in points that have only p inside them."},
    {"general_position", (PyCFunction)general_position_wrapper, METH_VARARGS | METH_KEYWORDS, "Verify if a point set is in general position"},
    {NULL, NULL, 0, NULL}
};

extern "C" PyMODINIT_FUNC
initholesCpp(void)
{
    (void) Py_InitModule3("holesCpp", holesCppMethods,
                          "Extension written in C++ intended to help finding sets with few r-holes.");
}
