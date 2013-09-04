#include <stdio.h>
#include <stdlib.h>
#include "bigint.h"

long pivote[2];

int turn(long p0[],long p1[],long p2[]);
int cmp_points(const void *qp, const void *rp);
void sort_points(long p[],void *pts,int length);
long range_crossing(long pts[][2],int n,int range_begin,int range_end);
long crossing(long /* **pts*/pts[][2],int n);
void imprime_piv_pts(long pi[],long pts[][2],int n);
void imprimepts(long pts[][2],int n);
int signo(long num);

int turn(long p0[],long p1[],long p2[]){
        BIG_INT p00=(BIG_INT)p0[0],p01=(BIG_INT)p0[1],p10=(BIG_INT)p1[0],p11=(BIG_INT)p1[1],p20=(BIG_INT)p2[0],p21=(BIG_INT)p2[1];
	BIG_INT tempres;
	int res=0;
	tempres=((p20-p00)*(p11-p01))-((p10-p00)*(p21-p01));
        //printf("tempres= %lld",tempres);
	if(tempres<0)
	  return -1;
	else
	  if(tempres>0)
	    return 1;

	return 0;
}

void sort_points(long p[2],void *pts, int length)
{
  pivote[0]=p[0];
  pivote[1]=p[1];
  qsort(pts, length, 2*sizeof(long), cmp_points);
}

/////////////////////////////////////////////////////////////////////////
int cmp_points(const void *qp, const void *rp)
{
  long qx,qy,rx,ry;
  int sign;
  long q[2];
  long r[2];
  q[0]=*((const long*) qp);//
  q[1]=*((const long*) qp+1);
  r[0]=*((const long*) rp);
  r[1]=*((const long*)rp+1);
  qx=q[0]-pivote[0];
  qy=q[1]-pivote[1];
  rx=r[0]-pivote[0];
  ry=r[1]-pivote[1];
  sign=signo(rx)*signo(qx);

//////////////////////////////////////////////////////////////////////////////
/*printf("en cmp-points\n");
printf("pivote=( %d, %d)\n",pivote[0],pivote[1]);
printf("q=(%d- %d=  %d, %d- %d= %d)\n",q[0],pivote[0],qx,q[1],pivote[1],qy);
printf("r=(%d- %d= %d , %d- %d= %d)\n",r[0],pivote[0],rx,r[1],pivote[1],ry);
printf("signo=%d * %d =%d\n",rx,qx,sign);*/
//////////////////////////////////////////////////////////////////////////////

  if(sign>0){////////////////////////////////////////
//printf("resultado de turn= %d\n",turn(pivote,q,r));
///////////////////////////////////////
    return turn(pivote,q,r);}
  
  else{
	if(sign<0){
		if(qx>0){//printf("singno es negativo y qx es positivo regresamos -1\n");
		   return -1;}
		else{//printf("singo es negativo y qx es negativo regresamos 1\n");
	  	   return 1;}	
   	}
	else{//caso sign==0
		if(qx==0){
			if(rx!=0){//caso q=(0,qy) y r=(rx,ry)
				if(qy<0){//printf("signo es 0 y qx es cero, rx no y qy negativo regresamos 1\n");
				   return 1;}
				else{//caso qy>0
				   if(rx>0){//printf("signo es 0 qx es cero rx es positivo y qy positivo o cero regresamos 1\n");
				      return 1;}
				   else{//printf("signo es 0 qx es cero rx es negativo y qy positivo o cero\n");
				      return -1;}
				}
			}	
			else/*/caso q(0,qy) y r(0,ry)*/{//printf("signo es 0 rx y qx es cero, se regresa el signo de la diferencia %d\n", signo(qy-ry));
				  return signo(qy-ry);}//qy-ry;}
			
		}

		else{//caso q=(qx,qy) y r=(0,ry)
			if(ry<0){//printf("signo es 0 qx no es cero, rx es 0 y ry es negativo\n");
				return -1;}
			else{
				if(qx>0){//printf("signo es 0 y qx es positivo rx es cero y ry es no negativo regresa -1\n");
				   return -1;}
				else{//printf("signo es 0 qx es < 0 ry es no negativo regresa 1\n");
				   return 1;}
			}
		}
	}

  }    

}

long crossing(long pts[][2],int n)
{
  long total,cr;
  total=n*(n-3)*(n-2)*(n-1)/2;
  cr=range_crossing(pts,n,0,n);
  cr-=total/4;    
  return cr;
}
////////////////////////////////////////////////////////////////////////////////////////////

long range_crossing(long pts[][2],int n,int range_begin,int range_end)
{
  int i,j,k,start,end,total;
  long cr=0;
  long temp_pts[n-1][2];
//imprimepts(pts,n);//////////////////////////////////////////
  /*int **temp_pts;
  temp_pts=(int**)malloc(n*sizeof(int*));
  
  for(i=0;i<n;i++)
      temp_pts[i]=(int*)malloc(2*sizeof(int));
  */
  cr=0;
  //total=(n*(n-3)*(n-2)*(n-1)/2)/10;//el diez es para que sea el mismo resultado que en geometricbasics,revisar este punto
  //total=n*(n-3)*(n-2)*(n-1)/2;
//printf("Esta bien la operacion?\n total=[%d]*[%d-3]*[%d-2]*[%d-1]/2= %d",n,n,n,n,total);

//printf("C TOTAL= %d",total);////

  for(i=range_begin;i<range_end;i++)
    {
///////////////////////////////
  //    printf("\nEn la iteracion %d\n",i);
///////////////////////////////
      //copiamos el arreglo de puntos
      k=0;
      for(j=0;j<n;j++)
	{
	  if(j!=i)
	    {
	      temp_pts[k][0]=pts[j][0];
	      temp_pts[k][1]=pts[j][1];
	      k=k+1;
	    }
	}
      //
      sort_points(pts[i],temp_pts,n-1);
///////////////////////////////////////

    //  imprime_piv_pts(pts[i],temp_pts,n-1);
//////////////////////////////////////
      end=0;
      for(start=0;start<n-1;start++)
	{
          int vuelta=turn(pts[i],temp_pts[start],temp_pts[(end+1)%(n-1)]);
	while(vuelta<=0 && (end+1)%(n-1)!=start){
	  //while(turn(pts[i],temp_pts[start],temp_pts[(end+1)%(n-1)])<=0 &&
		//(end+1)%(n-1)!=start)
              
	      end++;
vuelta=turn(pts[i],temp_pts[start],temp_pts[(end+1)%(n-1)]);}////////este si se borra el end++ de arriba no
	      //end=end+1
	  k=(end-start+n-1)%(n-1);
  //        printf("\nVuelta= %d\tstart= %d\tend=%d",turn(pts[i],temp_pts[start],temp_pts[(end+1)%(n-1)]),start,end);

  // printf("\nEl valor de k = [%d-%d+%d-1=%d] mod %d= %d\n",end,start,n,end-start+(n-1), n-1, k); ///////////////////
          //printf("valores antes de calcular cr: \ncr=%lld\nk=%d",cr,k);
	  cr=cr+(k*(k-1))/2;
       
          
	  //printf("con lo cual el valor de cr es: %lld\n",cr);
	}
    }
//    printf("\nla operacion final es cr= cr-total/4");
//    printf("= %d - %d/4=",cr,total);
//    printf("cr antes de dividir=%lld-%d/4",cr,total);
//    cr-=total/4;
  //  printf("\acr=%lld\n",cr);
  return cr;
//cr=0;
//return cr;
}

void imprime_piv_pts(long pi[],long pts[][2],int n){

    int i;
    printf("\npivote= (%d , %d)\n",pi[0],pi[1]);
    for(i=0;i<n;i++)
            printf("pts[%d]= (%d , %d)\n",i,pts[i][0]-pi[0],pts[i][1]-pi[1]);
}

void imprimepts(long pts[][2],int n){
int i;
    printf("la lista original de puntos es:\n");
	for(i=0;i<n;i++)
		printf("p(%d)=(%d,%d)\n",i,pts[i][0],pts[i][1]);
}

int signo(long num){
   int res=0;
   
   if (num<0)
      res=-1;
   else
      if(num>0)
         res=1;

   return res;
}


//q mas grande 1
