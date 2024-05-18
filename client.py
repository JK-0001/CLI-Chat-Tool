import socket, pickle, threading    

def recv_messages(connection: socket.socket):
    try:
        while True:
            msg = pickle.loads(connection.recv(5120))
            if msg:
                print(msg)
            else:
                connection.close()
                break
    except:
        print("Connection closed")

def Main():
    
    host = "64.227.166.49"
    port = 5001        

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    
    receive = threading.Thread(target=recv_messages, args=[s])
    
    print("Welcome to CLI Chat Tool")
    client_name = str(input("Type your username & press enter to continue:\n"))
    
    print("You can create a new chat room or join an existing chat room")
    print("1. List all chat rooms")
    print("2. Create a new chat room")
    print("3. Join an existing chat room")
    selected_option = input("Enter your option:\n")
    data = []
    
    while selected_option == '1' or selected_option == '2' or selected_option == '3':    
        if selected_option == '1':
            while selected_option == '1':
                s.send(pickle.dumps(selected_option))
                data = pickle.loads(s.recv(5120))
                if data == "No chat rooms to show":
                    print(data)
                    print("You can create a new chat room or join an existing chat room")
                    print("1. List all chat rooms")
                    print("2. Create a new chat room")
                    print("3. Join an existing chat room")
                    selected_option = input("Enter your option:\n")
                elif data != "No chat rooms to show":
                    print("Room Number | Room Name") 
                    for obj in data:
                        print(obj['room_no'], "|", obj['room_name'])
                    print("You can create a new chat room or join an existing chat room")
                    print("1. List all chat rooms")
                    print("2. Create a new chat room")
                    print("3. Join an existing chat room")
                    selected_option = input("Enter your option:\n")
        if selected_option == '2':
            s.send(pickle.dumps(selected_option))
            room_number = input("Enter the new chat room number:\n")
            room_name = input("Enter the new chat room name:\n")
            chat_room = {
                "room_no": room_number,
                "room_name": room_name,
                "clients": client_name
            }
            data = pickle.dumps(chat_room)
            s.send(data)
            receivedData = pickle.loads(s.recv(5120))
            if receivedData == 'Room with this number already exist!':
                print("Room with this number already exist! Choose a different number!")
                print("You can create a new chat room or join an existing chat room")
                print("1. List all chat rooms")
                print("2. Create a new chat room")
                print("3. Join an existing chat room")
                selected_option = input("Enter your option:\n")
            else:
                print("You're currently on chat room number", room_number)
                print("Welcome", client_name, "If you ever want to quit, type {--quit--} to exit")
                print(receivedData)
                selected_option = 4
        if selected_option == '3':
            s.send(pickle.dumps(selected_option))
            join_room = input("Enter a room number you want to join\n")
            data = pickle.loads(s.recv(5120))
            exist = 0
            if data:  
                for obj in data:
                    if obj['room_no'] == join_room:
                        sending_data = {
                            "room_no": obj['room_no'],
                            "client_name": client_name
                        }
                        data = pickle.dumps(sending_data)
                        s.send(data)
                        print("You're currently on chat room number", obj['room_no'])
                        print("Welcome", client_name, "If you ever want to quit, type {--quit--} to exit")
                        exist = 1
                        selected_option = 4
                if exist == 0:
                    data = pickle.dumps("No chat room available in this number!")
                    s.send(data)
                    print("No chat room available in this number!")
                    print("You can create a new chat room or join an existing chat room")
                    print("1. List all chat rooms")
                    print("2. Create a new chat room")
                    print("3. Join an existing chat room")
                    selected_option = input("Enter your option:\n")
                        
            else:
                data = pickle.dumps("No Chat room available! Create a new chat room.")
                s.send(data)
                print("No Chat room available! Create a new chat room.")
                print("You can create a new chat room or join an existing chat room")
                print("1. List all chat rooms")
                print("2. Create a new chat room")
                print("3. Join an existing chat room")
                selected_option = input("Enter your option:\n")
            
    receive.start()
    
    while True:
        message = input("")
        
        data = client_name + ": " + message
        s.send(pickle.dumps(data))

        if message == '--quit--':
            break
        
    s.close()


            
if __name__ == "__main__":
    Main()