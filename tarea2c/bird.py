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


# Función que crea la GPU de un patito
def createBird():
    gpuGris = es.toGPUShape(bs.createColorNormalsCube(0.8,0.8,0.8))
    gpuAmarillo = es.toGPUShape(bs.createColorNormalsCube(252/256, 191/256, 0))
    gpuNegro = es.toGPUShape(bs.createColorNormalsCube(0.1,0.1,0.1))
    gpuVerde = es.toGPUShape(bs.createColorNormalsCube(0,0.5,0))
    
    # Cuerpo
    cuerpo = sg.SceneGraphNode("cuerpo")
    cuerpo.transform = tr.scale(1.2, 0.5, 0.4)
    cuerpo.childs += [gpuGris]
    
    # Cuello
    cuello = sg.SceneGraphNode("cuello")
    cuello.transform = tr.matmul([tr.translate(0.7, 0, 0.3), tr.rotationY(3*np.pi/4), tr.scale(0.5, 0.2, 0.2)])
    cuello.childs += [gpuNegro]
    
    # Cara
    cara = sg.SceneGraphNode("cara")
    cara.transform = tr.matmul([tr.translate(0.9, 0, 0.5), tr.uniformScale(0.5)])
    cara.childs += [gpuVerde]
    
    # Ala izquierda
    alaIzq = sg.SceneGraphNode("alaIzq")
    alaIzq.transform = tr.matmul([tr.rotationX(np.pi/4), tr.translate(0.1, -0.55, 0.1), tr.scale(0.5, 0.7, 0.1)])
    alaIzq.childs += [gpuGris]
    
    # Ala derecha
    alaDer = sg.SceneGraphNode("alaDer")
    alaDer.transform = tr.matmul([tr.rotationX(3*np.pi/4), tr.translate(0.1, 0.55, 0.1), tr.scale(0.5, 0.7, 0.1)])
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
    
    # Visera gorro
    visGorro = sg.SceneGraphNode("visGorro")
    visGorro.transform = tr.matmul([tr.translate(1, 0, 0.8), tr.scale(0.7, 0.5, 0.1)])
    visGorro.childs += [gpuNegro]
    
    # Gorra
    gorra = sg.SceneGraphNode("gorra")
    gorra.transform = tr.matmul([tr.translate(0.9, 0, 0.95), tr.scale(0.5, 0.5, 0.3)])
    gorra.childs += [gpuNegro]
    
    # Amarillo 1
    amarillo1 = sg.SceneGraphNode("amarillo1")
    amarillo1.transform = tr.matmul([tr.translate(1.17, 0, 0.87), tr.scale(0.05, 0.5, 0.05)])
    amarillo1.childs += [gpuAmarillo]
    
    # Amarillo 2
    amarillo2 = sg.SceneGraphNode("amarillo2")
    amarillo2.transform = tr.matmul([tr.translate(1.17, -0.08, 0.95), tr.scale(0.05, 0.09, 0.09)])
    amarillo2.childs += [gpuAmarillo]
    
    # Amarillo 3
    amarillo3 = sg.SceneGraphNode("amarillo3")
    amarillo3.transform = tr.matmul([tr.translate(1.17, 0.07, 1.0), tr.scale(0.05, 0.11, 0.16)])
    amarillo3.childs += [gpuAmarillo]
    
    # Cabeza
    cabeza = sg.SceneGraphNode("cabeza")
    cabeza.childs += [cara, ojoIzq, ojoDer, boca, visGorro, gorra, amarillo1, amarillo2, amarillo3]
    
    
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
    bird.childs += [cuerpo, cuello, cabeza, alaIzq, alaDer, cola, pataIzq, pataDer]
    bird.transform = tr.rotationZ(-1*np.pi)
    return bird

# Función que dibuja al pato
def drawStaticBird(gpu, mousePosX, mousePosY, lightingPipeline):
    # Moviendo partes del cuerpo
    alaIzqNodo = sg.findNode(gpuBird, "alaIzq")
    alaIzqNodo.transform = tr.matmul([tr.rotationX(-mousePosY*0.5), tr.translate(0.1, -0.55, 0.1), tr.scale(0.5, 0.7, 0.1)])
        
    alaDerNodo = sg.findNode(gpuBird, "alaDer")
    alaDerNodo.transform = tr.matmul([tr.rotationX(mousePosY*0.5), tr.translate(0.1, 0.55, 0.1), tr.scale(0.5, 0.7, 0.1)])
        
    colaNodo = sg.findNode(gpuBird, "cola")
    colaNodo.transform = tr.matmul([tr.rotationY(-mousePosY*0.1), tr.translate(-0.7, 0, 0), tr.scale(0.4, 0.2, 0.1)])
        
    cabezaNodo = sg.findNode(gpuBird, "cabeza")
    cabezaNodo.transform = tr.translate(0, 0, -mousePosY*0.02)
        
    cuelloNodo = sg.findNode(gpuBird, "cuello")
    cuelloNodo.transform = tr.matmul([tr.translate(0.7 + mousePosY*0.03 , 0, 0.3), tr.rotationY(3*np.pi/4), tr.scale(0.6, 0.2, 0.2)])
        
    # Drawing
    sg.drawSceneGraphNode(gpu, lightingPipeline, "model")
    
    



if __name__ == "__main__":
    

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width =800
    height = 800

    window = glfw.create_window(width, height, "Patito Bonito", None, None)

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
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    
    gpuBird = createBird()

    gpuAxis = es.toGPUShape(bs.createAxis(4))
    
    # Función nueva agregada en basic_shapes.py: createtextureCubeIncomplete(...)
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
    
        atX = 0
        atY = 0
        atZ = 0
        
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt
                
        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt
                
        camX = -5 * np.sin(camera_theta)
        camY = -5 * np.cos(camera_theta)
        camZ = 3


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

        
        # Dibujando el patito
        drawStaticBird(gpuBird, mousePosX, mousePosY, lightingPipeline)


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


