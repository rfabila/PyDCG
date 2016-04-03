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

//Definiciones de la clase Punto

Punto::Punto() : x(0), y(0), color(0), _has_color(false)
{}

Punto::Punto(long long x, long long y) : x(x), y(y), color(0), _has_color(false)
{}

Punto::Punto(long long x, long long y, int c) : x(x), y(y), color(c), _has_color(true)
{}

bool Punto::operator==(const Punto& q) const
{
	return (x==q.x && y == q.y);
}

bool Punto::operator!=(const Punto& q) const
{
	return !(*this==q);
}

bool Punto::operator<(const Punto& rhs) const
{
	if(this->x == rhs.x)
		return this->y < rhs.y;
	else
		return this->x < rhs.x;
}

bool Punto::operator>(const Punto& rhs) const
{
	return rhs < *this;
}

//-------------------------------------------------------------

//Definiciones de la clase triángulo

triangulo::triangulo() : a(0,0), b(1,0), c(0,1)
{}

triangulo::triangulo(Punto va, Punto vb, Punto vc) : a(va), b(vb), c(vc)
{}

bool triangulo::operator==(const triangulo& q) const
{
	return (a==q.a && b == q.b && c == q.c);
}

bool triangulo::operator!=(const triangulo& q) const
{
	return !(*this == q);
}

//-------------------------------------------------------------

//Definiciones para puntos_ordenados
puntos_ordenados::puntos_ordenados() : p(), r(), l() { }

puntos_ordenados::puntos_ordenados(Punto p, vector<Punto> r, vector<Punto> l) : p(p), r(r), l(l)
{}

//-------------------------------------------------------------

int turn(const long long p[2], const long long q[2], const long long r[2])
{
    BIG_INT px, py, qx, qy, rx, ry, t;

	px = BIG_INT(p[0]);
	qx = BIG_INT(q[0]);
	rx = BIG_INT(r[0]);
	py = BIG_INT(p[1]);
	qy = BIG_INT(q[1]);
	ry = BIG_INT(r[1]);

	t = ((rx - px) * (qy - py)) - ((qx - px) * (ry - py));

    if(t>0)
		return RIGHT;
	else if(t<0)
		return LEFT;
	return COLLINEAR;
}

int turn(const Punto& p, const Punto& q, const Punto& r)
{
	//Function to check whether the segments p0p1 and p1p2 make
	//a LEFT or RIGHT turn at p1 or are COLLINEAR
	long long ap[2] = {p.x, p.y}, aq[2] = {q.x, q.y}, ar[2] = {r.x, r.y};
	return turn(ap, aq, ar);
}

bool eqPoints(const long long p[2], const long long q[2])
{
    return p[0] == q[0] and p[1] == q[1];
}

void sort_around_point2(long long const *p, long long** const pts, int n)
{
	/*
	 * Sorts a set of points by angle around a point p.
	 * If join == false, returns a vector with the points at the right of p
	 * and a vector with the points at the left of p. Otherwise it returns
	 * just one vector.
	 */

	long long p1[2] = {p[0], p[1] + 1};
	long long** res;
	res = new long long*[n];
	for(int i=0; i<n; i++)
        res[i] = new long long[2];
    int nr=0, nl=n-1, nsame=0;

	for (int i=0; i<n; i++)
	{
	    if(eqPoints(pts[i], p))
            nsame++;
		else if (turn(p, p1, pts[i]) == RIGHT)
        {
            res[nr][0] = pts[i][0];
            res[nr++][1] = pts[i][1];
        }
        else if (turn(p, p1, pts[i]) == LEFT)
        {
            res[nl][0] = pts[i][0];
            res[nl--][1] = pts[i][1];
        }
		else if (p[1] >= pts[i][1])
        {
            res[nl][0] = pts[i][0];
            res[nl--][1] = pts[i][1];
        }
		else
        {
            res[nr][0] = pts[i][0];
            res[nr++][1] = pts[i][1];
        }
	}
    nl++;

	std::stable_sort(res+nl, res+n, [&p](long long r[2], long long q[2])->bool
			{
				if(turn(p, r, q) < 0)
					return true;
				return false;
			}
	);

	std::stable_sort(res, res+nr, [&p](long long r[2], long long q[2])->bool
			{
				if(turn(p, r, q) < 0)
					return true;
				return false;
			}
	);

	int i=0, j=0;
	while(i < nsame)
	{
	    pts[i][0] = p[0];
	    pts[i++][1] = p[1];
	}

	while(j < nr)
    {
        pts[i][0] = res[j][0];
	    pts[i++][1] = res[j++][1];
    }
    j=nl;

    while(j < n)
    {
        pts[i][0] = res[j][0];
	    pts[i++][1] = res[j++][1];
    }

    int start = -1;
    for(int i=0; i<n-1; i++)
    {
        if(turn(pts[i], p, pts[i+1]) < 0)
        {
            start = i;
            break;
        }
    }

    if(start > -1)
    {
        std::reverse(pts+nsame, pts+start+1);
        std::reverse(pts+start+1, pts+n);
        std::reverse(pts+nsame, pts+n);
    }
    for(int i=0; i<n; i++)
        delete[] res[i];
    delete[] res;
    return;
}

void sort_around_point(long long const *op, long long** const pts, int n)
{
    struct cmp
    {
        long long p[2];
        cmp(const long long parg[2])
        {
            p[0] = parg[0];
            p[1] = parg[1];
        }
        bool operator () (const long long q[2], const long long r[2])
        {
            if(eqPoints(p, q) and !eqPoints(p, r))
                return true;
            long long qxcoord = q[0]-p[0], rxcoord = r[0]-p[0];

            //One point to the left and one to the right of p, the one to the right goes first
            if((qxcoord > 0 and rxcoord < 0) or (qxcoord < 0 and rxcoord > 0))
                return q[0] > p[0] ? true : false;
            //At least one point with same x-coordinate than p
            else if(qxcoord == 0 or rxcoord == 0)
            {
                //Exactly one point with same x-coordinate than p, and that point is below p. The one below p goes last
                if(q[0] != r[0])
                {
                    if(q[0] == p[0] and q[1] < p[1])
                        return false;
                    if(r[0] == p[0] and r[1] < p[1])
                        return true;
                }
                else
                {
                    long long qycoord = q[1]-p[1], rycoord = r[1]-p[1];
                    //Two with same x-coordinate than p, one above and one below. The one below p goes last
                    if((qycoord > 0 and rycoord < 0) or (qycoord < 0 and rycoord > 0))
                        return q[1] < p[1] ? false : true;
                }
            }
        int t = turn(p, q, r);
        return t < 0 ? true : false;
        }
    };

    std::stable_sort(pts, pts+n, cmp(op));

    int start = -1;
    for(int i=0; i<n-1; i++)
    {
        if(turn(pts[i], op, pts[i+1]) < 0)
        {
            start = i;
            break;
        }
    }

    if(start > -1)
    {
        int difs = 0;

        while(eqPoints(pts[difs], op))
            difs++;

        std::reverse(pts+difs, pts+start+1);
        std::reverse(pts+start+1, pts+n);
        std::reverse(pts+difs, pts+n);
    }
    return;
}

void orderandsplit(const vector<Punto>& points, vector<puntos_ordenados> &orderedpoints)
{
	/*
	 * For each p in points, sorts the remaining elements
	 * that lie to the left and right of p, respectively, ccw.
	 * The result is stored in orderedpoints.
	 */
	vector<Punto> l, r;
	r.reserve(points.size());
	l.reserve(points.size());
	for(auto &p : points)
	{
		Punto p1(p.x, p.y+1);

		for(auto &q : points)
			if(q!=p)
			{
				if(turn(p, p1, q) == RIGHT)
					r.push_back(q);
				else if(turn(p, p1, q) == LEFT)
					l.push_back(q);
				else if(p.y >= q.y)
					l.push_back(q);
				else
					r.push_back(q);
			}

		sort(l.begin(), l.end(), [&p](Punto r, Punto q)->bool{
			if(turn(p, r, q)<0)
				return true;
			return false;
		});

		sort(r.begin(), r.end(), [&p](Punto r, Punto q)->bool{
			if(turn(p, r, q)<0)
				return true;
			return false;
		});

		orderedpoints.emplace_back(p,r,l);

		r.clear();
		l.clear();
	}
}

int slow_generalposition(vector<Punto>& pts)
{
	/*
	 * Verifies if the points are in general position. Returns
	 * the number of collinear subsets of 3 points.
	 */
	int col=0;

	for(unsigned int i=0, s=pts.size(); i<s; i++)
		for(unsigned int j=i+1; j<s; j++)
			for(unsigned k=j+1; k<s; k++)
				if(turn(pts[i], pts[j], pts[k]) == COLLINEAR)
				{
					printf("(%lld, %lld), (%lld, %lld), (%lld, %lld)\n",
							pts[i].x, pts[i].y,
							pts[j].x, pts[j].y,
							pts[k].x, pts[k].y);
					col++;
				}

	return col;
}

int general_position(vector<Punto>& points)
{
	vector<puntos_ordenados> ord_points;
	orderandsplit(points, ord_points);
	int col=0;

	for(auto& p : ord_points)
	{
		Punto point(p.p);
		auto rpoints=p.r;

		for(unsigned int i=0, s=rpoints.size(); s>0 && i<s-1; i++)
		{
			vector<Punto> temp = {point, rpoints[i], rpoints[i+1]};
			col+=slow_generalposition(temp);
		}
	}
	return col;
}

void print_pts(long pts[][2], int n)
{
    int i;
    for (i = 0; i < n; i++)
        printf("[%ld,%ld]\n", pts[i][0], pts[i][1]);
}
