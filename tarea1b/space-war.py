# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 01:40:08 2020

@author: crist
"""
import glfw
import math
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import scene_graph as sg
import transformations as tr
import basic_shapes as bs
import easy_shaders as es

# A class to store the application control
class Controller:
        fillPolygon = True
        useShader2 = False


# global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller



    if key == glfw.KEY_ESCAPE:
        sys.exit()

def createNaveAliada():
    naveAliadaTexture1 = es.toGPUShape(bs.createTextureQuad("naveAliada1.png"), GL_REPEAT, GL_LINEAR)
    naveAliadaTexture2 = es.toGPUShape(bs.createTextureQuad("naveAliada2.png"), GL_REPEAT, GL_LINEAR)
    naveAliadaTexture3 = es.toGPUShape(bs.createTextureQuad("naveAliada3.png"), GL_REPEAT, GL_LINEAR)
    naveAliadaTexture4 = es.toGPUShape(bs.createTextureQuad("naveAliada4.png"), GL_REPEAT, GL_LINEAR)
    
    
    nX = 0
    nY = -0.7
    naveTransform = tr.matmul([tr.translate(nX, nY, 0), tr.uniformScale(0.4)])
    
    naveAliada1 = sg.SceneGraphNode("naveAliada1")
    naveAliada1.childs += [naveAliadaTexture1]
    naveAliada1.transform = naveTransform
    
    naveAliada2 = sg.SceneGraphNode("naveAliada2")
    naveAliada2.childs += [naveAliadaTexture2]
    naveAliada2.transform = naveTransform
    
    naveAliada3 = sg.SceneGraphNode("naveAliada3")
    naveAliada3.childs += [naveAliadaTexture3]
    naveAliada3.transform = naveTransform
    
    naveAliada4 = sg.SceneGraphNode("naveAliada4")
    naveAliada4.childs += [naveAliadaTexture4]
    naveAliada4.transform = naveTransform
    
    naveAliada = sg.SceneGraphNode("naveAliada")
    naveAliada.childs += [naveAliada1, naveAliada2, naveAliada3, naveAliada4]
    
    return naveAliada


def createNaveEnemiga():

    
    naveEnemigaTexture = es.toGPUShape(bs.createTextureQuad("naveAlien.png"), GL_REPEAT, GL_LINEAR)
    
    naveEnemiga = sg.SceneGraphNode("naveEnemiga")
    naveEnemiga.childs += [naveEnemigaTexture]
    
    return naveEnemiga

    
def createNavesEnemigas(n):
    nEX = 0
    nEY = 0.7
    navesEnemigasNodos = sg.SceneGraphNode("navesEnemigasNodos")
    navesEnemigasNodos.childs += [createNaveEnemiga()] # Re-using the previous function
    
    navesEnemigas = sg.SceneGraphNode("navesEnemigas")
    
    baseName = "naveEnemiga"
    for i in range(n):
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = tr.matmul([tr.translate(nEX, nEY, 0), tr.uniformScale(0.4)])
        newNode.childs += [navesEnemigasNodos]
        
        navesEnemigas.childs += [newNode]
        
    return navesEnemigas
        
    

if __name__ == "__main__":
    
    N = int(sys.argv[1])
    
   
    

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 800
    height =800
    
    window = glfw.create_window(width, height, "Space War", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    
    pipelineTexture = es.SimpleTextureTransformShaderProgram()
    pipelineNoTexture = es.SimpleTransformShaderProgram()
 
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipelineTexture.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Creamos las GPUs
    
    # Espacio exterior
    spaceTexture = es.toGPUShape(bs.createTextureQuad("FondoSpaceWar2.png"), GL_REPEAT, GL_LINEAR)
    space = sg.SceneGraphNode("space")
    space.childs += [spaceTexture]
    space.transform = tr.matmul([tr.translate(0, 3, 0), tr.scale(2, 8, 1)])
    
    spacePosition = 0.0
    
    
    # Nave Aliada
    naveAliada = createNaveAliada()
    nX = 0
    nY = -0.7
    
  
    
    # Naves Enemigas
    nEX = 0
    nEY = 0.7
    
    navesEnemigas = createNavesEnemigas(N)
    
    # Lista con los nodos de las naves enemigas
    naves = []    
    for i in range(N):
        nave_i = sg.findNode(navesEnemigas, "naveEnemiga"+str(i))
        naves += [nave_i]

    
        
    
    while not glfw.window_should_close(window):
        
        
        # Using GLFW to check for input events
        glfw.poll_events()
        # Update Time
        t = glfw.get_time()
        spacePosition = 0.7 * t
        
        
        if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
            if nX > -0.8:  # Para evitar que se salga de la pantalla
                nX -= 0.0013
        
        if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
            if nX < 0.8:
                nX += 0.0013
        
        if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
            if nY < 0:
                nY += 0.0013
        
        if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
            if nY > -0.8:
                nY -= 0.0013

        

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        
        if controller.fillPolygon:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Create transform matrix
        glUseProgram(pipelineTexture.shaderProgram)

    
        # Drawing the texture background
        
        # Modifying only the space Texture
        # This condition translates the space so it can be seen as a loop
        
        # Espacio exterior
        if spacePosition > 6.0:
            spacePosition = spacePosition % 6
            
            
        espacio = sg.findNode(space, "space")
        espacio.transform = tr.matmul([tr.translate(0, 3 - spacePosition, 0), tr.scale(2, 8, 1)])
        
        sg.drawSceneGraphNode(space, pipelineTexture, "transform")
        
        
        # Nave aliada
        
        naveAliada1 = sg.findNode(naveAliada, "naveAliada1")
        naveAliada2 = sg.findNode(naveAliada, "naveAliada2")
        naveAliada3 = sg.findNode(naveAliada, "naveAliada3")
        naveAliada4 = sg.findNode(naveAliada, "naveAliada4")
        
        naveAliada1.transform = tr.matmul([tr.translate(nX, nY, 0), tr.uniformScale(0.4)])
        naveAliada2.transform = tr.matmul([tr.translate(nX, nY, 0), tr.uniformScale(0.4)])
        naveAliada3.transform = tr.matmul([tr.translate(nX, nY, 0), tr.uniformScale(0.4)])
        naveAliada4.transform = tr.matmul([tr.translate(nX, nY, 0), tr.uniformScale(0.4)])
        
        if t % 2 < 0.5:
            sg.drawSceneGraphNode(naveAliada1, pipelineTexture, "transform")
            
        if t % 2 <1.0 and t % 2 >= 0.5:
            sg.drawSceneGraphNode(naveAliada2, pipelineTexture, "transform")
            
        if t % 2 <1.5 and t % 2 >= 1.0:
            sg.drawSceneGraphNode(naveAliada3, pipelineTexture, "transform")
            
        if t % 2 <2.0 and t % 2 >= 1.5:
            sg.drawSceneGraphNode(naveAliada4, pipelineTexture, "transform")
            
        
        # Naves enemigas
        pos_nEY = []
        for j in range(N):
            ti = t % 3 # Tiempo inicial en que aparecerá cada nave
            # lista de tiempos de entrada
            pos_nEY += [1.3 - 0.2 * ti] 
            
        for i in range(N):
            
                
            # Haremos que las naves aparezcan gradualmente
            if t > 3*(i+1):
                nEX = 0.8 * np.sin(t + i) # Posicion de la nave en el eje X
                
                # Referenciamos a la lista con los nodos de las naves enemigas
                
                
                "if pos_nEY[i] < 0.8:"
                naves[i].transform = tr.matmul([tr.translate(nEX, 0.8, 0), tr.uniformScale(0.1*(i+1))])
                sg.drawSceneGraphNode(naves[i], pipelineTexture, "transform")
                
                """else:
                    naves[i].transform = tr.matmul([tr.translate(nEX, pos_nEY[i], 0), tr.uniformScale(0.1*(i+1))])
                    sg.drawSceneGraphNode(naves[i], pipelineTexture, "transform")"""
            
        
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)
        
        t0 = glfw.get_time()
        
    glfw.terminate()