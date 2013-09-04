#include <stdio.h>
#include <stdlib.h>
#include "bigint.h"

long pivote[2];

int turn(long p0[],long p1[],long p2[]);
int cmp_points(const void *qp, const void *rp);

int main(int argc, char *argv[])
{
  long p[2]={0,0};
  long q[2]={1,1};
  long r[2]={2,1};
  long res;
  res=turn(p,q,r);
  printf("%d",res);
  	
}

int turn(long p0[],long p1[],long p2[]){
        BIG_INT p00=(BIG_INT)p0[0],p01=(BIG_INT)p0[1],p10=(BIG_INT)p1[0],p11=(BIG_INT)p1[1],p20=(BIG_INT)p2[0],p21=(BIG_INT)p2[1];
	BIG_INT tempres;
	int res=0;
	tempres=((p20-p00)*(p11-p01))-((p10-p00)*(p21-p01));
        //printf("tempres= %lld",tempres);
	if(tempres>0)
	  return 1;
	if(tempres<1)
	  return -1;
	return 0;
}

int cmp_points(const void *qp, const void *rp)
{
  long qx,qy,rx,ry;
  long q[2];
  long r[2];
  long origin[2]={0,0};
  q[0]=*((const long*) qp)-pivote[0];
  q[1]=*((const long*) qp+1)-pivote[1];
  r[0]=*((const long*) rp)-pivote[0];
  r[1]=*((const long*)rp+1)-pivote[1];
  
  //Both in the same open semiplane
  if (r[0]*q[0]>0)
    return turn(origin,q,r);

  //Each in a different open semiplane
  if (r[0]*q[0]<0)
    if (r[0]<0)
      return -1;
    else
      return 1;
  //Both on them on the Y-axis  
  if(r[0]==q[0])
    //One below and one above the X-axis
    if (r[1]*q[1]<0)
      if (r[1]>0)
	return 1;
      else
	return -1;
    else
      return 0;
  //only one in the Y-axis
  if (r[0]==0)
    if(r[1]>0)
      if(q[0]>0)
	return -1;
      else
	return 1;
    else
      return -1;
  else
    if(q[1]>0)
      if(r[0]>0)
	return 1;
      else
	return -1;
    else
      return 1;
  
}

void reverse_in_place(long pts[][2],int start,int end)
{
  int m=(end+1-start)/2;
  int i;
  long tmp[2];
  for(i=0;i<m;i++)
    {
      tmp[0]=pts[start+i][0];
      tmp[1]=pts[start+i][1];
      pts[start+i][0]=pts[end-i][0];
      pts[start+i][1]=pts[end-i][1];
      pts[end-i][0]=tmp[0];
      pts[end-i][1]=tmp[1];
    }
}

int concave(long p[2],long pts[][2],int n)
{
  int i;
  for(i=0;i<n;i++)
    {
      if (turn(pts[i],p,pts[(i+1)%n])<0)
	  return i;
    }
  return -1;
}

void shift(long pts[][2],int s,int n)
{
  if (s>0)
    {
    reverse_in_place(pts,0,s-1);
    reverse_in_place(pts,s,n-1);
    reverse_in_place(pts,0,n-1);
    }
  
}

void sort_around_point(long p[2],long **pts, int n)
{
  int i,concave_val;
  pivote[0]=p[0];
  pivote[1]=p[1];
  qsort(pts, n, 2*sizeof(long), cmp_points);
  concave_val=concave(p,pts,n);
  if(concave_val!=-1)
    {
      concave_val=(concave_val+1)%n;
      shift(pts,concave_val,n) ;
    }
}



