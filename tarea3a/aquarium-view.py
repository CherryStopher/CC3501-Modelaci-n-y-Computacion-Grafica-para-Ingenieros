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
def drawMovementFish(gpu,theta, lightingPipeline, posX=0, posY=0, posZ=0, scala=0.5):
    
    # Moviendo la cola
    cola = sg.findNode(gpu, "colaFinal")
    cola.transform = tr.matmul([tr.rotationZ(0.3*np.cos(4*theta)), tr.scale(1, 0.5, 1)])
    
    #Moviéndose a través del espacio
    pez = sg.findNode(gpu, "pez")
    xPos = 2*np.cos(theta)
    
    print(theta%(2*np.pi))
    
    
    
    if theta%(2*np.pi) < 3.0:
        reflex = tr.identity()
    else:
        reflex = tr.scale(-1, 1, 1)
    
    pez.transform = tr.matmul([tr.translate(xPos, 0, 0),reflex, tr.uniformScale(0.7)])
    
    # Drawing
    sg.drawSceneGraphNode(gpu, lightingPipeline, "model")
    
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

    # Different shader programs for different lighting strategies
    flatPipeline = ls.SimpleFlatShaderProgram()
    gouraudPipeline = ls.SimpleGouraudShaderProgram()
    phongPipeline = ls.SimplePhongShaderProgram()

    # This shader program does not consider lighting
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    
    gpuPez = createFish(1, 102/255, 0) # Naranjo
    #gpuPez = createFish(0.2, 0.8, 0.2) # Verde
    #gpuPez = createFish(0, 153/255, 153/255) # Verde Agua
    
    gpuAxis = es.toGPUShape(bs.createAxis(4))
    
    t0 = glfw.get_time()
    camera_theta = np.pi/4

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt


        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = -7 * np.sin(camera_theta)
        camY = -7 * np.cos(camera_theta)
        camZ = 3

        viewPos = np.array([camX,camY,camZ])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

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

        # Drawing
        
        drawMovementFish(gpuPez, t0, lightingPipeline)
        
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
