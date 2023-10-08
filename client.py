import socket

#configuracion del cliente
host = "127.0.0.1" #ip del servidor al cual va a hacer la peticion
port = 12345 #puerto del server a donde haŕa la peticion

#crear el socket UDP
client_socket  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#pedir inicio de sesion
message = "inicio"
while True:
    
    #enviar el mensaje al servidor
    client_socket.sendto(message.encode("utf-8"), (host, port))
    
    #recibe la respuesta del servidor (esto es opcional)
    response, server_add = client_socket.recvfrom(1024)
    print(f"Servidor ({server_add[0]}:{server_add[1]}): {response.decode('utf-8')}")
    
    message = input("$")
    
    if message.lower() == "q":
        break