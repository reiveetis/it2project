import tkinter as tk
from tkinter import simpledialog


def generate_password():
    pass


def check_password():
    # TODO: check for existing password
    # generate_password()
    pass


def intialize_root():
    pass


# the program starts here
if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    # Hide the main window
    root.withdraw()

    # Ask for the password
    password = simpledialog.askstring("Password Required", "Please enter your password:", show='*')

    # Display result (optional)
    if password != '' and password is not None:
        # check password
        check_password()
        print("Password entered:", password)
        # show root window
        intialize_root()
    else:
        print("User canceled input.")
