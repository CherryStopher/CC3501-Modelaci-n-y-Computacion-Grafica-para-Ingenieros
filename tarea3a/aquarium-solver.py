# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as mpl

# Problem setup
H = 4
W = 3
L = 6
h = 0.1
wL = 0.01
heater_a = 5
heater_b = 30
ambient_temperature = 25

# Number of unknowns
nw = int(W / h) - 1
nl = int(L / h) - 1
nh = int(H / h) - 1

N = nh * nv * nl

# We define a function to convert the indices from i,j,k to p and viceversa
# i,j,k indexes the discrete domain in 3D.
# p parametrize those i,j,k, this way we can tidy the unknowns
# in a column vector and use the standard algebra

def getP(i,j,k):
    return k*nl*nv + j*nv + i

def getIJK(p):
    i = p % nv
    k = (p // nv) // nl
    j = (p - k*nl*nv - i)/nv 
    
    return (i, j, k)

# Matriz Sparse
A = csc_matrix((N,N))

# In this vector we will write all the right side of the equations
b = np.zeros((N,))

# Note: To write an equation is equivalent to write a row in the matrix system

# We iterate over each point inside the domain
# Each point has an equation associated
# The equation is different depending on the point location inside the domain
for i in range(0, nw):
    for j in range(0, nl):
        for k in range(0,nh):
            # We will write the equation associated with row k
            p = getP(i,j,k)
            
            # We obtain indices of the other coefficients
            p_up = getP(i, j, k+1)
            p_down = getP(i, j, k-1)
            p_left = getP(i-1, j, k)
            p_right = getP(i+1, j, k)
            p_near = getP(i, j-1, k)
            p_far = getP(i, j+1, k)
            
            # Depending on the location of the point, the equation is different
            # Interior
            if 1 <= i and i <= nw - 2 and 1 <= j and j <= nl - 2 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = 0
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        