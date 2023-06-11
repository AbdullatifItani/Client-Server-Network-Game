# Client 
import socket
HOST = '127.0.0.1'
Port = 5000

s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket Created")
s.connect((HOST,Port))
print("Connected")  ## Mahdi wrote the initial client and everyone debugged it
data = s.recv(8196)
data = data.decode() 
print(data)
while True:
    data = s.recv(8196)
    data = data.decode()
    isdigit = data.isdigit()
    if data == "The Game Has Ended!": # The game has ended and we exit
        print(data)
        break
    elif isdigit: # We recieved a digit so the game is still going
        print("THE NUMBER GENERATED IS: ", data)
        to_send = input("ENTER THE NUMBER GENERATED ASAP: ")
        to_send = str.encode(to_send)
        s.sendall(to_send)
    elif data == "You have quitted the game and lost":
        print(data)
        break
    else: # We recieved a message so we print it
        print(data)
s.close()