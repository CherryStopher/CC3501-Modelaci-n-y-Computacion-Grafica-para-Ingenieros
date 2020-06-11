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

LIGHT_FLAT    = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG   = 2


SHAPE_RED_CUBE     = 0
SHAPE_GREEN_CUBE   = 1
SHAPE_BLUE_CUBE    = 2
SHAPE_YELLOW_CUBE  = 3
SHAPE_RAINBOW_CUBE = 4

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.lightingModel = LIGHT_FLAT
        self.shape = SHAPE_RED_CUBE


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
        

def createBird():
    gpuGris = es.toGPUShape(bs.createColorNormalsCube(0.8,0.8,0.8))
    gpuAmarillo = es.toGPUShape(bs.createColorNormalsCube(252/256, 191/256, 0))
    gpuNegro = es.toGPUShape(bs.createColorNormalsCube(0.2,0.2,0.2))
    gpuVerde = es.toGPUShape(bs.createColorNormalsCube(0,0.5,0))
    
    # Cuerpo
    cuerpo = sg.SceneGraphNode("cuerpo")
    cuerpo.transform = tr.scale(1.2, 0.5, 0.4)
    cuerpo.childs += [gpuGris]
    
    # Cuello
    cuello = sg.SceneGraphNode("cuello")
    cuello.transform = tr.matmul([tr.translate(0.7, 0, 0.3), tr.rotationY(3*np.pi/4), tr.scale(0.5, 0.2, 0.2)])
    cuello.childs += [gpuNegro]
    
    # Cabeza
    cabeza = sg.SceneGraphNode("cabeza")
    cabeza.transform = tr.matmul([tr.translate(0.9, 0, 0.5), tr.uniformScale(0.5)])
    cabeza.childs += [gpuVerde]
    
    # Ala izquierda
    alaIzq = sg.SceneGraphNode("alaIzq")
    alaIzq.transform = tr.matmul([tr.rotationX(np.pi/4), tr.translate(0.1, -0.4, 0.2), tr.scale(0.5, 0.7, 0.1)])
    alaIzq.childs += [gpuGris]
    
    # Ala derecha
    alaDer = sg.SceneGraphNode("alaDer")
    alaDer.transform = tr.matmul([tr.rotationX(3*np.pi/4), tr.translate(0.1, -0.4, -0.2), tr.scale(0.5, 0.7, 0.1)])
    alaDer.childs += [gpuGris]
    
    # Cola
    cola = sg.SceneGraphNode("cola")
    cola.transform = tr.matmul([tr.translate(-0.65, 0, 0.2), tr.rotationY(np.pi/4), tr.scale(0.3, 0.2, 0.1)])
    cola.childs += [gpuGris]
    
    # Boca
    boca = sg.SceneGraphNode("boca")
    boca.transform = tr.matmul([tr.translate(1.2, 0, 0.4), tr.scale(0.4, 0.3, 0.1)])
    boca.childs += [gpuAmarillo]
    
    
    # Ojo
    ojo = sg.SceneGraphNode("ojo")
    ojo.transform = tr.uniformScale(0.05)
    ojo.childs += [gpuNegro]
    
    # Ojo izquierdo
    ojoIzq = sg.SceneGraphNode("ojoIzq")
    ojoIzq.transform = tr.translate(1.15, -0.1, 0.55)
    ojoIzq.childs += [ojo]
    
    # Ojo derecho
    ojoDer = sg.SceneGraphNode("ojoDer")
    ojoDer.transform = tr.translate(1.15, 0.1, 0.55)
    ojoDer.childs += [ojo]
    
    # Pata
    pata = sg.SceneGraphNode("pata")
    pata.transform =tr.matmul([tr.rotationY(-1*np.pi/6), tr.scale(0.5, 0.1, 0.1)])
    pata.childs += [gpuAmarillo]
    
    # Pata izquierda
    pataIzq = sg.SceneGraphNode("pataIzq")
    pataIzq.transform = tr.translate(-0.2, 0.1, -0.2)
    pataIzq.childs += [pata]
    
    # Pata derecha
    pataDer = sg.SceneGraphNode("pataDer")
    pataDer.transform = tr.translate(-0.2, -0.1, -0.2)
    pataDer.childs += [pata]
    
    
    # Bird
    bird = sg.SceneGraphNode("bird")
    bird.childs += [cuerpo, cuello, cabeza, alaIzq, alaDer, cola, boca, ojoIzq, ojoDer,
                    pataIzq, pataDer]
    bird.transform = tr.rotationZ(-1*np.pi)
    return bird

    
if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width =800
    height = 800

    window = glfw.create_window(width, height, "birds", None, None)

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
    
    
    gpuAxis = es.toGPUShape(bs.createAxis(4))
    gpuBird = createBird()


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

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = 5 * np.sin(camera_theta)
        camY = 5 * np.cos(camera_theta)

        viewPos = np.array([camX,camY,1])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        rotation_theta = glfw.get_time()

        axis = np.array([1,-1,1])
        #axis = np.array([0,0,1])
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

        # The axis is drawn without lighting effects
        if controller.showAxis:
            glUseProgram(mvpPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawShape(gpuAxis, GL_LINES)
        
        
        lightingPipeline = phongPipeline
        
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

        # TO DO: Explore different parameter combinations to understand their effect!

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
        sg.drawSceneGraphNode(gpuBird, lightingPipeline, "model")
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()


