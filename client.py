import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
from threading import Thread as t
from socket import socket, AF_INET, SOCK_STREAM
import aes, os, time

veri = ""
sifre = ""
ad = ""

ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")

try:
    os.mkdir("AlinanDosyalar")
except:
    pass

try:
    server = socket(AF_INET, SOCK_STREAM)
    server.connect(("localhost",7523))
except Exception as e:
    server = False

def mesajGonderFunc():
    mesaj = atilacakMesaj.get("0.0","end-1c")
    server.sendall(bytes(ad+" : "+mesaj,"utf-8"))
    ctk.CTkLabel(master=gelenMesajlarr, text=mesaj, corner_radius = 10,justify = "left", fg_color = "gray").pack(pady=5, anchor = "e")
    atilacakMesaj.delete("0.0","end-1c")
    gelenMesajlarr._parent_canvas.yview_moveto(1.0)

def DosyagonderFunc(key):
    if veri != "":
        d_yol = str(dosya_yolu).split("/")[-1]
        server.sendall(bytes(str(len(veri)),"utf-8"))
        time.sleep(0.1)
        server.sendall(key+bytes("-??-??-"+d_yol,"utf-8"))
        time.sleep(0.1)
        server.sendall(veri)
        ctk.CTkButton(master=gelenMesajlarr, text=d_yol, fg_color = "gray", command = lambda yol=dosya_yolu : os.startfile(yol)).pack(pady=5, anchor = "e")
        gelenMesajlarr._parent_canvas.yview_moveto(1.0)
    else:
        messagebox.showerror("Hata", "Dosya Seçilmedi!")
    
def recv_all(serv, length):
    data = b""
    while len(data) < length:
        packet = serv.recv(51200)
        if not packet:
            break
        data += packet
    return data


def dinle():
    while 1:
        try:
            dataUzunluguyadaMesaj = server.recv(1024).decode("utf-8")
            try:
                int(dataUzunluguyadaMesaj)
                Dosyaaliniyor = ctk.CTkLabel(master=gelenMesajlarr, text="Bir dosya alınıyor...", corner_radius = 10,justify = "left", fg_color = "gray")
                Dosyaaliniyor.pack(pady=5, anchor = "w")
                anahtar = server.recv(1024).split(b"-??-??-")
                dosyaAdi = str(anahtar[-1]).replace("b'" ,"").replace("'","")
                data = recv_all(server, int(dataUzunluguyadaMesaj))
                dec = aes.decrypt(anahtar[0], data , aad = b"meta")
                with open("AlinanDosyalar/"+dosyaAdi,"wb") as yaz:
                    yaz.write(dec)
                ctk.CTkButton(master=gelenMesajlarr, text=dosyaAdi, fg_color = "gray", command = lambda yol = os.getcwd()+"\\AlinanDosyalar\\"+dosyaAdi : os.startfile(yol)).pack(pady=5, anchor = "w")
                Dosyaaliniyor.destroy()
            except ValueError:
                ctk.CTkLabel(master=gelenMesajlarr, text=str(dataUzunluguyadaMesaj), corner_radius = 10,justify = "left", fg_color = "gray").pack(pady=5, anchor = "w")
                gelenMesajlarr._parent_canvas.yview_moveto(1.0)
        except Exception as e:
            messagebox.showerror("Hata", f"Sunucu taraflı bir sorun oluştu!\nHata : {e}")
            return
        
        gelenMesajlarr._parent_canvas.yview_moveto(1.0)

def dosyaSecGUI():
    global veri, sifre, dosya_yolu
    dosya_yolu = filedialog.askopenfilename(
        title="Bir dosya seç", 
        filetypes=(("Tüm Dosyalar", "*.*"), ("Metin Dosyaları", "*.txt"))
        )
    if not dosya_yolu:
        messagebox.showerror("Hata", "Dosya Seçmediniz!")
    else:
        with open(dosya_yolu, "rb") as oku:
            veri,sifre = aes.verial(oku.read())
            messagebox.showinfo(title="Başarılı",message=f"Dosya Şifrelendi:\n{sifre}")

                
def giris():
    global app, user_entry

    app = ctk.CTk()
    app.geometry(f"500x500")
    app.resizable(0,0)
    app.title("CryptSend Giriş") 

    def login():
        global ad
        ad = str(user_entry.get())
        server.sendall(bytes(ad,"utf-8"))
        messagebox.showinfo(title="Başarılı",message="Giriş Başarılı")
        app.destroy()
        
    if server:        
        frame = ctk.CTkFrame(app) 
        frame.place(relx =0.1, rely = 0.1, relheight = 0.8,relwidth = 0.8)
          
        label = ctk.CTkLabel(frame,text='Giriş Yap') 
        label.place(relx =0.35, rely = 0.025, relheight = 0.2,relwidth = 0.3)
        
        user_entry = ctk.CTkEntry(frame,placeholder_text="Kullanıcı Adı") 
        user_entry.place(relx = 0.25, rely = 0.35, relheight = 0.1, relwidth = 0.5)
        
        button = ctk.CTkButton(frame,text='Giriş', fg_color = "cyan", text_color = "black",command=login) 
        button.place(relx =0.327, rely = 0.65, relheight = 0.1,relwidth = 0.3)
    else:
        ctk.CTkLabel(app, text = "Sunucuya Bağlanamadı!", text_color = "red", font=("Consolas",17)).place(relx = 0.28, rely = 0.45)
        
    app.mainloop()

def mesajlarBoyutKontrol():
    global mesajrelheight
    uzunluk = len(atilacakMesaj.get("0.0","end-1c").split("\n"))
    if 0.06+(0.02*uzunluk) < 0.2:
        atilacakMesaj.place(relx = 0.1, rely = 0.72,relwidth = 0.72, relheight = 0.06+(0.02*uzunluk))

    pencere.after(100,mesajlarBoyutKontrol)
    

def dosyaGonderScreen():
    global gelenMesajlarr, atilacakMesaj, pencere
    
    pencere = ctk.CTk()
    pencere.geometry("500x500")
    pencere.title("CryptSend")
    pencere.resizable(0,0)

    gelenMesajlarr = ctk.CTkScrollableFrame(master=pencere)
    gelenMesajlarr.place(relx = 0.1, rely = 0.1,relwidth = 0.8, relheight = 0.6)
    ctk.CTkLabel(master=gelenMesajlarr, text="Sohbete Katıldın.").pack(pady=5, anchor = "e")
    gelenMesajlarr._parent_canvas.yview_moveto(1.0)

    atilacakMesaj = ctk.CTkTextbox(pencere)
    atilacakMesaj.place(relx = 0.1, rely = 0.72,relwidth = 0.72, relheight = 0.06)

    mesaj_gonder = ctk.CTkButton(pencere, text = ">", fg_color = "green", command = mesajGonderFunc)
    mesaj_gonder.place(relx = 0.83, rely = 0.725, relheight = 0.07, relwidth = 0.07)

    dosya_sec = ctk.CTkButton(pencere, text = "Dosya Seç", command = dosyaSecGUI)
    dosya_sec.place(relx = 0.25, rely = 0.93, relheight = 0.05, relwidth = 0.19)
    
    dosya_gonder = ctk.CTkButton(pencere, text = "Dosya Gönder", command = lambda: t(target = DosyagonderFunc, args = (sifre,)).start())
    dosya_gonder.place(relx = 0.5, rely = 0.93, relheight = 0.05, relwidth = 0.19)

    t(target = dinle).start()
    pencere.after(100,mesajlarBoyutKontrol)
    pencere.mainloop()

    
giris()
if ad:
    dosyaGonderScreen()
