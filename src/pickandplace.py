
import serial
import time

# 角度控制
senddatetemp= [0x01, 0x06, 0x00, 0x22, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64
                       , 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64]

class hand_control():
    def __init__(self, port='/dev/ttyACM0'):
        # 设置一个合理的超时时间，例如0.2秒，以避免无限等待
        self.ser = serial.Serial(port, 115200, timeout=0.2)


    def CheckSUM(self,buf,len):
        checktemp = 0
        for i in range(0, len-1):
            checktemp += buf[i]
        return checktemp & 0xff

    # 角度控制
    def RS485_AngleSend(self, angle, speed, current):
        global senddatetemp
        headerval=[0x5a]
        endval =[0x5d]
        senddatetemp= [0x01, 0x06, 0x00, 0x22, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64
                       , 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64]
        for i in range(9):
            senddatetemp[4+3*i] = angle[i]&0xff
            senddatetemp[5 + 3 * i] = speed[i]
            senddatetemp[6 + 3 * i] = current[i]
        senddatavaltemp = [self.CheckSUM(senddatetemp, 32)]
        senddatetemp = headerval + senddatetemp + senddatavaltemp + endval
        self.ser.reset_input_buffer()
        self.ser.write(senddatetemp)
        # 使用带超时的读取，而不是阻塞循环
        recvdate = self.ser.read(8)
        if not (len(recvdate) == 8 and recvdate[0] == 0x5a and recvdate[2] == 0x06):
            print("警告: 角度设置后未收到有效确认")

    # 急停
    def RS485_Stop(self, flag):
        headerval = [0x5a]
        endval = [0x5d]
        senddatetemp = [0x01, 0x20, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        for i in range(9):
            senddatetemp[4+i] = flag[i]
        senddatavaltemp = [self.CheckSUM(senddatetemp, 14)]
        senddatetemp = headerval + senddatetemp + senddatavaltemp + endval
        self.ser.reset_input_buffer()
        self.ser.write(senddatetemp)
        # 使用带超时的读取
        recvdate = self.ser.read(8)
        if not (len(recvdate) == 8 and recvdate[0] == 0x5a and recvdate[2] == 0x20):
            print("警告: 急停后未收到有效确认")
    #急停恢复
    def RS485_LiftStop(self, flag):
        headerval = [0x5a]
        endval = [0x5d]
        senddatetemp = [0x01, 0x30, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        for i in range(9):
            senddatetemp[4+i] = flag[i]
        senddatavaltemp = [self.CheckSUM(senddatetemp, 14)]
        senddatetemp = headerval + senddatetemp + senddatavaltemp + endval
        self.ser.reset_input_buffer()
        self.ser.write(senddatetemp)
        # 使用带超时的读取
        recvdate = self.ser.read(8)
        if not (len(recvdate) == 8 and recvdate[0] == 0x5a and recvdate[2] == 0x30):
            print("警告: 解除急停后未收到有效确认")
    #角度查询
    def RS485_FeedbackAngle(self):
        headerval = [0x5a]
        endval = [0x5d]
        senddatetemp = [0x01, 0xf1, 0x00, 0x08, 0x00]
        senddatavaltemp = [self.CheckSUM(senddatetemp, 6)]
        senddatetemp = headerval + senddatetemp + senddatavaltemp + endval
        self.ser.reset_input_buffer()
        self.ser.write(senddatetemp)
        angletemp = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # 使用带超时的读取
        recvdate = self.ser.read(16)
        if len(recvdate) == 16 and recvdate[0] == 0x5a:
            for i in range(9):
                angletemp[i] = recvdate[5+i]
        else:
            print("警告: 角度查询失败")
        print(f"angletemp:{angletemp}")
        return angletemp
    #电流查询
    def RS485_FeedbackCurrent(self):
        headerval = [0x5a]
        endval = [0x5d]
        senddatetemp = [0x01, 0xf2, 0x00, 0x08, 0x00]
        senddatavaltemp = [self.CheckSUM(senddatetemp, 6)]
        senddatetemp = headerval + senddatetemp + senddatavaltemp + endval
        self.ser.reset_input_buffer()
        self.ser.write(senddatetemp)
        currenttemp = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # 使用带超时的读取
        recvdate = self.ser.read(25)
        if len(recvdate) == 25 and recvdate[0] == 0x5a:
            for i in range(9):
                currenttemp[i] = (recvdate[5 + 2 * i] << 8 | recvdate[6 + 2 * i])
        else:
            print("警告: 电流查询失败")
        return currenttemp

    # 传感器查询
    def RS485_SenSor(self):
        headerval = [0x5a]
        endval = [0x5d]
        senddatetemp = [0x01, 0x01, 0x00, 0x08, 0x00]
        senddatavaltemp = [self.CheckSUM(senddatetemp, 6)]
        senddatetemp = headerval + senddatetemp + senddatavaltemp + endval
        self.ser.reset_input_buffer()
        self.ser.write(senddatetemp)
        
        # 初始化6个传感器的数组 (5个指尖 + 1个手掌)
        sensorval = [[0] * 16 for _ in range(5)]
        sensorval.append([0] * 64) # 手掌有64个点

        # 使用 read_until 来高效地等待响应结束符
        recvdate = self.ser.read_until(expected=b'\x5d')

        if not (recvdate and recvdate[0] == 0x5a and recvdate[-1] == 0x5d):
            print("警告: 传感器查询失败或响应不完整")
            return sensorval

        # 协议规定数据头固定18字节，数据内容可变
        if len(recvdate) >= 25: # 帧头+ID+命令+长度+数据头(18)+校验+帧尾 > 25
            data_headers = recvdate[5:23]
            data_content = recvdate[23:-2]
            data_content_idx = 0

            # 1. 解析5个指尖传感器 (每个16点)
            for i in range(5):
                header_val = (data_headers[i*2] << 8) | data_headers[i*2+1]
                for j in range(16):
                    if (header_val >> j) & 1:
                        if data_content_idx + 1 < len(data_content):
                            point_val = (data_content[data_content_idx] << 8) | data_content[data_content_idx+1]
                            # 恢复被验证为正确的反向映射
                            sensorval[i][15-j] = point_val
                            data_content_idx += 2
                        else:
                            break # 避免数据内容越界

            # 2. 解析手掌传感器 (63点，但我们用64点数组)
            # 手掌数据头在偏移10字节处，占8字节
            palm_header_val = int.from_bytes(data_headers[10:18], 'big')
            for j in range(63):
                if (palm_header_val >> j) & 1:
                    if data_content_idx + 1 < len(data_content):
                        point_val = (data_content[data_content_idx] << 8) | data_content[data_content_idx+1]
                        # 手掌传感器也可能需要反向映射，但协议未明确，我们先用直接映射
                        sensorval[5][j] = point_val
                        data_content_idx += 2
                    else:
                        break # 避免数据内容越界
                        
        return sensorval

    # 力控设定
    def RS485_ForceControl(self, startangle, endangle, speed, current, threshold):
        headerval = [0x5a]
        endval = [0x5d]
        senddatetemp = [0x01, 0x40, 0x00, 0x50, 0x01, 0x4b, 0x64, 0x64, 0x4b, 0x14
                        , 0x14, 0x01, 0x00, 0x64, 0x64, 0x2d, 0x14, 0x14, 0x01, 0x00
                        , 0x64, 0x64, 0x5a, 0x14, 0x14, 0x00, 0x0a, 0x01, 0x00, 0x64
                        , 0x64, 0x00, 0x64, 0x64, 0x01, 0x00, 0x64, 0x64, 0x5a, 0x14
                        , 0x14, 0x00, 0x0a, 0x01, 0x00, 0x64, 0x64, 0x00, 0x64, 0x64
                        , 0x01, 0x00, 0x64, 0x64, 0x5a, 0x14, 0x14, 0x00, 0x0a, 0x01
                        , 0x00, 0x64, 0x64, 0x5a, 0x14, 0x14, 0x00, 0x0a, 0x01, 0x00
                        , 0x64, 0x64, 0x5a, 0x14, 0x14, 0x00, 0x0a]
        szflag = 0
        for i in range(9):
            senddatetemp[4 + i * 7 + szflag] = 0x01
            senddatetemp[5 + i * 7 + szflag] = startangle[i]
            senddatetemp[6 + i * 7 + szflag] = 0x64
            senddatetemp[7 + i * 7 + szflag] = 0x64
            senddatetemp[8 + i * 7 + szflag] = endangle[i]
            senddatetemp[9 + i * 7 + szflag] = speed[i]
            senddatetemp[10 + i * 7 + szflag] = current[i]
            if i == 2 or i == 4 or i == 6 or i == 7:
                szflag += 2
        senddatetemp[25] = (threshold[0] >> 8)
        senddatetemp[26] = (threshold[0] & 0xff)
        senddatetemp[41] = (threshold[1] >> 8)
        senddatetemp[42] = (threshold[1] & 0xff)
        senddatetemp[57] = (threshold[2] >> 8)
        senddatetemp[58] = (threshold[2] & 0xff)
        senddatetemp[66] = (threshold[3] >> 8)
        senddatetemp[67] = (threshold[3] & 0xff)
        senddatetemp[75] = (threshold[4] >> 8)
        senddatetemp[76] = (threshold[4] & 0xff)
        # senddatetemp[77] = (threshold[4] & 0xff)
        senddatavaltemp = [self.CheckSUM(senddatetemp, 78)]
        senddatetemp = headerval + senddatetemp + senddatavaltemp + endval
        self.ser.write(senddatetemp)
        while True:
            recvlentemp = self.ser.inWaiting()
            if recvlentemp == 8:
                recvdate = self.ser.read(8)
                if recvdate[0] == 0x5a and recvdate[2] == 0x40:
                    break
            time.sleep(1)
    #力控启动
    def RS485_ForceStart(self, forceflag):
        headerval = [0x5a]
        endval = [0x5d]
        senddatetemp = [0x01, 0x4a, 0x00, 0x08, 0x00]
        if forceflag == True:
            senddatetemp[4]=0X03
        else:
            senddatetemp[4] = 0X00
        senddatavaltemp = [self.CheckSUM(senddatetemp, 6)]
        senddatetemp = headerval + senddatetemp + senddatavaltemp + endval
        self.ser.write(senddatetemp)
        while True:
            recvlentemp = self.ser.inWaiting()
            if recvlentemp == 8:
                recvdate = self.ser.read(8)
                if recvdate[0] == 0x5a and recvdate[2] == 0x4a:
                    break
            time.sleep(1)
def move_phone_test():
    # global senddatetemp
    action = hand_control()
    angleval = [00, -40, 00, 0, 00, 0, 00, 0, 0]
    close_angle = [60, 20, 90, 0, 53, 0, 90, 90, 90]
    open_angle = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    speedval = [100, 100, 100, 100, 100, 100, 100, 100, 100]
    currentvalval = [100, 100, 100, 100, 100, 100, 100, 100, 100]
    stopval = [1, 1, 1, 1, 0, 0, 0, 0, 1]
    #action.RS485_Stop(stopval)
    #action.RS485_LiftStop(stopval)

    threshold=[10, 10, 10, 10, 10]
    time1 = time.time()
    startangle = action.RS485_FeedbackAngle()
    time2 = time.time()
    print(f"startangle:{startangle}, time taken for feedback: {time2 - time1:.8f} seconds")
    action.RS485_ForceControl(startangle, close_angle, speedval, currentvalval, threshold)
    time3 = time.time()
    print(f"Time taken for force control: {time3 - time2:.8f} seconds")
    action.RS485_ForceStart(True)
    time4 = time.time()
    print(f"Time taken for force start: {time4 - time3:.8f} seconds")
    startangle = action.RS485_FeedbackAngle()
    action.RS485_ForceControl(startangle, open_angle, speedval, currentvalval, threshold)
    action.RS485_ForceStart(False)


    # action.RS485_AngleSend(open_angle, speedval, currentvalval) # 
    # time.sleep(2)
    # action.RS485_AngleSend(close_angle, speedval, currentvalval) # 

    # angleval=action.RS485_FeedbackAngle()
    # currentvalval=action.RS485_FeedbackCurrent()
    # sensorval = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    # sensorval = action.RS485_SenSor()
    # print("sensorval:", sensorval)
    # threshold=[10, 10, 10, 10, 10]
    # action.RS485_ForceControl(angleval,open_angle,speedval,currentvalval,threshold)
    # action.RS485_ForceStart(True)
    # action.RS485_ForceStart(False)

if __name__ == "__main__":
    move_phone_test()
