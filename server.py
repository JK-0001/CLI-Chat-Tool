import json
import socket, pickle
from _thread import *
import sys
import threading

clients = []
chatRooms = []
chatHistory = []


def clientThread(connection, ip, port, max_buffer_size = 5120):
   is_active = True
   while is_active:
      decoded_input = pickle.loads(connection.recv(max_buffer_size))
      if "--quit--" in decoded_input:
         print("Client is requesting to quit")
         
         connection.close()
         
         selected_clients = []
         for room in chatRooms:
            for client in room['clients']:
               if port == client['port']:
                  selected_clients = room['clients']

         for i, c in enumerate(clients):
            if "closed" in str(c):
               clients.pop(i)
               
         leaving_client = []
         leaving_room = ''
         for room in chatRooms:
            for j, roomClients in enumerate(room['clients']):
               if port == roomClients['port']:
                  leaving_client = roomClients
                  leaving_room = room['room_no']     
                  room['clients'].pop(j)
         
         for ch in chatHistory:
            if ch["room_no"] == leaving_room:
               ch['chats'].append(leaving_client['client_name'] + " has left the chat!")
               with open(f"{leaving_room}.txt", 'w') as f:
                  # json.dump(ch['chats'], f)
                  for chat in ch['chats']:
                     f.write(chat + '\n')
         
         for client in selected_clients:
            for c in clients:
               if client["port"] in str(c):
                  data = pickle.dumps(leaving_client['client_name'] + " has left the chat!")
                  c.send(data)  
               
         print("Connection " + ip + ":" + port + " closed")
         is_active = False
         
      elif "1" in decoded_input:
         if len(chatRooms) == 0:
            data = pickle.dumps("No chat rooms to show")
            connection.send(data)
         else:
            data = pickle.dumps(chatRooms)
            connection.send(data)
            
      elif "2" in decoded_input:
         data = pickle.loads(connection.recv(5120))
         exists = 0
         for room in chatRooms:
            if data['room_no'] == room['room_no']:
               connection.send(pickle.dumps("Room with this number already exist!"))
               exists = 1
         if exists == 0:
            chatRooms.append({
               "room_no": data["room_no"],
               "room_name": data["room_name"],
               "clients": [{
                  "client_name": data["clients"],
                  "port": port
               }]
            })
            
            joined = data["clients"] + " has joined the chat!"
            chatHistory.append({"room_no": data["room_no"],
                                "chats": [data["clients"] + " has joined the chat!"]})
            for ch in chatHistory:
               if ch["room_no"] == data['room_no']:
                  with open(f"{data['room_no']}.txt", 'w') as f:
                     # json.dump(ch['chats'], f)
                     for chat in ch['chats']:
                        f.write(chat + '\n')
            connection.send(pickle.dumps(joined))
         
      elif "3" in decoded_input:
         data = pickle.dumps(chatRooms)
         connection.send(data)
         receivedData = pickle.loads(connection.recv(5120))
         if receivedData == "No Chat room available! Create a new chat room.":
            print("No chat room available!")
         elif receivedData == "No chat room available in this number!":
            print("No chat room available")
         else:
            for room in chatRooms:
               if room['room_no'] == receivedData['room_no']:
                  room['clients'].append({
                  "client_name": receivedData['client_name'],
                  "port": port
                  })
                  
            selected_clients = []
            selected_room = ''
            for room in chatRooms:
               for client in room['clients']:
                  if receivedData['client_name'] in client['client_name']:
                     selected_room = room['room_no']
                     selected_clients = room['clients']
            
            for client in selected_clients:
               for c in clients:
                  if client["port"] in str(c):
                     joined = receivedData['client_name'] + " has joined the chat!"
                     c.send(pickle.dumps(joined))
            
            for ch in chatHistory:
               if ch["room_no"] == selected_room:
                  ch['chats'].append(receivedData['client_name'] + " has joined the chat!")
               with open(f"{selected_room}.txt", 'w') as f:
                  # json.dump(ch['chats'], f)
                  for chat in ch['chats']:
                     f.write(chat + '\n')
         
      else:
         selected_clients = []
         selected_room = ''
         for room in chatRooms:
            for client in room['clients']:
               if client['client_name'] in decoded_input:
                  selected_room = room['room_no']
                  selected_clients = room['clients']
               
         for client in selected_clients:
            for c in clients:
               if client["port"] in str(c):
                  c.send(pickle.dumps(decoded_input))
         
         for ch in chatHistory:
            if ch["room_no"] == selected_room:
               ch['chats'].append(decoded_input)
            with open(f"{selected_room}.txt", 'w') as f:
               for chat in ch['chats']:
                  f.write(chat + "\n")
         
         
    
def Main():
   
    host = ""
    port = 5001
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port))

    s.listen(5)
    print("Waiting for connections...")

    while True:
    
        connection, addr = s.accept()
        ip, port = str(addr[0]), str(addr[1])
        print("Got connection from: ", addr)
        
        # print_lock.acquire()
        print("Connected to : ", addr[0], ":", addr[1])
        
        clients.append(connection)
        threading.Thread(target=clientThread, args=(connection, ip, port)).start()
            
        # start_new_thread(threaded, (c,))
    
    s.close()
    
if __name__ == "__main__":
    Main()