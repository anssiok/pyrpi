#!/usr/bin/python3
import tkinter as tk
from urllib import request
from datetime import datetime

syottovali=1000 * 60 * 60 * 24
vaihtovali=1000 * 60 * 60 * 24 * 7

msg1="Kalat nälissään"
msg2="Akvaario rempallaan"
timer1_id=None
timer2_id=None

def button1_pressed():
    global timer1_id, msg1, syottovali
    msg1="Kalat syötetty:\n" + datetime.now().strftime("%a %d.%m klo %H.%M")
    message1.config(bg="LightGreen", text=msg1)
    if timer1_id is not None:
        root.after_cancel(timer1_id)
    timer1_id=root.after(syottovali, alarm1)

def button2_pressed():
    global timer2_id, msg2
    msg2="Vesi vaihdettu:\n" + datetime.now().strftime("%a %d.%m klo %H.%M")
    message2.config(bg="LightGreen", text=msg2)
    if timer2_id is not None:
        root.after_cancel(timer2_id)
    timer2_id=root.after(vaihtovali, alarm2)
    
def alarm1():
    global msg1, message1
    message1.config(bg="red")
    data = "Kalat on nälissään.\n" + msg1
    data = data.encode('utf-8')
    req = request.Request("http://ntfy.sh/kannistenkalat", data=data)
    res = request.urlopen(req)

def alarm2():
    global msg2, message2
    message2.config(bg="red")
    data = "Akvaario on rempallaan.\n" + msg2
    data = data.encode('utf-8')
    req = request.Request("http://ntfy.sh/kannistenkalat", data=data)
    res = request.urlopen(req)

root = tk.Tk()
root.title("Touchscreen Demo")
root.attributes('-fullscreen', True)
root.config(bg="black")

btn1 = tk.Button(
    root,
    text="Syötin kalat",
    font=("Arial", 24),
    width=12,
    height=2,
    command=button1_pressed
)
btn1.pack(pady=5)

message1 = tk.Label(
    root,
    text=msg1,
    font=("Arial", 20)
)
message1.pack()

btn2 = tk.Button(
    root,
    text="Vaihdoin vedet",
    font=("Arial", 24),
    width=12,
    height=2,
    command=button2_pressed
)
btn2.pack(pady=5)

message2 = tk.Label(
    root,
    text="Ei oo kukaan vaihtanut vettä",
    font=("Arial", 20)
)
message2.pack()

root.mainloop()
