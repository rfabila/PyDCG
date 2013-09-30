#ifndef HOLESCPP_H_
#define HOLESCPP_H_
#include "geometricbasicsCpp.h"
#include <vector>
#include <queue>



//-------------------------------------------------------------

void sort_around_point(punto, const std::vector<punto>&, std::vector<punto> &, std::vector<punto> &, bool);

std::vector<std::vector<std::pair<std::vector<int>, std::vector<int> > > > compute_visibility_graph(const std::vector<puntos_ordenados>&);

std::vector<std::pair<std::vector<int>, std::vector<int> > > visibility_graph_around_p(punto, const std::vector<punto>&, bool debug=false);

int slow_generalposition(std::vector<punto>&);

//-------------------------------------------------------------

bool pointInTriang(punto, triangulo);

bool pointsInTriang(const std::vector<punto>&, triangulo);

int slowcountemptyTriang(const std::vector<punto>&);

int countEmptyTriangsVertex(const std::vector<punto>&);

int countEmptyTriangs(const std::vector<punto>&);

int slow_count_empty_triangles_containing_p(punto p, const std::vector<punto>&);

int count_empty_triangles_around_p(punto, const std::vector<punto>&);

void slow_count_empty_triangles_p(punto, const std::vector<punto>&, int&, int&);

void count_empty_triangles_p(punto, const std::vector<punto>&, int&, int&);

int count_empty_triangles_for_each_p(std::vector<punto>);

//-------------------------------------------------------------

int count_convex_rholes(const std::vector<punto>&, int, bool=false);

std::deque<std::vector<punto> > report_convex_rholes(const std::vector<punto>&, int, bool=false);

void count_convex_rholes_p(punto, const std::vector<punto>&, int, int&, int&, bool=false);

#endif /* HOLES_H_ */
