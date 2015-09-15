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

#ifndef HOLESCPP_H_
#define HOLESCPP_H_
#include "geometricbasicsCpp.h"
#include <vector>
#include <queue>
#include <list>
#include <unordered_set>
#include <functional>

//-------------------------------------------------------------

void sort_around_point(Punto, const std::vector<Punto>&, std::vector<Punto> &, std::vector<Punto> &, bool);

std::vector<std::vector<std::pair<std::vector<int>, std::vector<int> > > > compute_visibility_graph(const std::vector<puntos_ordenados>&);

std::vector<std::pair<std::vector<int>, std::vector<int> > > visibility_graph_around_p(Punto, const std::vector<Punto>&, bool debug=false);

int slow_generalposition(std::vector<Punto>&);

//-------------------------------------------------------------
class pairHash{
public:
    size_t operator()(const std::pair<int, int> &k) const{
//    	if(k.first>=k.second)
//    		return k.second*k.second+k.first;
//    	return k.first*k.first+k.first+k.second;
//
//    	return ((k.first+k.second)*(k.first+k.second+1)+k.second)/2;

    	return (k.first << 16) ^ k.second;
    }
};

class pointHash{
public:
    size_t operator()(const Punto &k) const{
    	return (k.x << 16) ^ k.y;
    }
};

bool pointInTriang(Punto, triangulo);

bool pointsInTriang(const std::vector<Punto>&, triangulo);

int slowcountemptyTriang(const std::vector<Punto>&);

int countEmptyTriangsVertex(const std::vector<Punto>&);

int countEmptyTriangs(const std::vector<Punto>&);

std::vector<std::vector<Punto> > report_empty_triangles(const std::vector<Punto>&);

int slow_count_empty_triangles_containing_p(Punto p, const std::vector<Punto>&);

int count_empty_triangles_around_p(Punto, const std::vector<Punto>&);

class triangHash{
public:
    size_t operator()(const triangulo &triang) const{
    	pointHash phash;
    	return (phash(triang.a) << 22) ^ (phash(triang.b) << 12 ^ phash(triang.c));
    }
};

std::pair<std::list<triangulo>, std::unordered_set<triangulo, triangHash> > WHYreport_empty_triangles_p(Punto, const vector<Punto>&);
void report_empty_triangles_p(Punto, const vector<Punto>&, vector<vector<Punto> >&, vector<vector<Punto> >&);

void slow_count_empty_triangles_p(Punto, const std::vector<Punto>&, int&, int&);

void count_empty_triangles_p(Punto, const std::vector<Punto>&, int&, int&);

int count_empty_triangles_for_each_p(std::vector<Punto>);

//-------------------------------------------------------------

int count_convex_rholes(const std::vector<Punto>&, int, bool=false);

std::deque<std::vector<Punto> > report_convex_rholes(const std::vector<Punto>&, int, bool=false);

void count_convex_rholes_p(Punto, const std::vector<Punto>&, int, int&, int&, bool=false);

#endif /* HOLES_H_ */
