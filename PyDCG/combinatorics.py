""" Implementacion de las funciones basicas
   de combinatoria, factorial, binomial, etc..."""

def factorial(n):
    """n!"""
    fact=1
    for i in range(1,n+1):
        fact=fact*i
    return fact

def binomial(n,k):
    """combinaciones de n en k"""
    bin=1
    for i in range(n-k+1,n+1):
        bin=bin*i
    return bin/factorial(k)

def ncombinations(n,k):
    combs=[]
    c=[]
    def rec_comb(i):
        if len(c)>=k:
            combs.append(c[:])
        else:
            for j in range(i+1,n):
                c.append(j)
                rec_comb(j)
                c.pop()
    rec_comb(-1)
    return combs

def combinations(S,k):
    """returns all k-sets of S"""
    combs=ncombinations(len(S),k)
    setcomb=[[] for i in range(binomial(len(S),k))]
    for i in range(len(setcomb)):
        for j in combs[i]:
            setcomb[i].append(S[j])
    return setcomb
    
    
        
            
    
    