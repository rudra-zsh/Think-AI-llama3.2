import json
import time
import datetime
import ollama
import tkinter as tk
from tkinter import scrolledtext

MEMORY_FILE = "memory.json"
MODEL_NAME = "llama3.2"

# Initialize memory file if it doesn't exist
try:
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    memory = []

def log_message(role, message):
    """Logs messages to memory.json."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory.append({"timestamp": timestamp, "role": role, "message": message})
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def get_full_memory():
    """Returns the conversation history as a string."""
    return "\n".join(f"{msg['timestamp']} {msg['role']}: {msg['message']}" for msg in memory)

def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return
    
    chat_display.insert(tk.END, f"You >> {user_input}\n", "user")
    entry.delete(0, tk.END)
    log_message("User", user_input)
    
    if user_input.lower() == "/bye":
        chat_display.insert(tk.END, "\nFinalizing conversation. Generating summary...\n", "bot")
        full_memory = get_full_memory()
        response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": "Summarize this conversation briefly:\n" + full_memory}])
        summary_text = response["message"]["content"]
        chat_display.insert(tk.END, f"\nSummary: {summary_text}\n\nGoodbye!\n", "bot")
        log_message("You", summary_text)
        return
    
    full_memory = get_full_memory()
    prompt = f"Here is our full conversation history:\n{full_memory}\nUser: {user_input}"
    chat_display.insert(tk.END, "\nThink:\n>> ", "bot")
    
    response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
    ai_response = response["message"]["content"]
    
    for char in ai_response:
        chat_display.insert(tk.END, char, "bot")
        chat_display.update()
        time.sleep(0.02)
    chat_display.insert(tk.END, "\n", "bot")
    
    log_message("You", ai_response)

# GUI Setup
root = tk.Tk()
root.title("AI Chatbot")
root.geometry("500x600")
root.configure(bg="#2C2F33")

chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, bg="#23272A", fg="white", font=("Arial", 12))
chat_display.tag_config("user", foreground="#00FF00")
chat_display.tag_config("bot", foreground="#FFFF00")
chat_display.pack(pady=10)

entry = tk.Entry(root, width=50, font=("Arial", 12), bg="#40444B", fg="white")
entry.pack(pady=5)
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(root, text="Send", command=send_message, bg="#7289DA", fg="white", font=("Arial", 12))
send_button.pack()

root.mainloop()

