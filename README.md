# RemoteControl
python 实现的远程监控
# python 实现远程桌面控制

## 1.使用到的模块

[socket](https://docs.python.org/zh-cn/3/library/socket.html?highlight=socket)（ 底层网络接口）

cv2(图像处理模块)

[numpy](https://numpy.org/)(图像转矩阵)

[struct](https://blog.csdn.net/qq_30638831/article/details/80421019)(Python数据转换为字节流)

[PIL](https://www.osgeo.cn/pillow/reference/)模块的[Image](https://www.osgeo.cn/pillow/reference/Image.html).fromarray()[array到image的转换]

[PIL](https://www.osgeo.cn/pillow/reference/)模块的[ImageGrab](https://www.osgeo.cn/pillow/reference/ImageGrab.html).grab()[屏幕截图]

[PIL](https://www.osgeo.cn/pillow/reference/)模块的[ImageTk](https://www.osgeo.cn/pillow/reference/ImageTk.html).PhotoImag()[与tkinter兼容的照片图像]

## 2.屏幕共享

- 被控端

  - 截图
  - 图像减法

  - 定义传输协议
    - 数据长度 -> uint32 
    - 数据

- 控制端

  - 协议解析
    - 读4字节(数据长度)
    - 读取第一步的数据大小

  - 图像加法
  - 图像显示

## 2.模拟键盘鼠标

利用mouse模块，keyboard模块实现被控端的鼠标键盘模拟。

控制端将tkinter绑定鼠标键盘事件到画布上，传输（按键，按下or起来，x坐标，y坐标）

控制端利用mouse keyboard模逆操作。

