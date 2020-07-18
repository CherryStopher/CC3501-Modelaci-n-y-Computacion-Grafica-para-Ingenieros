# -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as mpl
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve

# Problem setup
H = 4
W = 3
h = 0.1
window_loss = 10

heater_a = 5
heater_b = 30
ambient_temperature = 25
aislant_temperature = 0


# Number of unknowns
# left, bottom and top sides are known (Dirichlet condition)
# right side is unknown (Neumann condition)
nh = int(W / h) - 1
nv = int(H / h) - 1

# In this case, the domain is just a rectangle
N = nh * nv


# We define a function to convert the indices from i,j to k and viceversa
# i,j indexes the discrete domain in 2D.
# k parametrize those i,j, this way we can tidy the unknowns
# in a column vector and use the standard algebra

def getK(i,j):
    return j * nh + i

def getIJ(k):
    i = k % nh
    j = k // nh
    return (i, j)

#def getIJH():
    


# Matriz Sparse

A = csc_matrix((N,N))


# In this vector we will write all the right side of the equations
b = np.zeros((N,))

# Note: To write an equation is equivalent to write a row in the matrix system

# We iterate over each point inside the domain
# Each point has an equation associated
# The equation is different depending on the point location inside the domain
for i in range(0, nh):
    for j in range(0, nv):

        # We will write the equation associated with row k
        k = getK(i,j)

        # We obtain indices of the other coefficients
        k_up = getK(i, j+1)
        k_down = getK(i, j-1)
        k_left = getK(i-1, j)
        k_right = getK(i+1, j)

        # Depending on the location of the point, the equation is different
        # Interior
        if 1 <= i and i <= nh - 2 and 1 <= j and j <= nv - 2:
            A[k, k_up] = 1
            A[k, k_down] = 1
            A[k, k_left] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = 0
        
        # left side
        elif i == 0 and 1 <= j and j <= nv - 2:
            A[k, k_up] = 1
            A[k, k_down] = 1
            A[k, k_right] = 2
            A[k, k] = -4
            b[k] = 2 * h * window_loss
        
        # right side
        elif i == nh - 1 and 1 <= j and j <= nv - 2:
            A[k, k_up] = 1
            A[k, k_down] = 1
            A[k, k_left] = 2
            A[k, k] = -4
            b[k] = -2 * h * window_loss
        
        # bottom side
        elif 1 <= i and i <= nh - 2 and j == 0:
            A[k, k_up] = 2
            A[k, k_left] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = 2 * h * aislant_temperature
        
        # top side
        elif 1 <= i and i <= nh - 2 and j == nv - 1:
            A[k, k_down] = 1
            A[k, k_left] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = - ambient_temperature

        # corner lower left
        elif (i, j) == (0, 0):
            A[k, k_up] = 2
            A[k, k_right] = 2
            A[k, k] = -4
            b[k] = 2 * h * aislant_temperature + 2 * h * window_loss

        # corner lower right
        elif (i, j) == (nh - 1, 0):
            A[k, k_up] = 2
            A[k, k_left] = 2
            A[k, k] = -4
            b[k] = 2 * h * aislant_temperature - 2 * h * window_loss

        # corner upper left
        elif (i, j) == (0, nv - 1):
            A[k, k_down] = 2
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = -ambient_temperature + 2 * h * window_loss

        # corner upper right
        elif (i, j) == (nh - 1, nv - 1):
            A[k, k_down] = 1
            A[k, k_left] = 2
            A[k, k] = -4
            b[k] =  -ambient_temperature - 2 * h * window_loss
            
    
        else:
            print("Point (" + str(i) + ", " + str(j) + ") missed!")
            print("Associated point index is " + str(k))
            raise Exception()


# Reguladores
for i in range(0, nh):
    for j in range(0, nv):

        # We will write the equation associated with row k
        k = getK(i,j)

        # We obtain indices of the other coefficients
        k_up = getK(i, j+1)
        k_down = getK(i, j-1)
        k_left = getK(i-1, j)
        k_right = getK(i+1, j)

        # Depending on the location of the point, the equation is different
        # Interior
        if 1 <= i and i <= nh - 2 and 1 <= j and j <= nv - 2:
            A[k, k_up] = 1
            A[k, k_down] = 1
            A[k, k_left] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = 0
        
        # left side
        elif i == 0 and 1 <= j and j <= nv - 2:
            A[k, k_up] = 1
            A[k, k_down] = 1
            A[k, k_right] = 2
            A[k, k] = -4
            b[k] = 2 * h * window_loss
        
        # right side
        elif i == nh - 1 and 1 <= j and j <= nv - 2:
            A[k, k_up] = 1
            A[k, k_down] = 1
            A[k, k_left] = 2
            A[k, k] = -4
            b[k] = -2 * h * window_loss
        
        # bottom side
        elif 1 <= i and i <= nh - 2 and j == 0:
            A[k, k_up] = 2
            A[k, k_left] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = 2 * h * aislant_temperature
        
        # top side
        elif 1 <= i and i <= nh - 2 and j == nv - 1:
            A[k, k_down] = 1
            A[k, k_left] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = - ambient_temperature

        # corner lower left
        elif (i, j) == (0, 0):
            A[k, k_up] = 2
            A[k, k_right] = 2
            A[k, k] = -4
            b[k] = 2 * h * aislant_temperature + 2 * h * window_loss

        # corner lower right
        elif (i, j) == (nh - 1, 0):
            A[k, k_up] = 2
            A[k, k_left] = 2
            A[k, k] = -4
            b[k] = 2 * h * aislant_temperature - 2 * h * window_loss

        # corner upper left
        elif (i, j) == (0, nv - 1):
            A[k, k_down] = 2
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = -ambient_temperature + 2 * h * window_loss

        # corner upper right
        elif (i, j) == (nh - 1, nv - 1):
            A[k, k_down] = 1
            A[k, k_left] = 2
            A[k, k] = -4
            b[k] =  -ambient_temperature - 2 * h * window_loss
            
    
        else:
            print("Point (" + str(i) + ", " + str(j) + ") missed!")
            print("Associated point index is " + str(k))
            raise Exception()            

# A quick view of a sparse matrix
#mpl.spy(A)

# Solving our system

#S = A.todense()

#x = np.linalg.solve(S, b)

x = spsolve(A, b)

# Now we return our solution to the 2d discrete domain
# In this matrix we will store the solution in the 2d domain
u = np.zeros((nh,nv))

for k in range(0, N):
    i, j = getIJ(k)
    u[i,j] = x[k]

# Adding the borders, as they have known values
ub = np.zeros((nh + 2, nv + 2))
ub[1:nh + 1, 1:nv + 1] = u[:,:]

# Dirichlet boundary condition
# top 
ub[0:nh + 2, nv + 1] = ambient_temperature


# this visualization locates the (0,0) at the lower left corner
# given all the references used in this example.
# The K indices worked with numpy start at the top left corner, so the solution
# is to transpose the matrix.
fig, axs = mpl.subplots(ncols=1, nrows=2, figsize=(3, 5))

# Color Mesh
axs[0].set_title('Laplace equation solution with colormesh')
axs[0].pcolormesh(ub.T, cmap='RdBu_r')
axs[0].set_xlabel('x')
axs[0].set_ylabel('y')

# Contour
axs[1].contour(ub.T, 60, cmap='RdBu_r')
axs[1].set_xlabel('x')
axs[1].set_ylabel('y')
mpl.show()
"""

# Graph in 3D 
# 3D
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
from matplotlib import cm
# Make data.
X = np.arange(0, ub.shape[0], 1, dtype=int)
Y = np.arange(0, ub.shape[1], 1, dtype=int)
X, Y = np.meshgrid(X, Y)

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_title('Poisson equation solution with a surface')
ax.set_xlabel('x')
ax.set_ylabel('y')

ax.set_zlabel('Value of U(x,y)')

# Plot the surface.
surf = ax.plot_surface(X, Y, ub.T, cmap=cm.coolwarm,
                       linewidth=0, antialiased=True)

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()
"""