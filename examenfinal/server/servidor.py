"""
-----------
Examen Final - Grupo 15
-----------
SERVIDOR - PMJO
-----------
"""
# PMJO Optimizado para 5 usuarios

import paho.mqtt.client as mqtt
import logging    
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
    level = logging.INFO, 
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
# para el manejo corrrecto dependiendo del mensaje que llegue al topico comandos
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
        logging.debug(msg.payload)

        # PMJO condicional para manejo de comando FTR, se guardan los 
        # datos de destino, remitente y tamaño de archivo
        if COMMAND_FTR in listOfText:
            logging.debug('Se recibio FTR')
            server.setDest(listOfText[1])
            server.setSender(listOfTopic[2])
            server.setSize(listOfText[2])
            server.setFTR(True)

        # PMJO condicional para manejo de comando ALIVE, se contesta con un ACK y se guarda 
        # el timestamp del momento en que llego el ALIVE para luego poder comparar el ultimo 
        # timestamp con el actual timestamp
        if COMMAND_ALIVE in listOfText:
            logging.debug("Se recibio ALIVE")
            destAlive = listOfTopic[2]
            logging.debug(destAlive)
            tramaAckALIVE = COMMAND_ACK+SEPARADOR+destAlive.encode()
            com.publicar("comandos/15",destAlive,tramaAckALIVE)
            now = datetime.datetime.now()
            hora = now.strftime("%S")
            clasificados = server.getSalas()
            for i in range(len(clasificados)):
                nuevoClasificado = clasificados[i]
                if(nuevoClasificado[0]==listOfTopic[2]):
                    server.setAlive(i,listOfTopic[2],hora)

#-----------------------------------------------------------------------------------------------------------
# JDBM funcion para la lectura del archivo usuarios
def fileRead(fileName):                                                                         
    archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA                                              
    data = []                                                 #|JDBM
    for linea in archivo: #Leer cada linea del archivo                                                      
        registro = linea.split(',')                           #|Recorre archivo de configuracion    
        data.append(registro)                                                                               
    archivo.close() #Cerrar el archivo al finalizar                                                         
    return data  

# PMJO clase para el control del Servidor
class servidor:
    usuariosconectados = [['10','10'],['20','20'],['30','30'],['40','40'],['50','50']]
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

    def setAlive(self,numero,numerousuario,hora):
        self.numero = numero
        self.numerousuario = numerousuario
        self.hora = hora
        self.usuariosconectados[self.numero][0]=self.numerousuario
        self.usuariosconectados[self.numero][1]=self.hora

    # PMJO metodo en donde se compara el timestamp actual y el ultimo timestamp 
    # guardado cuando se recibio el comando ALIVE
    def getAlive(self,buscado):
        self.buscado = buscado
        for i in range(len(self.usuariosconectados)):
            if(self.buscado==self.usuariosconectados[i][0]):
                now = datetime.datetime.now()
                hora = now.strftime("%S")
                if(abs(int(hora)-int(self.usuariosconectados[i][1]))<6):
                    return True
                else:
                    return False

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
    
    # JDBM metodo para obtener el tamaño del archivo recibido
    def getTamano(self,archivo='temporal.wav'):
        tamano = os.stat(archivo).st_size
        return str(tamano)

#--------------------------------------------------------------
# JCAG clase para el manejo del suscripcion
class ServerManagment:
    def __init__(self, user, destino,  text, fsize):
        self.user = user
        self.destino = destino                         
        self.text = text
        self.fsize = fsize

    # JCAG Funcion para suscribirse a un topic
    def ServerSubsMsg(self):
        client.subscribe(("comandos/15/"+str(self.user), qos)) 
        return

# PMJO Clase para el control de comandos del servidor
class comandos(object):
    def __init__(self,datos=''):
        self.datos = datos

    # PMJO Metodo para la publicacion de comando en MQTT
    def publicar(self, topicRoot, topicName, value, qos = 0, retain = False):
        topic = topicRoot + "/" + topicName
        client.publish(topic, value, qos, retain)
    
    # PMJO metodo para recibir los datos por conexion TCP
    def leer(self):
        data = conn.recv(BUFFER_SIZE)
        return data

    # PMJO metodo para el envio de los datos por conexion TCP
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
# PMJO inicio de objetos
server = servidor()
com = comandos()  
#-----------------------------------------------------------------------------------------------------------

#Se lee el archivo de usuarios, para usar el carne que esta en el archivo                      
subs = fileRead(USERS_FILENAME)                                                                   
for i in range(len(subs)):
    subsa = subs[i]                                                                               
    usuario = subsa[0]          
    usuario = usuario.strip()                    #|JCAG - JDBM                                                                                                  
    # Subscripcion simple con tupla (topic,qos)  #|Subscricion topics de archivo de configuracion
    # Se crea el objeto send de la clase ServerManagment
    send = ServerManagment(usuario,0,0,0)
    logging.info("Suscribiendose al usuario: "+usuario)
    ServerManagment.ServerSubsMsg(send)                   

# PMJO ciclo para el llenado de informacion de usuarios y a que salas pertenecen
for i in range(len(subs)):
    sublistasala = []
    subsa = subs[i]
    sublistasala.append(subsa[0])
    for j in range(2,len(subsa)):
        subsala = subsa[j].strip()
        sublistasala.append(subsala)
    server.setSalas(sublistasala)

#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa
client.loop_start()
 
# --------------------  MAIN   ----------------------
# PMJO main en donde se realiza la recepcion y envio de archivo de audio a través de una conexion por TCP
# se chequea si el destino es un usuario o una sala. 
# ---------------------------------------------------
# Si es un usuario, se chequea si esta conectado y si esta 
# conectado se recibe el archivo del remitente por TCP, luego se manda FRR a destinatario y se envia archivo 
# por TCP. 
# ---------------------------------------------------
# Si el destino es una sala, se chequea los usuarios involucrados de esa sala y se chequea que esten conectados,
# si estan conectados se agregan a una lista y se va recorriendo la lista como nuevo destino para el envio del
# archivo por TCP. 
# ---------------------------------------------------
# Si en los dos casos no hay nadie conectado, se manda un NO y no se inicia la conexion por TCP.
# ------------------------------------------------------------------------------------------------------------
try:
    while True:
        logging.info("Esperando comando FTR...")
        logging.debug(str(server.usuariosconectados))
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
            if(len(dest)>5):
                logging.info("El audio se quiere enviar a usuario")
                if(server.getAlive(dest)):
                    logging.debug("Enviando OK")
                    tramaOK = COMMAND_OK+SEPARADOR+sender.encode()
                    com.publicar('comandos/15',str(sender),tramaOK)
                    logging.info("\nEsperando conexion remota...\n")
                    conn, addr = server_socket.accept()
                    logging.info('Conexion establecida desde '+str(addr))
                    buff = com.leer()
                    currentSize = 0
                    archivo = open('temporal.wav', 'wb') #PMJO aqui se guarda el archivo
                    while buff:
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
                    logging.info("Transferencia finalizada, cerrando conexion..")
                    fSize = server.getTamano()
                    logging.info("Comenzando conexion con el destinatario...")
                    tramaFRR = COMMAND_FRR+SEPARADOR+sender.encode()+SEPARADOR+fSize.encode()
                    com.publicar('comandos/15',str(dest),tramaFRR)
                    logging.info("\nEsperando conexion remota...\n")
                    conn, addr = server_socket.accept()
                    logging.info('Conexion establecida desde '+str(addr))
                    logging.info('Transfiriendo archivo')
                    with open('temporal.wav', 'rb') as f:
                        data = f.read()
                        com.enviar(data)
                    logging.info("Transferencia finalizada, cerrando conexion..")
                    conn.close()
                    server.setFTR(False)
                else:
                    # PMJO se rechaza el envio de archivo al servidor
                    tramaNO = COMMAND_NO+SEPARADOR+sender.encode()
                    com.publicar('comandos/15',str(sender),tramaNO)
                    logging.info("Se rechaza la conexion, no hay destinatario activo")
                    server.setFTR(False)
            else:
                logging.info("El audio se quiere enviar a sala")
                salas = server.getSalas()
                nuevodestino = []
                for i in range(len(salas)):
                    salausuario = salas[i]
                    logging.debug(salausuario)
                    if dest in salausuario:
                        newdest = salausuario[0]
                        if(server.getAlive(newdest)):
                            nuevodestino.append(newdest)
                if(len(nuevodestino)>0):
                    logging.debug("USUARIOS CONECTADOS DE LA SALA: "+str(len(nuevodestino)))
                    logging.debug("Enviando OK")
                    tramaOK = COMMAND_OK+SEPARADOR+sender.encode()
                    com.publicar('comandos/15',str(sender),tramaOK)
                    logging.info("\nEsperando conexion remota...\n")
                    conn, addr = server_socket.accept()
                    logging.info('Conexion establecida desde '+str(addr))
                    buff = com.leer()
                    currentSize = 0
                    archivo = open('temporal.wav', 'wb') #PMJO aqui se guarda el archivo
                    while buff:
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
                    logging.info("Transferencia finalizada, cerrando conexion..")
                    conn.close()
                    fSize = server.getTamano()
                    for i in range(len(nuevodestino)):
                        destinonuevo = nuevodestino[i]
                        logging.info("El nuevo destino de la sala es:"+destinonuevo)
                        tramaFRR = COMMAND_FRR+SEPARADOR+sender.encode()+SEPARADOR+fSize.encode()
                        com.publicar('comandos/15',str(destinonuevo),tramaFRR)
                        logging.info("\nEsperando conexion remota...\n")
                        conn, addr = server_socket.accept()
                        logging.info('Conexion establecida desde '+str(addr))
                        logging.info('Transfiriendo archivo')
                        with open('temporal.wav', 'rb') as f:
                            data = f.read()
                            com.enviar(data)
                        logging.info("Transferencia finalizada, cerrando conexion..")
                        conn.close()
                    server.setFTR(False)
                else:
                    # PMJO se rechaza el envio de archivo al servidor
                    tramaNO = COMMAND_NO+SEPARADOR+sender.encode()
                    com.publicar('comandos/15',str(sender),tramaNO)
                    logging.info("Se rechaza la conexion, no hay ningun destinatario activo en la sala")
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