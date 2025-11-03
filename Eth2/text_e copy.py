import subprocess
import signal
import shutil
import sys
import importlib
import re
from datetime import datetime
import tkinter as tk
import os
from tkinter.filedialog import askopenfilename, asksaveasfilename
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure()
#Configure the model to prefer plain text output
generation_config = genai.GenerationConfig(
    response_mime_type="text/plain",
)
model = genai.GenerativeModel('gemini-2.5-pro',generation_config=generation_config)

new_app_process = None

def install_libraries_from_new_app():
    """
    Reads D:/Workspace/Eth2/new_app.py, detects imported libraries,
    and installs them into the current virtual environment.
    """
    file_path = r"D:/Workspace/Eth2/new_app.py"

    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return

    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Regex to capture imports like:
    # import pygame
    # from flask import Flask
    # from numpy import array
    pattern = r'^\s*(?:from|import)\s+([a-zA-Z0-9_\.]+)'
    matches = re.findall(pattern, code, re.MULTILINE)

    # Extract only the top-level package names
    modules = sorted(set(m.split('.')[0] for m in matches))

    if not modules:
        print("📭 No imports found in new_app.py")
        return

    print(f"📦 Detected libraries: {', '.join(modules)}")

    # Try installing each one
    for module in modules:
        try:
            print(f"⬇️ Installing {module} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
            print(f"✅ {module} installed successfully.\n")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {module}. You may need to install it manually.\n")

def import_libraries_from_new_app():
    """
    Reads 'new_app.py' from D:/Workspace/Eth2,
    detects all import statements, and dynamically imports those modules.
    """
    file_path = r"D:/Workspace/Eth2/new_app.py"

    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return

    # Read file content
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Regex to match import statements
    pattern = r'^\s*(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\.]+))'
    matches = re.findall(pattern, code, re.MULTILINE)

    # Extract module names
    modules = set()
    for m in matches:
        mod = m[0] or m[1]
        root_module = mod.split('.')[0]  # e.g., "os.path" -> "os"
        modules.add(root_module)

    print(f"📦 Detected modules: {', '.join(modules) if modules else 'none'}")

    # Try to import each module
    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"✅ Successfully imported '{mod}'")
        except ImportError:
            print(f"❌ Failed to import '{mod}' (might need installation)")

def create_file(code):
    """
    Creates (or overwrites) a file named 'new_app.py' in D:/Workspace/Eth2
    and writes the contents of 'code' into it.
    """
    folder_path = r"D:/Workspace/Eth2"
    file_path = os.path.join(folder_path, "new_app.py")

    # Make sure the directory exists
    os.makedirs(folder_path, exist_ok=True)

    # Write the string to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ Successfully wrote content to: {file_path}")

    install_libraries_from_new_app()
    import_libraries_from_new_app()

def create_app(window, text_edit):
    user_input = text_edit.get("1.0",'end-1c')
    prompt = f"""Generate only the raw source code for the following request. Your entire response must be valid, runnable code. Do not include markdown formatting like ```python or ```. Do not include explanations, comments, or any text other than the code itself.

Request: {user_input}
"""
    response = model.generate_content(prompt)
    #code = response.text
    code = re.sub(r'^\s*```(python)?\n|```\s*$', '', response.text, flags=re.MULTILINE).strip()

    create_file(code)

    run_new_app()   

def improve_app(window, text_edit):
    user_input = text_edit.get("1.0",'end-1c')
    stop_new_app()

    # Read the content of the file
    # Path to the "new_app.py" file
    file_path = r"D:/Workspace/ETH2/new_app.py"

    # Check if the file exists before reading
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            #print("=== Contents of improved.py ===")
            #print(content)
    else:
        print(f"File not found: {file_path}")
    
    prompt = content + "improve according to following request on given code, return only code and nothing else" + user_input
    response = model.generate_content(prompt)
    code = response.text
    code = clean_response(code)

    create_file(code)

    run_new_app()     
    
def clean_response(code):
    """
    Removes ``` or ´´´ from the beginning and end of the string 'code'.
    """
    code = code.strip()  # Remove leading/trailing spaces or newlines

    # Remove starting markers if present
    if code.startswith("```") or code.startswith("´´´"):
        code = code[3:]

    # Remove ending markers if present
    if code.endswith("```") or code.endswith("´´´"):
        code = code[:-3]

    # Remove python word in beginning if present
    if code.startswith("python") or code.startswith("´´´"):
        code = code[6:]

    # Strip again to clean any leftover whitespace/newlines
    return code.strip()  

def run_new_app():
    """Start new_app.py as a background process."""
    global new_app_process
    file_path = r"D:/Workspace/Eth2/new_app.py"

    if not os.path.exists(file_path):
        print("⚠️ File not found:", file_path)
        return

    # Start the process
    new_app_process = subprocess.Popen(
        ["python", file_path],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # Windows-safe
    )
    print(f"🚀 new_app.py started with PID {new_app_process.pid}")

def stop_new_app():
    """Stop the running new_app.py process."""
    global new_app_process
    if new_app_process and new_app_process.poll() is None:
        new_app_process.send_signal(signal.CTRL_BREAK_EVENT)  # Graceful stop on Windows
        new_app_process.terminate()
        print("🛑 new_app.py has been stopped.")
    else:
        print("⚠️ No running new_app.py process found.")

def main():
    #Creates window then names it
    window = tk.Tk()
    window.title("Text Editor")
    
    #Set the size of text_edit components
    window.rowconfigure(0, minsize = 50)
    window.columnconfigure(1, minsize = 50)

    #Defines what text-type then implements it with ".grid"
    text_edit = tk.Text(window, font = "Helvetica 18")
    text_edit.grid(row = 0, column = 1)

    #Creates frame that "stores" buttons
    frame = tk.Frame(window, relief = tk.RAISED, bd = 2)

    #Command refers to what function button has
    #lambda allows us to insert several arguments
    create_button = tk.Button(frame, text = "Create", command = lambda: create_app(window, text_edit))
    improve_button = tk.Button(frame, text = "improve", command = lambda: improve_app(window, text_edit))


    create_button.grid(row = 0, column = 0, padx=5, pady=5, sticky = "ew")
    improve_button.grid(row = 1, column = 0, padx=5, pady=5, sticky = "ew")
    frame.grid(row = 0, column = 0, sticky = "ns")
    
    #Keeps the window running until pressing x
    window.mainloop()

main()