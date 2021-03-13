'''
    Autores:
        Hernández López Ángel Zait
        Luciano Espina Melisa
'''
import os
import sys
import wave
import pyaudio
import random as rand
import speech_recognition as sr

class AdivinaQuien():
    def __init__(self,numJuga):
        self.persDoc=""
        self.personaje=list()
        self.pistas=list()
        self.numJuga=numJuga
        self.r=sr.Recognizer()
        self.elegirPersonaje()

    def elegirPersonaje(self):
        a=rand.randrange(5)
        if a==0:    
            self.persDoc="Porfirio Diaz.txt"
            self.personaje=["porfirio díaz","porfirio diaz"]
        elif a==1:
            self.persDoc="Francisco I Madero.txt"
            self.personaje=["francisco i madero","francisco imadero"]
        elif a==2:
            self.persDoc="Emiliano Zapata.txt"
            self.personaje=["emiliano zapata","emiliano zapata"]
        elif a==3:
            self.persDoc="Venustiano Carranza.txt"
            self.personaje=["venustiano carranza","venustiano carranza" ]
        elif a==4:
            self.persDoc="Francisco Villa.txt"
            self.personaje=["francisco villa","pancho villa"]

#Convierte el audio a texto
    def convAudText(self):
        #La respuesta se convierte en .wav
        respuesta = sr.AudioFile('respuesta.wav')
        with respuesta as source:
            audio=self.r.record(source)
        texto=self.r.recognize_google(audio,language='es-mx',show_all=True)
        listaTexto=texto['alternative']
        #Guarda las respuestas recibidas en una lista
        listaRespuestas=list()
        for i in listaTexto:
            listaRespuestas.append(i['transcript'].lower())
        return self.verifica(listaRespuestas)

    def pistaPersonaje(self,line):
        f=open(self.persDoc,'rb')
        i=1; psta=""
        for linea in f.readlines():
            if i==line:
                psta=linea
                break
            i+=1
        return psta

#Verifica si la lista de los personajes es igual a los que se tiene en las respuestas
    def verifica(self,listaPersona):
        ganador=False
        print(listaPersona)
        for pp in listaPersona:
            if pp==self.personaje[0] or pp==self.personaje[1]:
                print("Hay un ganador")
                ganador=True
                break
        return ganador