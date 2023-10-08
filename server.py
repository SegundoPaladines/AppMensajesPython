import socket
import multiprocessing
from usuario import Usuario
import os

# Configuración del servidor
host = "127.0.0.1"
port = 12345

# Crear el socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enlazar el socket a la dirección IP y el puerto
server_socket.bind((host, port))

print("Escuchando por el puerto 12345...")

clientes = [Usuario("Spaladines","123","","")]
ocupados = [12345]

# Cola para compartir datos entre procesos
cola_de_comunicacion = multiprocessing.Queue()

def escucharPuerto(puerto, client_add, cola):
    sv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sv_socket.bind((host, puerto))
    
    cliente = None
    sesion = False
    
    while True:
        #pedir usuario
        response = f"Ingrese su usuario: {puerto}"
        sv_socket.sendto(response.encode("utf-8"), client_add)
        data, client_add = sv_socket.recvfrom(1024)
        
        usr = data.decode("utf-8")
        
        existe = False
        
        for usuario in clientes:
            if(usr == usuario.nombre):
                cliente = usuario
                existe = True
                break
        
        if existe:
            #pedir contraseña
            response = f"Contraseña para {usuario.nombre}"
            sv_socket.sendto(response.encode("utf-8"), client_add)
            data, client_add = sv_socket.recvfrom(1024)
            
            if data.decode("utf-8") == usuario.password:
                sesion = True
            else:
                contador = 1
                while usuario.password != data.decode("utf-8") and contador < 3:
                    #pedir contraseña
                    response = f"Contraseña incorrecta, intente denuevo"
                    sv_socket.sendto(response.encode("utf-8"), client_add)
                    data, client_add = sv_socket.recvfrom(1024)
                    
                    if data.decode("utf-8") == usuario.password:
                        sesion = True
                        break
                    
                    contador += 1
                    
                if contador > 3:
                    response = f"Demaciados intentos con contraseña incorrecta"
                    sv_socket.sendto(response.encode("utf-8"), client_add)
                    break
            
            if sesion:
                #si se logeo
                response = f"""
                Logeado con exito, Bienvenido denuevo {cliente.nombre}
                Listado de comandos:
                m -a <- enviar un mensaje a todos los usuarios
                m -u <nombre_usuario> enviar mensaje a un usuario en especifico
                h <- listar comandos
                q <-salir
                """
                sv_socket.sendto(response.encode("utf-8"), client_add)
                usuario.add = client_add
                
                try:
                    ocupados.remove(usuario.port)
                
                except Exception as e:
                    print("Error No se pudo quitar el puerto ocupado")
                    
                usuario.port = puerto
                
            break
        
        else:
            response = f"El usuario no existe, desea crear uno Nuevo [Y/n]"
            sv_socket.sendto(response.encode("utf-8"), client_add)
            data, client_add = sv_socket.recvfrom(1024)
            
            if data.decode("utf-8").lower() == "y":
                response = f"Ingrese la nueva Contraseña"
                sv_socket.sendto(response.encode("utf-8"), client_add)
                data, client_add = sv_socket.recvfrom(1024)
                
                cliente = Usuario(usr, data.decode("utf-8"), client_add, puerto)
                clientes.append(cliente)
                
                response = f"Bienvenido {cliente.nombre}"
                sv_socket.sendto(response.encode("utf-8"), client_add)
                
                sesion = True

                break
    
    cola.put((clientes, ocupados))
       
    while sesion:
        try:
            nuevos_clientes, nuevos_ocupados = cola_de_comunicacion.get_nowait()
            clientes[:] = nuevos_clientes 
            ocupados[:] = nuevos_ocupados
            cola.put((clientes, ocupados))
            
        except Exception:
            pass
        
        data, client_add = sv_socket.recvfrom(1024) 
        # Muestra el mensaje del cliente
        print(f"Cliente ({client_add[0]}:{client_add[1]}): {data}")
        
        if data.decode("utf-8") == "q":
            break
        
        # Responder al cliente
        response = f"""{puerto}${cliente.nombre}"""
        sv_socket.sendto(response.encode("utf-8"), client_add)
        
        
    sv_socket.close()
    ocupados.remove(puerto)
    cola.put((clientes, ocupados))
    os._exit(0)

def asignarPuerto(client_add):
    
    libre = 0
    for i in range (12345, 12445):
        if not i in ocupados:
            libre = i
            ocupados.append(libre)
            break
    
    if libre != 0:
        response = str(libre)
        proceso = multiprocessing.Process(target=escucharPuerto, args=(libre, client_add, cola_de_comunicacion))
        proceso.start()
    
    else:
        response = "12345"
    
    server_socket.sendto(response.encode("utf-8"), client_add)

while True:
    try:
        nuevos_clientes, nuevos_ocupados = cola_de_comunicacion.get_nowait()
        clientes[:] = nuevos_clientes 
        ocupados[:] = nuevos_ocupados
            
    except Exception:
        pass
    
    # Obtener los datos del cliente
    data, client_add = server_socket.recvfrom(1024)
    
    # Decodificar los datos
    message = data.decode("utf-8")
    
    # Muestra el mensaje del cliente
    print(f"Cliente ({client_add[0]}:{client_add[1]}): Iniciando Sesion...")
    
    asignarPuerto(client_add)