"""
    Hernández López Ángel Zait
    Juego de gato
"""

import numpy as np
import random as rand
import os

class Gato:
    def __init__(self,tam,numPlay):
        self.t=np.zeros((tam,tam),dtype=np.int)     # Matriz inicial de ceros
        self.tam=tam                                # Tamaño de la matriz
        self.xy=[]                                  # Coordenadas a guardar en enteros
        self.tt=['-']*(tam+1)                       # Matriz de vista
        self.llenoTT()                              # Crear tablero visual
        self.marcas=list()                          # Marca de los jugadores
        self.numPlayers=numPlay                     # Numero de jugadores

    def bienvenida(self):   # Mensaje de bienvenida
        print("Bienvenido al juego de gato\n")

    def doyMarcas(self,dato):
        self.marcas=dato

    def verGato(self):  # Muestra del tablero
        tabla=""
        for i in range(self.tam+1):
            for j in range(self.tam+1):
                tabla=tabla+str(self.tt[i][j])+" "
            tabla=tabla+"\n"
        return str(tabla)
    
    def llenoTT(self):  # Generar tablero
        for i in range(self.tam+1):
            self.tt[i]=["-"]*(self.tam+1)
        self.tt[1][0]=0
        for i in range(self.tam):
            for j in range(self.tam):
                if i==0:
                    self.tt[i][j+1]=j
                elif j==0:
                    self.tt[i+1][j]=i
        
    def verifica(self,tipo,tam):    # Verifica si hay un ganador
        ganador=False; rango=0
        gan=np.ones((tam),dtype=np.int)  # Hace una copia del vector ganador
        
        gan=gan*(tipo+1)
        
        if tam==3:
            ganador=self.veoCon3(gan)
        else:
            ganador=self.veoCon5(gan)

        return ganador

    def jugadorPlay(self,coor,tipo):  # Jugada del 
        sip=False
        self.xy=coor.split(",")   # Separación del string recibido
        if self.t[int(self.xy[0])][int(self.xy[1])]==0: # Si es que la casilla está vacía, ingrese el numero
            self.t[int(self.xy[0])][int(self.xy[1])]=(tipo+1)
            self.tt[int(self.xy[0])+1][int(self.xy[1])+1]=self.marcas[tipo]
            sip=True
        else:
            sip=False
        return sip

    def veoCon3(self,gan):
        final=False
        for i in range(3):  # Pasa por toda la matriz
            if (self.t[i,:]==gan).all():    # Verifica filas completas
                final=True; break
            elif (self.t[:,i]==gan).all():  # Verifica columnas completas
                final=True; break
        if (np.diag(self.t)==gan).all():    # Diagonal de la matriz
            final=True
        elif (np.diag(np.fliplr(self.t))==gan).all():   # Diagonal inversa
            final=True
        return final  # Devuelve verdadero si es que alguien ganó
    
    def veoCon5(self,gan):
        final=False
        aux=np.zeros((5,5),dtype=np.int)    # Matriz auxiliar para verificar la diagonal de 5
        for i in range(10):  # Pasa por toda la matriz
            for j in range(5):
                if (self.t[i,j:j+5]==gan).all():    # Verifica filas completas
                    final=True; break
                elif (self.t[j:j+5,i]==gan).all():  # Verifica columnas completas
                    final=True; break
                if i<=5:
                    aux=self.t[i:i+5,j:j+5]
                    if (np.diag(aux)==gan).all():
                        final=True
                    elif (np.diag(np.fliplr(aux))==gan).all():
                        final=True
        return final  # Devuelve verdadero si es que alguien ganó

    def empate(self):
        if (self.t!=0).all():
            return True
        else:
            return False

    def tiempoPartida(self,tiempo): # Mensaje de tiemop
        mensaje="" 
        if tiempo<60:   # Si el tiempo es menor a los 60 seg. envia el mensaje
            mensaje="\tTiempo de juego: {0:.2f} seg.".format(float(tiempo))
        else:
            mensaje="\tTiempo de juego: {} min. ".format(int(tiempo/60))
            mensaje=mensaje+"{} seg.".format(int(tiempo%60))
        return mensaje