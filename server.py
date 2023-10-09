import socket
import multiprocessing
import os
from usuario import Usuario

# Configuración del servidor
host = "127.0.0.1"
port = 12345

# Crear el socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enlazar el socket a la dirección IP y el puerto
server_socket.bind((host, port))

print("Escuchando por el puerto 12345...")

# Utilizamos un multiprocessing.Manager para crear listas compartidas
manager = multiprocessing.Manager()
clientes = manager.list([])
ocupados = manager.list([12345])

clientes.append(Usuario("Spaladines", "123", "", 1))

# Cola para compartir datos entre procesos
cola_de_comunicacion = multiprocessing.Queue()

def escucharPuerto(puerto, client_add, cola, clientes, ocupados):
    sv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sv_socket.bind((host, puerto))

    cliente = None
    sesion = False

    while True:
        try:
            nuevos_clientes, nuevos_ocupados = cola.get_nowait()
            clientes[:] = nuevos_clientes
            ocupados[:] = nuevos_ocupados
        except Exception:
            pass

        # Pedir usuario
        response = f"Ingrese su usuario: {puerto}"
        sv_socket.sendto(response.encode("utf-8"), client_add)
        data, client_add = sv_socket.recvfrom(1024)

        usr = data.decode("utf-8")

        existe = False
        contador = 0
        for usuario in clientes:
            if usr == usuario.nombre:
                cliente = usuario
                existe = True
                break
            
        if existe:
            nuevos_clientes = [u for u in clientes if u.nombre != cliente.nombre]
            clientes[:] = nuevos_clientes
            
            # Pedir contraseña
            response = f"Contraseña para {cliente.nombre}"
            sv_socket.sendto(response.encode("utf-8"), client_add)
            data, client_add = sv_socket.recvfrom(1024)

            if data.decode("utf-8") == cliente.password:
                sesion = True
            else:
                contador = 1
                while cliente.password != data.decode("utf-8") and contador < 3:
                    # Pedir contraseña
                    response = f"Contraseña incorrecta, intente denuevo"
                    sv_socket.sendto(response.encode("utf-8"), client_add)
                    data, client_add = sv_socket.recvfrom(1024)

                    if data.decode("utf-8") == cliente.password:
                        sesion = True
                        break

                    contador += 1

                if contador > 3:
                    response = f"Demasiados intentos con contraseña incorrecta"
                    sv_socket.sendto(response.encode("utf-8"), client_add)
                    break

            if sesion:
                # Si se logeó
                response = f"""
                Logeado con éxito, Bienvenido denuevo {cliente.nombre}
                Listado de comandos:
                m -a <mensaje> <- enviar un mensaje a todos los usuarios
                m -u <nombre_usuario> <mensaje> enviar mensaje a un usuario en específico
                h <- listar comandos
                q <- salir
                """
                sv_socket.sendto(response.encode("utf-8"), client_add)
                cliente.add = client_add[0]
                cliente.port = client_add[1]

                clientes.append(cliente)
                    
            break

        else:
            response = f"El usuario no existe, ¿desea crear uno Nuevo [Y/n]?"
            sv_socket.sendto(response.encode("utf-8"), client_add)
            data, client_add = sv_socket.recvfrom(1024)

            if data.decode("utf-8").lower() == "y":
                response = f"Ingrese la nueva Contraseña"
                sv_socket.sendto(response.encode("utf-8"), client_add)
                data, client_add = sv_socket.recvfrom(1024)

                cliente = Usuario(usr, data.decode("utf-8"), client_add[0], client_add[1])
                clientes.append(cliente)

                response = f"Bienvenido {cliente.nombre}"
                sv_socket.sendto(response.encode("utf-8"), client_add)

                sesion = True

                ocupados.append(puerto)

            break

    cola.put((clientes, ocupados))

    while sesion:
        try:
            nuevos_clientes, nuevos_ocupados = cola.get_nowait()
            clientes[:] = nuevos_clientes
            ocupados[:] = nuevos_ocupados
        except Exception:
            pass

        data, client_add = sv_socket.recvfrom(1024)

        # Muestra el mensaje del cliente
        print(f"Cliente ({client_add[0]}:{client_add[1]}): {data}")

        comando = data.decode("utf-8")

        if comando == "q":
            response = f"""{puerto}@{cliente.nombre}
            Hasta la próxima
            """
            break
        elif comando == "h":
            response = f"""{puerto}@{cliente.nombre}
                Listado de comandos:
                m -a <mensaje> <- enviar un mensaje a todos los usuarios
                m -u <nombre_usuario> <mensaje> enviar mensaje a un usuario en específico
                h <- listar comandos
                q <- salir
                """
        elif len(comando) > 2:
            response = f"""{puerto}@{cliente.nombre}"""
            comando = comando.split(" ")

            if comando[0] == "m" and comando[1] == "-a":
                comando = " ".join(comando[2:])
                msg = f"""
                {cliente.nombre} dice:
                {comando}
                """
                for ur in clientes:
                    print(ur.nombre)
                    sv_socket.sendto(msg.encode("utf-8"), (ur.add, ur.port))

            elif comando[0] == "m" and comando[1] == "-u":
                ur = comando[2]
                comando = " ".join(comando[3:])
                msg = f"""
                {cliente.nombre} dice:
                {comando}
                """
                for cl in clientes:
                    print(cl.nombre)
                    if cl.nombre == ur:
                        sv_socket.sendto(msg.encode("utf-8"), (cl.add, cl.port))
                        break
        else:
            response = f"""{puerto}@{cliente.nombre}"""

        # Responder al cliente
        sv_socket.sendto(response.encode("utf-8"), client_add)

    sv_socket.close()
    ocupados.remove(puerto)
    cola.put((clientes, ocupados))
    os._exit(0)

def asignarPuerto(client_add):
    libre = 0
    for i in range(12345, 12445):
        if not i in ocupados:
            libre = i
            ocupados.append(libre)
            break

    if libre != 0:
        response = str(libre)
        proceso = multiprocessing.Process(target=escucharPuerto, args=(libre, client_add, cola_de_comunicacion, clientes, ocupados))
        proceso.start()

    else:
        response = "12345"

    server_socket.sendto(response.encode("utf-8"), client_add)

while True:
    # Obtener los datos del cliente
    data, client_add = server_socket.recvfrom(1024)

    # Decodificar los datos
    message = data.decode("utf-8")

    # Muestra el mensaje del cliente
    print(f"Cliente ({client_add[0]}:{client_add[1]}): Iniciando Sesión...")

    asignarPuerto(client_add)