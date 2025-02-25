import json
import time
import datetime
import ollama

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

print(f"Starting {MODEL_NAME} with memory...")
print("Type '/bye' to exit.")

while True:
    user_input = input("\nYou >> ").strip()
    
    if not user_input:
        continue  # Ignore empty input
    
    if user_input.lower() == "/bye":
        print("\nFinalizing conversation. Generating summary...\n")
        
        full_memory = get_full_memory()
        response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": "Summarize this conversation briefly:\n" + full_memory}])
        
        # Extract response text properly
        summary_text = response["message"]["content"]
        
        print("\nSummary: ")
        for char in summary_text:
            print(char, end="", flush=True)
            time.sleep(0.02)  # Simulate live output
        
        print("\n\nGoodbye!")
        log_message("User", user_input)
        log_message("You", summary_text)
        break

    # Prepare prompt with full conversation history
    full_memory = get_full_memory()
    prompt = f"Here is our full conversation history:\n{full_memory}\nUser: {user_input}"

    print("\nThink:\n>> ", end="", flush=True)
    
    # Generate response from Ollama (Streaming)
    response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
    
    # Extract response text properly
    ai_response = response["message"]["content"]
    
    for char in ai_response:
        print(char, end="", flush=True)
        time.sleep(0.02)  # Simulate real-time response
    
    print("\n")
    
    # Log the conversation
    log_message("User", user_input)
    log_message("You", ai_response)
