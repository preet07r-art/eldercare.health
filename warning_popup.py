import tkinter as tk
from tkinter import messagebox
import sys

def show_warning(reason):
    root = tk.Tk()
    root.withdraw() # Hide the main window
    root.attributes("-topmost", True) # Make it pop up on top of everything
    messagebox.showerror("🚨 EMERGENCY ALERT", 
                         f"DANGEROUS HEALTH LEVELS DETECTED!\n\n"
                         f"Issue: {reason}\n\n"
                         f"An emergency notification has been sent to your caretaker.")
    root.destroy()

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Manual SOS Triggered"
    show_warning(msg)
