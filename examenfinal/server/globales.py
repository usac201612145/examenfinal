# Parametros de conexion
MQTT_HOST = "167.71.243.238"
MQTT_PORT = 1883

# Credenciales
MQTT_USER = "proyectos"
MQTT_PASS = "proyectos980"

# COMMANDS
COMMAND_FRR = b'\x02'
COMMAND_FTR = '\x03'
COMMAND_ALIVE = '\x04'
COMMAND_ACK = b'\x05'
COMMAND_OK = b'\x06'
COMMAND_NO = b'\x07'
SEPARADOR = b'$'

# System filenames
USERS_FILENAME = 'usuarios'

# Datos para conexion por TCP
SERVER_ADDR = "167.71.243.238"
SERVER_PORT = 9815

# PMJO 64 KB para buffer de transferencia de archivos
BUFFER_SIZE = 64 * 1024 