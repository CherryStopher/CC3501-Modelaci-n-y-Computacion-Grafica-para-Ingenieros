# -*- coding: utf-8 -*-
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import json

import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import lighting_shaders as ls
import scene_graph as sg

import random

def jsonDict(filename):
    with open(filename) as file:
        data = json.load(file)
        return data

dim = jsonDict('problem-setup.json')
# Problem setup
H = int(dim["height"])
W = int(dim["width"])
L = int(dim["lenght"])


archivo = sys.argv[1]

num = jsonDict(archivo)

t_a = int(num['t_a'])
t_b = int(num["t_b"])
t_c = int(num["t_c"])
n_a = int(num["n_a"])
n_b = int(num["n_b"])
n_c = int(num["n_c"])
filename = num["filename"]

"""
t_a = 15
t_b = 10
t_c = 25
n_a = 5
n_b = 3
n_c = 7
"""


def createFish(r,g,b):
    gpuNaranjo = es.toGPUShape(bs.createColorNormalsCube(r,g,b))
    gpuNegro = es.toGPUShape(bs.createColorNormalsCube(0, 0, 0))
    
    
    # Cola 1
    cola1 = sg.SceneGraphNode("cola1")
    cola1.transform = tr.matmul([tr.translate(0, 0, 0.5), tr.shearing(0, 0, 0.7, 0, 0, 0)])
    cola1.childs += [gpuNaranjo]
   
    # Cola 2
    cola2 = sg.SceneGraphNode("cola1")
    cola2.transform = tr.rotationX(np.pi)
    cola2.childs += [cola1]
    
    # Cola
    cola = sg.SceneGraphNode("cola")
    cola.transform = tr.matmul([tr.translate(1, 0, 0),tr.scale(0.6, 0.3, 0.4)])
    cola.childs += [cola1, cola2]
    
    # Cola Final
    colaFinal = sg.SceneGraphNode("colaFinal")
    colaFinal.transform = tr.scale(1, 0.5, 1)
    colaFinal.childs += [cola]
    
    # Cuerpo1
    cuerpo1 = sg.SceneGraphNode("cuerpo1")
    cuerpo1.transform = tr.matmul([tr.translate(-1.7, 0, 0), tr.uniformScale(1.4)])
    cuerpo1.childs += [cola]
    
    # Cuerpo2
    cuerpo2 = sg.SceneGraphNode("cuerpo2")
    cuerpo2.transform = tr.matmul([tr.rotationZ(np.pi)])
    cuerpo2.childs += [cuerpo1]
    
    # Cuerpo3
    cuerpo3 = sg.SceneGraphNode("cuerpo3")
    cuerpo3.transform = tr.uniformScale(0.42)
    cuerpo3.childs += [gpuNaranjo]
    
    # Cuerpo
    cuerpo = sg.SceneGraphNode("cuerpo")
    cuerpo.transform = tr.translate(-0.4, 0, 0)
    cuerpo.childs += [cuerpo1, cuerpo2, cuerpo3]
    
    # Ojos
    ojos = sg.SceneGraphNode("ojos")
    ojos.transform = tr.matmul([tr.translate(-1, 0, 0), tr.scale(0.1, 0.5, 0.1)])
    ojos.childs += [gpuNegro]
    
    # Aleta Superior
    aletaTop = sg.SceneGraphNode("aletaTop")
    aletaTop.transform = tr.matmul([tr.translate(-0.3, 0, 0.5), tr.scale(0.6, 0.1, 0.4)])
    aletaTop.childs += [cola1]
    
    # Aleta Inferior
    aletaBot = sg.SceneGraphNode("aletaBot")
    aletaBot.transform = tr.rotationX(np.pi)
    aletaBot.childs += [aletaTop]
    
    # Pez
    pez = sg.SceneGraphNode("pez")
    pez.transform = tr.uniformScale(0.7)
    pez.childs += [colaFinal, cuerpo, ojos, aletaTop, aletaBot]
    
    return pez


# Función que dibuja los peces moviendose
def drawMovementFish(gpu,theta, posX, posY, posZ, lightingPipeline, scala=0.5):
    

    # Moviendo la cola
    cola = sg.findNode(gpu, "colaFinal")
    cola.transform = tr.matmul([tr.rotationZ(0.3*np.cos(4*theta)), tr.scale(1, 0.5, 1)])
    
    #Moviéndose a través del espacio
    pez = sg.findNode(gpu, "pez")
    
    rot = 10 * (posX+posY+posZ)


    if theta%(2*np.pi) < 3.0:
        reflex = tr.identity()
    else:
        reflex = tr.scale(-1, 1, 1)
    
    pez.transform = tr.matmul([ tr.translate(posX-2, posY-3, posZ),reflex, tr.rotationZ(rot), tr.uniformScale(0.2)])
    
    # Drawing
    sg.drawSceneGraphNode(gpu, lightingPipeline, "model")
    
    
    
def createColorCube(i, j, k, X, Y, Z ,c):
    l_x = X[i, j, k]
    r_x = X[i+1, j, k]
    b_y = Y[i, j, k]
    f_y = Y[i, j+1, k]
    b_z = Z[i, j, k]
    t_z = Z[i, j, k+1]

    #   positions    colors
    vertices = [
    # Z+: number 1
        l_x, b_y,  t_z, c[0],c[1],c[2],
         r_x, b_y,  t_z, c[0],c[1],c[2],
         r_x,  f_y,  t_z, c[0],c[1],c[2],
        l_x,  f_y,  t_z, c[0],c[1],c[2],
    # Z-: number 6
        l_x, b_y, b_z, c[0],c[1],c[2],
         r_x, b_y, b_z, c[0],c[1],c[2],
         r_x,  f_y, b_z, c[0],c[1],c[2],
        l_x,  f_y, b_z, c[0],c[1],c[2],
    # X+: number 5
         r_x, b_y, b_z, c[0],c[1],c[2],
         r_x,  f_y, b_z, c[0],c[1],c[2],
         r_x,  f_y,  t_z, c[0],c[1],c[2],
         r_x, b_y,  t_z, c[0],c[1],c[2],
    # X-: number 2
        l_x, b_y, b_z, c[0],c[1],c[2],
        l_x,  f_y, b_z, c[0],c[1],c[2],
        l_x,  f_y,  t_z, c[0],c[1],c[2],
        l_x, b_y,  t_z, c[0],c[1],c[2],
    # Y+: number 4
        l_x,  f_y, b_z, c[0],c[1],c[2],
        r_x,  f_y, b_z, c[0],c[1],c[2],
        r_x,  f_y, t_z, c[0],c[1],c[2],
        l_x,  f_y, t_z, c[0],c[1],c[2],
    # Y-: number 3
        l_x, b_y, b_z, c[0],c[1],c[2],
        r_x, b_y, b_z, c[0],c[1],c[2],
        r_x, b_y, t_z, c[0],c[1],c[2],
        l_x, b_y, t_z, c[0],c[1],c[2],
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
        4, 5, 1, 1, 0, 4,
        6, 7, 3, 3, 2, 6,
        5, 6, 2, 2, 1, 5,
        7, 4, 0, 0, 3, 7]

    return bs.Shape(vertices, indices)

def merge(destinationShape, strideSize, sourceShape):

    # current vertices are an offset for indices refering to vertices of the new shape
    offset = len(destinationShape.vertices)
    destinationShape.vertices += sourceShape.vertices
    destinationShape.indices += [(offset/strideSize) + index for index in sourceShape.indices]


    
# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.mousePos = (0.0, 0.0)
        self.voxel1 = False
        self.voxel2 = False
        self.voxel3 = False
        self.zoom = 2


# We will use the global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller
    
    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        sys.exit()
    
    elif key == glfw.KEY_A:
        controller.voxel1 = not controller.voxel1
    
    elif key == glfw.KEY_B:
        controller.voxel2 = not controller.voxel2
        
    elif key == glfw.KEY_C:
        controller.voxel3 = not controller.voxel3
    
def createBordePecera():
    gpuNegro = es.toGPUShape(bs.createColorNormalsCube(0, 0, 0))


    
    # Borde Horizontal
    bordeH = sg.SceneGraphNode("bordeH")
    bordeH.transform = tr.scale(1, 0.02, 0.02)
    bordeH.childs += [gpuNegro] 
    
    
    # Borde H1
    bordeH1 = sg.SceneGraphNode("bordeH1")
    bordeH1.transform = tr.translate(0, -0.5, 0.5)
    bordeH1.childs += [bordeH]  
    
    # Borde H2
    bordeH2 = sg.SceneGraphNode("bordeH2")
    bordeH2.transform = tr.translate(0, 0.5, 0.5)
    bordeH2.childs += [bordeH]  
    
    # Borde H3
    bordeH3 = sg.SceneGraphNode("bordeH3")
    bordeH3.transform = tr.translate(0, 0.5, -0.5)
    bordeH3.childs += [bordeH] 
    
    # Borde H4
    bordeH4 = sg.SceneGraphNode("bordeH4")
    bordeH4.transform = tr.translate(0, -0.5, -0.5)
    bordeH4.childs += [bordeH]  
    
    
    
    # Borde Horizontal_2
    bordeH_2 = sg.SceneGraphNode("bordeH_2")
    bordeH_2.transform = tr.rotationZ(np.pi/2)
    bordeH_2.childs += [bordeH] 
    
    # Borde H21
    bordeH21 = sg.SceneGraphNode("bordeH21")
    bordeH21.transform = tr.translate(-0.5, 0, 0.5)
    bordeH21.childs += [bordeH_2]  
    
    # Borde H22
    bordeH22 = sg.SceneGraphNode("bordeH22")
    bordeH22.transform = tr.translate(0.5, 0, 0.5)
    bordeH22.childs += [bordeH_2]  
    
    # Borde H23
    bordeH23 = sg.SceneGraphNode("bordeH23")
    bordeH23.transform = tr.translate(0.5, 0, -0.5)
    bordeH23.childs += [bordeH_2] 
    
    # Borde H24
    bordeH24 = sg.SceneGraphNode("bordeH24")
    bordeH24.transform = tr.translate(-0.5, 0, -0.5)
    bordeH24.childs += [bordeH_2]  
    
    
    
  
    # Borde Vertical
    bordeV = sg.SceneGraphNode("bordeV")
    bordeV.transform = tr.scale(0.02, 0.02, 1)
    bordeV.childs += [gpuNegro]  
    
    # Borde V1
    bordeV1 = sg.SceneGraphNode("bordeV1")
    bordeV1.transform = tr.translate(-0.5, -0.5, 0)
    bordeV1.childs += [bordeV]
    
    # Borde V2
    bordeV2 = sg.SceneGraphNode("bordeV2")
    bordeV2.transform = tr.translate(0.5, -0.5, 0)
    bordeV2.childs += [bordeV]
    
    # Borde V3
    bordeV3 = sg.SceneGraphNode("bordeV3")
    bordeV3.transform = tr.translate(-0.5, 0.5, 0)
    bordeV3.childs += [bordeV]
    
    # Borde V4
    bordeV4 = sg.SceneGraphNode("bordeV4")
    bordeV4.transform = tr.translate(0.5, 0.5, 0)
    bordeV4.childs += [bordeV]
    
    
    
    bordes = sg.SceneGraphNode("bordes")
    bordes.childs += [bordeH1, bordeH2, bordeH3, bordeH4,
                      bordeH21, bordeH22, bordeH23, bordeH24,
                      bordeV1, bordeV2, bordeV3, bordeV4]  
    
    return bordes
    
    
def cursor_pos_callback(window, x, y):
    global controller
    controller.mousePos = (x,y)





if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1000
    height = 1000

    window = glfw.create_window(width, height, "Pecesitos hermosos UwU", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    pipeline = es.SimpleModelViewProjectionShaderProgram2()  
    pipelineNormal = es.SimpleModelViewProjectionShaderProgram()  
    lightingPipeline = ls.SimplePhongShaderProgram()
    
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    

    # Creating shapes on GPU memory
    
    
    gpuAxis = es.toGPUShape(bs.createAxis(7))
    
    # Visualizar los voxeles
    load_voxels = np.load(filename)
    X, Y, Z = np.mgrid[0:W:11j, 0:L:21j, 0:H:14j]

    
    isosurface1 = bs.Shape([], [])
    isosurface2 = bs.Shape([], [])
    isosurface3 = bs.Shape([], [])
    # Now let's draw voxels!
    for i in range(X.shape[0]-1):
        for j in range(X.shape[1]-1):
            for k in range(X.shape[2]-1):
                #print(X[i,j,k])
                if load_voxels[i,j,k] >= t_a -2 and load_voxels[i,j,k] <= t_a +2:
                    temp_shape = createColorCube(i,j,k, X,Y, Z, [1, 100/255, 0])
                    merge(destinationShape=isosurface1, strideSize=6, sourceShape=temp_shape)
                
                if load_voxels[i,j,k] >= t_b -2 and load_voxels[i,j,k] <= t_b +2:
                    temp_shape = createColorCube(i,j,k, X,Y, Z, [129/255, 2, 27/255])
                    merge(destinationShape=isosurface2, strideSize=6, sourceShape=temp_shape)
                    
                if load_voxels[i,j,k] >= t_c -2 and load_voxels[i,j,k] <= t_c +2:
                    temp_shape = createColorCube(i,j,k, X,Y, Z, [0, 100/255, 1])
                    merge(destinationShape=isosurface3, strideSize=6, sourceShape=temp_shape)
    

    
    gpu_surface1 = es.toGPUShape(isosurface1)
    gpu_surface2 = es.toGPUShape(isosurface2)
    gpu_surface3 = es.toGPUShape(isosurface3)
    
    
    

    gpuPecera = es.toGPUShape(bs.createColorCube(0.0, 0.7, 0.7))
    gpuLineas = es.toGPUShape(bs.createColorCube(0, 0, 0))
    gpuBordes = createBordePecera()
    
    gpuFondo=es.toGPUShape(bs.createTextureCube("fondo.png"), GL_REPEAT, GL_LINEAR)
    gpuTecho=es.toGPUShape(bs.createTextureQuad("techo.png"), GL_REPEAT, GL_LINEAR)
    gpuSuelo=es.toGPUShape(bs.createTextureQuad("suelo.png"), GL_REPEAT, GL_LINEAR)
    
    
    gpuAxis = es.toGPUShape(bs.createAxis(4))
    
    t0 = glfw.get_time()
    camera_theta = np.pi/4
    
    # Peces
    
    #Tipo A
    A = isosurface1.vertices

    pezLocA = []
    pezPosA = []
    pecesA = []
    
    for i in range(0, len(A), 6):
        pos = (A[i], A[i+1], A[i+2])
        pezLocA += [pos]
    
    for i in range(n_a):
        pez = createFish(1, 0, 0)
        pecesA += [pez]
        
        pezPosA += [random.choice(pezLocA)]
    
    #Tipo B
    B = isosurface2.vertices
    pezLocB = []
    pezPosB = []
    pecesB = []
    
    for i in range(0, len(B), 6):
        pos = (B[i], B[i+1], B[i+2])
        pezLocB += [pos]
    
    for i in range(n_b):
        pez = createFish(0, 1, 0)
        pecesB += [pez]
        
        pezPosB += [random.choice(pezLocB)]
        
        
    #Tipo C
    C = isosurface3.vertices
    pezLocC = []
    pezPosC = []
    pecesC = []
    
    for i in range(0, len(C), 6):
        pos = (C[i], C[i+1], C[i+2])
        pezLocC += [pos]
    
    for i in range(n_c):
        pez = createFish(0, 130/255, 1)
        pecesC += [pez]
        
        pezPosC += [random.choice(pezLocC)]
        
        
    
    
    

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta += 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta -= 2* dt
            
        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            controller.zoom += 0.05
            
        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            if controller.zoom >= 1:
                controller.zoom -= 0.05


        projection = tr.perspective(45, float(width)/float(height), 0.1, 200)

        camX = -5 * controller.zoom * np.sin(camera_theta)
        camY = -5 * controller.zoom* np.cos(camera_theta)
        camZ = 4

        viewPos = np.array([camX,camY,camZ])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,1]),
            np.array([0,0,1])
        )

        rotation_theta = glfw.get_time()
        
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        axis = np.array([1,-1,1])
        axis = axis / np.linalg.norm(axis)
        model = tr.rotationA(rotation_theta, axis)
        model = tr.identity()
        


        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            
            
        
        
        # Dibujando el fondo
        escala = 100
        textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()

        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(escala))
        textureShaderProgram.drawShape(gpuFondo)
        
        cieloTransf = tr.matmul([tr.translate(0, 0, escala/2-10), tr.uniformScale(escala)])
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, cieloTransf)
        textureShaderProgram.drawShape(gpuTecho)
        
        lagoTransf = tr.matmul([tr.translate(0, 0, -escala/2+10), tr.uniformScale(escala)])
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, lagoTransf)
        textureShaderProgram.drawShape(gpuSuelo)
            
        
        glUseProgram(lightingPipeline.shaderProgram)
        
        
        
        # Setting all uniform shader variables
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 0.2, 0.2, 0.2)


        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), -5, -5, 5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 30)
        
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)
        
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        

        # Drawing
        # Peces
        transf2 = tr.matmul([tr.translate(-0.5,0,2),tr.scale(3.5,6.5,4.5)])
        sg.drawSceneGraphNode(gpuBordes, lightingPipeline, "model", transf2)
        
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        # Peces A
        
        for i in range(n_a):
            gpuPez = pecesA[i]
            posPez = pezPosA[i]
            drawMovementFish(gpuPez, t0*(i+1), posPez[0], posPez[1], posPez[2], lightingPipeline)
                
        
        # Peces B
        
        for i in range(n_b):
            gpuPez = pecesB[i]
            posPez = pezPosB[i]
            drawMovementFish(gpuPez, t0*(i+1), posPez[0], posPez[1], posPez[2], lightingPipeline)
                
            
        # Peces C
        
        for i in range(n_c):
            gpuPez = pecesC[i]
            posPez = pezPosC[i]
            drawMovementFish(gpuPez, t0*(i+1), posPez[0], posPez[1], posPez[2], lightingPipeline)    
            
            
        
                

        
        glUseProgram(pipeline.shaderProgram)
        
        
        # Voxeles

        transf = tr.matmul([tr.translate(-2,-3,0),tr.uniformScale(1)])
               
        transf2 = tr.matmul([tr.translate(-0.5,0,2),tr.scale(3.5,6.5,4.5)])
        
        
        
        
        
        if controller.voxel2 == True:
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, transf)
            
            pipeline.drawShape(gpu_surface2)
       
        
        if controller.voxel1 == True:
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, transf)
            pipeline.drawShape(gpu_surface1)
            
            
            
        if controller.voxel3 == True:
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, transf)
            
            pipeline.drawShape(gpu_surface3) 
            
          
        # Pecera    
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, transf2)
        pipeline.drawShape(gpuPecera)
        
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, transf2)
        pipeline.drawShape(gpuLineas, GL_LINES)
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
