import socket

# Configuración del cliente
host = "127.0.0.1"
port = 12345

# Crear el socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = ""

def pedirPuerto():
    message = "puerto"
    client_socket.sendto(message.encode("utf-8"), (host, port))

    response, server_add = client_socket.recvfrom(1024)

    response = response.decode("utf-8")

    return int(response)

while True:
    if port != 12345:
        # Enviar el mensaje al servidor
        client_socket.sendto(message.encode("utf-8"), (host, port))
        
        # Recibe la respuesta del servidor (esto es opcional)
        response, server_add = client_socket.recvfrom(1024)
        
        print(f"Servidor ({server_add[0]}:{server_add[1]}): {response.decode('utf-8')}")
        
        # Enviar mensaje
        message = input("$")

        if message.lower() == "q":
            break
        
    else:
        port = pedirPuerto()

client_socket.close()