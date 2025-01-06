import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

SERVER = '127.0.0.1'
PORT = 8080

class ChatClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Klient Chat")
        self.master.geometry("600x500")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.chat_frame = tk.Frame(self.master)
        self.chat_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, state='disabled', wrap=tk.WORD)
        self.chat_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.message_entry = tk.Entry(self.chat_frame)
        self.message_entry.pack(padx=5, pady=(0, 5), fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.chat_frame, text="Wyślij", command=self.send_message)
        self.send_button.pack(pady=(0, 5))

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client.connect((SERVER, PORT))
            self.username = simpledialog.askstring("Nazwa użytkownika", "Podaj swoją nazwę użytkownika:", parent=self.master)
            if not self.username:
                raise ValueError("Nazwa użytkownika jest wymagana.")
            self.client.send(self.username.encode())
            response = self.client.recv(1024).decode()
            if response.startswith("Nazwa użytkownika jest już zajęta"):
                messagebox.showerror("Błąd", response)
                self.master.destroy()
                return

            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się połączyć z serwerem: {e}")
            self.master.destroy()

    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode()
                self.display_message(msg)
            except:
                self.display_message("Połączenie z serwerem zostało przerwane.")
                self.client.close()
                break

    def send_message(self, event=None):
        msg = self.message_entry.get()
        if msg:
            try:
                self.client.send(msg.encode())
                self.message_entry.delete(0, tk.END)
            except:
                messagebox.showerror("Błąd", "Nie udało się wysłać wiadomości. Połączenie z serwerem zostało przerwane.")
                self.master.destroy()

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def on_closing(self):
        try:
            self.client.close()
        except:
            pass
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()
