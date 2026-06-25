#!/usr/bin/python3
import dbm
import locale
from urllib import request
from datetime import datetime

locale.setlocale(locale.LC_TIME, "fi_FI.UTF-8")

syottovali=1000 #* 60 * 60 * 24
vaihtovali=1000 #* 60 * 60 * 24 * 7

myurl="http://ntfy.sh/kannistenkalat"

with dbm.open('akvaarionapit_db', 'c') as db:
    dt_syotetty = db.get("syotetty", None)
    if dt_syotetty != None:
        dt_syotetty = datetime.fromisoformat(dt_syotetty.decode())

    dt_vaihdettu = db.get("vaihdettu", None)
    if dt_vaihdettu != None:
        dt_vaihdettu = datetime.fromisoformat(dt_vaihdettu.decode())

    dt_syotetty_ilm = db.get("syotetty_ilm", None)
    if dt_syotetty_ilm != None:
        dt_syotetty_ilm = datetime.fromisoformat(dt_syotetty_ilm.decode())

    dt_vaihdettu_ilm = db.get("vaihdettu_ilm", None)
    if dt_vaihdettu_ilm != None:
        dt_vaihdettu_ilm = datetime.fromisoformat(dt_vaihdettu_ilm.decode())

if (datetime.now() - dt_syotetty).total_seconds()*1000 > syottovali:
    if dt_syotetty_ilm == None or (datetime.now() - dt_syotetty_ilm).days > 0:
        data = "Akvaario on rempallaan! Kalat syötetty viimeksi " + dt_syotetty.strftime("%Ana %d.%m klo %H.%M")
        req = request.Request(myurl, data=data.encode('utf-8'))
#        res = request.urlopen(req)
        print(data)
        with dbm.open('akvaarionapit_db', 'c') as db:
            db['syotetty_ilm'] = datetime.now().isoformat()

            
if (datetime.now() - dt_vaihdettu).total_seconds()*1000 > vaihtovali:
    if dt_vaihdettu_ilm == None or (datetime.now() - dt_vaihdettu_ilm).days > 0:
        data = "Akvaario on rempallaan! Vesi vaihdettu viimeksi " + dt_vaihdettu.strftime("%Ana %d.%m klo %H.%M")
        req = request.Request(myurl, data=data.encode('utf-8'))
#        res = request.urlopen(req)
        print(data)
        with dbm.open('akvaarionapit_db', 'c') as db:
            db['vaihdettu_ilm'] = datetime.now().isoformat()
