# -*- coding: utf-8 -*-
import jkrc
import json
import time
from pickandplace import hand_control
import select
import sys

robot = None
action = None

def safe_close_hand(action, close_angle, speedval, currentval, safety_limit):
    """
    安全闭手函数：在闭手过程中监控力度，超过安全限制立即停止
    """
    print("开始安全闭手...")
    
    # 首先启动闭手动作
    action.RS485_AngleSend(close_angle, speedval, currentval)
    
    # 监控闭手过程中的力度
    start_time = time.time()
    max_monitor_time = 5  # 最大监控5秒
    
    try:
        while time.time() - start_time < max_monitor_time:
            # 读取传感器数据
            sensor_data = action.RS485_SenSor()
            
            # 计算全局最大值
            all_sensor_values = []
            for finger_idx in range(5):
                finger_sensors = sensor_data[finger_idx]
                all_sensor_values.extend(finger_sensors)
            
            current_max_force = max(all_sensor_values)
            
            print(f"\r闭手中... 当前最大力度: {current_max_force:3d}", end="", flush=True)
            
            # 检查是否超过安全限制
            if current_max_force > safety_limit:
                print(f"\n!!! 安全保护触发 !!! 力度 {current_max_force} 超过安全限制 {safety_limit}")
                
                # 立即停止所有运动
                stop_flags = [1, 1, 1, 1, 1, 1, 1, 1, 1]  # 全部急停
                action.RS485_Stop(stop_flags)
                print("已执行急停，保护安全")
                
                # 等待一下再解除急停
                time.sleep(1)
                action.RS485_LiftStop(stop_flags)
                print("急停已解除")
                
                return False  # 返回False表示因安全保护而停止
            
            time.sleep(0.2)  # 200ms检查一次
        
        print("\n闭手动作完成")
        return True  # 返回True表示正常完成
        
    except Exception as e:
        print(f"\n安全监控过程中发生错误: {e}")
        return False

def adaptive_force_grasp():
    global action
    """
    自适应力度抓握程序
    根据不同手指设置不同的阈值，带安全保护
    """
    print("=== 自适应力度抓握程序 ===")
    
    # action = hand_control()
    
    open_angle = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    close_angle = [60, 20, 90, 0, 53, 0, 90, 90, 90]
    speedval = [60, 60, 60, 60, 60, 60, 60, 60, 60]  # 较慢的速度
    currentval = [100, 100, 100, 100, 100, 100, 100, 100, 100]
    
    # 不同传感器组不同阈值
    safety_limit = 1200  # 安全限制

    try:
        # 使用安全闭手函数
        # success = safe_close_hand(action, close_angle, speedval, currentval, safety_limit)
        # is_hand_open = False
        action.RS485_AngleSend(close_angle, speedval, currentval)
        if success:
            print("智能安全抓握完成!")
        else:
            print("抓握过程中触发安全保护")
    
    except Exception as e:
        print(f"\r传感器错误: {e}", end="", flush=True)
        time.sleep(0.5)
    
    time.sleep(0.1)




def replay_positions(robot, positions):
    print("开始复现运动...")
    for i, position in enumerate(positions):
        print(f"移动到位置 {i+1}: {position}")
        
        # 使用 joint_move 进行关节运动，阻塞模式，速度 0.1 rad/s
        ret = robot.joint_move(position, 0, True, 0.3) # 参数0表示绝对运动表示
        
        if ret[0] == 0:
            print(f"成功移动到位置 {i+1}")
        else:
            print(f"移动失败，错误码: {ret[0]}")
            break
        
    print("运动复现完成")

def JsonLoad(filePath):
    try:
        with open(filePath, 'r') as f:
            positions = json.load(f)
    except FileNotFoundError:
        print("错误: 找不到 recorded_positions.json 文件")
        return
    except json.JSONDecodeError:
        print("错误: recorded_positions.json 文件格式错误")
        return
    if len(positions) == 0:
        print("没有找到记录的位置数据")
        return
    else:
        print(f"找到 {len(positions)} 个记录的位置")
    return positions

def robotInit():
    global robot
    robot = jkrc.RC("192.168.10.90")
    try:
        robot.login()
        print("机器人连接成功")
        robot.power_on()
        print("机器人上电")
        robot.enable_robot()
        print("机器人使能")
    
    except Exception as e:
        print(f"发生错误: {e}")
    return robot


def main():
    global action
    open_angle = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    speedval = [60, 60, 60, 60, 60, 60, 60, 60, 60]  # 较慢的速度
    currentval = [100, 100, 100, 100, 100, 100, 100, 100, 100]

    # 读取记录的位置数据
    # positions_zhuaqu_reverse = JsonLoad('/home/xuanwu/jakaPythonSdk/json/zhuaqu_reverse.json')
    positions_zhuaqu = JsonLoad('/home/xuanwu/jakaPythonSdk/json/zhuaqu.json')
    positions_fangxia = JsonLoad('/home/xuanwu/jakaPythonSdk/json/fangxia.json')
    positions_gohome = JsonLoad('/home/xuanwu/jakaPythonSdk/json/go_home.json')
    # 初始化机器人,启动程序时先确保机器人处于手放下的状态
    robot = robotInit()
    action = hand_control()
    action.RS485_AngleSend(open_angle, speedval, currentval)

    # 回放数据
    replay_positions(robot, positions_zhuaqu)

    # 抓取物体
    adaptive_force_grasp()

    # 回放数据
    replay_positions(robot, positions_fangxia)

    time.sleep(2)
    # 放下物体
    action.RS485_AngleSend(open_angle, speedval, currentval)
    time.sleep(1)

    # 回放数据
    replay_positions(robot, positions_gohome)

    robot.logout()
        

if __name__ == "__main__":
    main()