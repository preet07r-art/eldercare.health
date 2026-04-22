import tkinter as tk
from tkinter import messagebox
import sys

def show_goal_reached():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True) # Pop up on top
    messagebox.showinfo("💧 GOAL REACHED!", 
                        "Congratulations!\n\n"
                        "You have completed your daily water intake goal of 8 glasses.\n\n"
                        "Stay healthy and stay hydrated!")
    root.destroy()

if __name__ == "__main__":
    show_goal_reached()
