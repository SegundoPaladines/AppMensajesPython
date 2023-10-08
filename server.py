import socket

#configuracion del servidor
host = "127.0.0.1" #ip del server
port = 12345  #puerto por donde el server está escuchando

#crear el socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#enlazar el socket a la direccion ip y el puerto
server_socket.bind((host, port))

print("Escuchando por el puerto 12345...")

clientes = []

while True:
    #obtener los datos del cliente
    data, client_add = server_socket.recvfrom(1024)
    
    #Decodificar los datos
    message = data.decode("utf-8")
    
    #Muestra el mensaje del cliente
    print(f"Cliente ({client_add[0]}: {client_add[1]}): {message}")
    
    #Responder al cliente (opcional)
    response = "Ingrese su nombre de usuario"
    server_socket.sendto(response.encode("utf-8"), client_add)