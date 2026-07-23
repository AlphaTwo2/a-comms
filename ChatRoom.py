# COMMUNCATIONS PROGRAM, MADE BY ALPHA-TWO

# IMPORTS
import threading, socket
import customtkinter as CTk
import sys, os

#-------------------------------------#
# SETUP
root = CTk.CTk()
root.title("A-comms")
root.geometry("510x600")

# LOGO
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root.iconbitmap(resource_path("assets/logo.ico"))

#-------------------------------------#
# Variables
server_running = False
port = ""
fallback_port = 59000
fallback_address = None
address = ""
connected = False
debug_job = None

max_msgs = 17
max_username_length = 30
max_msg_length = 40
entry_width = 140
button_width = 140

#-------------------------------------#
# Lists
clients = []
nicknames = []
messages = []

#-------------------------------------#
# FUNCTIONS SERVER
def startserver():
    global server, server_running, nickname, address,fallback_address, port

    if entry_username.get() == "":
        print("Please choose a nickname first")
        debug_message("Please choose a nickname first")
        return
    
    try:
        message_user = entry_username.get()
        if len(message_user) <= max_username_length:
            server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

            address = entry_address.get()
            if address == "":
                address = fallback_address # must be set manually in the code

            port = entry_port.get()
            if port == "":
                port = fallback_port
            else:
                port = int(port)
            
            UI_connected()

            server.bind((address,port))
            server.listen()
            print("Server SUCCESFULLY started!")
            debug_message("Server succesfully started!")
            server_running = True
            label_connection.configure(text="HOSTING")
            entry_username.configure(state='disabled')

            thread = threading.Thread(target=receive, daemon=True)
            thread.start()
            
            choose_client()

        else:
            print("Your username is too long!")
            debug_message("Your username is too long!")

    except:
        print("Server FAILED to start!")
        debug_message("Server FAILED to start")

        #Layout
        UI_reset()


def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            pass

# Function to handle client's connection
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)

            if not message: # If message is empty (bytes) meaning connection closed
                raise Exception # jump straight down to exception block

            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} has left the chat room!".encode("utf-8"))
            nicknames.remove(nickname)
            break

def receive():
    global address

    print("Server is running and listening...")
    debug_message("Server is running and listening...")
    while server_running:
        try:
            client,address = server.accept()
        except:
            break
        print(f"connection is established with {str(address)}")
        debug_message(f"Connection is established with {str(address)}")
        client.send("Nickname: ".encode("utf-8"))
        nickname = client.recv(1024).decode("utf-8") # max bytes server recieves from single client
        nicknames.append(nickname)
        clients.append(client)
        print(f"The nickname of this client is {nickname}")
        broadcast(f"{nickname} has connected to the chatroom".encode("utf-8"))
        client.send("You are now connected!".encode("utf-8"))
        thread = threading.Thread(target = handle_client, args=(client,),daemon=True)
        thread.start()

#-------------------------------------#
# FUNCTIONS CLIENT
def choose_client():
    global client, nickname, address, connected,fallback_address, port
    
    try:
        if not server_running:
            address = entry_address.get()
            if address == "":
                address = fallback_address
            
        port = entry_port.get()
        if port == "":
            port = fallback_port
        else:
            port = int(port)    

        nickname = entry_username.get()
        
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((address,port))

        #UI
        UI_connected()
        but_send.configure(state="normal")

        # Threading
        recieve_thread = threading.Thread(target=client_recieve, daemon=True)
        recieve_thread.start()

        label_connection.configure(text=f"Connected to: {address}")
        connected = True
    except:
        print("That server does not exist!")
        debug_message("That server does not exist!")

def client_recieve():
    global client, connected
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message == "Nickname: ":
                client.send(nickname.encode("utf-8"))
            else:
                root.after(0,update_chat,message)
        except:
            if connected:
                print("Error!")
                debug_message("Error!")
            try:
                client.close()
            except:
                pass

            break

def update_chat(message):
    messages.append(message)
    if len(messages) > max_msgs:
        messages.pop(0)   
    text = ""
    for msg in messages:
        text += msg + "\n"
    
    label_recieve.configure(text=text)

def client_send():
    global client
    try:
        message_text = entry_message.get()
        if message_text != "" and len(message_text) <= max_msg_length:
            message = f"{nickname}: {message_text}"

            client.send(message.encode("utf-8"))

            entry_message.delete(0,"end")
        else:
            print("Your message is invalid")
            debug_message("Your message is invalid!")
    except:
        print("You are not connected yet!")
        debug_message("You are not connected yet!")

#-------------------------------------#
# FUNCTIONS GENERAL
def UI_connected(): # cleans UI when user joins a server
    entry_address.grid_remove()
    entry_port.grid_remove()
    label_address.grid_remove()
    label_port.grid_remove()

    but_host_server.grid_remove()
    but_join_server.grid_remove()
    but_disconnect.grid()

def UI_reset(): # resets UI back to normal
    entry_address.grid()
    entry_port.grid()
    label_address.grid()
    label_port.grid()
    entry_message.delete(0, "end")

    but_host_server.grid()
    but_join_server.grid()
    but_disconnect.grid_remove()
    label_connection.configure(text="")

def disconnect():
    global server, server_running, clients, nicknames, messages, connected

    UI_reset()

    if server_running:
        debug_message("Server closed")
        clients = []
        nicknames = []
        messages = []
        server_running = False
        server.close()
        connected = False
    else:
        connected = False
        client.close()
        debug_message("Client disconnected")

    messages.clear()
    label_recieve.configure(text="")

    entry_username.configure(state='normal')
    but_send.configure(state="disabled")

def check_length_text():
    # MESSAGE LENGTH:
    length_text = len(entry_message.get())
    label_text_length.configure(text=f"{length_text}/{max_msg_length}")

    if length_text >= max_msg_length+1:
        label_text_length.configure(text_color = "#C80F0F")
    else:
        label_text_length.configure(text_color = "#FFFFFF")

    # USERNAME LENGTH:
    length_user = len(entry_username.get())
    label_username_length.configure(text=f"{length_user}/{max_username_length}")

    if length_user >= max_username_length+1:
        label_username_length.configure(text_color = "#C80F0F")
    else:
        label_username_length.configure(text_color = "#FFFFFF")


def on_key_release(event):
    check_length_text()

    key_name = event.keysym
    if key_name == "Return":
        client_send()

# DEBUG logic
def clear_debug():
    label_debug.configure(text="")

def debug_message(text):
    global debug_job

    def show():
        global debug_job

        label_debug.configure(text=text)

        if debug_job:
            root.after_cancel(debug_job)

        debug_job = root.after(1800, clear_debug)

    root.after(0,show)

#-------------------------------------#
##### LAYOUT #####

main_frame = CTk.CTkFrame(root)
main_frame.grid(padx=10,pady=10)

#----------#
# HOST / JOIN
but_host_server = CTk.CTkButton(main_frame, text="HOST",width=button_width,command=startserver)
but_host_server.grid(column=0, row=1,pady=10)

but_join_server = CTk.CTkButton(main_frame, text="JOIN",width=button_width,command=choose_client)
but_join_server.grid(column=0, row=3,pady=10)

#----------#
# ADDRESS ENTRY AND TEXT FOR HOSTING/JOINING
label_address = CTk.CTkLabel(main_frame, text="ADDRESS:")
label_address.grid(column=1, row=1, sticky="W",padx=(5,0))

entry_address = CTk.CTkEntry(main_frame, width=entry_width)
entry_address.grid(column=1,row=1,sticky="W",padx=(80, 0))

#----------#
# PORT ENTRY AND TEXT FOR HOSTING/JOINING
label_port = CTk.CTkLabel(main_frame, text="PORT:")
label_port.grid(column=1, row=3, sticky="W",padx=(5,0))

entry_port = CTk.CTkEntry(main_frame, width=entry_width)
entry_port.grid(column=1,row=3,sticky="W",padx=(80, 0))

#----------#
# Send message input
label_send = CTk.CTkLabel(main_frame, text="Message:",width=entry_width)
label_send.grid(column=0, row=7, columnspan=4, sticky="W")

entry_message = CTk.CTkEntry(main_frame, width=entry_width)
entry_message.grid(column=0,row=8,columnspan=4,sticky="W")

but_send = CTk.CTkButton(main_frame, text="Send",command=client_send)
but_send.grid(column=1, row=8)
but_send.configure(state="disabled")

#----------#
# RECIEVE label
label_recieve = CTk.CTkLabel(main_frame, text="", fg_color="#FFFFFF",text_color="black", width= 490, height=250, anchor="nw",justify="left")
label_recieve.grid(column=0, row=11, columnspan=4, sticky="EW",pady=10)

#----------#
# DEBUG label
label_debug = CTk.CTkLabel(main_frame, text="", fg_color="transparent",text_color="white",width=100, height=10,anchor="nw",justify="left")
label_debug.grid(column=0, row=10, columnspan=4, sticky="EW",pady=5,padx=10)

#----------#
# USERNAME
label_username = CTk.CTkLabel(main_frame, text="Username:",width=entry_width)
label_username.grid(column=0, row=4, columnspan=4, sticky="W")

entry_username = CTk.CTkEntry(main_frame, width=entry_width)
entry_username.grid(column=0,row=5,columnspan=4,sticky="W")

#----------#
# Connection/Host info label (text)
label_connection = CTk.CTkLabel(main_frame, text="")
label_connection.grid(column=1, row=1, columnspan=4, sticky="W")

but_disconnect = CTk.CTkButton(main_frame, text="DISCONNECT",width=button_width,command=disconnect)
but_disconnect.grid(column=0, row=1,pady=10,sticky="W",padx=15)
but_disconnect.grid_remove()

#----------#
# Keyrealeses
entry_message.bind('<KeyRelease>',on_key_release)
entry_username.bind('<KeyRelease>',on_key_release)

#----------#
# Length of message
label_text_length = CTk.CTkLabel(main_frame,text=f"0/{max_msg_length}",width=entry_width)
label_text_length.grid(column=0, row=9, columnspan=4, sticky="W")

label_username_length = CTk.CTkLabel(main_frame,text=f"0/{max_username_length}",width=entry_width)
label_username_length.grid(column=0, row=6, columnspan=4, sticky="W")
#----------#
#CREDITS
label_username = CTk.CTkLabel(main_frame, text="Application made by Alpha-Two",width=entry_width)
label_username.grid(column=0, row=12, columnspan=4, sticky="W")

#-------------------------------------#
root.mainloop()