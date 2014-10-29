#include <Python.h>
#include <vector>
#include "geometricbasicsCpp.h"

#ifdef INT32
static const long long max_val = (1L << 30);
const char max_val_error[] = "The coordinates of each point must less than or equal to 2^30 in absolute value.";
#else
static const long long max_val = (1L << 62);
const char max_val_error[] = "The coordinates of each point must less than or equal to 2^62 in absolute value.";
#endif

void pyPointCPoint(PyObject* py_p, punto& p)
{
    Py_ssize_t size_pt = PyList_Size(py_p);
    if(size_pt > 3 || size_pt < 2)
    {
        PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
        return NULL;
    }
    if(size_pt == 3)
        p.color = (int)PyInt_AsLong(PyList_GetItem(py_p, 2)); //Borrowed References

    p.x = PyInt_AsLong(PyList_GetItem(py_p, 0)); //Borrowed References
    p.y = PyInt_AsLong(PyList_GetItem(py_p, 1)); //Borrowed References

}

void pyPointsetCPointset(PyObject* py_pts, vector<punto>& pts)
{
    Py_ssize_t size_pt = PyList_Size(py_p);
    if(size_pt > 3 || size_pt < 2)
    {
        PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
        return NULL;
    }
    if(size_pt == 3)
        p.color = (int)PyInt_AsLong(PyList_GetItem(py_p, 2)); //Borrowed References

    p.x = PyInt_AsLong(PyList_GetItem(py_p, 0)); //Borrowed References
    p.y = PyInt_AsLong(PyList_GetItem(py_p, 1)); //Borrowed References

}

extern "C" PyObject* count_convex_rholes_p_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    //The C++ function prototype is:
    //void count_convex_rholes_p(punto, const std::vector<punto>&, int, int&, int&, bool=false);
    PyObject* py_pts;
    PyObject* py_p;
    PyObject* py_mono = NULL;

    int r;
    int mono = 0;
    punto p;

    static const char *kwlist[] = {"p", "points", "r", "mono", NULL};

    //The arguments must be: a point (each point is a list of two or three integers),
    //a list with the points, an integer (r) and a boolean (mono). The boolean is optional.
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!i|O!:count_convex_rholes", (char**)kwlist, &PyList_Type, &py_p, &PyList_Type, &py_pts, &r, &PyBool_Type, &py_mono))
        return NULL;                                                               //See comment in count_convex_rholes_p_wrapper about this cast.

    if(py_mono != NULL && py_mono == Py_True)
        mono = 1;

    Py_ssize_t points_size = PyList_Size(py_pts);

    vector<punto> pts;

    //Py_ssize_t can be bigger than an 2^32, but we don't expect
    //to work with that many points.
    pts.reserve(int(points_size));

    for(Py_ssize_t i=0; i < points_size; i++)
    {
        PyObject *punto = PyList_GetItem(py_pts, i); //Borrowed Reference
        Py_ssize_t n_coords = PyList_Size(punto);
        long long x, y;
        int color = 0;

        if(n_coords == 3)
            color = (int)PyInt_AsLong(PyList_GetItem(punto, 2)); //Borrowed Reference
        else if(n_coords > 3 || n_coords < 2)
        {
            PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
            return NULL;
        }

        x = PyInt_AsLong(PyList_GetItem(punto, 0)); //Borrowed References
        y = PyInt_AsLong(PyList_GetItem(punto, 1)); //Borrowed References

        if(x > max_val || y > max_val || x < -max_val || y < -max_val)
        {
            PyErr_SetString(PyExc_ValueError, max_val_error);
            return NULL;
        }

        pts.emplace_back(x, y, color);
    }

    //Constructing the point p

    Py_ssize_t size_pt = PyList_Size(py_p);
    if(size_pt > 3 || size_pt < 2)
    {
        PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
        return NULL;
    }
    if(size_pt == 3)
        p.color = (int)PyInt_AsLong(PyList_GetItem(py_p, 2)); //Borrowed References

    p.x = PyInt_AsLong(PyList_GetItem(py_p, 0)); //Borrowed References
    p.y = PyInt_AsLong(PyList_GetItem(py_p, 1)); //Borrowed References

    int A, B;
    count_convex_rholes_p(p, pts, r, A, B, mono);

    return Py_BuildValue("ii", A, B);
}

PyObject* report_convex_rholes_wrapper(PyObject* self, PyObject* args, PyObject *keywds)
{
    //The C++ function prototype is:
    //std::deque<std::vector<punto> > report_convex_rholes(const std::vector<punto>&, int, bool=false);
    PyObject* py_pts;
    PyObject* py_mono = NULL;

    int r;
    int mono = 0;

    static const char *kwlist[] = {"points", "r", "mono", NULL};

    //The arguments must be: a list with the points (each point is a list of two integers),
    //an integer (r) and a boolean (mono). The boolean is optional.
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!i|O!:count_convex_rholes", (char**)kwlist, &PyList_Type, &py_pts, &r, &PyBool_Type, &py_mono))
        return NULL;                                                            //See comment in count_convex_rholes_p_wrapper about this cast.

    if(py_mono != NULL && py_mono == Py_True)
        mono = 1;

    Py_ssize_t points_size = PyList_Size(py_pts);

    vector<punto> pts;
    //Py_ssize_t can be bigger than an 2^32, but we don't expect
    //to work with that many points.
    pts.reserve(int(points_size));

    for(Py_ssize_t i=0; i < points_size; i++)
    {
        PyObject *punto = PyList_GetItem(py_pts, i); //Borrowed Reference
        Py_ssize_t n_coords = PyList_Size(punto);
        long long x, y;
        int color = 0;

        if(n_coords == 3)
            color = (int)PyInt_AsLong(PyList_GetItem(punto, 2)); //Borrowed Reference
        else if(n_coords > 3 || n_coords < 2)
        {
            PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
            return NULL;
        }

        x = PyInt_AsLong(PyList_GetItem(punto, 0)); //Borrowed References
        y = PyInt_AsLong(PyList_GetItem(punto, 1));

        if(x > max_val || y > max_val || x < -max_val || y < -max_val)
        {
            PyErr_SetString(PyExc_ValueError, max_val_error);
            return NULL;
        }

        pts.emplace_back(x, y, color);
    }
    auto res = report_convex_rholes(pts, r, mono);

    PyObject* py_res = PyList_New(0);

    for (auto poli : res)
    {
        PyObject* py_poli = PyList_New(0);
        for(auto point : poli)
        {
            PyObject* py_point = PyList_New(0);

            PyObject* coord = PyInt_FromLong(point.x);
            if(PyList_Append(py_point, coord) == -1) //Append increases reference count
                return NULL;
            Py_DECREF(coord);

            coord = PyInt_FromLong(point.y);
            if(PyList_Append(py_point, coord) == -1) //Append increases reference count
                return NULL;
            Py_DECREF(coord);

            coord = PyInt_FromLong(point.color);
            if(PyList_Append(py_point, coord) == -1) //Append increases reference count
                return NULL;
            Py_DECREF(coord);

            if(PyList_Append(py_poli, py_point) == -1)
                return NULL;
            Py_DECREF(py_point);
        }
        if(PyList_Append(py_res, py_poli) == -1)
            return NULL;
        Py_DECREF(py_poli);
    }

    return py_res;
}
