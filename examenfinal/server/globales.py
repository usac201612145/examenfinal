#Parametros de conexion
MQTT_HOST = "167.71.243.238"
MQTT_PORT = 1883

#Credenciales
#Se acostumbra solicitar al usuario que ingrese su user/pass
#no es buena practica dejar escritas en el codigo las credenciales
MQTT_USER = "proyectos"
MQTT_PASS = "proyectos980"

ALIVE_PERIOD = 2 #Período entre envío de tramas ALIVE
ALIVE_CONTINUOUS = 0.1 #Período entre envío de tramas ALIVE si no hay respuesta

#COMMANDS
COMMAND_FRR = b'\x02'
COMMAND_FTR = '\x03'
COMMAND_ALIVE = '\x04'
COMMAND_ACK = b'\x05'
COMMAND_OK = b'\x06'
COMMAND_NO = b'\x07'
Command_FRR = '02'
command_FTR = '03'
command_ALIVE = '04'
command_ACK = '05'
command_OK = '06'
command_NO = '07'
SEPARADOR = b'$'


#System filenames
USERS_FILENAME = 'usuarios'
ROOMS_FILENAME = 'salas'


SERVER_ADDR = "167.71.243.238"
SERVER_PORT = 9815


BUFFER_SIZE = 64 * 1024 # PMJO 64 KB para buffer de transferencia de archivos
