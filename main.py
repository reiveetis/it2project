import tkinter as tk
from tkinter import simpledialog

# Create the main window
root = tk.Tk()
root.withdraw()  # Hide the main window

# Ask for the password
password = simpledialog.askstring("Password Required", "Please enter your password:", show='*')

# Display result (optional)
if password != '' and password is not None:
    print("Password entered:", password)
else:
    print("User canceled input.")
