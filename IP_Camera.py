# -*- coding:utf-8 -*-
import cv2
import threading
import tkinter as tk
from tkinter import *
import tkinter
from PIL import Image, ImageTk  # 图像控件
import numpy as np
import configparser
import tkinter.messagebox as tkm

content = configparser.ConfigParser()
content.read("config.ini")
ip_link = content.get("IP_link", "ip_link")
windows_title = content.get("Title", "windows_title")
windows_size = content.get("Size", "windows_size")


top = tkinter.Tk()  #
top.title(windows_title)  # 窗口标题
top.geometry(windows_size)  # 窗口大小
top.resizable(0, 0)  # 禁止缩放

font_Radio = ("微软雅黑", 12, "bold")  # Radio字体
font_Button = ("微软雅黑", 9, "bold")  # 按钮字体
font_Label = ("微软雅黑", 9, "bold")  # 标签字体

image_width = 640  # 画布宽度
image_height = 480  # 画布高度(4:3)

# 多线关联按钮
class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
        self.setDaemon(True)
        self.start()  # 在这里开始

    def run(self):
        self.func(*self.args)

# 绘制画布
canvas = Canvas(top, bg='white', width=image_width, height=image_height)
canvas.place(x=80, y=50)

# 图像转化
def imgConvert(img, resize_flag=False, image_width=image_width, image_height=image_height):
    # 将颜色由BGR转为RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.uint8)
    # 转换成可以显示的图片640x480
    img = Image.fromarray(img)
    # resize图像大小为400x300
    if resize_flag:
        img = img.resize((image_width, image_height),
                         Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    return img

# 关闭打开按钮状态功能
def close_radio(flag):
    if flag:
        cam_01_Ra.config(state='disable')
        cam_02_Ra.config(state='disable')
        cam_03_Ra.config(state='disable')
    else:
        cam_01_Ra.config(state='normal')
        cam_02_Ra.config(state='normal')
        cam_03_Ra.config(state='normal')


# 放置初始背景图
bg = np.zeros((640,480),dtype=np.uint8)
bg = imgConvert(bg, True)
canvas.create_image(0, 0, anchor='nw', image=bg, tag='bg_img')

var_camdev = tk.IntVar()
# 摄像头标签
l2 = tk.Label(top, width=9, height=1, text='empty', font=font_Button)
l2.place(x=80, y=14)

camera_parameter = {'#1': 0, '#2': 1, '#3': 2}
camera_dict = {0: "#1", 1: "#2", 2: "#3"}
# 设置初始摄像头
var_camdev.set(0)
l2.config(text='摄像头 [ ' + camera_dict[var_camdev.get()] + ' ]')
camera_parameter_elem = camera_parameter[camera_dict[var_camdev.get()]]


# 摄像头选择触发函数
def camera_trigger():
    global camera_parameter_elem
    l2.config(text='摄像头 [ ' + camera_dict[var_camdev.get()] + ' ]')
    camera_parameter_elem = camera_parameter[camera_dict[var_camdev.get()]]

    if var_camdev.get()==2:
        ip_link_path = tk.StringVar()
        ip_link_Entry = tk.Entry(top,
                                 textvariable=ip_link_path,
                                 width=32)
        ip_link_Btn = tk.Button(top,
                                text="确定",
                                command=lambda: [
                                    [ip_link_path.set(ip_link_path.get()), tkm.showinfo(title="提示", message="更新成功!")]
                                    if ip_link_path.get().startswith(
                                        ('rtsp://', 'rtmp://', 'http://', 'https://'))
                                    else [tkm.showinfo(title="提示", message="链接格式错误!"),
                                          ip_link_path.set(ip_link)]],
                                relief=GROOVE,
                                width=3,
                                height=1,
                                font=font_Label)
        ip_link_Entry.place(x=380, y=17)

        ip_link_Btn.place(x=680, y=13)
        ip_link_path.set(ip_link)
        camera_parameter_elem = ip_link_path.get()


# #1 Radiobutton
cam_01_Ra = tk.Radiobutton(top, text='#1', variable=var_camdev, value=0, command=camera_trigger, font=font_Radio)
cam_01_Ra.place(x=190, y=10)
# #2 Radiobutton
cam_02_Ra = tk.Radiobutton(top, text='#2', variable=var_camdev, value=1, command=camera_trigger, font=font_Radio)
cam_02_Ra.place(x=250, y=10)
# #3 Radiobutton
cam_03_Ra = tk.Radiobutton(top, text='#3', variable=var_camdev, value=2, command=camera_trigger, font=font_Radio)
cam_03_Ra.place(x=310, y=10)

camera_switch = False
def open_close_camera():

    open_close_camera_Btn.config(state='disable')
    global camera_switch
    if camera_switch == False:
        global cap, frame
        close_radio(True)
        cap = cv2.VideoCapture(camera_parameter_elem)  # 创建摄像头对象
        flag = True
        while True:
            if flag:
                flag = False
                camera_switch = True
                open_close_camera_Btn.config(state='normal')
                open_close_camera_Btn.config(text="关闭摄像头")
            # 读取图像
            ref, frame = cap.read()
            # 摄像头翻转
            if camera_parameter_elem in [0, 1]:
                frame = cv2.flip(frame, 1)
            tkimg = imgConvert(frame)
            # 参数1，2是相对于canvas偏移量
            canvas.create_image(0, 0, anchor='nw', image=tkimg)
            temp = tkimg
            top.update()
            top.after(1)

    else:
        camera_switch = False
        cap.release()
        close_radio(False)
        canvas.create_image(0, 0,
                            anchor='nw',
                            image=bg)
        canvas.create_image(0, 0,
                            anchor='nw')
        open_close_camera_Btn.config(state='normal')
        open_close_camera_Btn.config(text="打开摄像头")

# 摄像头开关
open_close_camera_Btn = tk.Button(top, text='打开摄像头', command=lambda: MyThread(open_close_camera), relief=RIDGE, width=10, height=2, font=font_Button)
open_close_camera_Btn.place(x=350, y=540)


# 退出程序提示
def top_level_close():
    if tkm.askokcancel(title="提示", message="确定退出程序？"):
        top.destroy()
top.protocol("WM_DELETE_WINDOW", top_level_close)


cv2.destroyAllWindows()
top.mainloop()
