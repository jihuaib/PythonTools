from tkinter import messagebox


def show_error(message):
    messagebox.showerror("错误", message)


def show_info(message):
    messagebox.showinfo("提示", message)


def show_confirm(msg1, msg2, func):
    if messagebox.askokcancel(msg1, msg2):
        func()
        return True
    return False
