# -*- coding: utf-8 -*-
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import lighting_shaders as ls
import scene_graph as sg

from bird import *

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.mousePos = (0.0, 0.0)


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
        
def cursor_pos_callback(window, x, y):
    global controller
    controller.mousePos = (x,y)

def drawMovementBird(gpu,theta, lightingPipeline, posX, posY, posZ, scala=0.5):
    # Moviendo partes del cuerpo
    alaIzqNodo = sg.findNode(gpu, "alaIzq")
    alaIzqNodo.transform = tr.matmul([tr.rotationX(-0.5*np.cos(theta)), tr.translate(0.1, -0.55, 0.1), tr.scale(0.5, 0.7, 0.1)])
        
    alaDerNodo = sg.findNode(gpu, "alaDer")
    alaDerNodo.transform = tr.matmul([tr.rotationX(0.5*np.cos(theta)), tr.translate(0.1, 0.55, 0.1), tr.scale(0.5, 0.7, 0.1)])
        
    colaNodo = sg.findNode(gpu, "cola")
    colaNodo.transform = tr.matmul([tr.rotationY(-np.cos(theta)*0.1), tr.translate(-0.7, 0, 0), tr.scale(0.4, 0.2, 0.1)])
        
    cabezaNodo = sg.findNode(gpu, "cabeza")
    cabezaNodo.transform = tr.translate(0, 0, -np.cos(theta)*0.07)
        
    cuelloNodo = sg.findNode(gpu, "cuello")
    cuelloNodo.transform = tr.matmul([tr.translate(0.7 + np.cos(theta)*0.07 , 0, 0.3), tr.rotationY(3*np.pi/4), tr.scale(0.6, 0.2, 0.2)])
        
    gpu.transform = tr.matmul([tr.translate(posX, posY, posZ), tr.rotationZ(-1*np.pi), tr.uniformScale(scala)])
    
    # Drawing
    sg.drawSceneGraphNode(gpu, lightingPipeline, "model")
    
# Curvas 
    
def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

def catmullRomMatrix(P0, P1, P2, P3):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Catmull-Rom base matrix is a constant
    Mcr = [[0, -1/2, 2/2, -1/2], [2/2, 0, -5/2, 3/2], [0, 1/2, 4/2, -3/2], [0, 0, -1/2, 1/2]]
    
    return np.matmul(G, Mcr)  

 
# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T

        
    return curve


def readOBJ(filename):

    vertices = []
    

    with open(filename, 'r') as file:
        puntos = []
        curva = []
        for line in file.readlines():
            aux = line.strip().split(",")
            puntos += [np.array([[float(coord) for coord in aux[0:]]]).T]
        
        
        GMcr1 = catmullRomMatrix(puntos[0], puntos[1], puntos[2], puntos[3])
        GMcr2 = catmullRomMatrix(puntos[1], puntos[2], puntos[3], puntos[4])
        
        
        N = 100
        
        catmullRomCurve1 = evalCurve(GMcr1, N)
        catmullRomCurve2 = evalCurve(GMcr2, N)
        
        coordenadas = []
        
        for i in range(N):
            coordenadas.append(catmullRomCurve1[i])
            
        for j in range(1,N):
            coordenadas.append(catmullRomCurve2[j])
            
        catmullRomCurveTotal = np.array(coordenadas)
        
        return catmullRomCurveTotal
        
    
    
if __name__ == "__main__":
    
    
    #archivo = sys.argv[1]
    archivo = "path4.csv"
   

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width =800
    height = 800

    window = glfw.create_window(width, height, "Patitos Bonitos", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

     # Connecting callback functions to handle mouse events:
    # - Cursor moving over the window
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)


    # This shader program does not consider lighting
    #mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    
    
    birdPosX = []
    birdPosY = []
    birdPosZ = []
    N = 100
    
    puntos = readOBJ(archivo)
    
    gpuBird1 = createBird()
    gpuBird2 = createBird()
    gpuBird3 = createBird()
    gpuBird4 = createBird()
    gpuBird5 = createBird()
    gpuBirds = [gpuBird1, gpuBird2, gpuBird3, gpuBird4, gpuBird5]
        
    # Creamos las coordenadas basadas en la curva
    for i in range(2*N-1):
        birdPosX.append(puntos[i][0])
        birdPosY.append(puntos[i][1])
        birdPosZ.append(puntos[i][2])
        


    gpuAxis = es.toGPUShape(bs.createAxis(4))
    
    gpuFondo = es.toGPUShape(bs.createTextureCubeIncomplete("fondo1alreves.png"), GL_REPEAT, GL_LINEAR)
    gpuCielo = es.toGPUShape(bs.createTextureQuad("nubes.png"), GL_REPEAT, GL_LINEAR)
    gpuLago = es.toGPUShape(bs.createTextureQuad("lago.png"), GL_REPEAT, GL_LINEAR)


    t0 = glfw.get_time()
    camera_theta = np.pi/4

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()
        
        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        
        
        # Getting the mouse location in opengl coordinates
        mousePosX = 2 * (controller.mousePos[0] - width/2) / width
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height
        
        
        #Posiciones
            
        camX = -9
        camY = -3
        camZ = 5
                
        atX = (5 * np.sin(np.pi*mousePosX) + camX)
        atY = (5 * np.cos(np.pi*mousePosX) + camY)
        atZ = (5 * np.sin(2*mousePosY) + camZ)
            


        projection = tr.perspective(45, float(width)/float(height), 0.1, 300)

        

        viewPos = np.array([camX,camY,camZ])

        view = tr.lookAt(
            viewPos,
            np.array([atX,atY,atZ]),
            np.array([0,0,1]))

        rotation_theta = glfw.get_time()

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
            

        
        
        lightingPipeline = ls.SimplePhongShaderProgram()
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

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, model)

        
 
        # Dibujando los patitos 
        # Los -num es para que aparezcan gradualmente
        
        indice1 = int(t0*10//1) -20
        indice2 = int(t0*10//1) -60
        indice3 = int(t0*10//1) -100
        indice4 = int(t0*10//1) -140
        indice5 = int(t0*10//1) -180
        indices = [indice1, indice2, indice3, indice4, indice5]
            
        for i in range(5):
            if indices[i] >= 0:
                if indices[i] < 2*N-1:
                    drawMovementBird(gpuBirds[i] , (i/2+1)*t0*6, lightingPipeline, birdPosX[indices[i]], birdPosY[indices[i]], birdPosZ[indices[i]],0.5*(i/3+1)/2)


        
        
        # Dibujando el fondo con texturas
        
        escala = 100
        textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()

        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(escala))
        textureShaderProgram.drawShape(gpuFondo)
        
        cieloTransf = tr.matmul([tr.translate(0, 0, escala/2), tr.uniformScale(escala)])
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, cieloTransf)
        textureShaderProgram.drawShape(gpuCielo)
        
        lagoTransf = tr.matmul([tr.translate(0, 0, -escala/2), tr.uniformScale(escala)])
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, lagoTransf)
        textureShaderProgram.drawShape(gpuLago)
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()




