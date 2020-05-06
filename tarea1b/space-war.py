# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 01:40:08 2020

@author: crist
"""

"""
IMPORTANTE: En el video el programa se ejecuta con la tarjeta Nvidia, ya que al hacerlo con la integrada
la nave y las balas van mucho más rápido debido a la parte de las posiciones con el posY += 0.02 (por ejemplo)
Para ejecutarlo con la integrada y que salga bien, debe ser posY += 0.002 (por ejemplo)
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
        
    if key == glfw.KEY_SPACE: # Si se presiona espacio, se crea un disparo
        if disparoBool == False:
            disparoBool = True

# Fuciones auxiliares

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


def createDisparosEnemigos():
    disparoGPU = es.toGPUShape(bs.createTextureQuad("disparoEnemigo.png"), GL_REPEAT, GL_LINEAR)
    disparosEnemigos = sg.SceneGraphNode("disparosEnemigos")
    for i in range(N):
        dispEne = sg.SceneGraphNode("disparoEnemigo" + str(i))
        dispEne.childs += [disparoGPU]
        dispEne.transform = tr.matmul([tr.translate(-3,-3,0),tr.uniformScale(0.2)]) #Lo trasladamos fuera de a pantalla para que no ocurran cosas raras
        disparosEnemigos.childs += [dispEne]
    return disparosEnemigos
        
    

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
    spaceTexture = es.toGPUShape(bs.createTextureQuad("FondoSpaceWar3.png"), GL_REPEAT, GL_LINEAR)
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
    existeDisparo = [] # Lista de Booleanos para ir poniendo si existe el disparo o no
    
    
    
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
    
    
    # Ponemos los nodos de cada nave en una lista para acceder más fácilmente (al menos para mí)
    for i in range(N):
        nave_i = sg.findNode(navesEnemigas, "naveEnemiga"+str(i))
        naves += [nave_i]
        existeNave += [True] # Decimos que la nave recién creada existe
        
    
    # Creamos los disparos de las naves enemigas
    posBX = []
    posBY = []    
    dispEnem = createDisparosEnemigos()
    disparosEnemigos = []    

    for i in range(N):
        disparoEnemigo_i = sg.findNode(dispEnem, "disparoEnemigo" + str(i))
        disparosEnemigos += [disparoEnemigo_i]

        posBX += [-3] #Así evitamos que se muestren erroneamente, en verdad da lo mismo este valor porque después lo reemplazaremos
        posBY += [-3]
        

    # Valor para saber si ganamos el juego
    ganaste = False
    gpuGanaste1 = es.toGPUShape(bs.createTextureQuad("ganaste.png"), GL_REPEAT, GL_LINEAR)
    gpuGanaste2 = es.toGPUShape(bs.createTextureQuad("ganaste2.png"), GL_REPEAT, GL_LINEAR)
    
    # Vidas de la nave aliada
    vidas = 3
    gpuPerdiste1 = es.toGPUShape(bs.createTextureQuad("perdiste.png"), GL_REPEAT, GL_LINEAR)
    gpuPerdiste2 = es.toGPUShape(bs.createTextureQuad("perdiste2.png"), GL_REPEAT, GL_LINEAR)
    
    gpuVida3 = es.toGPUShape(bs.createTextureQuad("vidas3.png"), GL_REPEAT, GL_LINEAR)
    gpuVida2 = es.toGPUShape(bs.createTextureQuad("vidas2.png"), GL_REPEAT, GL_LINEAR)
    gpuVida1 = es.toGPUShape(bs.createTextureQuad("vidas1.png"), GL_REPEAT, GL_LINEAR)
    while not glfw.window_should_close(window):
        
        
        # Using GLFW to check for input events
        glfw.poll_events()
        # Update Time
        t = glfw.get_time()
        
        
        spacePosition = 0.7 * t
        
        # Lo que pasa cuando se presionan las teclas WASD (la tecla espacio está al principio)
        if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
            if nX > -0.8:  # Para evitar que se salga de la pantalla
                nX -= 0.02
        
        if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
            if nX < 0.8:
                nX += 0.02
        
        if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
            if nY < 0:
                nY += 0.02
        
        if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
            if nY > -0.8:
                nY -= 0.02
                


        

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
        if disparoBool:                                                  # Si se creó un disparo al presionar espacio:
            disparoNave = sg.SceneGraphNode("disparo" + str(numDisparo)) # Creamos un nodo con el disparo
            disparoNave.childs += [disparoNodo]                          # Se le agrega el nodo que tiene como hijo el gpu del disparo
            numDisparo += 1                       # Pasamos al siguiente para cuando se cree otro disparo, el nombre quede con el numero siguiente
            disparos.childs += [disparoNave]                             # Agregamos el nodo recién creado al nodo gigante
            xD += [nX]                                                # La posición en X será la posición de la nave al momento de crear el disparo
            yD += [nY + 0.2]                    # Lo mismo de antes pero en Y. Le sumamos 0.2 para que la bala no salga desde el centro de la nave
            existeDisparo += [True]             # Decimos que este disparo existe
            disparoBool = False        # Ahora decimos que el Booleano del disparo es False para así volver a crear otro cuando se pulse espacio
            
            
            
        # Posiciones enemigas
        
        pos_nEY = []
        for j in range(N):
            ti = t % 3 # Tiempo inicial en que aparecerá cada nave
            # lista de tiempos de entrada
            pos_nEY += [1.3 - 0.2 * ti] 
        
        
        
        # Posiciones de las naves enemigas    
            
        for i in range(N):
                 
            # Haremos que las naves aparezcan gradualmente si su valor es True, es decir, si existen
            # También haremos aparecer los disparos
            if (existeNave[i]):
                
                if t > 3*(i+2):
                    pos_nEX[i] = 0.8 * np.sin(t + i) # Posicion de la nave en el eje X
                    
                
                    
                    if t > 3*(i+2) and t > 3*(i+3): # despues de un tiempo, la nave deja de bajar y oscila en el 0.7
                        pos_nEY[i] = 0.7  - 0.1 * np.sin(10*(t + i))
         
                    naves[i].transform = tr.matmul([tr.translate(pos_nEX[i], pos_nEY[i], 0), tr.uniformScale(0.3)])
                    sg.drawSceneGraphNode(naves[i], pipelineTexture, "transform")
                    
                    
        # Disparos de las naves enemigas
        for i in range(N):
            if t > 3*(i+3): # Se crearán cuando la nave i se posicione en el 0.7 y empiece a oscilar
                # Las haremos que avancen en X para agregarle algo de dificultad al juego
                posBX[i] = 0.8 * np.sin(t + i) 
                if existeNave[i]:

                    if posBY[i] < -1.2: # Si la bala salió de la pantalla:
                        posBY[i] = 0.7 # Hacemos que vuelva a disparar
                        disparosEnemigos[j].transform = tr.matmul([tr.translate(posBX[i], posBY[i], 0), tr.uniformScale(0.2)])
                        sg.drawSceneGraphNode(disparosEnemigos[i], pipelineTexture, "transform")
                                
                    else:
                        posBY[i] -= 0.015 # Si la bala aún no sale de la pantalla, va bajando
                        disparosEnemigos[i].transform = tr.matmul([tr.translate(posBX[i], posBY[i], 0), tr.uniformScale(0.2)])
                        sg.drawSceneGraphNode(disparosEnemigos[i], pipelineTexture, "transform")   
                        
                else: # Si la nave ya no existe, el disparo se sigue moviendo y solo de dibuja hasta antes de salir de la pantalla
                    if posBY[i] > -1.2:
                        posBY[i] -= 0.015
                        disparosEnemigos[i].transform = tr.matmul([tr.translate(posBX[i], posBY[i], 0), tr.uniformScale(0.2)])
                        sg.drawSceneGraphNode(disparosEnemigos[i], pipelineTexture, "transform")  
                    

        
        # Dibujando el disparo y le vemos la condición para cuando choque con una nave enemiga
                    
        if (numDisparo > 0): # Si existe algún disparo
            for i in range(numDisparo):
                disparosArray += [sg.findNode(disparos, "disparo" + str(i))] # Se agregan los disparos a una lista para acceder a ellos con mas facilidad
                
           
            for i in range(numDisparo): # Aqui veremos cuando impacte a una nave enemiga
                if yD[i] < 1.1 and existeDisparo[i]: # Si aún no llega al borde superior de la vetana y si existe el disparo
                    for j in range(N): # Aquí veremos cuando impacte a una nave enemiga
                        epsilon = 0.05
                        
                        # Si el disparo toca una nave enemiga, desaparece el disparo y la nave
                        if ((abs(yD[i] - 0.7) < epsilon) and pos_nEY[j] < 0.81 and(xD[i] <= pos_nEX[j] + 0.2 and xD[i] >= pos_nEX[j] - 0.2)):
                            if existeNave[j]: # Revisamos si la nave numero j existe, si sí, entonces:
                                existeNave[j] = False # Se actualiza su valor de existencia, esto hará que no se dibuje
                                
                                
                                # Con estos valores nos aseguramos de que la nave ya no esté al alcance del disparo
                                pos_nEX[j] = 5 
                                pos_nEY[j] = -5 
                                
                                # Así nos aseguramos de que el disparo no interfiera con otras naves después de impactar alguna
                                xD[i] = -5
                                yD[i] = -6
                                
                                existeDisparo[i] = False # Ahora el disparo no existe
                                
                        else: # Si el disparo aun no ha impactado una nave enemiga entonces se dibuja avanzando hacia arriba 
                            yD[i] +=0.005
                            disparosArray[i].transform = tr.matmul([tr.translate(xD[i], yD[i], 0), tr.uniformScale(0.2)])
                            sg.drawSceneGraphNode(disparosArray[i], pipelineTexture, "transform")
                            
                            
                else: # Si el disparo ya pasó el borde superior de la pantalla entonces:
                    existeDisparo[i] = False # Ahora el disparo no existe
                            
        
        # Aquí sabremos si ganamos      
        if True in existeNave:
            ganaste = False
        else:
            ganaste = True
            
        if ganaste:
            vidas = 100 # Así nos aseguramos de no morir en caso de que nos quede 1 vida y nos mate la bala de un enemigo que matamos
            if t % 1 < 0.5:
                glUniformMatrix4fv(glGetUniformLocation(pipelineTexture.shaderProgram, "transform"), 1, GL_TRUE, tr.scale(2, 2, 1))
                pipelineTexture.drawShape(gpuGanaste1)
            
            if t % 1 <1.0 and t % 1 >= 0.5:
                glUniformMatrix4fv(glGetUniformLocation(pipelineTexture.shaderProgram, "transform"), 1, GL_TRUE, tr.scale(2, 2, 1))
                pipelineTexture.drawShape(gpuGanaste2)
                
                
                
        # Veremos si alguna bala nos golpeó
        for i in range(N):
            epsilon = 0.05
            if abs(posBY[i] - nY) < epsilon and (posBX[i] < nX + 0.2 and posBX[i] > nX - 0.2): # Si su posición es muy cercana
                vidas -= 1
                posBY[i] = -2 # Ponemos la bala abajo para que el programa lo detecte y vuelva a ponerla desde arriba
                
        
        # Mostrador de vidas:
        if vidas == 3:
            glUniformMatrix4fv(glGetUniformLocation(pipelineTexture.shaderProgram, "transform"), 1, GL_TRUE, tr.uniformScale(2))
            pipelineTexture.drawShape(gpuVida3)
        
        if vidas == 2:
            glUniformMatrix4fv(glGetUniformLocation(pipelineTexture.shaderProgram, "transform"), 1, GL_TRUE, tr.uniformScale(2))
            pipelineTexture.drawShape(gpuVida2)
        
        if vidas == 1:
            glUniformMatrix4fv(glGetUniformLocation(pipelineTexture.shaderProgram, "transform"), 1, GL_TRUE, tr.uniformScale(2))
            pipelineTexture.drawShape(gpuVida1)
        
        
        # Si pierdes
        if vidas == 0:
        
            # Ponemos la nave bien lejos para que pareciera que desapareció xd
            nX = -5
            nY = -5
            if t % 1 < 0.5:
                glUniformMatrix4fv(glGetUniformLocation(pipelineTexture.shaderProgram, "transform"), 1, GL_TRUE, tr.scale(2, 2, 1))
                pipelineTexture.drawShape(gpuPerdiste1)
            if t % 1 <1.0 and t % 1 >= 0.5:
                glUniformMatrix4fv(glGetUniformLocation(pipelineTexture.shaderProgram, "transform"), 1, GL_TRUE, tr.scale(2, 2, 1))
                pipelineTexture.drawShape(gpuPerdiste2)
            
            for j in range(numDisparo):
                existeDisparo[j] = False # Nos aseguramos de verdad perder y que nuestro disparo no mate un enemigo y ganar y perder al mismo tiempo xd
        
        
       
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)
        
        
        
    glfw.terminate()