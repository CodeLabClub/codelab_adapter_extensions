"""
驱动硬件的库文件，arduino模式
所有和串口有关的操作全都在此,包括通过串口给硬件发送命令，接受串口消息
"""
import struct
from time import sleep
import time
import functools

from serial import Serial
from serial.tools.list_ports import comports as list_serial_ports

# 串口引用
ser = Serial()


# 测试时间的装饰器
def timer(function):
    @functools.wraps(function)
    def decorated(*args, **kwargs):
        start = time.time()
        print("结果：", function(*args, **kwargs))
        end = time.time()
        print("cost time :", end - start)

    return decorated


# 扫描所有的串口，发现ardiuno架构的硬件
def find_ardiuno():
    """
    Finds the port to which the device is connected.
    https://github.com/mu-editor/mu/blob/803153f661097260206ed2b7cc9a1e71b564d7c3/mu/contrib/microfs.py#L44
    window用户需要按照发现服务
    """
    ports = list_serial_ports()
    for port in ports:
        if 'VID:PID=1A86:7523' in port[2].upper():
            return port[0]


# 一直尝试连接硬件直到成功
def RoboCon():
    while True:
        env_is_valid = find_ardiuno()
        # 等待用户连接ardiuno
        if not env_is_valid:
            sleep(2)
        else:
            port = find_ardiuno()
            ser.port = port
            ser.baudrate = 115200  # 设置波特率
            ser.open()
            ser.write(
                bytearray(
                    [0x56, 0x65, 0x72, 0x73, 0x69, 0x6f, 0x6e, 0x3a, 0x20, 0x31, 0x32, 0x2e, 0x32, 0x32, 0x2e, 0x31,
                     0x38, 0x0d, 0x0a]))
            ser.readline()
            break


def RoboClose():
    ser.close()


# 板载蜂鸣
tones = {"C2": [0x41, 0x00],
         "D2": [0x49, 0x00],
         "E2": [0x52, 0x00],
         "F2": [0x57, 0x00],
         "G2": [0x62, 0x00],
         "A2": [0x6e, 0x00],
         "B2": [0x7b, 0x00],
         "C3": [0x83, 0x00],
         "D3": [0x93, 0x00],
         "E3": [0xa5, 0x00],
         "F3": [0xaf, 0x00],
         "G3": [0xc4, 0x00],
         "A3": [0xdc, 0x00],
         "B3": [0xf7, 0x00],
         "C4": [0x06, 0x01],
         "D4": [0x26, 0x01],
         "E4": [0x4a, 0x01],
         "F4": [0x5d, 0x01],
         "G4": [0x88, 0x01],
         "A4": [0xb8, 0x01],
         "B4": [0xee, 0x01],
         "C5": [0x0b, 0x02],
         "D5": [0x4b, 0x02],
         "E5": [0x93, 0x02],
         "F5": [0xba, 0x02],
         "G5": [0x10, 0x03],
         "A5": [0x70, 0x03],
         "B5": [0xdc, 0x03],
         "C6": [0x17, 0x04],
         "D6": [0x97, 0x04],
         "E6": [0x27, 0x05],
         "F6": [0x75, 0x05],
         "G6": [0x20, 0x06],
         "A6": [0xe0, 0x06],
         "B6": [0xb8, 0x07],
         "C7": [0x2d, 0x08],
         "D7": [0x2d, 0x09],
         "E7": [0x4d, 0x0a],
         "F7": [0xea, 0x0a],
         "G7": [0x40, 0x0c],
         "A7": [0xc0, 0x0d],
         "B7": [0x6f, 0x0f],
         "C8": [0x5a, 0x10],
         "D8": [0x5b, 0x12]}

beats = {'二分之一': [0xf4, 0x01], '四分之一': [0xfa, 0x00], '八分之一': [0x7d, 0x00], '整拍': [0xe8, 0x03], '双拍': [0xd0, 0x07]}


# 蜂鸣器
def DoBuzzer(tone='C2', beat='二分之一'):
    # tone(音调):A2,A3,A4,B2,B3,B4~G2,G3,G4;  beat(节拍):二分之一,四分之一,八分之一,整拍,双拍
    # beatslist = ['二分之一', '四分之一', '八分之一', '整拍', '双拍']
    try:
        ser.write(bytearray([0xff, 0xaa, 0x7, 0x0, 0x2, 0x22, tones[tone][0], tones[tone][1], beats[beat][0],
                             beats[beat][1]]))  # 发送信息
        x = ser.readline()  # 接收信息
        return "success"
    except:
        return "error"


# 板载亮灯
# index为亮灯位置（left,right,all:左，右，全部），red,green,blue可填0-255
def DoRGBLed(index="all", red=0, green=0, blue=0):
    try:
        index = {"left": 1, "right": 2, "all": 0}[index]
        ser.write(
            bytearray([0xff, 0xaa, 0x9, 0x0, 0x2, 0x8, 0x7, 0x2, index, red, green, blue]))  # 发送信息
        x = ser.readline()  # 接收信息
        return "success"
    except Exception as e:
        return "error"


# 光线传感器(板载和外接)
# @timer
def RequestLightOnBoard(port=6):  # port: 3（外接），4（外接），6（载板）
    try:
        ser.write(bytearray([0xff, 0xaa, 0x04, 0x00, 0x01, 0x03, port]))  # 发送信息
        x = ser.readline()  # 接收信息
        y = x[4:8]
        value = struct.unpack('<f', y)[0]
        return value  # 返回光线值
    except Exception as e:
        return


# 风扇马达模块
def Fan(port=1, direction="clockwise"):  # port ：接口端口1，2，3，4；  direction：旋转方向（stop 停止；clockwise 顺时针；Anti-clockwise逆时针）
    try:
        PortDict = {1: [0x0b, 0x0c], 2: [0x09, 0x0a], 3: [0x10, 0x11], 4: [0x0e, 0x0f]}
        port = PortDict[port]
        directionDict = {"stop": [0x00, 0x00], "clockwise": [0x01, 0x00], "Anti-clockwise": [0x00, 0x01]}
        direction = directionDict[direction]  # 转的方向
        ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x02, 0x1e, port[0], direction[0]]))  # 第一次发送数据
        ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x02, 0x1e, port[1], direction[1]]))  # 第二次发送数据
        x = ser.readline()  # 接受消息
        return "success"
    except:
        return "error"


# RGB灯
def Fourlamp(port=1,
             lamp=1,
             red=50,
             green=0,
             blue=0):  # port接口1,2,3,4； lamp亮哪个灯0,1,2,3,4；  红色red：0~255；绿色green：0~255；蓝色blue：0~255
    try:
        ser.write(
            bytearray([0xff, 0xaa, 0x9, 0x0, 0x2, 0x8, port, 2, lamp, red, green, blue]))  # 发送请求
        # sleep(0.01)
        x = ser.readline()  # 接收消息
        return "success"
    except Exception as e:
        return "error"


# TT马达模块
def Engine(plug="L", speed=50):  # plug插头：'L','R'左右；转速：speed-255~+255
    try:
        plug = {"L": 1, "R": 2}[plug]
        if -255 <= speed <= 255 and int(speed) == speed:
            if speed <= 0:
                speedlist = [-speed, 0x00]
            else:
                speedlist = [256 - speed, 0xff]
            # 插口
            PortDict = {1: 0x09, 2: 0x0a}
            plug = PortDict[plug]
            # 转速speed
            ser.write(bytearray([0xff, 0xaa, 0x06, 0x00, 0x02, 0x0a, plug] + speedlist))  # 发送请求
            x = ser.readline()
            return "success"
    except:
        return "error"


# 马达模块的前进，后退，左转和右转
def EngineWithDirection(direction='前进', speed=50):
    direction_map = {
        '前进': [256 - speed, 0xff, speed, 0x00],
        '后退': [speed, 0x00, 256 - speed, 0xff],
        '左转': [speed, 0x00, speed, 0x00],
        '右转': [256 - speed, 0xff, 256 - speed, 0xff]
    }
    try:
        if speed == 0:
            ser.write(bytearray([0xff, 0xaa, 0x07, 0x00, 0x02, 0x05, 0x00, 0x00, 0x00, 0x00]))
        else:
            ser.write(bytearray([0xff, 0xaa, 0x07, 0x00, 0x02, 0x05] + direction_map[direction]))
        ser.readline()
        return 'success'
    except Exception as e:
        return 'error'


# 微笑表情模块
face0 = [
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]


# 点阵屏
def MatrixScreen(mode=1, port=1, num=0, char="Hi", x=0, y=0, hour=0, space=1, minute=0, matrix=face0, face=1):
    # mode（模式）：1，2，3，4，5；  port（接口）：1，2，3，4；
    # mode1
    # num（数字）：-999~9999；
    # mode2
    # char（字符串）：只能由大小写字母组成；  x（横轴方向右偏距离）：整数；  y（横轴方向右偏距离）：整数；
    # mode3
    # hour（小时数）：0~99;  minute（分钟数）：0~99；  space（小时数与分钟数的间隔符）：0（空格），1（冒号）；
    # mode4
    # matrix：16x8的0和1组成的矩阵
    # mode5
    # face（表情）：1，2，3，4，5，6，7，8，9，10，11，12
    try:
        # 数字
        if mode == 1:
            if isinstance(num, float) or isinstance(num, int):
                numbyt = bytearray(struct.pack("f", num))
                a = ["0x%02x" % b for b in numbyt]
                for i in range(4):
                    a[i] = int(a[i], 16)

                ser.write(
                    bytearray([0xff, 0xaa, 0x9, 0x0, 0x2, 0x29, port, 0x04, a[0], a[1], a[2], a[3]]))  # 发送请求
                # sleep(0.01)
                x = ser.readline()
                return "success"
        # 字母
        if mode == 2:
            if x == int(x):
                if y == int(y):
                    if isinstance(char, str):
                        try:
                            if len(char) >= 4:
                                charlen = 4
                                char = char[0:4]
                            else:
                                charlen = len(char)
                            # 把字母转换成字节数组
                            charlist = [hex(ord(c)).replace('0x', '') for c in char]
                            for i in range(charlen):
                                charlist[i] = int(charlist[i], 16)
                            if x < 0:
                                x = 255 + x
                            sendarray = [0xff, 0xaa, 8 + charlen, 0x00, 0x02, 0x29, port, 0x01, x, y + 7,
                                         charlen] + charlist
                            ser.write(bytearray(sendarray))
                            # sleep(0.01)
                            x = ser.readline()
                            return "success"
                        except:
                            return "error"
        # 时间
        if mode == 3:
            # port：接口1，2，3，4； space：小时分钟的间隔符，空格（0） 或 引号（1）
            # hour：小时数；  minute：分钟数
            if space in [0, 1]:
                if 0 <= hour <= 99 and isinstance(hour, int):
                    if 0 <= minute <= 99 and isinstance(minute, int):
                        ser.write(bytearray(
                            [0xff, 0xaa, 0x8, 0x0, 0x2, 0x29, port, 0x03, space, hour, minute]))  # 发送请求
                        # sleep(0.01)
                        x = ser.readline()
                        return "success"
        # 绘画
        if mode == 4:
            try:
                msg = []  # 十六位 亮灯信息
                for i in range(16):
                    msg.append([])
                # 处理接受到的矩阵,转换为十六位的列表
                for i in range(8):
                    for j in range(16):
                        msg[j].append(str(matrix[i][j]))
                for i in range(16):
                    msg[i] = int("".join(msg[i]), 2)
                ser.write(bytearray([0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, port, 0x02, x, y] + msg))
                # sleep(0.01)
                x = ser.readline()
                return "success"
            except:
                return "error"
        # 表情
        if mode == 5:
            if face in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                facelist = [
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x3c, 0x62, 0x5e,
                     0x5e, 0x3c, 0x01, 0x01, 0x3c, 0x5e, 0x5e, 0x62, 0x3c, 0x00, 0x00],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x10, 0x20, 0x40, 0x44,
                     0x22, 0x13, 0x03, 0x03, 0x13, 0x22, 0x44, 0x40, 0x20, 0x10, 0x00],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x10, 0x2e, 0x2e, 0x28,
                     0x28, 0x10, 0x00, 0x00, 0x10, 0x28, 0x2b, 0x2b, 0x28, 0x10, 0x00],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x10, 0x2f, 0x2f, 0x2c,
                     0x28, 0x10, 0x00, 0x00, 0x10, 0x28, 0x2e, 0x2e, 0x28, 0x10, 0x00],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0xf8, 0x7c, 0x3c,
                     0x18, 0x08, 0x00, 0x00, 0x08, 0x18, 0x3c, 0x7c, 0xf8, 0x00, 0x00],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x18, 0x1c, 0x1c,
                     0x1c, 0x18, 0x00, 0x00, 0x18, 0x1c, 0x1c, 0x1c, 0x18, 0x00, 0x00],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x30, 0x78, 0x7c, 0x3e, 0x7c,
                     0x78, 0x30, 0x00, 0x00, 0x30, 0x78, 0x7c, 0x3e, 0x7c, 0x78, 0x30],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x10, 0x38, 0x1c,
                     0x38, 0x10, 0x00, 0x00, 0x30, 0x78, 0x7c, 0x3e, 0x7c, 0x78, 0x30],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x18, 0x30, 0x30,
                     0x38, 0x18, 0x00, 0x00, 0x18, 0x38, 0x30, 0x30, 0x18, 0x00, 0x00],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1c, 0x22,
                     0x22, 0x1c, 0x00, 0x00, 0x3c, 0x42, 0x42, 0x42, 0x3c, 0x00, 0x00],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3c, 0x7e,
                     0x7e, 0x3c, 0x00, 0x00, 0x0c, 0x18, 0x18, 0x18, 0x0c, 0x00, 0x00],
                    [0xff, 0xaa, 0x17, 0x00, 0x02, 0x29, 0x01, 0x02, 0x00, 0x00, 0x00, 0x08, 0x1c, 0x1c, 0x3c,
                     0x38, 0x20, 0x00, 0x00, 0x20, 0x38, 0x3c, 0x1c, 0x1c, 0x08, 0x00]
                ]
                face = facelist[face - 1]
                ser.write(bytearray(face))
                # sleep(0.01)
                x = ser.readline()
                return "success"
    except:
        return "error"


# 触摸传感器
def Touch(port=1):  # port（接口）：1，2，3，4
    try:
        ser.write(bytearray([0xff, 0xaa, 0x04, 0x00, 0x01, 0x33, port]))  # 发送信息
        # sleep(0.01)
        y = ser.readline()  # 接收信息
        y = y[4]
        if y == 1:
            y = True
        else:
            y = False
        return y  # 返回判断结果
    except:
        pass


# 四按键
def FourKey(port=3, key=1):  # port：3，4；   key：1，2，3，4
    try:
        for i in range(6):  # 循环6次发送信息，因为从第6次开始才接收到有用数据
            ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x16, port, key]))  # 发送信息
            # sleep(0.01)
            y = ser.readline()  # 接收信
        value = y[4]
        if value == 1:
            value = True
        else:
            value = False
        return value  # 返回结果
    except:
        pass


# 超声传感器
def Ultrasound(port=1):  # port：1，2，3，4
    try:
        ser.write(bytearray([0xff, 0xaa, 0x04, 0x00, 0x01, 0x01, port]))  # 发送信息
        sleep(0.01)
        y = ser.readline()  # 接收信息
        # sleep(0.01)
        x = y[4:-2]
        value = struct.unpack('<f', x)[0]
        return value  # 返回结果
    except:
        pass


# 摇杆传感器
def Rocker(port=3, x_or_y='x轴'):  # port:3,4
    try:
        # x方向
        ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x05, port, 0x01]))  # 发送信息
        # sleep(0.01)
        x = ser.readline()  # 接收信息
        # sleep(0.01)
        # y方向
        ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x05, port, 0x02]))  # 发送信息
        # sleep(0.01)
        y = ser.readline()  # 接收信息
        # sleep(0.01)

        x = struct.unpack("<f", x[4:8])[0]
        y = struct.unpack("<f", y[4:8])[0]
        if x_or_y == "x轴":
            return x
        if x_or_y == 'y轴':
            return y
    except:
        pass


# 陀螺仪
def Gyroscope(axis='x轴'):
    try:
        if axis == 'x轴':
            # x轴
            ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x06, 0x00, 0x01]))
            # sleep(0.01)
            try:
                x = ser.readline()
                # sleep(0.01)
                xlen = x
                x = struct.unpack("<f", x[4:8])[0]
            except:
                x = 0
                u = ser.readline()
            return x

        if axis == 'y轴':
            # y轴
            ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x06, 0x00, 0x02]))
            # sleep(0.01)
            try:
                y = ser.readline()
                # sleep(0.01)
                ylen = y
                y = struct.unpack("<f", y[4:8])[0]
            except:
                y = 0
                u = ser.readline()
            return y

        if axis == 'z轴':
            # z轴
            ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x06, 0x00, 0x03]))
            # sleep(0.01)
            try:
                z = ser.readline()
                # sleep(0.01)
                zlen = z
                z = struct.unpack("<f", z[4:8])[0]
            except:
                z = 0
                u = ser.readline()
            return z
    except:
        pass


# 人体红外传感器
def Infrared(port=1):  # port:1,2,3,4
    try:
        ser.write(bytearray([0xff, 0xaa, 0x04, 0x00, 0x01, 0x0f, port]))  # 发送信息
        # sleep(0.01)
        y = ser.readline()  # 接收信息
        # sleep(0.01)
        y = struct.unpack("<f", y[4:8])[0]
        if int(y) == 1:
            y = True
        else:
            y = False
        return y
    except:
        pass


# 温度传感器
def Temperature(port=1, plug=1):  # port(接口)：1，2，3，4；  plug（插口）：1，2
    try:
        ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x02, port, plug]))  # 发送信息
        # sleep(0.01)
        t = ser.readline()  # 接收信息
        # sleep(0.01)
        t = struct.unpack("<f", t[4:8])[0]
        return t
    except:
        pass


# 舵机模块
def Steer(angle=0, port=1, plug=1):  # angle（角度）：0~180；  port（接口）：1，2，3，4； plug（插口）：1，2
    try:
        angle = int(angle)
        # angle=hex(angle)[2:]
        ser.write(bytearray([0xff, 0xaa, 0x06, 0x00, 0x02, 0x0b, port, plug, angle]))  # 发送信息
        # sleep(0.01)
        x = ser.readline()  # 接收信息
        # sleep(0.01)
        return x
    except:
        pass


# 电子罗盘
def Compass(port=1):  # port(接口)：1，2，3，4
    try:
        ser.write(bytearray([0xff, 0xaa, 0x04, 0x00, 0x01, 0x1a, port]))  # 发送信息
        # sleep(0.01)
        c = ser.readline()  # 接收信息
        # sleep(0.01)
        c = struct.unpack("<f", c[4:8])[0]
        return c
    except:
        pass


# 电位器
def Potentiometer(port=3):  # port:3,4
    try:
        ser.write(bytearray([0xff, 0xaa, 0x04, 0x00, 0x01, 0x04, port]))  # 发送信息
        # sleep(0.01)
        p = ser.readline()  # 接收信息
        # sleep(0.01)
        p = struct.unpack("<f", p[4:8])[0]
        return p
    except:
        pass


# 音量传感器
def Volume(port=3):  # port:3,4
    try:
        ser.write(bytearray([0xff, 0xaa, 0x04, 0x00, 0x01, 0x07, port]))  # 发送信息
        # sleep(0.01)
        v = ser.readline()  # 接收信息
        # sleep(0.01)
        v = struct.unpack("<f", v[4:8])[0]
        return v
    except:
        pass


# 限位开关
def Limit_switch(port=1):  # port:1,2,3,4
    try:
        ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x15, port, 0x01]))  # 发送信息
        # sleep(0.01)
        l = ser.readline()  # 接收信息
        # sleep(0.01)
        l = struct.unpack("<f", l[4:8])[0]
        l = [False, True][int(l)]
        return l
    except:
        pass


# 颜色传感器(RGB)
def ColorRGB(port=1, color='red'):  # port:1,2,3,4
    try:
        if color == 'red':
            # R
            ser.write(bytearray([0xff, 0xaa, 0x06, 0x00, 0x01, 0x34, port, 0x01, 0x00]))
            # sleep(0.01)
            try:
                RR = ser.readline()
                # sleep(0.01)
                R = RR[4]
            except:
                R = 0
            return R

        if color == 'green':
            # G
            ser.write(bytearray([0xff, 0xaa, 0x06, 0x00, 0x01, 0x34, port, 0x01, 0x01]))
            # sleep(0.01)
            try:
                GG = ser.readline()
                # sleep(0.01)
                G = GG[4]
            except:
                G = 0
            return G

        if color == 'blue':
            # B
            ser.write(bytearray([0xff, 0xaa, 0x06, 0x00, 0x01, 0x34, port, 0x01, 0x02]))
            # sleep(0.01)
            try:
                BB = ser.readline()
                # sleep(0.01)
                B = BB[4]
            except:
                B = 0
            return B
    except:
        pass


# 颜色传感器(判断) 0 2 4 5 7 9
def Color_judge(port=1, color="white"):  # port（接口）:1，2，3，4；color（颜色）：'white'，'red'，'yellow'，'green'，'blue'，'black'
    try:
        color = {"white": 0, "red": 2, "yellow": 4, "green": 5, "blue": 7, "black": 9}[color]
        ser.write(bytearray([0xff, 0xaa, 0x06, 0x00, 0x01, 0x34, port, 0x02, color]))  # 发送信息
        # sleep(0.01)
        j = ser.readline()[4]  # 接收信息
        if int(j) == 1:
            return True
        else:
            return False
    except:
        pass


# 巡线传感器
def Grayscale(port=1):  # port:1,2,3,4
    try:
        ser.write(bytearray([0xff, 0xaa, 0x04, 0x00, 0x01, 0x11, port]))
        g = ser.readline()
        # sleep(0.01)
        g = struct.unpack("<f", g[4:8])[0]
        return int(g)
    except:
        pass


# 巡线传感器（判断）
def Grayscale_judge(port=1, color="white", lr="left"):  # port:1,2,3,4;    color:颜色 white 或 black；  lr:left 或 right 方向
    try:
        ser.write(bytearray([0xff, 0xaa, 0x04, 0x00, 0x01, 0x11, port]))
        # sleep(0.01)
        ans = ser.readline()
        ans = int(struct.unpack("<f", ans[4:8])[0])
        color = {"white": 0, "black": 1}[color]
        lr = {"left": 0, "right": 1}[lr]
        if color == 0 and lr == 0:
            anslist = [False, False, True, True]
            a = anslist[ans]
        if color == 0 and lr == 1:
            anslist = [False, True, False, True]
            a = anslist[ans]
        if color == 1 and lr == 0:
            anslist = [True, True, False, False]
            a = anslist[ans]
        if color == 1 and lr == 1:
            anslist = [True, False, True, False]
            a = anslist[ans]
        return a
    except:
        pass


# 遥控器
def Control(key):  # key(按键):'A'，'B'，'C'，'D'，'E'，'F'，'up'，'down'，'right'，'left'，'middle'，0，1，2，3，4，5，6，7，8，9
    if key in ['A', 'B', 'C', 'D', 'E', 'F', 'up', 'down', 'right', 'left', 'middle', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
        keys = {"A": 0x45, "B": 0x46, "C": 0x47, "D": 0x44, "E": 0x43, "F": 0x0d, "up": 0x40, "down": 0x19,
                "right": 0x09, "left": 0x07, "middle": 0x15,
                0: 0x16, 1: 0x0c, 2: 0x18, 3: 0x5e, 4: 0x08, 5: 0x1c, 6: 0x5a, 7: 0x42, 8: 0x52, 9: 0x4a}
        key = keys[key]
        while True:
            try:
                ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x0e, 0x00, key]))
                # sleep(0.01)
                y = ser.readline()[4]
                return y
            except:
                continue


# 灯带
def Lightbelt(port=1, plug=1, lamp=1, R=30, G=0, B=0):
    # port(接口)：1，2，3，4；  plug（插口）：1，2；  lamp（灯）：0，1，2，3，4，5，6，7，8，9，10，11，12，13，14，15
    # R:0~255;   G:0~255;  B:0~255
    try:
        ser.write(
            bytearray([0xff, 0xaa, 0x09, 0x00, 0x02, 0x08, port, plug, lamp, R, G, B]))  # 发送消息
        # sleep(0.01)
        x = ser.readline()  # 接收消息
        return x
    except:
        pass


# 温湿度
def TemAndHum(port=1, th="Tem"):  # port(接口)：1，2，3，4；  th（温度或湿度）：'Tem'，'Hum'
    try:
        th = {"Tem": 1, "Hum": 0}[th]
        ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x17, port, th]))
        # sleep(0.01)
        ans = ser.readline()[4]
        return ans
    except:
        pass


# 板载按钮是否按下
# @timer
def is_onboard_button_pressed(is_pressed):
    # is_pressed : 1: 已按下；False: 0
    try:
        ser.write(bytearray([0xff, 0xaa, 0x05, 0x00, 0x01, 0x23, 0x07, 1 - is_pressed]))
        response = ser.readline()
        response = response[4]
    except Exception as e:
        return
    else:
        return bool(response & 1)


if __name__ == "__main__":
    RoboCon()
    # import time
    for _ in range(3):
        is_onboard_button_pressed(1)
    for _ in range(2):
        is_onboard_button_pressed(0)
    RoboClose()
