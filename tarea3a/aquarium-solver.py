# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as mpl
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve
import json
import sys

def jsonDict(filename):
    with open(filename) as file:
        data = json.load(file)
        return data
    
archivo = sys.argv[1]

dim = jsonDict(archivo)

# Problem setup
H = int(dim["height"])
W = int(dim["width"])
L = int(dim["lenght" ])
h = 0.3
wL = float(dim["window_loss"])
heater_a = int(dim["heater_a"])
heater_b = int(dim["heater_b"])
ambient_temperature = int(dim["ambient_temperature"])
filename = dim["filename"]

# Number of unknowns
nv = int(W / h) + 1
nl = int(L / h) + 1
nh = int(H / h) 

N = nh * nv * nl

# We define a function to convert the indices from i,j,k to p and viceversa
# i,j,k indexes the discrete domain in 3D.
# p parametrize those i,j,k, this way we can tidy the unknowns
# in a column vector and use the standard algebra

def getP(i,j,k):
    return k*nl*nv + j*nv + i

def getIJK(p):
    i = int(p % nv)
    k = int((p // nv) // nl)
    j = int((p - k*nl*nv - i)/nv) 
    
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
            
            # Calentador A
            elif  i >= nv//3 and i <= 2*nv//3 and j >= 3*nl//5 and j <= 4*nl//5 and k == 0:
                A[p, p_up] = 0
                A[p, p_left] = 0
                A[p, p_right] = 0
                A[p, p_near] = 0
                A[p, p_far] = 0
                A[p, p] = 1
                b[p] = heater_a
                
            # Calentador B
            elif  i >= nv//3 and i <= 2*nv//3 and j >= nl//5 and j <= 2*nl//5 and k == 0:
                A[p, p_up] = 0
                A[p, p_left] = 0
                A[p, p_right] = 0
                A[p, p_near] = 0
                A[p, p_far] = 0
                A[p, p] = 1
                b[p] = heater_b
            
            # left side
            elif i == 0 and 1 <= j and j <= nl - 2 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = -2 * h * wL
                
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
                b[p] = -2 * h * wL
                
                
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
                b[p] = -2 * h * wL - 2 * h * wL
                
            # corner lower left far
            elif (i, j, k) == (0, nl-1, 0):
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -2 * h * wL - 2 * h * wL
                
            # corner top left near
            elif (i, j, k) == (0, 0, nh-1):
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -ambient_temperature - 2 * h * wL - 2 * h * wL
                
            # corner top left far
            elif (i, j, k) == (0, nl-1, nh-1):
                A[p, p_down] = 1
                A[p, p_right] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -ambient_temperature - 2 * h * wL - 2 * h * wL
                
            # corner lower right near
            elif (i, j, k) == (nv-1, 0, 0):
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = - 2 * h * wL - 2 * h * wL
                
            # corner lower right far
            elif (i, j, k) == (nv-1, nl-1, 0):
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = - 2 * h * wL - 2 * h * wL
                
            # corner top right near
            elif (i, j, k) == (nv-1, 0, nh-1):
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -ambient_temperature - 2 * h * wL - 2 * h * wL
                
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
                b[p] = -ambient_temperature - 2 * h * wL
                
            # corner bot left
            elif i == 0  and 1 <= j and j <= nl - 2 and k == 0:
                A[p, p_up] = 2
                A[p, p_right] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = - 2 * h * wL
                
            # corner bot right
            elif i == nv - 1  and 1 <= j and j <= nl - 2 and k == 0:
                A[p, p_up] = 2
                A[p, p_left] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = - 2 * h * wL
                
            # corner top right
            elif i == nv - 1  and 1 <= j and j <= nl - 2 and k == nh - 1:
                A[p, p_down] = 1
                A[p, p_left] = 2
                A[p, p_near] = 1
                A[p, p_far] = 1
                A[p, p] = -6
                b[p] = -ambient_temperature -2 * h * wL
                
            # corner top near
            elif 1 <= i and i <= nv - 2  and j == 0 and k == nh - 1:
                A[p, p_down] = 1
                A[p, p_right] = 1
                A[p, p_left] = 1
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = -ambient_temperature - 2 * h * wL
            
            # corner top far
            elif 1 <= i and i <= nv - 2  and j == nl - 1 and k == nh - 1:
                A[p, p_down] = 1
                A[p, p_right] = 1
                A[p, p_left] = 1
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = -ambient_temperature - 2 * h * wL
            
            # corner bot near
            elif 1 <= i and i <= nv - 2  and j == 0 and k == 0:
                A[p, p_up] = 2
                A[p, p_right] = 1
                A[p, p_left] = 1
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = - 2 * h * wL
            
            # corner bot far
            elif 1 <= i and i <= nv - 2  and j == nl - 1 and k == 0:
                A[p, p_up] = 2
                A[p, p_right] = 1
                A[p, p_left] = 1
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = - 2 * h * wL
                
            # corner left near
            elif i == 0 and j == 0 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_right] = 2
                A[p, p_down] = 1
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = - 2 * h * wL - 2 * h * wL
                
            # corner left far
            elif i == 0 and j == nl - 1 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_right] = 2
                A[p, p_down] = 1
                A[p, p_near] = 2
                A[p, p] = -6
                b[p] = - 2 * h * wL - 2 * h * wL
                
            # corner right near
            elif i == nv - 1 and j == 0 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_left] = 2
                A[p, p_down] = 1
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = - 2 * h * wL - 2 * h * wL
                
            # corner right far
            elif i == nv - 1 and j == nl - 1 and 1 <= k and k <= nh - 2:
                A[p, p_up] = 1
                A[p, p_left] = 2
                A[p, p_down] = 1
                A[p, p_far] = 2
                A[p, p] = -6
                b[p] = - 2 * h * wL - 2 * h * wL
                
            else:
                print("Point (" + str(i) + ", " + str(j) + ") missed!")
                print("Associated point index is " + str(k))
                raise Exception()
            
            
        
      
# Solving our system
x = spsolve(A, b)

     
u = np.zeros((nv,nl,nh))

for p in range(0, N):
    i,j,k = getIJK(p)
    u[i, j, k] = x[p]        

# Adding the borders, as they have known values
ub = np.zeros((nv, nl, nh+1))
ub[0:nv, 0:nl, 0:nh] = u[:,:,:]
# Dirichlet boundary condition
# top 
ub[0:nv, 0:nl, nh] = ambient_temperature

# Guardando la matriz
np.save(filename, ub)


# Plot
"""
X, Y, Z = np.mgrid[0:W:11j, 0:L:21j, 0:H:14j]

from mpl_toolkits import mplot3d 
import matplotlib.pyplot as plt
        
fig = plt.figure()
ax = plt.axes(projection='3d')

surf=ax.scatter(X, Y, Z, c=ub, cmap='winter',
            linewidth=0.5, marker="o", alpha=1, edgecolor="k")

fig.colorbar(surf, shrink=0.8, aspect=6)

ax.set_title('Preview')
ax.set_xlabel("Width")
ax.set_ylabel("Length")
ax.set_zlabel("Hight")

plt.show()
"""
        
        
   
   
        
        
        
        
        
        
        