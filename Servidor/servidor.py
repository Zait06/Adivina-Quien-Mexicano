'''
    Autores:
        Hernández López Ángel Zait
        Luciano Espina Melisa
'''
import os
import sys
import time
import socket
import select
import logging
import threading
from os import path
from adivinaQuien import *

logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-10s) %(message)s',)

class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.lock = threading.Lock()        
        self.active = []


    def makeActive(self,name,conn):    # Obtencion del candado
        self.lock.acquire()
        self.active.append(name)
        logging.debug('Turno obtenido')
        conn.sendall(str.encode('play'))
        f=open("respuesta.wav", "wb")     # Se crea un archivo de audio donde se guardará el archivo
        # Si hay datos a recibir, seguir escribiendo
        dato=conn.recv(8).decode()
        dato = dato.split('-')
        tamReciv=int(dato[0])
        datoAud=bytearray()

        logging.debug("Informacion recibida...")
        #datoAud=conn.recv(tamReciv)

        while len(datoAud) < tamReciv:
            logging.debug("Recibiendo ...")
            packet = conn.recv(tamReciv-len(datoAud))
            if not packet:
                return None
            logging.debug("Extendido...")
            datoAud.extend(packet)
        f.write(datoAud)
        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "respuesta.wav")

        
    def makeInactive(self,name,num,jue):     # Verificacion y liberacion del candado
        self.active.remove(name)
        acabado=jue.convAudText()              # El audio recibido, se manda a texto y verifica si alguien ha adivinado
        logging.debug('Liberando candado')        
        self.libera()
        if acabado:
            logging.debug(str(acabado))
        return acabado,name

    def libera(self):   # Liberacion del candado
        logging.debug("Candado liberado")
        self.lock.release()

class Servidor():
    def __init__(self,host,port,juga):
        self.HOST=host; self.PORT=int(port)             # IP y Puerto del servidor
        self.juga=int(juga); self.hayGanador=False      # num. jugadores y bandera por si hay un ganador
        self.serveraddr=(self.HOST,self.PORT)                # Dirección del servidor
        self.contador=1; self.numPistas=1
        self.listConec=list(); self.listHilos=list()	# Lista de conexiones recibidas e hilos
        self.pool=ActivePool(); self.ganador="" # pool=objeto de los candados; ganador=nombre del ganador
        self.sema=threading.Semaphore(1)    # creacion del semaforo con un proceso a la vez
        self.adqu=AdivinaQuien(juga)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.ServerTCP:   # Crea socket TCP
            self.ServerTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)     # No bloqueante
            self.ServerTCP.bind(self.serveraddr)                                    # Servidor a la escucha
            self.ServerTCP.listen(self.juga)
            os.system("cls")
            print("Servidor TCP a la escucha con direccion IP "+str(self.HOST))
            self.servirPorSiempre(self.ServerTCP)

    def servirPorSiempre(self,servidor):
        logging.debug("Esperando a los jugadores...")
        bandera=True
        try:
            j=1
            while True:
                conn,addr=servidor.accept()	# Coneccion y direccion del cliente
                # logging.debug("Conectado a: {}".format(addr))
                self.listConec.append(conn)

                if len(self.listHilos)<self.juga:
                    logging.debug('Conectando con Jugador-'+str(j)+' con direccion {}'.format(addr))
                    hilo_jugador=threading.Thread(name='Jugador-'+str(j),
                                                target=self.iniciarJuego,
                                                args=(conn,addr,j,self.pool,self.sema),)
                    self.listHilos.append(hilo_jugador)

                if len(self.listHilos)==self.juga and bandera:
                    logging.debug("Creando juego")
                    for t in self.listHilos:
                        t.start()
                        time.sleep(1)
                    bandera=False
                
                if len(self.listConec)>self.juga:
                    conn.sendall(bytes('Jugadores completos','ascii'))
                    self.listConec.remove(conn)
                    conn.close()

                self.gestion_conexiones(self.listConec)
                j+=1

        except Exception as e:
            print(e)

    def gestion_conexiones(self,listaConn):
        for conn in listaConn:
            if conn.fileno()==-1:
                self.listConec.remove(conn)

    def iniciarJuego(self,conn,addr,num,pool,s):
        logging.debug("Listo para jugar")
        try:
            conn.sendall(bytes('go','ascii'))
            conn.sendall(self.adqu.pistaPersonaje(self.numPistas))   # Manda la pista a todos los jugadores
            while not self.hayGanador:  # Si no hay un ganador, seguiremos jugando
                logging.debug("Esperando turno")
                time.sleep(1)
                with s:
                    if not self.hayGanador: # Si no hay un ganador, podemos jugar el turno
                        name=threading.currentThread().getName()    # nombre del jugador actual
                        time.sleep(1)
                        pool.makeActive(name,conn)    # Espera de tiro
                        time.sleep(1)
                        self.hayGanador,self.ganador=pool.makeInactive(name,num,self.adqu)
                        self.contador+=1
                        conn.sendall(bytes('otrotur','ascii'))  # Mensaje para que espere el tiro de los demas
                        conn.sendall("Espera la respuesta de los otros jugadores".encode())   # Mensaje de espera al cliente
                time.sleep(1)
                if self.numPistas<=5:   # Si el numero de las pistas es menor a 5 podemos mandar las otras
                    if (self.contador-1)==self.juga:    # Si el contador es igual al numero de jugadores,
                        self.numPistas+=1           # Envio las pistas a los demas
                        for i in self.listConec:  # Manda siguiente pista
                            i.sendall(bytes(self.adqu.pistaPersonaje(self.numPistas)))
                            time.sleep(1)
                        self.contador=0
                elif self.numPistas>5:
                    break
            conn.sendall(bytes('fin','ascii'))
            conn.sendall(bytes('Juego terminado\n','ascii'))
            name=threading.currentThread().getName()    # nombre del jugador actual
            conn.sendall(bytes(name,'ascii'))
            time.sleep(2)
            conn.sendall(bytes(self.ganador,'ascii'))
        except Exception as e:
            print(e)
        finally:
            conn.close()

s=Servidor(sys.argv[1],sys.argv[2],sys.argv[3])