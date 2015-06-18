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

//-------------------------------------------------------------

void sort_around_point(punto, const std::vector<punto>&, std::vector<punto> &, std::vector<punto> &, bool);

std::vector<std::vector<std::pair<std::vector<int>, std::vector<int> > > > compute_visibility_graph(const std::vector<puntos_ordenados>&);

std::vector<std::pair<std::vector<int>, std::vector<int> > > visibility_graph_around_p(punto, const std::vector<punto>&, bool debug=false);

int slow_generalposition(std::vector<punto>&);

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
    size_t operator()(const punto &k) const{
    	return (k.x << 16) ^ k.y;
    }
};

bool pointInTriang(punto, triangulo);

bool pointsInTriang(const std::vector<punto>&, triangulo);

int slowcountemptyTriang(const std::vector<punto>&);

int countEmptyTriangsVertex(const std::vector<punto>&);

int countEmptyTriangs(const std::vector<punto>&);

std::vector<std::vector<punto> > report_empty_triangles(const std::vector<punto>&);

int slow_count_empty_triangles_containing_p(punto p, const std::vector<punto>&);

int count_empty_triangles_around_p(punto, const std::vector<punto>&);

class triangHash{
public:
    size_t operator()(const triangulo &triang) const{
    	pointHash phash;
    	return (phash(triang.a) << 22) ^ (phash(triang.b) << 12 ^ phash(triang.c));
    }
};

std::pair<std::list<triangulo>, std::unordered_set<triangulo, triangHash> > report_empty_triangles_p(punto, const vector<punto>&);

void slow_count_empty_triangles_p(punto, const std::vector<punto>&, int&, int&);

void count_empty_triangles_p(punto, const std::vector<punto>&, int&, int&);

int count_empty_triangles_for_each_p(std::vector<punto>);

//-------------------------------------------------------------

int count_convex_rholes(const std::vector<punto>&, int, bool=false);

std::deque<std::vector<punto> > report_convex_rholes(const std::vector<punto>&, int, bool=false);

void count_convex_rholes_p(punto, const std::vector<punto>&, int, int&, int&, bool=false);

#endif /* HOLES_H_ */
