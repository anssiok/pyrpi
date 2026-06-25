#!/usr/bin/python3
import tkinter as tk
import dbm
import locale
from datetime import datetime

locale.setlocale(locale.LC_TIME, "fi_FI.UTF-8")

syottovali=1000 #* 60 * 60 * 24
vaihtovali=1000 #* 60 * 60 * 24 * 7

with dbm.open('akvaarionapit_db', 'c') as db:
    dt_syotetty = datetime.fromisoformat(db.get("syotetty", datetime.now().isoformat()).decode())
    dt_vaihdettu = datetime.fromisoformat(db.get("vaihdettu", datetime.now().isoformat()).decode())

timer1_id=None
timer2_id=None

def button1_pressed():
    global timer1_id, dt_syotetty, syottovali
    dt_syotetty = datetime.now()
    check_situation1()
    if timer1_id is not None:
        root.after_cancel(timer1_id)
    timer1_id=root.after(syottovali, alarm1)
    with dbm.open('akvaarionapit_db', 'c') as db:
        db['syotetty'] = dt_syotetty.isoformat()

def check_situation1():
    global dt_syotetty, syottovali, message1
    message1.config(text="Kalat syötetty:\n" + dt_syotetty.strftime("%Ana %d.%m klo %H.%M"))
    if (datetime.now() - dt_syotetty).total_seconds()*1000 > syottovali:
        message1.config(bg="red")
    else:
        message1.config(bg="LightGreen")        
    
def check_situation2():
    global dt_vaihdettu, vaihtovali, message2
    message2.config(text="Vesi vaihdettu:\n" + dt_vaihdettu.strftime("%Ana %d.%m klo %H.%M"))
    if (datetime.now() - dt_vaihdettu).total_seconds()*1000 > vaihtovali:
        message2.config(bg="red")
    else:
        message2.config(bg="LightGreen")        
    
def button2_pressed():
    global timer2_id, dt_vaihdettu, vaihtovali
    dt_vaihdettu = datetime.now()
    check_situation2()
    if timer2_id is not None:
        root.after_cancel(timer2_id)
    timer2_id=root.after(vaihtovali, alarm2)
    with dbm.open('akvaarionapit_db', 'c') as db:
        db['vaihdettu'] = dt_vaihdettu.isoformat()
    
def alarm1():
    check_situation1()

def alarm2():
    check_situation2()

# UI objects

root = tk.Tk()
root.title("Akvaarionapit")
#root.attributes('-fullscreen', True)
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
    font=("Arial", 20)
)
check_situation1()
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
    font=("Arial", 20)
)
check_situation2()
message2.pack()

root.mainloop()
