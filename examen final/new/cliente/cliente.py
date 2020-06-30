"""
-----------
Parcial 2 - Grupo 15
-----------
"""
import paho.mqtt.client as mqtt
import logging    
from time import time 
import binascii
import threading #JDBM Concurrencia con hilos
import os 
from brokerData import * 
import socket
from globalsV import *
import base64 #Encriptacion
import time

#Datos para conectarse al socket
SERVER_ADDR = '167.71.243.238'
SERVER_PORT = 9815

BUFFER_SIZE = 8 * 1024 


#---------------------------------------JDBM CLASE PARA PUBLICAR ALIVE---------------------------------------------

class comandosCliente(object):
    
    def __init__(self, ctopic, ccomando, cusuario):
        self.ctopic = ctopic
        self.ccomando = ccomando
        self.cusuario = cusuario

    def gettopic(self):
        return self.ctopic

    def getcomando(self):

        return self.ccomando

    def getusuario(self):
        return self.cusuario

    def publicarAlive(self):
        mensaje = self.ccomando.encode()
        client.publish(self.ctopic + str(usuario), mensaje, qos = 0, retain = False)
        return
#----------------------------------------------------FIN-----------------------------------------------------------


#-----------------------------------JCGA FUNCION PARA RECIBIR EL AUDIO POR TCP-------------------------------------
def tcpsockreceive():
    sock = socket.socket()
    sock.connect((SERVER_ADDR, SERVER_PORT))

    try:
        buff = sock.recv(BUFFER_SIZE)
        archivo = open('recibido.wav', 'wb') #Aca se guarda el archivo entrante
        while buff:
            archivo.write(buff)
            buff = sock.recv(BUFFER_SIZE) #Los bloques se van agregando al archivo

        archivo.close() #Se cierra el archivo

        print("Recepcion de archivo finalizada")

    finally:
        print('Conexion al servidor finalizada')
        sock.close() #Se cierra el socket
        thread2 = Hilos(2, "Audio", 1, False) #Objeto para inicializar el hilo de Alive



#-------------------------------------JCGA FUNCION PARA ENVIAR EL AUDIO POR TCP-------------------------------------
def tcpsocksend():
    sock = socket.socket()
    sock.connect((SERVER_ADDR, SERVER_PORT))
    
    try:
        archivo = open("ola.wav", "rb")
        audiodata = archivo.read()
        archivo.close()
        data= audiodata
        sock.sendall(data)

    finally:

        print('Conexion al servidor finalizada')
        sock.close() #Se cierra el socket
#------------------------------------------------------FIN--------------------------------------------------------   

# Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '%(message)s'
    )

# Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, rc):
    logging.info("Conectado al broker")

# Handler en caso se publique satisfactoriamente en el broker MQTT
"""
def on_publish(client, userdata, mid): 
    publishText = "✓✓"
    logging.info(publishText)
"""

#------------------------------------#JDBM Recorre archivo de configuracion----------------------------------------
def fileRead(fileName):                                                                         
    archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA                                              
    data = []                                                                                               
    for linea in archivo: #Leer cada linea del archivo                                                      
        registro = linea.split(',')                                                                             
        data.append(registro)                                                                               
    archivo.close() #Cerrar el archivo al finalizar                                                         
    return data      

#--------------------------------------------------FIN------------------------------------------------------------

#----------------------------------------------#JCGA CLASE PARA MANEJAR COMANDOS----------------------------------
class ClientCommands(object):
    
    def __init__(self, csize , cusuario, cdestino):
        self.csize = csize
        self.cusuario = cusuario
        self.cdestino = cdestino

    def PFTR(self):
        if len(self.cdestino)<8:
            client.publish("comandos/15/"+str(self.cusuario), str(FTR)+"$"+'15'+str(self.cdestino)+"$"+str(self.csize), qos = 0, retain = False)  #JDBM En este caso, usuario es el destinantario
        else:
            client.publish("comandos/15/"+str(self.cusuario), str(FTR)+"$"+str(self.cdestino)+"$"+str(self.csize), qos = 0, retain = False)  #JDBM En este caso, usuario es el destinantario
        return


#--------------------------------------#PMJO Clase para el manejo del cliente--------------------------------------

class ClientManagment:
    def __init__(self, user, destino,  text, fsize):
        self.user = user
        self.destino = destino                         
        self.text = text
        self.fsize = fsize

    #Funcion para publicar en el topic de salas o a un usuario, se le envia el destino(sala o carnet) 
    # y el mensaje que se va enviar
    def ClientMessage(self):
        if len(self.destino)<8:

            client.publish("salas/15/"+str(self.destino), ' '+str(self.user)+' ('+str(self.destino)+')'+' >>>: '+str(self.text), qos = 0, retain = False)  

        else:     

            client.publish("usuarios/15/"+str(self.destino), ' '+str(self.user)+' >>>: '+str(self.text), qos = 0, retain = False)  
        
        return

    #Funcion para suscribirse a un topic, se suscribe con el usuario al que se envia, esta funcion se usa cuando 
    # se selcciona la opcion de texto
    def ClientSubsMsg(self):
        client.subscribe(("usuarios/15/"+str(self.user), qos)) 
        client.subscribe(("comandos/15/"+str(self.user), qos)) 
        #client.subscribe(("audio/15/"+str(self.user), qos)) 
        return
    
    #Funcion para suscribirse a las salas y al topic de audio. Esta funcion se usa cuando se selecciona en el menu
    #la opcion de enviar audio
    def ClientSubsSalas(self):
        client.subscribe(("salas/15/"+str(self.text), qos)) 
        #client.subscribe(("audio/15/"+str(self.text), qos))  # ELIMINAR 
        return

    # PMJO envio de audio convirtiendo la informacion del archivo a bytearray 
    # para asegurar el envio correcto
    def ClientAudio(self, duracion, destino):
        if int(duracion)>30:
            duracion = '30'
            logging.warning('No se puede mandar archivos de mas de 30s, se enviara de 30s')
        logging.debug(duracion)
        mensajeAudio = 'arecord -d ' + duracion + ' -f U8 -r 8000 ola.wav'
        os.system(mensajeAudio)
        file_name = "ola.wav"
        file_stats = os.stat(file_name)
        size = file_stats.st_size
        send = ClientCommands(size, usuario, destinatario)

        ClientCommands.PFTR(send)
        #tcpsocksend()
        return
    #def getencrip(self):
        #return self.encrip
#--------------------------------------------------FIN----------------------------------------------------------

#-----------------------------------------------PMJO------------------------------------------------------------
# INICIO DE CLIENTE MQTT
client = mqtt.Client(clean_session=True) 
client.on_connect = on_connect
#client.on_publish = on_publish 
client.username_pw_set(MQTT_USER, MQTT_PASS) 
client.connect(host=MQTT_HOST, port = MQTT_PORT) 

qos = 0

#------------------------PMJO Subscricion topics de archivo de configuracion-----------------------------------

#Se lee el archivo de usuarios, para usar el carne que esta en el archivo                      
subs = fileRead('usuarios')                                                                   
subs = subs[0]                                                                               
usuario = subs[0]          
usuario = usuario.strip()                                                                      
del subs[0]                                                                                                     
#Subscripcion simple con tupla (topic,qos)                                                     
#Se crea el objeto send de la clase ClienteManagment
send = ClientManagment(usuario,0,0,0)
ClientManagment.ClientSubsMsg(send)     


#Se lee el archivo de usuarios, para usar las salas que estan en el archivo y suscribirse al topic  
subs = fileRead('salas')
subs = subs[0]  
newsubs = []

#Se toma solo el dato de la sala, por ejemplo S01 del archivo de salas
for i in subs:
    subs = i.split("15")
    element = subs[1]
    newsubs.append(element.strip()) 

#Se realiza la suscripcion a los topics de las salas usan la clase ClienteManagment
for i in newsubs:    
    send = ClientManagment(0,0,i,0)                                                                                          
    ClientManagment.ClientSubsSalas(send)                                                       
                                                                                                            
#--------------------------------------------------FIN-------------------------------------------------------

client.loop_start()
#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa

#------------------------------------------------------------------------------------------------------------  

#-------------------------JDBM CLASE PARA EL MANEJO DE HILOS DE AUDIO, ALIVE Y ON_MESSAGE---------------------

class Hilos(threading.Thread):
    def __init__(self, threadID, name, delay, daemon):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.delay = delay
      self.flagAck = False
      
      threading.Thread.start(self)

      client.on_message = self.mensaje
      

    #AFUERA SE INSTANCIAN LOS OBJETOS QUE DAN LOS PARAMETROS PARA CONFIGURAR LOS HILOS
    def run(self):
      print ("Empezando " + self.name)
      if self.threadID == 1:
             return self.H_Alive()
      print ("Saliendo " + self.name)

      if self.threadID == 2:
             return self.audioManage()
      print ("Saliendo " + self.name)

    def mensaje(self, client, userdata, msg):


        strtopic = str(msg.topic)
        listOfTopic = strtopic.split('/')
        logging.debug(listOfTopic)
        
        encriptado = ClientManagment(0,0,0,0)
        #tipo = encriptado.getencrip()

        strmsg = msg.payload

        """
        if tipo == True:
            decod = base64.b32decode(strmsg)
            decod = decod.decode()
        elif tipo == False:
            decod = strmsg.decode()
        """
        decod = strmsg.decode()
  
        listOfText = decod.split('$')          #Divide el mensaje en una lista

        

        if 'usuarios' or 'salas' in listOfTopic:
            #logging.info(strmsg)
            pass
            if str(usuario) not in listOfText:      #Comprueba si el mensaje es enviado por el mismo
                print('\n'+decod)                  #Imprime el mensaje si esta comprobacion da como resultado false
                publishText = "✓✓"
                logging.info(publishText)
       

        if 'comandos' in listOfTopic:

            if FTR in listOfText:

                print('Se recibio FTR')
            
            if ok in listOfText:

                print('Se recibio OK')
                tcpsocksend()


            if no in listOfText:

                print('Se recibio NO')
                pass

            if FRR in listOfText:
                print('Se recibio FRR')
                tcpsockreceive()

            
            if ACK in listOfText:
                #print('Se recibio ACK')
                self.flagAck = True
                self.H_Alive()


        if str(usuario) not in listOfText:      #Comprueba si el mensaje es enviado por el mismo
            pass
            print('\n'+strmsg)                  #Imprime el mensaje si esta comprobacion da como resultado false
        

    def H_Alive(self): #HILO DE ALIVE
        cnt = 0
        cnt1 = 0
        ciclo = 0
        flag = False
        constdelay = 1
        periodAlive = 2
        contadorACKS = 0
        while True:

            cnt += 1
            logging.debug(constdelay)

            
            if self.flagAck == True:
                contadorACKS += 1
            else:
                pass

            if cnt == periodAlive:
                #logging.debug(constdelay)
                calive = alive + '$' + str(usuario)                 #JDBM:  Comando alive a enviar
                textoalive = comandosCliente(tcomandos,calive,0)    #JDBM:  Se crea el objeto texto y se le mandan los parametros de
                                                                    #JDBM:  direccion (topic) y el comando
                textoalive.publicarAlive()                          #JDBM:  Se llama a la funcion publicarAlive del objeto texto para publicar el comando
                #print('Se envio un ALIVE')
                ciclo += 1
                cnt = 0
                mensaje()

                if ciclo == 3:
                    if contadorACKS > 1:
                        contadorACKS = 0
                        ciclo = 0
                        flag = False
                    elif contadorACKS == 0:
                        periodAlive = 1
                        constdelay = 0.1
                        flag = True
                        ciclo = 0

                    if flag == True:
                        cnt1 += 1
                        #logging.debug(cnt1)
                        if cnt1 > 200:
                            logging.critical("NO SE PUDO ESTABLECER CONEXION CON EL SERVIDOR")
                            constdelay = 1
                            cnt1 = 0
                            flag = False
                            time.sleep(1)
                    elif flag == False:
                        pass

            time.sleep(self.delay*constdelay) #JDBM Delay en segundos

        # JDBM funcion de manejo de audio por medio de hilo
    def audioManage(self):
        logging.info("Reproduciendo Mensaje de Voz")
        message = 'aplay recibido.wav'
        os.system(message)
        logging.info("Mensaje de Voz reproducido")

#--------------------------------------------------FIN-------------------------------------------------------

thread1 = Hilos(1, "Alive", 1, False) #Objeto para inicializar el hilo de Alive

#------------------------ JCGA BUCLE PARA EL INGRESO DE COMANDOS, TEXTO Y MANEJO DEL MENU --------------------------

try:    
    while True:     #Este codigo lo ejecutamos siempre para mantener el menu constante y seleccionar entre texto, audio
                    # ingresar la duracion del audio, salirse del chat, etc.
        time.sleep(2)
        formato = input("(Audio/Texto): ")                                                                                            
        destinatario = input("Destino(2016xxxxx/S00): ")    
        pase = True                                                                     
                                                                                                                        
        if formato == 'Texto' or formato =='texto':                                                 #Interfaz de usuario primera version
            while pase:           
                time.sleep(2)                                                                                  #JCGA   
                mensaje = input("Tu: ")        
                if mensaje == 'salir':
                    pase = False     
                else:
                    #Al haber guardado los datos ingresados por el usuario, se usan los datos de usuario, destinatario y mensaje
                    #para enviarlos a los topics ingresados y publicarlos por MQTT

                    send=ClientManagment(usuario,destinatario,mensaje,0)  
                    ClientManagment.ClientMessage(send)

                    #JCAGA | JDBM
                    #Si el usuario selecciono que desea enviar audio, se ejecuta este elif para que ingrese la duracion del audio
        elif formato == 'Audio' or formato == 'audio': 
            duracionIn = input("Ingrese la duracion del mensaje: ")
            send=ClientManagment(usuario,destinatario,0,0)
            ClientManagment.ClientAudio(send, duracionIn, destinatario)
            #logging.info('Enviando audio')
                                                                                                 
#--------------------------------------------------------FIN-----------------------------------------------------------------

except KeyboardInterrupt:
    
    logging.info("Terminando hilos")
    
    try:
        if thread1.is_alive():
            thread1._stop()
    except DeprecationWarning:
        'Usuario desconectado'
    
finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")