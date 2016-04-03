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

#ifndef GEOMETRICBASICSCPP_H_
#define GEOMETRICBASICSCPP_H_

#ifdef INT32
#define BIG_INT int64_t
#else
#define BIG_INT __int128_t
#endif

#include <cstdio>
#include <cstdlib>
#include <inttypes.h>
#include <vector>
#include <algorithm>

using std::vector;

static const short LEFT = -1;
static const short RIGHT = 1;
static const short COLLINEAR = 0;

struct Punto
{
	long long x, y;
	int color;
	bool _has_color;
	Punto();
	Punto(long long, long long);
	Punto(long long, long long, int);
	bool operator==(const Punto&) const;
	bool operator!=(const Punto&) const;
	bool operator<(const Punto& rhs) const;
	bool operator>(const Punto& rhs) const;
};

struct triangulo
{
	Punto a, b, c;
	triangulo();
	triangulo(Punto, Punto, Punto);
	bool operator==(const triangulo&) const;
	bool operator!=(const triangulo&) const;
};

struct puntos_ordenados
{
	Punto p;
	std::vector<Punto> r;
	std::vector<Punto> l;
	puntos_ordenados();
	puntos_ordenados(Punto, std::vector<Punto>, std::vector<Punto>);
};

int turn(const long long p0[], const long long p1[], const long long p2[]);
int turn(const Punto&, const Punto&, const Punto&);
void orderandsplit(const std::vector<Punto>&, std::vector<puntos_ordenados>&);
int general_position(std::vector<Punto>&);

void sort_around_point(long long const*, long long** const, int);
//void sort_around_point2(long long const*, long long** const, int);

#endif /* GEOMETRICBASICSCPP_H_ */
