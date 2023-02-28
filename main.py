import socket
import threading
import rsa
import tkinter as tk

class ChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("Messaging App")
        
        self.label = tk.Label(master, text="Enter '1' to host or '2' to connect")
        self.label.pack()

        self.entry = tk.Entry(master)
        self.entry.pack()

        self.button = tk.Button(master, text="Connect", command=self.connect)
        self.button.pack()

        self.text = tk.Text(master)
        self.text.pack()

        self.message_entry = tk.Entry(master)
        self.message_entry.pack()

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack()
        
        self.master = master
        master.title("Messaging App")
        
        self.public_key, self.private_key = rsa.newkeys(1024)
        self.public_partner = None

        self.button = tk.Button(master, text="Exit", command=self.exit_program)
        self.button.pack()

    def exit_program(self):
        self.master.destroy()

    def connect(self):
        option = self.entry.get()

        if option == "1":
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(("192.168.56.1", 9999))
            self.server.listen()

            self.client, _ = self.server.accept()
            self.client.send(self.public_key.save_pkcs1("PEM"))
            self.public_partner = rsa.PublicKey.load_pkcs1(self.client.recv(1024))
            self.text.insert(tk.END, "Connected to client.\n")
        elif option == "2":
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(("192.168.56.1", 9999))
            self.public_partner = rsa.PublicKey.load_pkcs1(self.client.recv(1024))
            self.client.send(self.public_key.save_pkcs1("PEM"))
            self.text.insert(tk.END, "Connected to server.\n")
        else:
            self.text.insert(tk.END, "Please enter either '1' or '2'.\n")
            return

        if self.public_partner is None:
            self.text.insert(tk.END, "Failed to establish public key with partner.\n")
            return

        threading.Thread(target=self.receive_message).start()

    def send_message(self):
        message = self.message_entry.get()
        encrypted_message = rsa.encrypt(message.encode(), self.public_partner)
        #encrypted_message = message.encode() #no-encryption
        self.client.send(encrypted_message)
        self.text.insert(tk.END, "You: " + message + "\n")
        self.message_entry.delete(0, tk.END)

    def receive_message(self):
        while True:
            try:
                received_message = self.client.recv(1024)
                if not received_message:
                    self.text.insert(tk.END, "Partner has disconnected.\n")
                    break
                decrypted_message = rsa.decrypt(received_message, self.private_key).decode()
                #decrypted_message = received_message.decode() #no-decryption
                self.text.insert(tk.END, "Partner: " + decrypted_message + "\n")
            except rsa.pkcs1.DecryptionError:
                self.text.insert(tk.END, "Failed to decrypt message from partner.\n")
            except socket.error:
                self.text.insert(tk.END, "Connection to partner lost.\n")
                break

root = tk.Tk()
gui = ChatGUI(root)
root.mainloop()