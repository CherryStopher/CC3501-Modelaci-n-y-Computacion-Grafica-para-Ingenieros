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
    global disparoBool


    if key == glfw.KEY_ESCAPE:
        sys.exit()
        
    if key == glfw.KEY_SPACE:
        if disparoBool == False:
            disparoBool = True

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
    #pipelineNoTexture = es.SimpleTransformShaderProgram()
 
    
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
    
    
    # Disparos
    disparoTexture = es.toGPUShape(bs.createTextureQuad("disparo.png"), GL_REPEAT, GL_LINEAR)
    disparoNodo = sg.SceneGraphNode("disparo")
    disparoNodo.childs += [disparoTexture]
    disparos = sg.SceneGraphNode("disparos")
    
    # Arreglo con las posiciones de cada disparo en x e y
    xD = []
    yD = []
    
    disparoBool = False # Booloeano que me dice si tengo que generar un disparo o no
    numDisparo = 0 # Numero que me ayudará para saber en qué nodo de disparo estoy
    disparosArray = [] # Lista para ir poniendo los nodos de disparo
    existeDisparo = []
    
    
    
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
    
    # Posición inicial de las naves enemigas en el eje X
    pos_nEX = []
    for j in range(N):
        pos_nEX += [0]
    
    
    # Arreglo de booleanos que me dice si la nave enemiga numero i existe o no,
    # lo usaré para cuando el disparo le pegue a una nave
    existeNave = [] 
    
    
    for i in range(N):
        nave_i = sg.findNode(navesEnemigas, "naveEnemiga"+str(i))
        naves += [nave_i]
        existeNave += [True]

    # Lista con los disparos
    disparosGPU = []
    
    t0 = glfw.get_time()    
    
    while not glfw.window_should_close(window):
        
        
        # Using GLFW to check for input events
        glfw.poll_events()
        # Update Time
        t = glfw.get_time()
        dt = t - t0
        t0 = t
        
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
        
        
        # Animación de la Nave aliada
        
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
         
            
        # Disparo de la nave aliada
        if disparoBool:
            disparoNave = sg.SceneGraphNode("disparo" + str(numDisparo))
            disparoNave.childs += [disparoNodo] # Se le agrega el nodo que tiene como hijo el gpu del disparo
            numDisparo += 1 # Pasamos al siguiente para cuando se cree otro disparo, quede con el nombre con el numero siguiente
            disparos.childs += [disparoNave] # Agregamos el nodo recién creado al nodo gigante
            xD += [nX]
            yD += [nY + 0.2]
            existeDisparo += [True]
            disparoBool = False
            
            
            
        # Posición de las naves enemigas en el eje x e y
        pos_nEY = []
        for j in range(N):
            ti = t % 3 # Tiempo inicial en que aparecerá cada nave
            # lista de tiempos de entrada
            pos_nEY += [1.3 - 0.2 * ti] 
            
            
        for i in range(N):
                 
            # Haremos que las naves aparezcan gradualmente si su valor es True, es decir, si existen
            if (existeNave[i]):
                
                if t > 3*(i+1):
                    pos_nEX[i] = 0.8 * np.sin(t + i) # Posicion de la nave en el eje X
                    
                
                    # Referenciamos a la lista con los nodos de las naves enemigas
                    if t > 3*(i+1) and t > 3*(i+2):
                        pos_nEY[i] = 0.7
                
                
                    naves[i].transform = tr.matmul([tr.translate(pos_nEX[i], pos_nEY[i], 0), tr.uniformScale(0.3)])
                    sg.drawSceneGraphNode(naves[i], pipelineTexture, "transform")
                
            
        
        
        # Dibujando el disparo
        if (numDisparo > 0): # Si existe algún disparo
            for i in range(numDisparo):
                disparosArray += [sg.findNode(disparos, "disparo" + str(i))]
                
           
            for i in range(numDisparo): # Aqui veremos cuando impacte a una nave enemiga
                if yD[i] < 1.1 and existeDisparo[i]: # Si aún no llega al borde superior de la vetana y si existe el disparo
                    for j in range(N): # Aquí veremos cuando impacte a una nave enemiga
                        epsilon = 0.01
                        # Si el disparo aún no toca alguna nave enemiga entonces se dibuja el disparo
                        if ((abs(yD[i] - 0.7) < epsilon) and pos_nEY[j] == 0.7 and(xD[i] <= pos_nEX[j] + 0.2 and xD[i] >= pos_nEX[j] - 0.2)):
                            if existeNave[j]: # Si no se cumple lo anterior, es porque el disparo impactó alguna nave, entonces esa nave se borra de la escena
                                existeNave[j] = False 
                                pos_nEX[j] = 5 
                                pos_nEY[j] = -5 # Con estos valores nos aseguramos de que la nave ya no esté al alcance del disparo
                                xD[i] = -5
                                yD[i] = -6 # Así nos aseguramos de que el disparo no interfiera con otras naves después de impactar alguna
                                existeDisparo[i] = False # Ahora el disparo no existe
                                print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                        else:
                            yD[i] +=0.001
                            disparosArray[i].transform = tr.matmul([tr.translate(xD[i], yD[i], 0), tr.uniformScale(0.2)])
                            sg.drawSceneGraphNode(disparosArray[i], pipelineTexture, "transform")
                            
                            
                else:
                    
                    existeDisparo[i] = False # Ahora el disparo no existe
                            
        
        
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)
        
        
        
    glfw.terminate()