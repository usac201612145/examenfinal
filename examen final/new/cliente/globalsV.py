#-------------------------------------Retardos-----------------------------------

timeAlive = 1             #JDBM Tiempo para indicar que el ciente esta en linea, se multiplica o divide depende de lo que se necesita
tiempolimite = 20         #JDBM Limite para desconectarse sino se recibe respuesta

#-------------------------------------Comandos-----------------------------------

FRR     = '\x02'            #JDBM Comando FRR
FTR     = '\x03'            #JDBM Comando FTR
alive   = '\x04'            #JDBM Comando alive
ack     = '\x05'            #JDBM Comando ack
ok      = '\x06'            #JDBM Comando OK
no      = '\x07'            #JDBM Comando NO

#-------------------------------------TOPICS-------------------------------------

tcomandos = "comandos/15/"
tusuarios = "usuarios/15/"


#-------------------------------------Otros--------------------------------------

contadorAlive = 0