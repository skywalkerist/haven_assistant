# -*- coding: utf-8 -*-
import os
import sys
jkrc_path = '/home/xuanwu/jakaPythonSdk'
if jkrc_path not in sys.path:
        sys.path.append(jkrc_path)
    
    # 设置动态库路径
current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
if jkrc_path not in current_ld_path:
        os.environ['LD_LIBRARY_PATH'] = f"{jkrc_path}:{current_ld_path}"
    
    # 切换到jkrc目录进行导入（因为jkrc.so可能需要在特定目录下才能正常工作）
original_cwd = os.getcwd()
os.chdir(jkrc_path)
    
import jkrc
import json
import time
from pickandplace import hand_control
import select
import sys

robot = None

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
    """
    自适应力度抓握程序
    根据不同手指设置不同的阈值，带安全保护
    """
    print("=== 自适应力度抓握程序 ===")
    
    action = hand_control()
    
    open_angle = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    close_angle = [60, 20, 90, 0, 53, 0, 90, 90, 90]
    speedval = [60, 60, 60, 60, 60, 60, 60, 60, 60]  # 较慢的速度
    currentval = [100, 100, 100, 100, 100, 100, 100, 100, 100]
    
    # 不同传感器组不同阈值
    group_thresholds = [30, 25, 25, 20, 15]  # 5个传感器组的阈值
    group_names = ["传感器组1", "传感器组2", "传感器组3", "传感器组4", "传感器组5"]
    safety_limit = 1200  # 安全限制
    
    print("各传感器组触发阈值:")
    for i, (name, threshold) in enumerate(zip(group_names, group_thresholds)):
        print(f"  {name}: {threshold}")
    print(f"  安全限制: {safety_limit}")
    
    # 触发模式选择
    print("\n选择触发模式:")
    print("1. 单组触发 - 任意一个传感器组超过阈值即触发")
    print("2. 多组触发 - 至少2个传感器组同时超过阈值")
    print("3. 主要组触发 - 传感器组1或组2超过阈值")
    
    # mode = input("输入选择 (1/2/3): ").strip()
    
    # if mode == "2":
    min_groups = 2
    mode_name = "多组触发"
    # elif mode == "3":
    #     min_groups = 1
    #     mode_name = "主要组触发"
    #     primary_groups = [0, 1]  # 组1和组2
    # else:
        # min_groups = 1
        # mode_name = "单组触发"
    
    print(f"使用模式: {mode_name}")
    print("-" * 50)
    
    # 初始化
    action.RS485_AngleSend(open_angle, speedval, currentval)
    time.sleep(2)
    
    is_hand_open = True
    
    print("开始智能检测...")
    print("按 Ctrl+C 退出，输入 'r' 重置")
    has_handshake = False
    while True:
        if has_handshake:
            break
        try:
            if is_hand_open:
                try:
                    sensor_data = action.RS485_SenSor()
                    
                    triggered_groups = []
                    for group_idx in range(5):
                        max_val = max(sensor_data[group_idx])
                        if max_val > group_thresholds[group_idx]:
                            triggered_groups.append(group_idx)
                    
                    # 显示状态
                    status_parts = []
                    for group_idx in range(5):
                        max_val = max(sensor_data[group_idx])
                        threshold = group_thresholds[group_idx]
                        if group_idx in triggered_groups:
                            status_parts.append(f"{group_names[group_idx]}:{max_val}*")
                        else:
                            status_parts.append(f"{group_names[group_idx]}:{max_val}")
                    
                    print(f"\r{' | '.join(status_parts)}", end="", flush=True)
                    
                    # 根据模式判断是否触发
                    should_trigger = False
                    
                    # if len(triggered_groups) >= min_groups: # mode == "1" and 
                    #     should_trigger = True
                    if len(triggered_groups) >= min_groups: # mode == "2" and 
                        should_trigger = True
                    # elif mode == "3" and any(g in primary_groups for g in triggered_groups):
                    #     should_trigger = True
                    
                    if should_trigger:
                        triggered_names = [group_names[i] for i in triggered_groups]
                        print(f"\n\n{mode_name}成功! 触发传感器组: {', '.join(triggered_names)}")
                        
                        # 使用安全闭手函数
                        success = safe_close_hand(action, close_angle, speedval, currentval, safety_limit)
                        is_hand_open = False
                        has_handshake = True
                        
                        if success:
                            print("智能安全抓握完成!")
                        else:
                            print("抓握过程中触发安全保护")
                
                except Exception as e:
                    print(f"\r传感器错误: {e}", end="", flush=True)
                    time.sleep(0.5)
            
            time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n程序退出")
    # 松手,停顿两秒给出握手时间
    action.RS485_AngleSend(open_angle, speedval, currentval)
    time.sleep(2)


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
    # 读取记录的位置数据
    positions = JsonLoad('/home/xuanwu/jakaPythonSdk/json/woshou1.json')
    positions_reverse = JsonLoad('/home/xuanwu/jakaPythonSdk/json/woshou1_reverse.json')
    # 初始化机器人
    robot = robotInit()

    # 回放数据
    replay_positions(robot, positions)

    # 安全抓取
    adaptive_force_grasp()

    # 回放数据
    replay_positions(robot, positions_reverse)

    robot.logout()
        

if __name__ == "__main__":
    main()