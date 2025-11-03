import subprocess
import shutil
import sys
from datetime import datetime
import tkinter as tk
import os
from tkinter.filedialog import askopenfilename, asksaveasfilename
import google.generativeai as genai
from dotenv import load_dotenv

def run_improved():
    """
    Executes the 'improved.py' file located in D:/Workspace/Ethereal
    using the same Python interpreter that runs this script.
    """
    file_path = r"D:/Workspace/Ethereal\improved"

    # Check if the file exists first
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return

    # Run the file as a separate Python process
    try:
        result = subprocess.run(
            [sys.executable, file_path],  # Use current Python interpreter
            capture_output=True,          # Capture stdout and stderr
            text=True                     # Decode bytes to string
        )

        # Print the results
        print("=== improved.py output ===")
        print(result.stdout)

        if result.stderr:
            print("=== Errors ===")
            print(result.stderr)

    except Exception as e:
        print(f"❌ Failed to run improved.py: {e}")

def new_tedit(code):
    
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

    # Strip again to clean any leftover whitespace/newlines
    code.strip()    


    file_path = r"D:/Workspace/Ethereal\improved"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the new content to the file (overwriting everything)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    #print(f"✅ 'improved.py' has been overwritten successfully at: {file_path}")
    run_improved()

def copy_script_to_target():
    # Define the target folder
    target_folder = r"D:/Workspace/Ethereal"

    # Get the full path of this script
    current_file = os.path.abspath(sys.argv[0])

    # Create a timestamped filename for the copy
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(current_file)
    name, ext = os.path.splitext(filename)
    new_filename = f"improved"

    # Define the destination path
    destination = os.path.join(target_folder, new_filename)

    # Copy the file
    shutil.copy2(current_file, destination)

    print(f"File copied to: {destination}")

def ai_response(input):
   
    load_dotenv()
    genai.configure()
    copy_script_to_target()
    #print(f"API Key: {os.environ.get('GOOGLE_API_KEY')}")  # Debugging line  # or use the .env as you have

    # Read the content of the file
    # Path to the "improved" file
    file_path = r"D:/Workspace/Ethereal\improved"

    # Check if the file exists before reading
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            #print("=== Contents of improved.py ===")
            #print(content)
    else:
        print(f"File not found: {file_path}")

    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = content + "add to the code and return full code and nothing else according to this request" + input + "!IMPORTANT: dont add ´'´ or ``` to the response"   
    response = model.generate_content(prompt)

    #print(response.text)

    new_tedit(response.text)

def open_file(window, text_edit):
    filepath = askopenfilename(filetypes = [("Text Files", "*.txt")])

    if not filepath:
        return
    
    #Delete everything from first char to last in our current window
    text_edit.delete(1.0, tk.END)
    
    #Reads and inserts new content
    with open(filepath, "r") as f:
        content = f.read()
        text_edit.insert(tk.END, content)
    window.title(f"Open File : {filepath}")

def save_file(window, text_edit):
    filepath = asksaveasfilename(filetypes = [("Text Files", "*.txt")])
    
    if not filepath:
        return
    
    with open(filepath, "w") as f:
        content = text_edit.get(1.0, tk.END)
        f.write(content)
    window.title(f"Open File: {filepath}")

def get_input(window, ask_ai):
    input = ask_ai.get("1.0",'end-1c')
    #print(input)
    ai_response(input)

def main():
    #Creates window then names it
    window = tk.Tk()
    window.title("Text Editor")
    
    #Set the size of text_edit components
    window.rowconfigure(0, minsize = 200)
    window.columnconfigure(1, minsize = 200)

    #Defines what text-type then implements it with ".grid"
    text_edit = tk.Text(window, font = "Helvetica 18")
    text_edit.grid(row = 0, column = 1)
    #Text box for ai interaction
    ask_ai = tk.Text(window, font = "Helvetica 18")
    ask_ai.grid(row = 1, column = 1, padx=10, sticky = "s")

    #Creates frame that "stores" buttons
    frame = tk.Frame(window, relief = tk.RAISED, bd = 2)

    #Command refers to what function button has
    #lambda allows us to insert several arguments
    save_button = tk.Button(frame, text = "Save", command = lambda: save_file(window, text_edit))
    open_button = tk.Button(frame, text = "Open", command = lambda: open_file(window, text_edit))
    ai_button = tk.Button(frame, text = "AI", command = lambda: get_input(window, ask_ai))

    save_button.grid(row = 0, column = 0, padx=5, pady=5, sticky = "ew")
    open_button.grid(row = 1, column = 0, padx=5, pady=5, sticky = "ew")
    ai_button.grid(row = 2, column = 0, padx=5, sticky = "ew")
    frame.grid(row = 0, column = 0, sticky = "ns")
    
    #Keeps the window running until pressing x
    window.mainloop()

main()