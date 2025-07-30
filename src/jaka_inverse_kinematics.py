#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAKA-Lumi 6轴机械臂解析逆运动学求解器
适用于树莓派低算力环境的高效解析解法
"""

import numpy as np
import math

class JakaInverseKinematics:
    def __init__(self):
        # 真实JAKA DH参数 (从机器人获取)
        # alpha: 连杆扭角 (弧度)
        self.alpha = [0.0, 1.5707963, 0.0, 0.0, 1.5707963, -1.5707963]
        # a: 连杆长度 (mm) 
        self.a = [0.0, 0.0, 897.0, 744.5, 0.0, 0.0]
        # d: 连杆偏移 (mm)
        self.d = [196.5, 0.0, 0.0, -188.35000610351562, 138.5, 120.5]
        # 关节零位偏移
        self.joint_homeoff = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # 关节角度限制 (弧度) - 根据JAKA实际限制设置
        self.joint_limits = [
            (-6.28, 6.28),   # θ1
            (-3.14, 3.14),   # θ2  
            (-3.14, 3.14),   # θ3
            (-6.28, 6.28),   # θ4
            (-3.14, 3.14),   # θ5
            (-6.28, 6.28),   # θ6
        ]
        
        self.eps = 1e-6  # 数值精度
    
    def normalize_angle(self, angle):
        """角度标准化到[-π, π]"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
    
    def check_joint_limits(self, angles):
        """检查关节角度是否在限制范围内"""
        for angle, (min_angle, max_angle) in zip(angles, self.joint_limits):
            if angle < min_angle or angle > max_angle:
                return False
        return True
    
    def dh_transform(self, theta, d, a, alpha):
        """DH变换矩阵"""
        ct = math.cos(theta)
        st = math.sin(theta)
        ca = math.cos(alpha)
        sa = math.sin(alpha)
        
        return np.array([
            [ct, -st*ca,  st*sa, a*ct],
            [st,  ct*ca, -ct*sa, a*st],
            [0,      sa,     ca,    d],
            [0,       0,      0,    1]
        ])
    
    def forward_kinematics(self, joint_angles):
        """正运动学验证"""
        theta1, theta2, theta3, theta4, theta5, theta6 = joint_angles
        
        # DH变换
        T01 = self.dh_transform(theta1, 0, 0, math.pi/2)
        T12 = self.dh_transform(theta2, 0, self.a2, 0)
        T23 = self.dh_transform(theta3, 0, self.a3, 0)
        T34 = self.dh_transform(theta4, 0, 0, math.pi/2)
        T45 = self.dh_transform(theta5, 0, 0, -math.pi/2)
        T56 = self.dh_transform(theta6, self.d6, 0, 0)
        
        # 累积变换
        T06 = T01 @ T12 @ T23 @ T34 @ T45 @ T56
        
        # 提取位置和方向
        position = T06[:3, 3]
        rotation_matrix = T06[:3, :3]
        
        return position, rotation_matrix
    
    def euler_to_rotation_matrix(self, rx, ry, rz):
        """欧拉角转旋转矩阵 (ZYX顺序)"""
        cx, sx = math.cos(rx), math.sin(rx)
        cy, sy = math.cos(ry), math.sin(ry) 
        cz, sz = math.cos(rz), math.sin(rz)
        
        return np.array([
            [cy*cz, -cy*sz, sy],
            [sx*sy*cz + cx*sz, -sx*sy*sz + cx*cz, -sx*cy],
            [-cx*sy*cz + sx*sz, cx*sy*sz + sx*cz, cx*cy]
        ])
    
    def check_workspace(self, position):
        """检查位置是否在工作空间内"""
        x, y, _ = position
        r = math.sqrt(x**2 + y**2)
        
        # 最大伸展半径 (考虑末端执行器长度)
        max_reach = self.a2 + self.a3 + self.d6  # ≈ 376.3mm
        min_reach = abs(self.a2 - self.a3)       # ≈ 79.7mm
        
        if r > max_reach:
            return False, f"位置距离基座过远 ({r:.1f}mm > {max_reach:.1f}mm)"
        if r < min_reach:
            return False, f"位置距离基座过近 ({r:.1f}mm < {min_reach:.1f}mm)"
        
        return True, "位置在工作空间内"
    
    def solve_ik_from_pose(self, pose):
        """
        从6D位姿求解逆运动学
        pose: [x, y, z, rx, ry, rz] - 位置(mm) + 欧拉角(弧度)
        返回: 所有可能的关节角度解
        """
        if len(pose) != 6:
            raise ValueError("pose必须是6个元素的列表: [x, y, z, rx, ry, rz]")
        
        target_pos = np.array(pose[:3])  # 位置
        
        # 检查工作空间
        is_reachable, msg = self.check_workspace(target_pos)
        if not is_reachable:
            print(f"工作空间检查: {msg}")
            return []
        
        target_rot = self.euler_to_rotation_matrix(*pose[3:])  # 欧拉角转旋转矩阵
        
        return self.solve_ik(target_pos, target_rot)
    
    def solve_ik(self, target_pos, target_rot):
        """
        逆运动学求解
        target_pos: 目标位置 [x, y, z] (mm)
        target_rot: 目标旋转矩阵 3x3
        返回: 所有可能的关节角度解
        """
        R = target_rot
        
        solutions = []
        
        # 计算腕部中心点位置 (去除末端执行器长度)
        wrist_center = target_pos - self.d6 * R[:, 2]  # Z轴方向
        wx, wy, wz = wrist_center
        
        # ======== 求解前3关节 (位置) ========
        
        # θ1 求解 (2解)
        r = math.sqrt(wx**2 + wy**2)
        if r < self.eps:
            # 奇点处理: 腕部中心在Z轴上
            theta1_solutions = [0]
        else:
            theta1_1 = math.atan2(wy, wx)
            theta1_2 = theta1_1 + math.pi
            theta1_solutions = [theta1_1, theta1_2]
        
        for theta1 in theta1_solutions:
            theta1 = self.normalize_angle(theta1)
            
            # 计算θ2, θ3 (肘部构型, 2解)
            # 在XZ平面投影求解
            wx_proj = wx * math.cos(theta1) + wy * math.sin(theta1)
            r_xz = math.sqrt(wx_proj**2 + wz**2)
            
            # 余弦定理
            cos_theta3 = (r_xz**2 - self.a2**2 - self.a3**2) / (2 * self.a2 * self.a3)
            
            if abs(cos_theta3) > 1:
                continue  # 无解
            
            # θ3 两解 (肘部朝上/朝下)
            sin_theta3_1 = math.sqrt(1 - cos_theta3**2)
            sin_theta3_2 = -sin_theta3_1
            
            theta3_1 = math.atan2(sin_theta3_1, cos_theta3)
            theta3_2 = math.atan2(sin_theta3_2, cos_theta3)
            
            for theta3 in [theta3_1, theta3_2]:
                theta3 = self.normalize_angle(theta3)
                
                # θ2 求解
                k1 = self.a2 + self.a3 * cos_theta3
                k2 = self.a3 * math.sin(theta3)
                
                theta2 = math.atan2(wz, wx * math.cos(theta1) + wy * math.sin(theta1)) - math.atan2(k2, k1)
                theta2 = self.normalize_angle(theta2)
                
                # ======== 求解后3关节 (姿态) ========
                
                # 计算前3关节的旋转矩阵
                T01 = self.dh_transform(theta1, 0, 0, math.pi/2)
                T12 = self.dh_transform(theta2, 0, self.a2, 0)
                T23 = self.dh_transform(theta3, 0, self.a3, 0)
                
                R03 = (T01 @ T12 @ T23)[:3, :3]
                
                # 腕部相对旋转矩阵
                R36 = R03.T @ R
                
                # 提取欧拉角 (ZYZ约定)
                # θ5 = ±acos(R36[2,2])
                if abs(R36[2, 2]) > 1 - self.eps:
                    # 奇点处理
                    if R36[2, 2] > 0:  # θ5 = 0
                        theta5 = 0
                        theta4 = 0
                        theta6 = math.atan2(R36[1, 0], R36[0, 0])
                    else:  # θ5 = π
                        theta5 = math.pi
                        theta4 = 0
                        theta6 = math.atan2(-R36[1, 0], R36[0, 0])
                    
                    theta4 = self.normalize_angle(theta4)
                    theta5 = self.normalize_angle(theta5)
                    theta6 = self.normalize_angle(theta6)
                    
                    solution = [theta1, theta2, theta3, theta4, theta5, theta6]
                    if self.check_joint_limits(solution):
                        solutions.append(solution)
                else:
                    # 两个θ5解
                    theta5_1 = math.acos(R36[2, 2])
                    theta5_2 = -theta5_1
                    
                    for theta5 in [theta5_1, theta5_2]:
                        sin_theta5 = math.sin(theta5)
                        
                        if abs(sin_theta5) < self.eps:
                            continue
                        
                        theta4 = math.atan2(R36[1, 2] / sin_theta5, R36[0, 2] / sin_theta5)
                        theta6 = math.atan2(R36[2, 1] / sin_theta5, -R36[2, 0] / sin_theta5)
                        
                        theta4 = self.normalize_angle(theta4)
                        theta5 = self.normalize_angle(theta5)
                        theta6 = self.normalize_angle(theta6)
                        
                        solution = [theta1, theta2, theta3, theta4, theta5, theta6]
                        if self.check_joint_limits(solution):
                            solutions.append(solution)
        
        return solutions
    
    def select_best_solution(self, solutions, current_angles=None):
        """
        从多个解中选择最优解
        优先级: 1) 关节限制内 2) 与当前角度最接近 3) 远离奇点
        """
        if not solutions:
            return None
        
        if current_angles is None:
            # 默认选择第一个解
            return solutions[0]
        
        # 选择与当前角度最接近的解
        min_distance = float('inf')
        best_solution = solutions[0]
        
        for solution in solutions:
            distance = sum((a - b)**2 for a, b in zip(solution, current_angles))
            if distance < min_distance:
                min_distance = distance
                best_solution = solution
        
        return best_solution
    
    def get_joint_angles(self, pose):
        """
        面向对象接口：输入位姿列表，输出关节角度列表
        
        Args:
            pose: [x, y, z, rx, ry, rz] - 位置(mm) + 欧拉角(弧度)
            
        Returns:
            joint_pos: [θ1, θ2, θ3, θ4, θ5, θ6] - 关节角度(弧度)
            如无解返回None
        """
        solutions = self.solve_ik_from_pose(pose)
        
        if not solutions:
            return None
            
        # 选择最优解
        best_solution = self.select_best_solution(solutions)
        
        return best_solution


def demo_simple_interface():
    """演示简洁的面向对象接口"""
    ik_solver = JakaInverseKinematics()
    
    # 测试位姿 (工作空间内)
    pose = [300.0, 50.0, 100.0, 0.0, 1.57, 0.0]  # 简单姿态
    
    print("=" * 60)
    print("JAKA逆运动学求解器 - 简洁接口演示")
    print("=" * 60)
    print(f"输入: pose = {pose}")
    
    # 一行代码获取结果
    joint_pos = ik_solver.get_joint_angles(pose)
    
    if joint_pos is not None:
        print("输出: joint_pos = [")
        for angle in joint_pos:
            print(f"    {angle},")
        print("]")
        
        print(f"\n这就是你需要的格式！直接用于机器人控制。")
    else:
        print("目标位置不可达")


def main():
    """测试程序"""
    print("JAKA-Lumi 6轴机械臂逆运动学求解器测试")
    print("="*50)
    
    # 创建求解器实例
    ik_solver = JakaInverseKinematics()
    
    # 测试输入位姿
    input_pose = [591.537473, 1.473219, -107.133057, 1.7403962760684102, 0.8401213944197699, 2.6678284629615354]
    
    print("面向对象接口测试:")
    print(f"输入位姿: {input_pose}")
    print()
    
    # 使用简洁接口
    joint_pos = ik_solver.get_joint_angles(input_pose)
    
    if joint_pos is not None:
        print("输出关节角度 (按你的格式):")
        print("joint_pos=[", end="")
        for i, angle in enumerate(joint_pos):
            if i == len(joint_pos) - 1:
                print(f"{angle}")
            else:
                print(f"{angle},")
        print("]")
        
        print("\n更清晰的格式:")
        print("joint_pos=[")
        for angle in joint_pos:
            print(f"    {angle},")
        print("]")
        
        print(f"\n角度值 (度):")
        for i, angle in enumerate(joint_pos):
            print(f"θ{i+1}: {math.degrees(angle):7.2f}°")
            
        # 验证结果
        print(f"\n正运动学验证:")
        fk_pos, _ = ik_solver.forward_kinematics(joint_pos)
        print(f"计算位置: [{fk_pos[0]:.2f}, {fk_pos[1]:.2f}, {fk_pos[2]:.2f}] mm")
        print(f"目标位置: [{input_pose[0]:.2f}, {input_pose[1]:.2f}, {input_pose[2]:.2f}] mm")
        pos_error = np.linalg.norm(fk_pos - np.array(input_pose[:3]))
        print(f"位置误差: {pos_error:.4f} mm")
        
    else:
        print("无法求解：位置超出工作空间或无可行解")
    
    # 运行简洁接口演示
    # demo_simple_interface()


if __name__ == "__main__":
    main()