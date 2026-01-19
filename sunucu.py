from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread as T
import time

kullanicilar = []

try:
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(("localhost",7523))
    server.listen(100)
    print("Sunucu başlatıldı...")
except:
    print("Sunucu başlatılamadı...")


def recv_all(conn, length):
    data = b""
    while len(data) < length:
        packet = conn.recv(51200)
        if not packet:
            break
        data += packet
        
    return data


def sunucuBildiri(mesaj, ip):
    for i in kullanicilar:
        if i != ip:
            i.sendall(bytes(mesaj,"utf-8"))


def dinle(ip):
    try:
        ad = ip.recv(1024).decode("utf-8")
    except:
        kullanicilar.remove(ip)
        ip.close()
        return
    
    sunucuBildiri("@"+ad+" sohbete katıldı.", ip)
    
    while 1:
        try:
            dataUzunlugu = ip.recv(1024).decode("utf-8")
            try:
                int(dataUzunlugu)
                anahtarDosyaAdi = ip.recv(1024)
                data = recv_all(ip, int(dataUzunlugu))
                
                if not data:
                    kullanicilar.remove(ip)
                    ip.close()
                    sunucuBildiri("@"+ad+" sohbetten ayrıldı.",ip)
                    break
                
                for i in kullanicilar:
                    if i != ip:
                        i.sendall(bytes(str(dataUzunlugu),"utf-8"))
                        i.sendall(anahtarDosyaAdi)
                        time.sleep(0.1)
                        i.sendall(data)
                        
            except ValueError:
                for i in kullanicilar:
                    if i != ip:
                        i.send(bytes(str(dataUzunlugu),"utf-8"))
                
        except Exception as e:
            kullanicilar.remove(ip)
            ip.close()
            sunucuBildiri("@"+ad+" sohbetten ayrıldı.",ip)
            break

while 1:
    ip, addr = server.accept()
    
    kullanicilar.append(ip)
    T(target = dinle,args = (ip,)).start()
    
