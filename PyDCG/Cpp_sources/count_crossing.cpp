#include "count_crossing.h"
#include "geometricbasicsCpp.h"

void sort_points(long p[2], void *pts, int length) {
	long pivote[2]; //Moví este arreglo aquí porque causaba conflictos con un arreglo
					//con el mismo nombre en geometricbasics. - Carlos
	pivote[0] = p[0];
	pivote[1] = p[1];
	qsort(pts, length, 2 * sizeof(long), cmp_points);
}

/////////////////////////////////////////////////////////////////////////


long crossing(long pts[][2], int n) {
	long total, cr;
	total = n * (n - 3) * (n - 2) * (n - 1) / 2;
	cr = range_crossing(pts, n, 0, n);
	cr -= total / 4;
	return cr;
}
////////////////////////////////////////////////////////////////////////////////////////////

long range_crossing(long pts[][2], int n, int range_begin, int range_end) {
	int i, j, k, start, end, total;
	long cr = 0;
	long temp_pts[n - 1][2];
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

	for (i = range_begin; i < range_end; i++) {
///////////////////////////////
		//    printf("\nEn la iteracion %d\n",i);
///////////////////////////////
		//copiamos el arreglo de puntos
		k = 0;
		for (j = 0; j < n; j++) {
			if (j != i) {
				temp_pts[k][0] = pts[j][0];
				temp_pts[k][1] = pts[j][1];
				k = k + 1;
			}
		}
		//
		sort_points(pts[i], temp_pts, n - 1);
///////////////////////////////////////

		//  imprime_piv_pts(pts[i],temp_pts,n-1);
//////////////////////////////////////
		end = 0;
		for (start = 0; start < n - 1; start++) {
			int vuelta = turn(pts[i], temp_pts[start],
					temp_pts[(end + 1) % (n - 1)]);
			while (vuelta <= 0 && (end + 1) % (n - 1) != start) {
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
	return cr;
//cr=0;
//return cr;
}

void imprime_piv_pts(long pi[], long pts[][2], int n) {

	int i;
	printf("\npivote= (%d , %d)\n", pi[0], pi[1]);
	for (i = 0; i < n; i++)
		printf("pts[%d]= (%d , %d)\n", i, pts[i][0] - pi[0], pts[i][1] - pi[1]);
}

void imprimepts(long pts[][2], int n) {
	int i;
	printf("la lista original de puntos es:\n");
	for (i = 0; i < n; i++)
		printf("p(%d)=(%d,%d)\n", i, pts[i][0], pts[i][1]);
}

int signo(long num) {
	int res = 0;

	if (num < 0)
		res = -1;
	else if (num > 0)
		res = 1;

	return res;
}

//q mas grande 1
