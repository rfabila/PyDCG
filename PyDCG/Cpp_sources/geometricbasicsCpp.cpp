#include "geometricbasicsCpp.h"
//long pivote[2];

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

int turn(const Punto& p0, const Punto& p1, const Punto& p2)
{
	//Function to check whether the segments p0p1 and p1p2 make
	//a LEFT or RIGHT turn at p1 or are COLLINEAR
	BIG_INT p0x, p1x, p2x, p0y, p1y, p2y;
	p0x = BIG_INT(p0.x);
	p1x = BIG_INT(p1.x);
	p2x = BIG_INT(p2.x);
	p0y = BIG_INT(p0.y);
	p1y = BIG_INT(p1.y);
	p2y = BIG_INT(p2.y);
	BIG_INT t=((p2x-p0x)*(p1y-p0y))-((p1x-p0x)*(p2y-p0y));
	if(t>0)
		return RIGHT;
	else if(t<0)
		return LEFT;
	return COLLINEAR;
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

int turn(long p0[], long p1[], long p2[])
{
    //printf("([%ld,%ld],[%ld,%ld],[%ld,%ld])",p0[0],p0[1],p1[0],p1[1],p2[0],p2[1]);
    BIG_INT p00 = (BIG_INT) p0[0], p01 = (BIG_INT) p0[1], p10 = (BIG_INT) p1[0],
                                         p11 = (BIG_INT) p1[1], p20 = (BIG_INT) p2[0], p21 = (BIG_INT) p2[1];
    BIG_INT tempres;
    tempres = ((p20 - p00) * (p11 - p01)) - ((p10 - p00) * (p21 - p01));
    //tempres=((p2[0]-p0[0])*(p1[1]-p0[1]))-((p1[0]-p0[0])*(p2[1]-p0[1]));
    //printf("tempres=%" PRId64 "\n",tempres);
    if (tempres > 0)
        return 1;
    if (tempres < 0)
        return -1;
    return 0;
}



void reverse_in_place(long pts[][2], int start, int end)
{
    int m = (end + 1 - start) / 2;
    int i;
    long tmp[2];
    for (i = 0; i < m; i++)
    {
        tmp[0] = pts[start + i][0];
        tmp[1] = pts[start + i][1];
        pts[start + i][0] = pts[end - i][0];
        pts[start + i][1] = pts[end - i][1];
        pts[end - i][0] = tmp[0];
        pts[end - i][1] = tmp[1];
    }
}

int concave(long p[2], long pts[][2], int n)
{
    int i;
    for (i = 0; i < n; i++)
        if (turn(pts[i], p, pts[(i + 1) % n]) < 0)
            return i;
    return -1;
}

void shift(long pts[][2], int s, int n)
{
    if (s > 0)
    {
        reverse_in_place(pts, 0, s - 1);
        reverse_in_place(pts, s, n - 1);
        reverse_in_place(pts, 0, n - 1);
    }
}

void print_pts(long pts[][2], int n)
{
    int i;
    for (i = 0; i < n; i++)
    {
        printf("[%ld,%ld]\n", pts[i][0], pts[i][1]);
    }
}
