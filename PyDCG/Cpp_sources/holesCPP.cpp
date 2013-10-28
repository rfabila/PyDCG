#include "holesCPP.h"
#include <cmath>
#include <algorithm>
#include <utility>
#include <deque>
#include <unordered_map>
#include <iostream>

using std::vector;
using std::pair;
using std::make_pair;
using std::list;

//-------------------------------------------------------------

static vector<punto> _default;

void sort_around_point(punto p, const vector<punto>& points, vector<punto>& r,
                       vector<punto>& l = _default, bool join = true)
{
	/*
	 * Sorts a set of points by angle around a point p.
	 * If join == false, returns a vector with the points at the right of p
	 * and a vector with the points at the left of p. Otherwise it returns
	 * just one vector.
	 */

	punto p1(p.x, p.y + 1);
	r.reserve(points.size());
	l.reserve(points.size());

	for (auto &q : points)
	{
		if (turn(p, p1, q) == RIGHT)
			r.push_back(q);
		else if (turn(p, p1, q) == LEFT)
			l.push_back(q);
		else if (p.y >= q.y)
			l.push_back(q);
		else
			r.push_back(q);
	}

	sort(l.begin(), l.end(), [&p](punto r, punto q)->bool
			{
				if(turn(p, r, q) < 0)
					return true;
				return false;
			}
	);

	sort(r.begin(), r.end(), [&p](punto r, punto q)->bool
			{
				if(turn(p, r, q) < 0)
					return true;
				return false;
			}
	);

	if (join)
	{
		r.insert(r.end(), l.begin(), l.end());
		bool concave = false;
		unsigned int i = 0;

		for (i = 0; i < r.size(); i++)
			if (turn(r[i], p, r[(i + 1) % r.size()]) < 0)
			{
				concave = true;
				break;
			}

		if (concave)
		{
			int start = (i + 1) % r.size();
			vector<punto> tmp(r);

			for (i = 0; i < tmp.size(); i++)
				r[i] = tmp[(start + i) % r.size()];
		}
	}
	_default.clear();
}

vector<vector<pair<vector<int>, vector<int> > > > compute_visibility_graph(const vector<puntos_ordenados>& sorted_points)
{
	/* Computes the visibility of every
	 * point as described in "Searching for empty convex polygons"
	 * The points must be already sorted.
     * sorted_points=orderandsplit(points)
     * sorts the points by angle around each point.
	 */

	//G contains the visibility graphs associated to each point
	vector<vector<pair<vector<int>, vector<int> > > > G;
	vector<pair<vector<int>, vector<int> > > vis_graph;
	vector<punto> right_points;
	vector<std::deque<int> > Q;

	std::function<void(int,int)> proceed=[&](int i, int j){
		while(Q[i].size()>0 && turn(right_points[Q[i][0]], right_points[i], right_points[j]) == LEFT)
				{
					proceed(Q[i][0], j);
					Q[i].pop_front();
				}
				Q[j].push_back(i);
				//We add ij to the graph
				vis_graph[j].first.push_back(i);
				vis_graph[i].second.push_back(j);
	};

	for(unsigned int i=0, s=sorted_points.size(); i<s; i++)
	{
		right_points=sorted_points[i].r;
		vis_graph = vector<pair<vector<int>, vector<int> > >(right_points.size());
		Q=vector<std::deque<int> >(right_points.size());
		for(unsigned int j=0, r=right_points.size(); r>0 && j<r-1; j++)
		{
			proceed(j, j+1);
		}
		G.emplace_back(std::move(vis_graph));
	}
	return G;
}

vector<pair<vector<int>, vector<int> > > visibility_graph_around_p(punto p, const vector<punto>& points, bool debug) {
	/* Computes the visibility graph of the point set
	 * polygon formed by the points ordered around p
	 * in ccw order. Each edge is oriented so p is at
	 * the left.
	 * The point set must not include p.
	 */
	vector<punto> sorted_points, l;

	sort_around_point(p, points, sorted_points, l, false);

	int limit = (int) sorted_points.size();

	sorted_points.insert(sorted_points.end(), l.begin(), l.end());


	vector<pair<vector<int>, vector<int> > > vis_graph(sorted_points.size());
	std::deque<vector<int> > Q(sorted_points.size());

	std::function<void(int,int,bool)> proceed=[&](int i, int j, bool first_pass){
		int k=0;
		while(k<(int)Q[i].size() && turn(sorted_points[Q[i][k]], sorted_points[i], sorted_points[j])<=0)
		{
			if(turn(p, sorted_points[Q[i][k]], sorted_points[j])<=0)
			{
				proceed(Q[i][k], j, first_pass);
				Q[i].erase(Q[i].begin()+k);
			}
			else
				k++;
		}
		Q[j].push_back(i);
		//We add ij to the graph
		if(!first_pass)
		{
			vis_graph[j].first.push_back(i);
			vis_graph[i].second.push_back(j);
		}
	};

	//We check whether p is a convex_hull point
	for (int i = 0, s = (int)sorted_points.size(); i < s; i++)
		if (turn(p, sorted_points[i], sorted_points[(i + 1) % s]) >= 0) {
			vector<punto> new_sorted_points(sorted_points.size());
			for (int j = 0; j < s; j++)
				new_sorted_points[j] = sorted_points[(i + 1 + j)% s];
			sorted_points = new_sorted_points;
			for (int j = 0; j < s - 1; j++)
				proceed(j, j + 1, false);
			return vis_graph;
		}

	for (int j = 0; j < limit - 1; j++)
		proceed(j, j + 1, true);

	proceed(limit - 1, limit, false);

	for (int j = limit; j < (int) sorted_points.size() - 1; j++)
		proceed(j, j + 1, false);

	vector<vector<int> > vis_graph_temp;
	for (int i = 0; i < limit; i++)
		vis_graph_temp.push_back(std::move(vis_graph[i].second));

	for (int i = 0; i < limit; i++) {
		vis_graph[i].second = vector<int>();
		Q[i]=vector<int>();
	}

	proceed(sorted_points.size() - 1, 0, false);

	for (int j = 0; j < limit - 1; j++)
		proceed(j, j + 1, false);

	for (int i = 0; i < limit; i++)
		vis_graph[i].second.insert(vis_graph[i].second.end(), vis_graph_temp[i].begin(),	vis_graph_temp[i].end());

	return vis_graph;
}

/*
 * Triángulos
 */

bool pointInTriang(punto p, triangulo triang)
{
	//Funci�n para decidir si un punto p est� en el interior de un tri�ngulo
	int sign1 = turn(triang.a, p, triang.b);
	int sign2 = turn(triang.b, p, triang.c);
	int sign3 = turn(triang.c, p, triang.a);

	//P est� en la frontera
	if(!(sign1 && sign2 && sign3))
		return false;
	else if(sign1>0)
		return (sign2 > 0 && sign3 > 0);
	else
		return (sign2 < 0 && sign3 < 0);
}

bool pointsInTriang(const vector<punto>& points, triangulo triang)
{
	//verifica si algun punto del arreglo esta contenido en el triangulo
	for(auto it=points.begin(); it!=points.end(); it++)
		if(pointInTriang(*it, triang))
			return true;
	return false;
}

int slowcountemptyTriang(const vector<punto>& points)
{
	//cuenta el numero de triangulos vacios en points (tiempo O(n^4))
	int num=0;
	for(unsigned int i=0; i<points.size(); i++)
		for(unsigned int j=i+1; j<points.size(); j++)
			for(unsigned int k=j+1; k<points.size(); k++)
				if (!pointsInTriang(points, triangulo(points[i], points[j], points[k])))
					num++;
	return num;
}

int countEmptyTriangsVertex(const vector<punto>& rpoints) {
	int triangs = 0;
	vector<std::queue<int> > q(rpoints.size(), std::queue<int>());

	std::function<int(int, int)> proceed=[&](int i, int j)->int{
		int tmp=0;
			while(q[i].size() > 0 && turn(rpoints[q[i].front()], rpoints[i], rpoints[j]) <= 0)
			{
				tmp+=proceed(q[i].front(), j);
				q[i].pop();
			}
			q[j].push(i);
			return tmp+1;
	};

	for (unsigned int i = 0; rpoints.size() > 0 && i < rpoints.size() - 1; i++)
		triangs += proceed(i, i + 1);
	return triangs;
}

int countEmptyTriangs(const vector<punto>& points)
{
	vector<puntos_ordenados> ordpoints;
	orderandsplit(points, ordpoints);
	int triangs=0;
	for(unsigned int i=0; i<points.size(); i++)
		triangs+=countEmptyTriangsVertex(ordpoints[i].r);
	return triangs;
}

vector<vector<punto> > report_empty_triangles(const vector<punto>& points)
{
	vector<vector<punto> > triangles;
	vector<puntos_ordenados> sorted_points;
	orderandsplit(points, sorted_points);
	auto G = compute_visibility_graph(sorted_points);
	for(unsigned int p=0; p<points.size(); p++)
	{
		auto& right_points = sorted_points[p].r;
		for(unsigned int q=0; q<right_points.size(); q++)
			for(auto& r:G[p][q].first)
				triangles.emplace_back(vector<punto>({points[p], right_points[r], right_points[q]}));
	}
	return triangles;
}

int slow_count_empty_triangles_containing_p(punto p, const vector<punto>& points)
{
	/* Counts the number of empty triangles in points that
	 * contain p in their interior
	 */
	int r=0;
	for(unsigned int i=0, s=points.size(); i<s; i++)
		for(unsigned int j=i+1; j<s; j++)
			for(unsigned int k=j+1; k<s; k++)
			{
				triangulo triang(points[i], points[j], points[k]);
				if(!pointsInTriang(points, triang))
					if(pointInTriang(p, triang))
						r++;
			}
	return r;
}

int count_empty_triangles_around_p(punto p, const vector<punto>& points)
{
	/*Counts the number of empty triangles of
	 * points union p which contain p as a vertex.
	 * p should not be in points
	 */
	auto G=visibility_graph_around_p(p,points, false);
	int triangs=0;
	for(unsigned int i=0; i<G.size(); i++)
		triangs+=G[i].first.size();

	return triangs;
}

void slow_count_empty_triangles_p(punto p, const vector<punto>& points, int& A, int& B)
{
	/*Slow version of count empty_triangles_p	 */
	B=slow_count_empty_triangles_containing_p(p, points);
	A=count_empty_triangles_around_p(p, points);
}

void count_empty_triangles_p(punto p, const vector<punto>& points, int& A, int& B) {
	/*
	 * Returns (A,B), where A is the number of empty triangles
	 * that contain p as a vertex and B the number of triangles
	 * that contain only p in their interior
	 */
	auto G = visibility_graph_around_p(p,
			points);
	vector<punto> sorted_points;
	sort_around_point(p, points, sorted_points);

	A = 0;
	B = 0;

	for (int q = 0; q < (int)sorted_points.size(); q++) {
		auto I = G[q].first, O = G[q].second;
		A += I.size();
		int j = 0;

		for (int i = 0; i < (int)I.size(); i++) {
			while (j < (int)O.size()
					&& turn(sorted_points[I[i]], sorted_points[q],
							sorted_points[O[j]]) > 0)
				j++;
			if (j < (int)O.size())
				for (int k = j; k < (int)O.size(); k++)
					if (turn(p, sorted_points[I[i]], sorted_points[O[k]])
							>= 0) {
						if (find(G[O[k]].second.begin(),
								G[O[k]].second.end(), I[i]) != G[O[k]].second.end())
							B++;
					}
		}
	}
	B /= 3;
}

struct trio
{
	int a;
	int b;
	int c;
};

void sort_trio(trio &t)
{
	bool swapped = false;
	do
	{
		swapped = false;
		if(t.a > t.b)
		{
			std::swap(t.a, t.b);
			swapped = true;
		}
		if(t.b > t.c)
		{
			std::swap(t.b, t.c);
			swapped = true;
		}
	}while(swapped);
}

pair<list<triangulo>, std::unordered_set<triangulo, triangHash> > report_empty_triangles_p(punto p, const vector<punto>& points)
{
	auto G = visibility_graph_around_p(p, points);
	vector<punto> sorted_points;
	sort_around_point(p, points, sorted_points);

	list<triangulo > A;
	std::unordered_set<triangulo, triangHash> B;

	for(unsigned int q = 0; q < sorted_points.size(); q++)
	{
		auto& incoming = G[q].first;
		auto& outgoing = G[q].second;

		for(auto r: incoming)
			A.emplace_back(p, sorted_points[q], sorted_points[r]);

		unsigned int j = 0;
		for(unsigned int i = 0; i < incoming.size(); i++)
		{
			while(j < outgoing.size() && turn(sorted_points[incoming[i]],
			                                  sorted_points[q], sorted_points[outgoing[j]]) > 0)
			{
				j++;
			}

			if(j < outgoing.size())
			{
				for(unsigned int k = j; k < outgoing.size(); k++)
				{
					if(turn(p, sorted_points[incoming[i]], sorted_points[outgoing[k]]) >= 0 &&
					   std::find(G[outgoing[k]].second.begin(), G[outgoing[k]].second.end(), incoming[i]) != G[outgoing[k]].second.end())
					{
						trio aux = {incoming[i], int(q), outgoing[k]};
						sort_trio(aux);
						B.emplace(sorted_points[aux.a], sorted_points[aux.b], sorted_points[aux.c]);
					}
				}
			}
		}
	}
	return make_pair(A, B);
}

int count_empty_triangles_for_each_p(vector<punto> points)
{
	/*Sums the the number of empty triangles
	 *containing each vertex and divides by 3*/
	int triangs=0;
	for(unsigned int i=0; i<points.size(); i++)
	{
		std::swap(points[i], points[0]);
		triangs+=count_empty_triangles_around_p(points[0], vector<punto>(points.begin()+1, points.end()));
	}
	return triangs;
}

/*
 * rholes
 */

int count_convex_rholes(const vector<punto> &points, int r, bool mono)
{
	/*
	 * Counts the number of rholes in points, as described
	 * in "Search for Empty Convex Polygons"
	 */
	int total = 0;
	vector<puntos_ordenados> sorted_points;
	orderandsplit(points, sorted_points);
	auto G=compute_visibility_graph(sorted_points);
	//vector<std::unordered_map<pair<int, int>, int, pairHash> > L_array;
	typedef std::unordered_map<pair<int, int>, int, pairHash> mapa;
	vector<mapa> L_array;
	L_array.reserve(points.size());

	//Start of MAX CHAIN

	for(unsigned int p=0, s=points.size(); p<s; p++)
	{
		vector<punto> &right_points=sorted_points[p].r;
		mapa L;
//		int tam=0;
//		for(auto &par : G[p])
//			tam+=par.second.size();
		L.reserve(G[p].size()*10);

		for(int q=right_points.size()-1; q>=0; q--)
		{
			vector<int> &outgoing_vertices=G[p][q].second;
			vector<int> &incoming_vertices=G[p][q].first;
			int max=0;
			int l=outgoing_vertices.size()-1;

			for(int vi=incoming_vertices.size()-1; vi>=0; vi--)
			{
				L[make_pair(incoming_vertices[vi], q)]=max+1;
				while(l>=0 && turn(right_points[incoming_vertices[vi]],
						right_points[q],
						right_points[outgoing_vertices[l]])==-1)
				{
					if(L[make_pair(q, outgoing_vertices[l])]>max)
					{
						max=L[make_pair(q, outgoing_vertices[l])];
						L[make_pair(incoming_vertices[vi], q)]=max+1;
					}
					l--;
				}
			}
		}
		L_array.push_back(std::move(L));
	}

	//End of MAX_CHAIN

	for(unsigned int p=0, ps=points.size(); p<ps; p++)
	{
		int color=0;
		if(mono)
			color=points[p].color;
		vector<punto> &right_points=sorted_points[p].r;
		mapa &L=L_array[p];

		//We create the sets holding the convex chains

		std::unordered_map<pair<int, int>, vector<int>, pairHash> C;
		for(unsigned int q=0, rs=right_points.size(); rs>0 && q<rs-1; q++)
		{
			vector<int> &outgoing_vertices=G[p][q].second;
			vector<int> &incoming_vertices=G[p][q].first;
			vector<int> idx;

			for(unsigned int i=0; i<outgoing_vertices.size(); i++)
				idx.push_back(i);

			std::sort(idx.begin(), idx.end(), [&](int i, int j)->bool{
				if(L[make_pair(q,outgoing_vertices[j])]-L[make_pair(q,outgoing_vertices[i])]<0)
					return true;
				else
					return false;
			});

			vector<int> outgoing_by_W;

			for(unsigned int i=0; i<idx.size(); i++)
				outgoing_by_W.push_back(outgoing_vertices[idx[i]]);

			for(auto vo : outgoing_vertices)
			{
				if(L[make_pair(q, vo)]>=r-2)
				{
					if(mono)
					{
						if(right_points[q].color == color &&
								right_points[vo].color==color)
							C[make_pair(q, vo)].push_back(1);
						else
							C[make_pair(q, vo)]=vector<int>();
					}
					else
						C[make_pair(q, vo)].push_back(1);
				}
				else
					C[make_pair(q, vo)]=vector<int>();
			}

			unsigned int m=0;
			int mprime=outgoing_vertices.size();

			for(auto vi : incoming_vertices)
			{
				while(m<outgoing_vertices.size() && turn(right_points[vi],
						right_points[q], right_points[outgoing_vertices[m]])==1)
				{
					outgoing_by_W.erase(find(outgoing_by_W.begin(), outgoing_by_W.end(), outgoing_vertices[m]));
					mprime--;
					m++;
				}

				for(auto ch : C[make_pair(vi, q)])
				{
					int t=0;
					int l=ch;
					while(t<mprime && L[make_pair(q, outgoing_by_W[t])]>=r-2-l)
					{
						int chprime=ch+1;
						if(l==r-3)
						{
							if(mono){
								if(right_points[outgoing_by_W[t]].color==color)
									total++;
							}
							else
								total++;
						}
						else{
							if(mono){
								if(right_points[outgoing_by_W[t]].color==color)
									C[make_pair(q, outgoing_by_W[t])].push_back(chprime);
							}
							else
								C[make_pair(q,outgoing_by_W[t])].push_back(chprime);
						}
						t++;
					}
				}
			}
		}
	}
	return total;
}

std::deque<vector<punto> > report_convex_rholes(const vector<punto>& points, int r, bool mono)
{
	/*
	 * Reports the number of rholes in points, as described
	 * in "Search for Empty Convex Polygons"
	 */
	std::deque<vector<punto> > report;
//	int total = 0;
	vector<puntos_ordenados> sorted_points;
	orderandsplit(points, sorted_points);
	auto G = compute_visibility_graph(sorted_points);
	vector<std::unordered_map<pair<int, int>, int, pairHash> > L_array;

	//Start of MAX CHAIN

	for (unsigned int p = 0, s = points.size(); p < s; p++)
	{
		auto right_points = sorted_points[p].r;
		std::unordered_map<pair<int, int>, int, pairHash> L;
		vector<int> idx_list;

		for (int i = right_points.size() - 1; i >= 0; i--)
			idx_list.push_back(i);

		for (auto q : idx_list)
		{
			auto outgoing_vertices = G[p][q].second;
			auto incoming_vertices = G[p][q].first;
			int max = 0;
			int l = outgoing_vertices.size() - 1;
			vector<int> idx_inc;

			for (int i = incoming_vertices.size()-1; i >= 0; i--)
				idx_inc.push_back(i);

			for (auto& vi : idx_inc)
			{
				L[make_pair(incoming_vertices[vi], q)] = max + 1;

				while (l >= 0 && turn(right_points[incoming_vertices[vi]],
								right_points[q],
								right_points[outgoing_vertices[l]]) == -1)
				{
					if (L[make_pair(q, outgoing_vertices[l])] > max)
					{
						max = L[make_pair(q, outgoing_vertices[l])];
						L[make_pair(incoming_vertices[vi], q)] = max + 1;
					}
					l--;
				}
			}
		}
		L_array.push_back(L);
	}
	//END OF MAX_CHAIN

	for (unsigned int p = 0, ps = points.size(); p < ps; p++)
	{
		int color = 0;

		if (mono)
			color = points[p].color;

		vector<punto> right_points = sorted_points[p].r;
		std::unordered_map<pair<int, int>, int, pairHash> L = L_array[p];

		//We create the sets holding the convex chains

		std::unordered_map<pair<int, int>, vector<vector<punto> >, pairHash> C;

		for (unsigned int q = 0, rs = right_points.size(); rs > 0 && q < rs - 1; q++)
		{
			vector<int> outgoing_vertices = G[p][q].second;
			vector<int> incoming_vertices = G[p][q].first;
			vector<int> idx;

			for (unsigned int i = 0; i < outgoing_vertices.size(); i++)
				idx.push_back(i);

			sort(idx.begin(), idx.end(),
					[&](int i, int j)->bool
					{
						if(L[make_pair(q,outgoing_vertices[j])]-L[make_pair(q,outgoing_vertices[i])]<0)
							return true;
						else
							return false;
					});

			vector<int> outgoing_by_W;

			for (auto i : idx)
				outgoing_by_W.push_back(outgoing_vertices[i]);

			for (auto vo : outgoing_vertices)
			{
				if (L[make_pair(q, vo)] >= r - 2)
				{
					if (mono)
					{
						if (right_points[q].color == color
								&& right_points[vo].color == color)
						{
							vector<punto> tmplist =
									{ right_points[vo], right_points[q],
											points[p] };

							C[make_pair(q, vo)].push_back(tmplist);
						}
						else
							C[make_pair(q, vo)] = vector<vector<punto> >();
					}
					else
					{
						vector<punto> tmplist =
						{ right_points[vo], right_points[q], points[p] };

						C[make_pair(q, vo)].push_back(tmplist);
					}
				}
				else
					C[make_pair(q, vo)] = vector<vector<punto> >();
			}

			unsigned int m = 0;
			int mprime = outgoing_vertices.size();

			for (auto vi : incoming_vertices)
			{
				while (m < outgoing_vertices.size()
						&& turn(right_points[vi], right_points[q],
								right_points[outgoing_vertices[m]]) == 1)
				{
					outgoing_by_W.erase(
							find(outgoing_by_W.begin(), outgoing_by_W.end(),
									outgoing_vertices[m]));
					mprime--;
					m++;
				}

				for (auto& ch : C[make_pair(vi, q)])
				{
					int t = 0;
					int l = ch.size() - 2;
					while (t < mprime
							&& L[make_pair(q, outgoing_by_W[t])]
									>= r - 2 - l)
					{
						vector<punto> chprime =
						{ right_points[outgoing_by_W[t]] };
						chprime.insert(chprime.end(), ch.begin(), ch.end());
						if (l == r - 3)
						{
							if (mono){
								if(right_points[outgoing_by_W[t]].color
											== color)
									report.push_front(chprime);
							}
							else
								report.push_front(chprime);
						}
						else
						{
							if (mono){
								if(right_points[outgoing_by_W[t]].color
											== color)
									C[make_pair(q, outgoing_by_W[t])].push_back(
										chprime);
							}
							else
								C[make_pair(q, outgoing_by_W[t])].push_back(
										chprime);
						}
						t++;
					}
				}
			}
		}
	}
	return report;
}

//void count_convex_rholes_p(punto p, const std::vector<punto>& points, int r, vector<vector<int> >& resA, vector<vector<int> >& resB, bool mono)
void count_convex_rholes_p(punto p, const std::vector<punto>& points, int r, int& resA, int& resB, bool mono)
{
	resA=0;
	resB=0;
	int rA=r, rB=r+1;
	vector<punto> rp, lp, sorted_points;
	rp.reserve(points.size()/2);
	lp.reserve(points.size()/2);
	sorted_points.reserve(points.size());

	vector<int> ir, il, indices;
	ir.reserve(points.size()/2);
	il.reserve(points.size()/2);
	indices.reserve(points.size());

	sort_around_point(p, points, rp, lp, false);
	sort_around_point(p, points, sorted_points);

	for(auto &punto : rp)
		ir.push_back(std::find(sorted_points.begin(), sorted_points.end(), punto) - sorted_points.begin());

	for(auto &punto : lp)
		il.push_back(std::find(sorted_points.begin(), sorted_points.end(), punto) - sorted_points.begin());

	punto q(p);
	punto qp(p);

	for(int ind=ir.size()-1; ind>=0; ind--)
	{
		int i = ir[ind];
		indices.push_back(i);
		if(sorted_points[i].y > q.y)
			q.y=sorted_points[i].y;
		if(sorted_points[i].y < qp.y)
			qp.y=sorted_points[i].y;
	}

	for(int ind=il.size()-1; ind>=0; ind--)
	{
		int i = il[ind];
		indices.push_back(i);
		if(sorted_points[i].y > q.y)
			q.y=sorted_points[i].y;
		if(sorted_points[i].y < qp.y)
			qp.y=sorted_points[i].y;
	}

	q.y++;
	qp.y--;

	//MAX_CHAIN_1
	auto VG = visibility_graph_around_p(p, points);
	//L contiene los pesos de cada arista
	std::unordered_map<pair<int, int>, int, pairHash> L;
	L.reserve(VG.size());

	for(auto& v : indices)
	{
		auto &inc=VG[v].first;
		auto &out=VG[v].second;

		auto pt=sorted_points[v];
		int l=out.size()-1, m=0;

		for(int ind=inc.size()-1; ind>=0; ind--)
		{

			int i=inc[ind];
			pair<int, int> i_v(i, v);

			L[i_v] = m+1;

			//Checar si es arista prohibida
			if((turn(p, q, sorted_points[i]) != turn(p, q, pt)) &&
			(turn(pt, sorted_points[i], p) != turn(pt, sorted_points[i], q)) && turn(p, q, pt)!=0 )
			{
				L[i_v]=0;
			}

			while(l>=0 && turn(sorted_points[i], pt, sorted_points[out[l]]) == LEFT)
			{
				pair<int, int> v_outl(v, out[l]);

				if(L.count(v_outl) == 1 &&
				L[v_outl] > m &&
				L[i_v] > 0)
				{
					m=L[v_outl];
					L[i_v]=m+1;
				}

				l--;
			}
		}
	}
	//END MAX_CHAIN_1

	//REPORTING_1
	std::unordered_map<pair<int, int>, vector<vector<int> >, pairHash> ChainsA, ChainsB;

	for(int i=0; i<(int)VG.size(); i++)
		for(auto& v : VG[i].first)
		{
			pair<int, int> v_i(v, i);
			ChainsA[v_i]=vector<vector<int> >();
			ChainsB[v_i]=vector<vector<int> >();
		}

	for(int ind=indices.size()-1; ind>=0; ind--)
	{
		//v es el índice del punto que se está tratando
		auto v = indices[ind];
		auto pt = sorted_points[v];
		auto &Si=VG[v].first;
		auto &So=VG[v].second;
		auto Sop=VG[v].second;

		std::sort(Sop.begin(), Sop.end(), [&L, &v](int v1, int v2)->bool{
			if(L[make_pair(v, v1)] > L[make_pair(v, v2)])
				return true;
			return false;
		    }
		);

		for(auto& out : So)
		{
			pair<int, int> v_out(v, out);
			vector<int> ch = {v, out};
			if(L[v_out]>=rA-2)
			{
				if (mono)
				{
					if (pt.color == p.color && sorted_points[out].color == p.color)
						ChainsA[v_out].push_back(ch);
				}
				else
					ChainsA[v_out].push_back(ch);
			}
			if(L[v_out]>=rB-2)
			{
				if(mono)
				{
					if(pt.color == sorted_points[out].color)
						ChainsB[v_out].push_back(ch);
				}
				else
					ChainsB[v_out].push_back(ch);
			}

		}

		//Para las cadenas de longitud r-2 con p como vértice:

		int m=0, mp=So.size()-1;

		for(auto& inc : Si)
		{
			while( m<(int)So.size() &&
					turn(sorted_points[inc],
						 pt,
						 sorted_points[So[m]]) > 0)
			{
				Sop.erase(std::find(Sop.begin(), Sop.end(), So[m]));
				mp--;
				m++;
			}

			for(auto& ch : ChainsA[make_pair(inc, v)])
			{
				int t=0;
				int l=ch.size()-1;

				while(t<=mp && L[make_pair(v, Sop[t])]>=rA-2-l)
				{
					auto chp = ch;
					chp.push_back(Sop[t]);
					if(l==rA-3)
					{
						//CHECAR SI TODAS LAS CONDICIONES SON NECESARIAS
						if(turn(sorted_points[chp[chp.size()-1]], p, sorted_points[chp[0]]) < 0 &&
						(turn(sorted_points[chp[chp.size()-2]], sorted_points[chp[chp.size()-1]], p)<0 &&
						turn(p, sorted_points[chp[0]], sorted_points[chp[1]])<0) )
						{
							if(mono)
							{
								if(sorted_points[Sop[t]].color == p.color)
									//resA.push_back(chp);
									resA++;
							}
							else
								//resA.push_back(chp);
								resA++;
						}
					}
					else
					{
						if(mono)
						{
							if(sorted_points[Sop[t]].color == p.color)
								ChainsA[make_pair(v, Sop[t])].emplace_back(chp);
						}
						else
							ChainsA[make_pair(v, Sop[t])].emplace_back(chp);
					}
					t++;
				}
			}
		}

		//Para las cadenas de longitud r-1 con p en su interior:

		m=0;
		mp=So.size()-1;

		Sop=So;
		std::sort(Sop.begin(), Sop.end(), [&L, &v](int v1, int v2)->bool{
					if(L[make_pair(v, v1)] > L[make_pair(v, v2)])
						return true;
					return false;
				    }
				);

		for(auto& inc : Si)
		{
			while( m<(int)So.size() &&
					turn(sorted_points[inc],
						 pt,
						 sorted_points[So[m]]) > 0)
			{
				Sop.erase(std::find(Sop.begin(), Sop.end(), So[m]));
				mp--;
				m++;
			}

			for(auto& ch : ChainsB[make_pair(inc, v)])
			{
				int t=0;
				int l=ch.size()-1;

				while(t<=mp && L[make_pair(v, Sop[t])]>=rB-2-l)
				{
					auto chp = ch;
					chp.push_back(Sop[t]);
					if(l == rB-3)
					{
						//CHECAR SI TODAS LAS CONDICIONES SON NECESARIAS
						if(turn(sorted_points[chp[chp.size()-1]], sorted_points[chp[0]], p) < 0 &&
						(turn(sorted_points[chp[chp.size()-2]], sorted_points[chp[chp.size()-1]], sorted_points[chp[0]])<0 &&
						turn(sorted_points[chp[chp.size()-1]], sorted_points[chp[0]], sorted_points[chp[1]])<0) &&
						L.find(make_pair(chp[chp.size()-1], chp[0])) != L.end() )
						{
							if(mono)
							{
								if(sorted_points[ch[0]].color == sorted_points[Sop[t]].color)
									//resB.push_back(chp);
									resB++;
							}
							else
								//resB.push_back(chp);
								resB++;
						}
					}
					else
					{
						if(mono)
						{
							if(sorted_points[ch[0]].color == sorted_points[Sop[t]].color)
								ChainsB[make_pair(v, Sop[t])].emplace_back(chp);
						}
						else
							ChainsB[make_pair(v, Sop[t])].emplace_back(chp);
					}
					t++;
				}
			}
		}
	}
	//END REPORTING_1

	//Se vuelve a tratar los puntos para enconrar cadenas
	//omitidas al tomar como referencia a q

	std::function<bool(const vector<int>&)> cruza_q=[&q, &sorted_points, &p](const vector<int>& ch){
		for(int i = 0; i < (int)ch.size()-1; i++)
		{
			auto v1 = sorted_points[ch[i]];
			auto v2 = sorted_points[ch[i+1]];
			if((turn(v1, v2, q) != turn(v1, v2, p)) &&
			(turn(p, q, v1) != turn(p, q, v2)) && turn(p, q, v2)!=0)
				return true;
		}
		return false;
	};

	indices.clear();
	for(int ind=il.size()-1; ind>=0; ind--)
		indices.push_back(il[ind]);

	for(int ind=ir.size()-1; ind>=0; ind--)
		indices.push_back(ir[ind]);

	//MAX_CHAIN_2

	L.clear();
	L.reserve(VG.size());

	for(auto& v : indices)
	{
		auto &inc=VG[v].first;
		auto &out=VG[v].second;

		auto pt=sorted_points[v];
		int l=out.size()-1, m=0;

		for(int ind=inc.size()-1; ind>=0; ind--)
		{

			int i=inc[ind];
			pair<int, int> i_v(i, v);

			L[i_v] = m+1;

			//Checar si es arista prohibida
			if((turn(p, qp, sorted_points[i]) != turn(p, qp, pt)) &&
			(turn(pt, sorted_points[i], p) != turn(pt, sorted_points[i], qp)) )
			{
				L[i_v]=0;
			}

			while(l>=0 && turn(sorted_points[i], pt, sorted_points[out[l]])<0)
			{
				pair<int, int> v_outl(v, out[l]);

				if(L.count(v_outl) == 1 &&
				L[v_outl] > m &&
				L[i_v] > 0)
				{
					m=L[v_outl];
					L[i_v]=m+1;
				}

				l--;
			}
		}
	}
	//END MAX_CHAIN_2

	//REPORTING_2
	ChainsA.clear();

	for(int i=0; i<(int)VG.size(); i++)
		for(auto& v : VG[i].first)
			ChainsA[make_pair(v, i)]=vector<vector<int> >();

	for(int ind=indices.size()-1; ind>=0; ind--)
	{
		//v es el índice del punto que se está tratando
		auto v = indices[ind];
		auto pt = sorted_points[v];
		auto &Si=VG[v].first;
		auto &So=VG[v].second;
		auto Sop=VG[v].second;

		std::sort(Sop.begin(), Sop.end(), [&L, &v](int v1, int v2)->bool{
			if(L[make_pair(v, v1)] > L[make_pair(v, v2)])
				return true;
			return false;
		    }
		);

		for(auto& out : So)
		{
			pair<int, int> v_out(v, out);
			ChainsA[v_out] = vector<vector<int> >();
			if(L[v_out]>=rA-2)
			{
				if(mono)
				{
					if(pt.color == p.color && sorted_points[out].color == p.color)
						ChainsA[v_out].push_back(vector<int>({v, out}));
				}
				else
					ChainsA[v_out].push_back(vector<int>({v, out}));
			}
		}

		//Para las cadenas de longitud r-2 con p como vértice:

		int m=0, mp=So.size()-1;

		for(auto& inc : Si)
		{
			while( m<(int)So.size() &&
					turn(sorted_points[inc],
						 pt,
						 sorted_points[So[m]]) > 0)
			{
				Sop.erase(std::find(Sop.begin(), Sop.end(), So[m]));
				mp--;
				m++;
			}

			for(auto& ch : ChainsA[make_pair(inc, v)])
			{
				int t=0;
				int l=ch.size()-1;

				while (t <= mp && L[make_pair(v, Sop[t])] >= rA - 2 - l)
				{
					auto chp = ch;
					chp.push_back(Sop[t]);
					if (l == rA - 3)
					{
						//CHECAR SI LAS ULTIMAS @ CONDICIONES SON NECESARIAS
						if (turn(sorted_points[chp[chp.size() - 1]], p,	sorted_points[chp[0]]) < 0 &&
						cruza_q(chp) &&
						(turn(sorted_points[chp[chp.size()-2]], sorted_points[chp[chp.size()-1]], p)<0 &&
						turn(p, sorted_points[chp[0]], sorted_points[chp[1]])<0) )
						{
							if(mono)
							{
								if(p.color == sorted_points[Sop[t]].color)
									//resA.push_back(chp);
									resA++;
							}
							else
								//resA.push_back(chp);
								resA++;
						}
					}
					else
					{
						if(mono)
						{
							if(p.color == sorted_points[Sop[t]].color)
								ChainsA[make_pair(v, Sop[t])].emplace_back(chp);
						}
						else
							ChainsA[make_pair(v, Sop[t])].emplace_back(chp);
					}

					t++;
				}
			}
		}
	}
	//END REPORTING_2
}
