#!/bin/python3
# 直接 唤醒 并且执行某个函数
import os
import sys
# 将src目录添加到Python路径中，以便导入模块
sys.path.append('/home/xuanwu/pyorbbecsdk/examples')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import snowboydecoder
import sys
import signal
import os
import subprocess as sub
sys.path.append("/home/xuanwu/haven_ws/demos")
import main_dialog
# 执行 bash 类
# pip3 install subprocess 

# class Run():
#     # 初始化 参数;args 为数组 ['python3','xx.py']
#     def __init__(self,args,
#     shell=True,encoding="utf-8"):
#         self.args = args
#         self.shell = shell
#         self.encoding =encoding
#     # 处理 args 为一个字符串 
#     def Handle(self):
#         arg = ''
#         for item in self.args:
#             arg += item +' '
#         return arg
#         # 执行 命令行
#     def run(self):
#         res = self.Handle()
#         res = sub.run(
#             res,
#             shell=self.shell,
#             encoding=self.encoding
#         )
#         #  方便以后对其进行操作
#         return res
# 第二种： 不使用demo，直接对demo进行再封装；只需要填写model的文件名即可
class Rundev():
    def __init__(self,model,sensitivity=0.5,sleep_time=0.03):
        # 外置参数
        self.model = model
        self.sensitivity = sensitivity
        self.sleep_time = sleep_time
        self.detector = None
        #内置参数 
        self.interrupted = False
        self.greeting = '/home/xuanwu/haven_ws/config/greeting.wav'

    def interrupt_callback(self):
        return self.interrupted
    def signal_handler(self,signal, frame):
        self.interrupted = True  

    #  回调函数，语音识别在这里实现
    def callbacks(self):

        # 语音唤醒后，提示ding两声
        # snowboydecoder.play_audio_file()
        # snowboydecoder.play_audio_file()

        #  关闭snowboy功能
        self.detector.terminate()
        
        if os.path.exists(self.greeting):
            print("正在播放招呼语音...")
            os.system(f'aplay -f S16_LE -r 16000 -c 1 {self.greeting}')
        else:
            print("❌ 未生成音频文件")

        # 添加自己的函数
        main_dialog.main()

        # 打开snowboy功能
        self.run()    # wake_up —> monitor —> wake_up  递归调用

    def run(self):
        print('正在监听中.........','按 Ctrl+C 停止运行')

        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)

        self.detector = snowboydecoder.HotwordDetector(
            self.model, 
            sensitivity =self.sensitivity)

        # main loop
        self.detector.start(detected_callback=self.callbacks,
               interrupt_check=self.interrupt_callback,
               sleep_time=self.sleep_time)
        # 使终止
        self.detector.terminate()
        


# 测试
if __name__ == "__main__":
    # os.getcwd()获取当前工作路径
    # args = [
    #     'python3',
    #     os.getcwd()+"/python/snowBoyDemo/demo.py",
    #     os.getcwd()+"/python/snowBoyDemo/xiaoai.pmdl"
    # ]
    # dev = Run(args=args)
    # dev.run()
    dev = Rundev("/home/xuanwu/haven_ws/src/resources/haven.pmdl")
    dev.run()


