#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取JAKA机器人真实DH参数和坐标系信息
用于校准逆运动学算法
"""

import sys
import time
# 添加当前目录到路径
sys.path.append('/home/xuanwu/haven_ws/src')
sys.path.append('/home/xuanwu/jakaPythonSdk')
import jkrc

def get_robot_parameters():
    """获取机器人DH参数和坐标系信息"""
    
    robot = jkrc.RC("192.168.10.90")
    
    try:
        # 登录机器人
        ret = robot.login()
        if ret[0] != 0:
            print(f"登录失败: {ret}")
            return None
        print("成功登录机器人")
        
        # 获取DH参数
        print("\n1. 获取DH参数:")
        ret = robot.get_dh_param()
        if ret[0] == 0:
            dh_params = ret[1]
            print(f"DH参数获取成功:")
            print(f"  alpha (连杆扭角): {dh_params['alpha']}")
            print(f"  a (连杆长度): {dh_params['a']}")  
            print(f"  d (连杆偏移): {dh_params['d']}")
            print(f"  joint_homeoff (关节零位偏移): {dh_params['joint_homeoff']}")
        else:
            print(f"获取DH参数失败: {ret}")
            dh_params = None
        
        # 获取当前工具坐标系信息
        print("\n2. 获取工具坐标系信息:")
        ret = robot.get_tool_id()
        if ret[0] == 0:
            current_tool_id = ret[1]
            print(f"当前工具ID: {current_tool_id}")
            
            ret = robot.get_tool_data(current_tool_id)
            if ret[0] == 0:
                tool_data = ret[2]
                print(f"工具坐标系数据: {tool_data}")
            else:
                print(f"获取工具数据失败: {ret}")
                tool_data = None
        else:
            print(f"获取工具ID失败: {ret}")
            current_tool_id = None
            tool_data = None
        
        # 获取当前用户坐标系信息
        print("\n3. 获取用户坐标系信息:")
        ret = robot.get_user_frame_id()
        if ret[0] == 0:
            current_user_id = ret[1]
            print(f"当前用户坐标系ID: {current_user_id}")
            
            ret = robot.get_user_frame_data(current_user_id)
            if ret[0] == 0:
                user_data = ret[2]
                print(f"用户坐标系数据: {user_data}")
            else:
                print(f"获取用户坐标系数据失败: {ret}")
                user_data = None
        else:
            print(f"获取用户坐标系ID失败: {ret}")
            current_user_id = None
            user_data = None
        
        # 获取当前关节角度
        print("\n4. 获取当前关节角度:")
        ret = robot.get_joint_position()
        if ret[0] == 0:
            joint_pos = list(ret[1])
            print(f"关节角度: {joint_pos}")
        else:
            print(f"获取关节角度失败: {ret}")
            joint_pos = None
        
        # 获取当前TCP位置
        print("\n5. 获取当前TCP位置:")
        ret = robot.get_tcp_position()
        if ret[0] == 0:
            tcp_pos = list(ret[1])
            print(f"TCP位置: {tcp_pos}")
        else:
            print(f"获取TCP位置失败: {ret}")
            tcp_pos = None
        
        robot.logout()
        print("\n机器人登出成功")
        
        return {
            'dh_params': dh_params,
            'tool_id': current_tool_id,
            'tool_data': tool_data,
            'user_frame_id': current_user_id,
            'user_frame_data': user_data,
            'current_joint_pos': joint_pos,
            'current_tcp_pos': tcp_pos
        }
        
    except Exception as e:
        print(f"获取参数时发生错误: {e}")
        try:
            robot.logout()
        except:
            pass
        return None

def test_known_pose():
    """测试已知的位姿数据"""
    print("\n" + "="*60)
    print("测试已知位姿数据")
    print("="*60)
    
    # 已知的测试数据
    joint_pos = [3.0842961823933233, -0.2715896269355082, -0.5782682961808643, 
                -1.4860420547306827, -2.0072935245137047, -0.3146226716101579]
    tcp_pos = [664, 143, 137, 2.220472221706119, 1.0168719843116243, 2.5074985063509914]
    
    print(f"已知关节角度: {joint_pos}")
    print(f"已知TCP位置: {tcp_pos}")
    
    robot = jkrc.RC("192.168.10.90")
    
    try:
        ret = robot.login()
        if ret[0] != 0:
            print(f"登录失败: {ret}")
            return
        
        print("\n正在移动到已知关节位置...")
        # 这里可以选择是否实际移动机器人
        # robot.joint_move(joint_pos, 0, True, 0.1)
        # time.sleep(2)
        
        # 验证当前位置
        ret = robot.get_joint_position()
        if ret[0] == 0:
            current_joint = list(ret[1])
            print(f"当前关节角度: {current_joint}")
        
        ret = robot.get_tcp_position()
        if ret[0] == 0:
            current_tcp = list(ret[1])
            print(f"当前TCP位置: {current_tcp}")
        
        robot.logout()
        
    except Exception as e:
        print(f"测试时发生错误: {e}")
        try:
            robot.logout()
        except:
            pass

if __name__ == "__main__":
    print("获取JAKA机器人参数")
    print("="*60)
    
    # 获取机器人参数
    params = get_robot_parameters()
    
    if params:
        print("\n" + "="*60)
        print("参数获取完成，可用于更新逆运动学算法")
        print("="*60)
        
        if params['dh_params']:
            print("\n请使用以下DH参数更新算法:")
            dh = params['dh_params']
            print("# 真实DH参数")
            print(f"self.alpha = {dh['alpha']}")  
            print(f"self.a = {dh['a']}")
            print(f"self.d = {dh['d']}")
            print(f"self.joint_homeoff = {dh['joint_homeoff']}")
    
    # 测试已知位姿
    test_known_pose()