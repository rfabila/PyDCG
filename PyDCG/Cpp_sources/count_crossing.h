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

#include "geometricbasicsCpp.h"
#include <stdio.h>
#include <stdlib.h>

long range_crossing(long pts[][2], int n, int range_begin, int range_end);
long crossing(long pts[][2], int n);
void imprime_piv_pts(long pi[], long pts[][2], int n);
void imprimepts(long pts[][2], int n);
int signo(long num);

vector<int> count_crossings_candidate_list(int, vector<Punto>&, vector<Punto>&);
