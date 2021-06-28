# Ctrl
import struct
import socket
import threading
import re
from cv2 import cv2
import numpy as np
import tkinter
import tkinter.messagebox
from PIL import Image, ImageTk

root = tkinter.Tk()

# 缩放大小
scale = 1

# 原传输画面尺寸
fixw, fixh = 0, 0

# 缩放标值
wscale = False

# 屏幕显示画布
showcan = None

# 缓存区大小
bufsize = 10240

# 线程
th = None

# socket
soc = None

# 初始化socket
def SetSocket():
    global soc, host_en

    host = host_en.get()
    if host is None:
        tkinter.messagebox.showinfo("提示", "Host设置错误！")
        return
    hs = host.split(":")
    if len(hs) != 2:
        tkinter.messagebox.showinfo("提示", "host设置错误！")
        return
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((hs[0], int(hs[1])))
    
def SetScale(x):
    global scale, wscale
    scale = float(x) / 100
    wscale = True

def ShowScreen():
    global  showcan, root, soc, th, wscale
    if showcan is None:
        wscale = True
        print("------------------------")
        showcan = tkinter.Toplevel(root)
        th = threading.Thread(target=run)
        th.start()
    else:
        soc.close()
        showcan.destroy()

def BindEvents(canvas):
    global soc, scale
    # 发送事件
    def EventDo(data):
        soc.sendall(data)
    # 鼠标左键按下&起来，ascii码100为d；ascii码117为u
    def LeftDown(e):
        print(e.x, e.y)
        return EventDo(struct.pack('>BBHH', 1, 100, int(e.x/scale), int(e.y/scale)))

    def LeftUp(e):
        print(e.x, e.y)
        return EventDo(struct.pack('>BBHH', 1, 117, int(e.x/scale), int(e.y/scale)))

    # 鼠标右键按下&起来
    def RightDown(e):
        print(e.x, e.y)
        return EventDo(struct.pack('>BBHH', 3, 100, int(e.x/scale), int(e.y/scale)))

    def RightUp(e):
        print(e.x, e.y)
        return EventDo(struct.pack('>BBHH', 3, 100, int(e.x/scale), int(e.y/scale)))

    # 鼠标滚轮0,回滚 1,前滚
    def Wheel(e):

        if e.delta<0:
            print(e.x, e.y)
            return EventDo(struct.pack('>BBHH', 2, 0, int(e.x/scale), int(e.y/scale)))
        else:
            print(e.x, e.y)
            return EventDo(struct.pack('>BBHH', 2, 1, int(e.x/scale), int(e.y/scale)))

    # 键盘按下&起来
    def KeyDown(e):
        print("KeyDown")
        return EventDo(struct.pack('>BBHH', e.keycode, 100, int(e.x/scale), int(e.y/scale)))
    def KeyUp(e):
        print("KeyUp")
        return EventDo(struct.pack('BBHH', e.keycode, 117, int(e.x/scale), int(e.y/scale)))

    # 绑定所有事件到画布
    canvas.bind(sequence="<1>", func=LeftDown)
    canvas.bind(sequence="<ButtonRelease-1>", func=LeftUp)
    canvas.bind(sequence="<3>", func=RightDown)
    canvas.bind(sequence="ButtonRelease-3", func=RightUp)
    canvas.bind(sequence="MouseWheel", func=Wheel)
    canvas.bind(sequence="KeyPress", func=KeyDown)
    canvas.bind(sequence="KeyRelease", func=KeyUp)


val = tkinter.StringVar()
host_lab = tkinter.Label(root, text="Host:")
host_en = tkinter.Entry(root, show=None, font=('Arial', 14), textvariabl=val)
sca_lab = tkinter.Label(root, text="Scale:")
sca = tkinter.Scale(root, from_=10, to=100, orient=tkinter.HORIZONTAL, length=100,
                        showvalue=100, resolution=0.1, tickinterval=50, command=SetScale)
show_btn = tkinter.Button(root, text="Show", command=ShowScreen)

host_lab.grid(row=0, column=0, padx=10, pady=10, ipadx=0, ipady=0)
host_en.grid(row=0, column=1, padx=0, pady=0, ipadx=40, ipady=0)
sca_lab.grid(row=1, column=0, padx=10, pady=10, ipadx=0, ipady=0)
sca.grid(row=1, column=1, padx=0, pady=0, ipadx=100, ipady=0)
show_btn.grid(row=2, column=1, padx=0, pady=10, ipadx=30, ipady=0)

sca.set(50)
val.set("127.0.0.1:8888")



def run():
    global soc, wscale, showcan, fixh, fixw
    SetSocket()

    lenb = soc.recv(5)

    imtype, le = struct.unpack(">BI", lenb)
    imb = b''
    while le> bufsize:
        t = soc.recv(bufsize)
        imb += t
        le -= len(t)
    while le > 0:
        t = soc.recv(le)
        imb += t
        le -= len(t)
    data = np.frombuffer(imb, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    h, w, _ = img.shape
    print(h, w)
    fixh, fixw = h, w
    imsh = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    imi = Image.fromarray(imsh)
    imgTK = ImageTk.PhotoImage(image=imi)
    tc = tkinter.Canvas(showcan, width=w, height=h, bg="white")
    tc.focus_set()
    BindEvents(tc)
    tc.pack()
    tc.create_image(0, 0, anchor=tkinter.NW, image=imgTK)
    h = int(h * scale)
    w = int(w * scale)

    while True:
        if wscale:
            h = int(fixh * scale)
            w = int(fixw * scale)
            tc.config(width=w, height=h)
            wscale = False
        try:
            lenb = soc.recv(5)
            imtype, le = struct.unpack(">BI", lenb)
            imb = b''
            while le> bufsize:
                t = soc.recv(bufsize)
                imb += t
                le -= len(t)
            while le > 0:
                t = soc.recv(le)
                imb += t
                le -= len(t)
            data = np.frombuffer(imb, dtype=np.uint8)
            ims = cv2.imdecode(data, cv2.IMREAD_COLOR)

            if imtype == 1:
                img = ims
            else:
                img = img + ims

            imt = cv2.resize(img, (w, h))
            imsh = cv2.cvtColor(imt, cv2.COLOR_BGR2RGB)
            imi = Image.fromarray(imsh)
            imgTK.paste(imi)
        except:
            showcan = None
            ShowScreen()
            return
root.mainloop()