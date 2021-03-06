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

#include "count_crossing.h"
#include "geometricbasicsCpp.h"

struct candidato
{
    Punto pt;
    int index;
    bool original;
    bool antipodal;

    candidato() : pt(0,0), index(0), original(false), antipodal(false)
    {
    }
};

long long crossing(long long **pts, long long n)
{
    long long total, cr;
    total = (n * (n - 3) * (n - 2) * (n - 1)) / 8;
    cr = range_crossing(pts, n, 0, n);
    cr -= total;
    return cr;
}
////////////////////////////////////////////////////////////////////////////////////////////

long long range_crossing(long long **pts, int n, int range_begin, int range_end)
{

    int i, j, k, start, end;
    long long cr = 0;
    long long **temp_pts;
    temp_pts = new long long*[n-1];
    for(int m = 0; m<n-1; m++)
        temp_pts[m] = new long long[2];
    //imprimepts(pts,n);//////////////////////////////////////////
    /*int **temp_pts;
     temp_pts=(int**)malloc(n*sizeof(int*));

     for(i=0;i<n;i++)
     temp_pts[i]=(int*)malloc(2*sizeof(int));
     */
    cr = 0;
    //total=(n*(n-3)*(n-2)*(n-1)/2)/10;//el diez es para que sea el mismo resultado que en geometricbasics,revisar este punto
    //total=n*(n-3)*(n-2)*(n-1)/2;
//printf("Esta bien la operacion?\n total=[%d]*[%d-3]*[%d-2]*[%d-1]/2= %d",n,n,n,n,total);

//printf("C TOTAL= %d",total);////

    for (i = range_begin; i < range_end; i++)
    {
///////////////////////////////
        //    printf("\nEn la iteracion %d\n",i);
///////////////////////////////
        //copiamos el arreglo de puntos
        k = 0;
        for (j = 0; j < n; j++)
        {
            if (j != i)
            {
                temp_pts[k][0] = pts[j][0];
                temp_pts[k][1] = pts[j][1];
                k = k + 1;
            }
        }
        //
        sort_around_point(pts[i], temp_pts, n - 1);
///////////////////////////////////////

        //  imprime_piv_pts(pts[i],temp_pts,n-1);
//////////////////////////////////////
        end = 0;
        for (start = 0; start < n - 1; start++)
        {
            int vuelta = turn(pts[i], temp_pts[start],
                              temp_pts[(end + 1) % (n - 1)]);
            while (vuelta <= 0 && (end + 1) % (n - 1) != start)
            {
                //while(turn(pts[i],temp_pts[start],temp_pts[(end+1)%(n-1)])<=0 &&
                //(end+1)%(n-1)!=start)

                end++;
                vuelta = turn(pts[i], temp_pts[start],
                              temp_pts[(end + 1) % (n - 1)]);
            }		////////este si se borra el end++ de arriba no
            //end=end+1
            k = (end - start + n - 1) % (n - 1);
            //        printf("\nVuelta= %d\tstart= %d\tend=%d",turn(pts[i],temp_pts[start],temp_pts[(end+1)%(n-1)]),start,end);

            // printf("\nEl valor de k = [%d-%d+%d-1=%d] mod %d= %d\n",end,start,n,end-start+(n-1), n-1, k); ///////////////////
            //printf("valores antes de calcular cr: \ncr=%lld\nk=%d",cr,k);
            cr = cr + (k * (k - 1)) / 2;

            //printf("con lo cual el valor de cr es: %lld\n",cr);
        }
    }
//    printf("\nla operacion final es cr= cr-total/4");
//    printf("= %d - %d/4=",cr,total);
//    printf("cr antes de dividir=%lld-%d/4",cr,total);
//    cr-=total/4;
    //  printf("\acr=%lld\n",cr);
    for(int m = 0; m<n-1; m++)
        delete[] temp_pts[m];
    delete[] temp_pts;
    return cr;
//cr=0;
//return cr;
}

void imprime_piv_pts(long pi[], long pts[][2], int n)
{

    int i;
    printf("\npivote= (%ld , %ld)\n", pi[0], pi[1]);
    for (i = 0; i < n; i++)
        printf("pts[%d]= (%ld , %ld)\n", i, pts[i][0] - pi[0], pts[i][1] - pi[1]);
}

void imprimepts(long pts[][2], int n)
{
    int i;
    printf("la lista original de puntos es:\n");
    for (i = 0; i < n; i++)
        printf("p(%d)=(%ld,%ld)\n", i, pts[i][0], pts[i][1]);
}

vector<candidato> sort_around_point(Punto p, const vector<candidato>& points)
{
    /*
     * Sorts a set of points by angle around a point p.
     * If join == false, returns a vector with the points at the right of p
     * and a vector with the points at the left of p. Otherwise it returns
     * just one vector.
     */

    Punto p1(p.x, p.y + 1);
    vector<candidato> r, l;
    r.reserve(points.size());
    l.reserve(points.size());

    for (auto &q : points)
    {
        if (turn(p, p1, q.pt) == RIGHT)
            r.push_back(q);
        else if (turn(p, p1, q.pt) == LEFT)
            l.push_back(q);
        else if (p.y >= q.pt.y)
            l.push_back(q);
        else
            r.push_back(q);
    }

    sort(l.begin(), l.end(), [&p](candidato r, candidato q)->bool
    {
        if(turn(p, r.pt, q.pt) < 0)
            return true;
        return false;
    }
        );

    sort(r.begin(), r.end(), [&p](candidato r, candidato q)->bool
    {
        if(turn(p, r.pt, q.pt) < 0)
            return true;
        return false;
    }
        );

    r.insert(r.end(), l.begin(), l.end());

    bool concave = false;
    unsigned int i = 0;

    for (i = 0; i < r.size(); i++)
        if (turn(r[i].pt, p, r[(i + 1) % r.size()].pt) < 0)
        {
            concave = true;
            break;
        }

    if (concave)
    {
        int start = (i + 1) % r.size();
        vector<candidato> tmp(r);

        for (i = 0; i < tmp.size(); i++)
            r[i] = tmp[(start + i) % r.size()];
    }
    return r;
}

vector<int> count_crossings_candidate_list(int point_index, vector<Punto> &candidate_list, vector<Punto> &puntos)
{
    Punto p(0,0);
    int pos_point_in_tp = 0;
    int num_cand = candidate_list.size();
    int num_pts = puntos.size();
    vector<candidato> candidates(num_cand);
    vector<int> cr_list (num_cand, 0);
    vector<int> cr_list2 (num_cand, 0);
    vector<int> cr_list3 (num_cand, 0);
    vector<int> count_change_of_list (num_cand, 0);
    vector<int> count_change_cr_for_q (num_cand, 0);
    int cr2=0;
    int cr3=0;

    for(int i=0; i<num_cand; i++)
    {
        candidates[i].pt = candidate_list[i];
        candidates[i].index =i;
        cr_list2[i]=0;
        cr_list3[i]=0;
        count_change_of_list[i]=0;
        count_change_cr_for_q[i]=0;
    }

    vector<candidato> temp_pts(num_pts-1);
    //int centro=0; unused variable
    vector<candidato> united_points(2*num_pts-3+num_cand);

    for(int centro = 0; centro<num_pts; centro++)
    {
        if(centro != point_index)
        {
            p = puntos[centro];

            for(int i=0; i<centro; i++)
                temp_pts[i].pt = puntos[i];

            for(int i=centro; i<num_pts-1; i++)
                temp_pts[i].pt = puntos[i+1];


            temp_pts=sort_around_point(p,temp_pts);

            for(int i=0; i<num_pts-1; i++)
            {
                temp_pts[i].index=i;
                temp_pts[i].original = true;
                temp_pts[i].antipodal = true;
            }

            //nis for p
            vector<int> nis(num_pts-1);
            int j=0;
            for(int i=0; i<num_pts-1; i++)
            {
                Punto p0 = temp_pts[i].pt;
                Punto p1 = temp_pts[(j+1)%(num_pts-1)].pt;

                while((turn(p,p0,p1)<=0) && ((j+1)%(num_pts-1)!=i))
                {
                    j++;
                    p0=temp_pts[i].pt;
                    p1=temp_pts[(j+1)%(num_pts-1)].pt;
                }

                if((j-i)%(num_pts-1)>=0)
                    nis[i]=(j-i)%(num_pts-1);
                else
                    nis[i]=(j-i)%(num_pts-1)+num_pts-1;
            }

            ///////////aca termina nis
            for(int i=0; i<num_pts-1; i++)                                    //puse un -1
                if(temp_pts[i].pt == puntos[point_index])
                    pos_point_in_tp=i;
            //Suma 2 cr2
            for(int i=0; i<num_pts-1; i++)
                if(i!=pos_point_in_tp)
                    cr2=cr2+(nis[i]*(nis[i]-1)/2);

            /////aca comienza el join_pts_antipodal_candidatelist
            j=0;
            for(int i=0; i<pos_point_in_tp; i++)
            {
                united_points[j] = temp_pts[i];
                j=j+1;
                united_points[j] = temp_pts[i];
                united_points[j].pt.x = 2*p.x-temp_pts[i].pt.x;
                united_points[j].pt.y = 2*p.y-temp_pts[i].pt.y;
                united_points[j].antipodal = false;
                j=j+1;
            }

            united_points[j].pt = temp_pts[pos_point_in_tp].pt;
            j=j+1;

            for(int i=pos_point_in_tp+1; i<num_pts-1; i++)
            {
                united_points[j] = temp_pts[i];
                j=j+1;
                united_points[j] = temp_pts[i];
                united_points[j].pt.x = 2*p.x-temp_pts[i].pt.x;
                united_points[j].pt.y = 2*p.y-temp_pts[i].pt.y;
                united_points[j].original = true;
                united_points[j].antipodal = false;
                j=j+1;
            }

            for(int i=0; i<num_cand; i++)
            {
                united_points[j] = candidates[i];
                j=j+1;
            }

            united_points=sort_around_point(p,united_points);
            ////aca termina el join_pts_antipodal_candidatelist
            int position_p;
            for(int i=0; i<2*num_pts-3+num_cand; i++)
                if(united_points[i].pt == puntos[point_index])
                    position_p=i;

            ///// Aca comenzamos el change_of_cr_for_list
            vector<int> aux_nis(num_pts-1);
            int count_ni=0;
            int sum_ni=0;

            for(int i=0; i<num_pts-1; i++)
                aux_nis[i]=nis[i];

            for(int i=1; i<2*num_pts-3+num_cand; i++)
            {
                int pos=(position_p+i)%(2*num_pts-3+num_cand);
                if (united_points[pos].original)
                {
                    if (united_points[pos].antipodal)
                    {
                        sum_ni=sum_ni+aux_nis[united_points[pos].index];
                        aux_nis[united_points[pos].index]=aux_nis[united_points[pos].index]+1;
                        count_ni--;
                    }
                    else
                    {
                        sum_ni=sum_ni-aux_nis[united_points[pos].index]+1;
                        aux_nis[united_points[pos].index]=aux_nis[united_points[pos].index]-1;
                        count_ni++;
                    }
                }
                else
                {
                    cr_list2[united_points[pos].index]=cr_list2[united_points[pos].index]+sum_ni;
                    count_change_of_list[united_points[pos].index]=count_ni;
                }
            }
            /////// aca terminamos el change_of_cr_for_list

            /////////////////Aca comienza la suma 3 cr3/////////////////
            cr3=cr3+(nis[pos_point_in_tp]*(nis[pos_point_in_tp]-1)/2);
            ///// cr_list3
            for(int i=0; i<num_cand; i++)
                cr_list3[i]=cr_list3[i]+(count_change_of_list[i]+nis[pos_point_in_tp])*(count_change_of_list[i]+nis[pos_point_in_tp]-1)/2;
            //////////////////////////////////fin de la suma 3
        }
    }
    int total=num_pts*(num_pts-1)*(num_pts-2)*(num_pts-3)/8;
    for(int i=0; i<num_cand; i++)
    {
        cr_list2[i]=cr_list2[i]+cr2;
        cr_list[i]=cr_list2[i]+2*cr_list3[i]-total;
    }

    return cr_list;
}
