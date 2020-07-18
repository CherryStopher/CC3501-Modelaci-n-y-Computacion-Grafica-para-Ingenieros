# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as mpl
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve

# Problem setup
H = 4
W = 3
L = 6
h = 0.5
wL = 0.01
heater_a = 5
heater_b = 30
ambient_temperature = 25

# Number of unknowns
nv = int(W / h) - 1
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
for i in range(0, nv):
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
            if 1 <= i and i <= nv - 2 and 1 <= j and j <= nl - 2 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = 0
            
            # left side
            elif i == 0 and 1 <= j and j <= nl - 2 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = 2 * h * wL
                
            # right side
            elif i == nv - 1 and 1 <= j and j <= nl - 2 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = -2 * h * wL
                
            # near side
            elif 1 <= i and i <= nv - 2 and j == 0 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = 2 * h * wL
                
                
            # far side
            elif 1 <= i and i <= nv - 2 and j == nl - 1 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -2 * h * wL
            
            # bottom side
            elif 1 <= i and i <= nv - 2 and 1 <= j and j <= nl - 2 and k == 0:
                A[p, p_up] = 2
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = 0
                
            # top side
            elif 1 <= i and i <= nv - 2 and 1 <= j and j <= nl - 2 and k == nh - 1:
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_right] = 1
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = -ambient_temperature
                
            # corner 
                
                
            # corner lower left near
            elif (i, j, k) == (0, 0, 0):
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = 2 * h * wL + 2 * h * wL
                
            # corner lower left far
            elif (i, j, k) == (0, nl-1, 0):
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -2 * h * wL + 2 * h * wL
                
            # corner top left near
            elif (i, j, k) == (0, 0, nh-1):
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -ambient_temperature + 2 * h * wL + 2 * h * wL
                
            # corner top left far
            elif (i, j, k) == (0, nl-1, nh-1):
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -ambient_temperature + 2 * h * wL - 2 * h * wL
                
            # corner lower right near
            elif (i, j, k) == (nv-1, 0, 0):
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = 2 * h * wL - 2 * h * wL
                
            # corner lower right far
            elif (i, j, k) == (nv-1, nl-1, 0):
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -2 * h * wL - 2 * h * wL
                
            # corner top right near
            elif (i, j, k) == (nv-1, 0, nh-1):
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -ambient_temperature + 2 * h * wL - 2 * h * wL
                
            # corner top right far
            elif (i, j, k) == (nv-1, nl-1, nh-1):
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -ambient_temperature - 2 * h * wL - 2 * h * wL    
            
            # corner top left
            elif i == 0  and 1 <= j and j <= nl - 2 and k == nh - 1:
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = -ambient_temperature + 2 * h * wL
                
            # corner bot left
            elif i == 0  and 1 <= j and j <= nl - 2 and k == 0:
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = 2 * h * wL
                
            # corner bot right
            elif i == nv - 1  and 1 <= j and j <= nl - 2 and k == 0:
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = -2 * h * wL
                
            # corner top right
            elif i == nv - 1  and 1 <= j and j <= nl - 2 and k == nh - 1:
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = -ambient_temperatur -2 * h * wL
                
            # corner top near
        elif 1 <= i and i <= nv - 2  and j == 0 and k = nh - 1:
                A[p, p_down] = 1
                A[p, p_left] = 1
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = -ambient_temperatur -2 * h * wL
            
                
            else:
                print("Point (" + str(i) + ", " + str(j) + ") missed!")
                print("Associated point index is " + str(k))
                raise Exception()
            
            
        
        
        
# Solving our system
x = spsolve(A, b)

ux = []
uy = []
uz = []
uc = []

for p in range(0,N):
    i,j,k = getIJK(p)
    uc += [int(x[p])]
    ux += [i]
    uy += [j]
    uz += [k]

from mpl_toolkits import mplot3d 
import matplotlib.pyplot as plt

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.scatter(ux, uy, uz, c=uc,
           cmap='viridis', linewidth=0.5)
plt.show()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        