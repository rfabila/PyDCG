#ifndef GEOMETRICBASICSCPP_H_
#define GEOMETRICBASICSCPP_H_

#ifdef INT32
#define BIG_INT long
#else
#define BIG_INT __int128_t
#endif

#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

static const short LEFT = -1;
static const short RIGHT = 1;
static const short COLLINEAR = 0;

struct punto
{
	long long x, y;
	int color;
	punto();
	punto(long long, long long);
	punto(long long, long long, int);
	bool operator==(const punto&) const;
	bool operator!=(const punto&) const;
};

struct triangulo
{
	punto a, b, c;
	triangulo();
	triangulo(punto, punto, punto);
};

int turn(const punto&, const punto&, const punto&);

int turn(long p0[], long p1[], long p2[]);
int cmp_points(const void *qp, const void *rp);
void sort_around_point(long p[2], long pts[][2], int n);

void reverse_in_place(long pts[][2], int start, int end);
int concave(long p[2], long pts[][2], int n);
void shift(long pts[][2], int s, int n);
void print_pts(long pts[][2], int n);

#endif /* GEOMETRICBASICSCPP_H_ */
