import tkinter as tk
from gui.app import TaskManagerApp

def main():
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
