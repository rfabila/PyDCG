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
#include <vector>
#include "geometricbasicsCpp.h"

#ifdef INT32
static const long long max_val = (1L << 30);
const char max_val_error[] = "The coordinates of each point must less than or equal to 2^30 in absolute value.";
#else
static const long long max_val = (1L << 62);
const char max_val_error[] = "The coordinates of each point must less than or equal to 2^62 in absolute value.";
#endif

using std::vector;

const int FAIL = 0;
const int SUCCESS = 1;

int pyPointCPoint(PyObject* py_p, punto& p)
{
    Py_ssize_t size_pt = PyList_Size(py_p);
    if(size_pt > 3 || size_pt < 2)
    {
        PyErr_SetString(PyExc_ValueError, "Wrong number of values representing a point, must be 2 or 3.");
        return FAIL;
    }
    if(size_pt == 3)
        p.color = (int)PyInt_AsLong(PyList_GetItem(py_p, 2)); //Borrowed References

    p.x = PyInt_AsLong(PyList_GetItem(py_p, 0)); //Borrowed References
    if(PyErr_Occurred() != NULL)
        return FAIL;

    p.y = PyInt_AsLong(PyList_GetItem(py_p, 1)); //Borrowed References
    if(PyErr_Occurred() != NULL)
        return FAIL;
    if(p.x > max_val || p.y > max_val || p.x < -max_val || p.y < -max_val)
    {
        PyErr_SetString(PyExc_OverflowError, max_val_error);
        return FAIL;
    }
    return SUCCESS;
}

int pyPointsetCPointset(PyObject* py_pts, vector<punto>& pts)
{
    Py_ssize_t points_size = PyList_Size(py_pts);
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
            return FAIL;
        }

        x = PyInt_AsLong(PyList_GetItem(punto, 0)); //Borrowed References
        if(PyErr_Occurred() != NULL)
            return FAIL;
        y = PyInt_AsLong(PyList_GetItem(punto, 1)); //Borrowed References
        if(PyErr_Occurred() != NULL)
            return FAIL;
        if(x > max_val || y > max_val || x < -max_val || y < -max_val)
        {
            PyErr_SetString(PyExc_OverflowError, max_val_error);
            return FAIL;
        }
        pts.emplace_back(x, y, color);
    }
    return SUCCESS;
}

PyObject* CPointPyPoint(punto point)
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

    return py_point;
}

PyObject* CPointsetPyPointset(vector<punto>& pts)
{
    PyObject* py_pts = PyList_New(0);
    for(auto point : pts)
    {
        PyObject* py_point = CPointPyPoint(point);

        if(PyList_Append(py_pts, py_point) == -1)
            return NULL;
        Py_DECREF(py_point);
    }
    return py_pts;
}
