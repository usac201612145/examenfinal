"""
-----------
Examen Final - Grupo 15
-----------
SERVIDOR - PMJO
-----------
"""

import paho.mqtt.client as mqtt
import logging    
import binascii
import threading #JDBM Concurrencia con hilos
import os 
import socket
import datetime
import time
from globales import *

server_socket = socket.socket()
server_socket.bind((SERVER_ADDR, SERVER_PORT))
server_socket.listen(1) # PMJO 1 conexion activa

# Configuracion inicial de logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )

# Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, rc):
    logging.info("Conectado al broker")

# Handler en caso se publique satisfactoriamente en el broker MQTT
def on_publish(client, userdata, mid): 
    publishText = "✓✓"
    logging.info(publishText)

# PMJO - JCAG - JDBM - funcion de recepcion con condicionantes
# para el manejo corrrecto dependiendo del topico al que llegue el mensaje
def on_message(client, userdata, msg):
    #PMJO separacion de comandos
    strtopic = str(msg.topic)
    listOfTopic = strtopic.split('/')
    
    strmsg = msg.payload                    # JCAG
    strmsg = strmsg.decode()                #Convierte mensaje en string     
    listOfText = strmsg.split('$')          #Divide el mensaje en una lista

    if 'comandos' in listOfTopic:
        logging.debug("Se recibio comando")
        logging.debug(msg.topic)
        if COMMAND_FTR in listOfText:
            logging.debug('Se recibio FTR')
            server.setDest(listOfText[1])
            server.setSender(listOfTopic[2])
            server.setSize(listOfText[2])
            server.setFTR(True)
            # bandera = server.getFTR()
            # logging.debug(str(bandera))

        if COMMAND_ALIVE in listOfText:
            destAlive = listOfTopic[2]
            tramaALIVE = COMMAND_ACK+SEPARADOR+destAlive.encode()
            com.publicar("comandos/15",destAlive,tramaALIVE)
            now = datetime.datetime.now()
            hora = now.strftime("%S")
            server.setAlive(1,listOfTopic[2],hora)

#-----------------------------------------------------------------------------------------------------------
def fileRead(fileName):                                                                         
    archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA                                              
    data = []                                                                                               #|JDBM
    for linea in archivo: #Leer cada linea del archivo                                                      
        registro = linea.split(',')                                                                         #|Recorre archivo de configuracion    
        data.append(registro)                                                                               
    archivo.close() #Cerrar el archivo al finalizar                                                         
    return data  

####################
# PMJO control del Servidor
class servidor:
    usuariosconectados = [['10','10'],['20','20'],['30','30']]
    usuariosreg = []
    usuariosala = []
    state = False

    def setFTR(self,estado):
        self.estado = estado
        self.state = self.estado

    def getFTR(self):
        return self.state
    
    def setSalas(self,salas):
        self.salas = salas
        self.usuariosala.append(self.salas)

    def getSalas(self):
        return self.usuariosala
    
    def setUser(self,user):
        self.user = user
        self.usuariosreg.append(self.user)

    def getUser(self,num):
        self.num = num
        return self.usuariosreg[num]    

    def setAlive(self,numero,numerousuario,hora):
        self.numero = numero
        self.numerousuario = numerousuario
        self.hora = hora

        if(self.numero==0):
            self.usuariosconectados[0][0]=self.numerousuario
            self.usuariosconectados[0][1]=self.hora
        if(self.numero==1):
            self.usuariosconectados[1][0]=self.numerousuario
            self.usuariosconectados[1][1]=self.hora
        if(self.numero==2):
            self.usuariosconectados[2][0]=self.numerousuario
            self.usuariosconectados[2][1]=self.hora

    # def getAlive(self,buscado):
    #     for i in range(3):
    #         if(buscado==self.usuariosconectados[i][0]):
    #             return True
    #         else:
    #             return False

    def separar(self,trama,separador):
        self.trama = trama
        datos = []
        registro = self.trama.split(separador)
        datos.append(registro)
        return datos
    
    def setDest(self,dest):
        self.dest = dest

    def getDest(self):
        destino = self.dest
        return destino
    
    def setSender(self,remitente):
        self.remitente = remitente

    def getSender(self):
        sender = self.remitente
        return sender

    def setSize(self,tamanio):
        self.tamanio = tamanio

    def getSize(self):
        archivoSize = self.tamanio
        return archivoSize
    
    def getTamano(self,archivo='temporal.wav'):
        tamano = os.stat(archivo).st_size
        return str(tamano)
    
    def leer(self,listado):
        self.listado = listado
        datos = []
        archivo = open(self.listado, 'r')
        for linea in archivo:
            registro = linea.split(',')
            registro[-1] = registro[-1].replace('\n', '')  
            datos.append(registro)
        archivo.close()
        return datos

########################


# JCAG
#Clase para el manejo del suscripcion
class ClientManagment:
    def __init__(self, user, destino,  text, fsize):
        self.user = user
        self.destino = destino                         
        self.text = text
        self.fsize = fsize

    #Funcion para suscribirse a un topic, se suscribe con el usuario al que se envia, esta funcion se usa cuando 
    # se selcciona la opcion de texto
    def ClientSubsMsg(self):
        client.subscribe(("comandos/15/"+str(self.user), qos)) 
        return

# PMJO Control de comandos del servidor
class comandos(object):
    def __init__(self,datos=''):
        self.datos = datos

    def publicar(self, topicRoot, topicName, value, qos = 0, retain = False):
        topic = topicRoot + "/" + topicName
        client.publish(topic, value, qos, retain)
    
    def leer(self):
        data = conn.recv(BUFFER_SIZE)
        return data

    def enviar(self,data):
        self.data = data
        conn.sendall(data)

#-------------------------------------------------------------------------------------------------------------------------------------A 
# PMJO
# INICIO DE CLIENTE MQTT
client = mqtt.Client(clean_session=True) 
client.on_connect = on_connect
client.on_publish = on_publish 
client.on_message = on_message 
client.username_pw_set(MQTT_USER, MQTT_PASS) 
client.connect(host=MQTT_HOST, port = MQTT_PORT) 

qos = 0
server = servidor()
com = comandos()  
#-----------------------------------------------------------------------------------------------------------

#Se lee el archivo de usuarios, para usar el carne que esta en el archivo                      
subs = fileRead('usuarios')                                                                   
for i in range(len(subs)):
    subsa = subs[i]                                                                               
    usuario = subsa[0]          
    usuario = usuario.strip()                    #|PMJO                                                                                                  
    # Subscripcion simple con tupla (topic,qos)  #|Subscricion topics de archivo de configuracion
    # Se crea el objeto send de la clase ClienteManagment
    send = ClientManagment(usuario,0,0,0)
    logging.debug(usuario)
    ClientManagment.ClientSubsMsg(send)                   

for i in range(len(subs)):
    sublistasala = []
    subsa = subs[i]
    sublistasala.append(subsa[0])
    for j in range(2,len(subsa)):
        subsala = subsa[j].strip()
        sublistasala.append(subsala)
    server.setSalas(sublistasala)
salasssss=server.getSalas()
logging.debug("Salas son: "+str(salasssss))



#------------------------------------------------------------------------------------------------------------
client.loop_start()
#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa
#------------------------------------------------------------------------------------------------------------  

try:
      
    while True:     #Este codigo lo ejecutamos siempre para mantener el menu constante y seleccionar entre texto, audio
        logging.info("Esperando comando FTR...")
        time.sleep(1)
        bandera = server.getFTR()
        logging.debug(bandera)
        if(bandera==True):
            logging.info("Se desea mandar un archivo de audio")
            dest = server.getDest()
            logging.debug("El destino es:"+str(dest))
            sender = server.getSender()
            logging.debug("El remitente es:"+str(sender))
            fSize = server.getSize()
            logging.debug("El tamaño es:"+str(fSize))
            #if(server.getAlive(dest)):
            if(True):
                logging.debug("Enviando OK")
                tramaOK = COMMAND_OK+SEPARADOR+sender.encode()
                com.publicar('comandos/15',str(sender),tramaOK)
                logging.debug("\nEsperando conexion remota...\n")
                conn, addr = server_socket.accept()
                logging.debug('Conexion establecida desde '+str(addr))
                buff = com.leer()
                currentSize = 0
                archivo = open('temporal.wav', 'wb') #PMJO aqui se guarda el archivo
                while buff:
                    #logging.debug(str(buff))
                    currentSize += len(buff)
                    logging.debug(currentSize)
                    logging.debug(len(buff))
                    archivo.write(buff)
                    buff = com.leer()
                archivo.close()
                # PMJO envio de ACK
                tramaACK = COMMAND_ACK+SEPARADOR+sender.encode()
                com.publicar('comandos/15',str(sender),tramaACK)
                # PMJO se desconecta del cliente que envia el archivo
                conn.close()
                fSize = server.getTamano()
                if(len(dest)>5):
                    logging.debug("se quiere enviar a usuario")
                    tramaFRR = COMMAND_FRR+SEPARADOR+sender.encode()+SEPARADOR+fSize.encode()
                    com.publicar('comandos/15',str(dest),tramaFRR)
                    logging.debug("\nEsperando conexion remota...\n")
                    conn, addr = server_socket.accept()
                    logging.debug('Conexion establecida desde '+str(addr))
                    logging.debug('Transfiriendo archivo')
                    with open('temporal.wav', 'rb') as f:
                        data = f.read()
                        com.enviar(data)
                    logging.debug("Transferencia finalizada, cerrando conexion..")
                    conn.close()
                    server.setFTR(False)
                else:
                    logging.debug("Se quiere enviar a sala")
                    salas = server.getSalas()
                    for i in range(len(salas)):
                        salita = salas[i]
                        logging.debug(salita)
                        if dest in salita:
                            newdest = salita[0]
                            logging.debug("El nuevo destino es:"+newdest)
                            tramaFRR = COMMAND_FRR+SEPARADOR+sender.encode()+SEPARADOR+fSize.encode()
                            com.publicar('comandos/15',str(newdest),tramaFRR)
                            logging.debug("\nEsperando conexion remota...\n")
                            conn, addr = server_socket.accept()
                            logging.debug('Conexion establecida desde '+str(addr))
                            logging.debug('Transfiriendo archivo')
                            with open('temporal.wav', 'rb') as f:
                                data = f.read()
                                com.enviar(data)
                            logging.debug("Transferencia finalizada, cerrando conexion..")
                            conn.close()
                            server.setFTR(False)
            else:
                # PMJO se rechaza el envio de archivo al servidor
                #com = comandos()
                tramaNO = COMMAND_NO+SEPARADOR+sender.encode()
                com.publicar('comandos/15',str(sender),tramaNO)
                logging.info("Se rechaza la conexion, no hay destinatario activo")
                server.setFTR(False)
        else:
            server.setFTR(False)
            time.sleep(1)
                                                                                                 
#----------------------------------------------------------------------------------------------------------------------------

except KeyboardInterrupt:
    logging.warning("\nDesconectando del broker...")

finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")