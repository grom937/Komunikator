import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ChatServer:
    def __init__(self):
        self.clients = {}  # Przechowywanie nazw użytkowników i ich połączeń
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 8080))
        self.server.listen(5)

        # GUI
        self.window = tk.Tk()
        self.window.title("Serwer Chat")

        # Lista użytkowników
        self.users_list = tk.Listbox(self.window, width=30)
        self.users_list.pack(side=tk.LEFT, fill=tk.Y)

        # Pole tekstowe czatu
        self.chat_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, state='disabled')
        self.chat_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Pole do wprowadzania wiadomości
        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.msg_entry = tk.Entry(self.input_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        # Przycisk "Wyślij do wybranego użytkownika"
        self.send_button_user = tk.Button(
            self.input_frame,
            text="Wyślij",
            command=self.send_to_selected_user
        )
        self.send_button_user.pack(side=tk.LEFT, padx=5, pady=5)

        # Przycisk "Wyślij do wszystkich"
        self.send_button_all = tk.Button(
            self.input_frame,
            text="Wyślij do wszystkich",
            command=self.send_broadcast_message
        )
        self.send_button_all.pack(side=tk.LEFT, padx=5, pady=5)

        threading.Thread(target=self.accept_connections, daemon=True).start()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()

    def accept_connections(self):
        while True:
            client, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

    def handle_client(self, client):
        # Zapytaj o nazwę użytkownika
        client.send("Podaj swoją nazwę użytkownika:".encode("utf8"))
        username = client.recv(1024).decode("utf8").strip()

        if not username or username in self.clients:
            client.send("Nazwa użytkownika jest już zajęta lub niepoprawna. Rozłączono.".encode("utf8"))
            client.close()
            return

        self.clients[username] = client
        self.update_user_list()
        self.broadcast(f"{username} dołączył do czatu.", "Serwer")

        while True:
            try:
                msg = client.recv(1024).decode("utf8")
                if msg:
                    self.broadcast(f"{username}: {msg}")
            except:
                client.close()
                del self.clients[username]
                self.update_user_list()
                self.broadcast(f"{username} opuścił czat.", "Serwer")
                break

    def broadcast(self, msg, sender="Serwer"):
        self.display_message(msg)
        for client in self.clients.values():
            try:
                client.send(msg.encode("utf8"))
            except:
                pass

    def send_to_user(self, username, msg):
        if username in self.clients:
            try:
                self.clients[username].send(msg.encode("utf8"))
                self.display_message(f"Serwer -> {username}: {msg}")
            except:
                pass
        else:
            self.display_message(f"Nie można wysłać wiadomości do użytkownika: {username}")

    def send_to_selected_user(self):
        selected_user = self.users_list.get(tk.ACTIVE)
        msg = self.msg_entry.get()
        if selected_user and msg:
            self.send_to_user(selected_user, f"Serwer: {msg}")
            self.msg_entry.delete(0, tk.END)

    def send_broadcast_message(self):
        msg = self.msg_entry.get()
        if msg:
            self.broadcast(f"Serwer: {msg}")
            self.msg_entry.delete(0, tk.END)

    def display_message(self, msg):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, msg + '\n')
        self.chat_area.config(state='disabled')
        self.save_message_to_file(msg)

    def save_message_to_file(self, message):
        with open("chat_log.txt", "a", encoding="utf-8") as file:
            file.write(message + "\n")

    def update_user_list(self):
        self.users_list.delete(0, tk.END)
        for user in self.clients.keys():
            self.users_list.insert(tk.END, user)

    def on_close(self):
        self.server.close()
        self.window.destroy()

if __name__ == "__main__":
    ChatServer()
