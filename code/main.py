#!/usr/bin/env python3.6


"""
    main.py

    Este programa tiene como objetivo realizar
    mediciones en 3D utilizando una cámara monocular

    author: Angel Velazquez
"""

#Importamos librerías
import numpy as np
import cv2
import json
import math
import argparse

#Inicializamos nuestras variables globales coordenadas
clickL_ix, clickL_iy = -1,-1 #Click izquierdo
clickR_ix, clickR_iy = -1,-1 #Click derecho
clickA_ix, clickA_iy = -1,-1 #Click Actual

#Función que detecta las acciones del mouse
def clickListener(event, x, y, flags, param):
   
    #Creamos nuestras variable globales
    global clickL_ix,clickL_iy
    global clickR_ix,clickR_iy
    global clickA_ix,clickA_iy

    #Si detecta que presionó el click izquierdo, gurda las coordenada
    if event == cv2.EVENT_LBUTTONDOWN:
        clickL_ix = x
        clickL_iy = y
        
 
    #Si detecta que presionó el click derecho, gurda las coordenada
    elif event == cv2.EVENT_RBUTTONDOWN:
        clickR_ix = x
        clickR_iy = y
        

    #Si detecta movimiento del mouse, gurda las coordenada
    elif event == cv2.EVENT_MOUSEMOVE:
        clickA_ix = x
        clickA_iy = y

#Obtenemos los parámetros de la terminal
parser = argparse.ArgumentParser('Medición de objetos')
parser.add_argument('-i', '--camId', help='Camera index', required=True)
parser.add_argument('-c', '--config', help='Config file', required=True)
parser.add_argument('-z', '--z', help='Z Distance', required=True)
args = vars(parser.parse_args())
z=float(args["z"])

#Leemos el archivo de configuración para obtener los parámetros intrínsecos
with open(args["config"],'r') as f:
    data = json.load(f)
cx=data["cx"]
cy=data["cy"]
fx=data["fx"]
fy=data["fy"]

#Creamos una variable con una parte de la ecuación
zfx=z/fx
zfy=z/fy

#Iniciamos el video
cap = cv2.VideoCapture(int(args["camId"]))

#Ciclo infinito
while(True):
    #Obtenemos frame
    ret, frame = cap.read()
    #Damos nombre a la ventana
    cv2.namedWindow("Frame")
    #Le agregamos la función de detección de acciones del mouse a la ventana
    cv2.setMouseCallback("Frame", clickListener, frame)
    #Creamos una segunda ventana de zoom
    cv2.namedWindow("Zoom")
    #Si se obtuvo el frame correctamente...
    if ret:
        
        #imagen, coord, color, tipoMarcador, tamaño,grosor
        #Dibujamos marcadores en donde se a hecho click, en el centro y en donde esta nuestro cursor
        cv2.drawMarker(frame, (clickL_ix,clickL_iy), (0,0,255), 0, 20, 2) #marcador de cruz
        cv2.drawMarker(frame, (clickR_ix,clickR_iy), (0,255,0), 0, 20, 2) #marcador de cruz
        cv2.drawMarker(frame, (clickA_ix,clickA_iy), (255,0,0), 0, 20, 1) #marcador de cruz
        cv2.drawMarker(frame, (cx,cy), (255,255,255), 0, 20, 1) #marcador de cruz

        #Desplegamos las coordenadas del cursor
        cv2.putText(frame,'X:', (0,20), cv2.FONT_HERSHEY_DUPLEX, 0.5,(255,255,255), 1)
        cv2.putText(frame,'Y:', (0,40), cv2.FONT_HERSHEY_DUPLEX, 0.5,(255,255,255), 1)
        cv2.putText(frame,'Z:', (0,60), cv2.FONT_HERSHEY_DUPLEX, 0.5,(255,255,255), 1)

        cv2.putText(frame,str((clickA_ix-cx)), (20,20), cv2.FONT_HERSHEY_DUPLEX, 0.5,(255,255,255), 1)
        cv2.putText(frame,str((clickA_iy-cy)*-1), (20,40), cv2.FONT_HERSHEY_DUPLEX, 0.5,(255,255,255), 1)
        cv2.putText(frame,str(z), (20,60), cv2.FONT_HERSHEY_DUPLEX, 0.5,(255,255,255), 1)

        #Desplegamos las coordenadas donde se hizo click
        cv2.putText(frame,str((clickL_ix-cx))+','+str((clickL_iy-cy)*-1), (clickL_ix,clickL_iy-15), cv2.FONT_HERSHEY_DUPLEX, .50,(0,255,0), 1)
        cv2.putText(frame,str((clickR_ix-cx))+','+str((clickR_iy-cy)*-1), (clickR_ix,clickR_iy-15), cv2.FONT_HERSHEY_DUPLEX, .50,(0,255,0), 1)

        #Condiciones para que dibuje la línea solo cuando ya existen dos puntos
        if clickR_ix < 0 and clickL_ix >= 0:
            cv2.line(frame, (clickA_ix, clickA_iy), (clickL_ix, clickL_iy), (255,0,0), 5)
        if clickL_ix < 0 and clickR_ix >= 0:
            cv2.line(frame, (clickA_ix, clickA_iy), (clickR_ix, clickR_iy), (255,0,0), 5) 
        if clickL_ix > 0 and clickR_ix > 0:
            cv2.line(frame, (clickL_ix, clickL_iy), (clickR_ix, clickR_iy), (255,0,0), 5)

            #Obtener distancia en pixeles en x y en y
            xsdif=clickL_ix-clickR_ix
            ysdif=clickL_iy-clickR_iy

            #calcular distancia en pixeles
            xp=math.pow(xsdif,2)
            yp=math.pow(ysdif,2)
            distanciapix=math.sqrt(xp+yp)

            #calcular distancia real
            xs=math.pow(xsdif*zfx,2)
            ys=math.pow(ysdif*zfy,2)
            distancia=math.sqrt(xs+ys)

            #desplegar el resultado en medio de la línea
            cv2.putText(frame,str(round(distancia,2))+'cm', (round((clickR_ix+clickL_ix)/2),round((clickR_iy+clickL_iy)/2)),
                        cv2.FONT_HERSHEY_DUPLEX, .60,(0,255,255), 1)
            cv2.putText(frame,str(round(distanciapix,2))+'px', (round((clickR_ix+clickL_ix)/2),round((clickR_iy+clickL_iy)/2)+30),
                        cv2.FONT_HERSHEY_DUPLEX, .60,(0,255,255), 1)
             
        #Realizar zoom solo cuando tiene un margen de 40 pixeles
        if clickA_ix > 40 and clickA_iy > 40:
            #[y1:y2,x1:x2]
            #Obtenemos nuestra región de interés
            roi = frame[clickA_iy-40:clickA_iy+40,clickA_ix-40:clickA_ix+40]
            #Le damos resize para que se vea con zoom
            roi = cv2.resize(roi,(int(480),int(480)))
            #Desplegar imagen
            cv2.imshow('Zoom',roi)
        
        #Desplegar frame
        cv2.imshow('Frame',frame)
        #Si presiona q se cierra
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

#Cerrar programa
cap.release()
cv2.destroyAllWindows()
