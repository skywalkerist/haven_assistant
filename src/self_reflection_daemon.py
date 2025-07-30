#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自思考后台守护进程 - 每30分钟触发一次自思考事件

事件概率配置：
- 记忆清理 (_summarize_similar_memories): 30%
- 画像更新 (_reflect_on_profile): 35% 
- 关系分析 (_discover_relationships): 25%
- 全局认知 (_synthesize_global_experience): 10%

运行间隔：30分钟
守护进程模式：后台低消耗运行
"""

import time
import signal
import sys
import os
import random
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional

# 添加必要的路径
sys.path.append('/home/xuanwu/haven_ws/src')

from memory_agent import MemoryAgent

class SelfReflectionDaemon:
    """
    自思考后台守护进程
    """
    
    def __init__(self, interval_minutes: int = 30):
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.is_running = False
        self.memory_agent: Optional[MemoryAgent] = None
        
        # 配置日志
        self._setup_logging()
        
        # 定义四个事件及其概率
        self.events = {
            'summarize_similar': {
                'probability': 0.30,
                'name': '记忆清理',
                'description': '随机挑选10条同一人的记忆，检测相似或无意义记忆，精简删除并保留最新记忆',
                'function': self._trigger_summarize_similar,
                'count': 0  # 执行次数统计
            },
            'update_profile': {
                'probability': 0.35,
                'name': '画像更新', 
                'description': '随机分析一个人物的记忆，更新优化其个人画像',
                'function': self._trigger_reflect_on_profile,
                'count': 0
            },
            'discover_relationships': {
                'probability': 0.25,
                'name': '关系分析',
                'description': '随机分析两个人的记忆，推断关系并更新用户画像',
                'function': self._trigger_discover_relationships,
                'count': 0
            },
            'global_synthesis': {
                'probability': 0.10,
                'name': '全局认知',
                'description': '提取时间相近记忆，理解总体主题，维护机器人脑海文件',
                'function': self._trigger_synthesize_global_experience,
                'count': 0
            }
        }
        
        # 统计信息
        self.total_runs = 0
        self.start_time = None
        self.last_run_time = None
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # 验证概率总和
        total_prob = sum(event['probability'] for event in self.events.values())
        if abs(total_prob - 1.0) > 0.001:
            raise ValueError(f"事件概率总和不等于1.0，当前总和：{total_prob}")
    
    def _setup_logging(self):
        """
        设置日志系统
        """
        log_dir = "/home/xuanwu/haven_ws/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "self_reflection_daemon.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        """
        信号处理函数 - 优雅关闭
        """
        self.logger.info(f"收到信号 {signum}，准备关闭守护进程...")
        self.stop()
    
    def _create_memory_agent(self):
        """
        创建记忆智能体实例
        """
        try:
            # DeepSeek API配置
            deepseek_api_key = "sk-fdabadb2973b4795b2444da60e75152f"
            deepseek_base_url = "https://api.deepseek.com"
            memory_file_path = "/home/xuanwu/haven_ws/demos/data/memory_tree.json"
            
            # 创建记忆智能体
            self.memory_agent = MemoryAgent(
                deepseek_api_key=deepseek_api_key,
                deepseek_base_url=deepseek_base_url,
                memory_file_path=memory_file_path
            )
            
            self.logger.info("✅ 记忆智能体初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 记忆智能体初始化失败: {e}")
            return False
    
    def _select_random_event(self) -> str:
        """
        基于概率随机选择一个事件
        
        Returns:
            选中的事件键名
        """
        rand_num = random.random()
        cumulative_prob = 0.0
        
        for event_key, event_info in self.events.items():
            cumulative_prob += event_info['probability']
            if rand_num <= cumulative_prob:
                return event_key
        
        # 如果由于浮点数精度问题没有选中，返回最后一个事件
        return list(self.events.keys())[-1]
    
    def _execute_reflection_event(self):
        """
        执行一次自思考事件
        """
        if not self.memory_agent:
            self.logger.error("❌ 记忆智能体未初始化")
            return
        
        # 选择随机事件
        selected_event_key = self._select_random_event()
        selected_event = self.events[selected_event_key]
        
        self.logger.info(f"🎯 触发事件: {selected_event['name']} (概率: {selected_event['probability']*100:.1f}%)")
        
        # 执行对应的函数
        try:
            start_time = time.time()
            selected_event['function']()
            execution_time = time.time() - start_time
            
            # 更新统计
            selected_event['count'] += 1
            self.total_runs += 1
            self.last_run_time = datetime.now()
            
            self.logger.info(f"✅ {selected_event['name']} 执行完成 (耗时: {execution_time:.2f}秒)")
            
        except Exception as e:
            self.logger.error(f"❌ {selected_event['name']} 执行失败: {e}")
            import traceback
            self.logger.error(f"错误详情: {traceback.format_exc()}")
    
    def _trigger_summarize_similar(self):
        """触发记忆清理事件"""
        self.memory_agent.self_reflect('summarize_similar')
    
    def _trigger_reflect_on_profile(self):
        """触发画像更新事件"""
        self.memory_agent.self_reflect('update_profile')
    
    def _trigger_discover_relationships(self):
        """触发关系分析事件"""
        self.memory_agent.self_reflect('discover_relationships')
    
    def _trigger_synthesize_global_experience(self):
        """触发全局认知事件"""
        self.memory_agent.self_reflect('global_synthesis')
    
    def _log_statistics(self):
        """
        记录统计信息
        """
        if self.start_time:
            running_time = datetime.now() - self.start_time
            self.logger.info(f"📊 运行统计 - 总运行时长: {running_time}")
            self.logger.info(f"📊 总执行次数: {self.total_runs}")
            
            if self.last_run_time:
                self.logger.info(f"📊 上次执行时间: {self.last_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 各事件执行次数统计
            for event_key, event_info in self.events.items():
                count = event_info['count']
                expected_rate = event_info['probability'] * 100
                actual_rate = (count / max(self.total_runs, 1)) * 100
                self.logger.info(f"📊 {event_info['name']}: {count}次 (实际{actual_rate:.1f}%, 期望{expected_rate:.1f}%)")
    
    def _daemon_loop(self):
        """
        守护进程主循环
        """
        self.logger.info(f"🔄 守护进程主循环启动，间隔: {self.interval_minutes}分钟")
        
        while self.is_running:
            try:
                # 计算下次执行时间
                next_run_time = datetime.now() + timedelta(minutes=self.interval_minutes)
                self.logger.info(f"⏰ 下次自思考时间: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 等待指定时间间隔
                sleep_start = time.time()
                while self.is_running and (time.time() - sleep_start) < self.interval_seconds:
                    time.sleep(1)  # 每秒检查一次是否需要停止
                
                # 如果在等待期间收到停止信号，退出循环
                if not self.is_running:
                    break
                
                # 执行自思考事件
                self.logger.info("🧠 开始执行定时自思考...")
                self._execute_reflection_event()
                
                # 每10次执行记录一次统计信息
                if self.total_runs % 10 == 0:
                    self._log_statistics()
                    
            except Exception as e:
                self.logger.error(f"❌ 守护进程循环出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续
    
    def start(self):
        """
        启动守护进程
        """
        if self.is_running:
            self.logger.warning("⚠️ 守护进程已在运行")
            return
        
        self.logger.info("🚀 启动自思考守护进程...")
        
        # 初始化记忆智能体
        if not self._create_memory_agent():
            self.logger.error("❌ 无法启动守护进程：记忆智能体初始化失败")
            return
        
        # 记录启动信息
        self.start_time = datetime.now()
        self.is_running = True
        
        self.logger.info("="*60)
        self.logger.info("🧠 自思考守护进程配置:")
        for event_key, event_info in self.events.items():
            self.logger.info(f"   📊 {event_info['name']}: {event_info['probability']*100:.1f}%")
        self.logger.info(f"   ⏱️ 执行间隔: {self.interval_minutes}分钟")
        self.logger.info("="*60)
        
        # 启动守护进程循环
        try:
            self._daemon_loop()
        except KeyboardInterrupt:
            self.logger.info("🛑 收到键盘中断信号")
        finally:
            self.stop()
    
    def stop(self):
        """
        停止守护进程
        """
        if not self.is_running:
            return
        
        self.logger.info("🛑 正在停止守护进程...")
        self.is_running = False
        
        # 记录最终统计
        self._log_statistics()
        
        self.logger.info("👋 自思考守护进程已停止")
    
    def get_status(self) -> Dict:
        """
        获取守护进程状态
        """
        status = {
            'is_running': self.is_running,
            'interval_minutes': self.interval_minutes,
            'total_runs': self.total_runs,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'event_counts': {key: info['count'] for key, info in self.events.items()}
        }
        return status


def create_pid_file(pid_file_path: str):
    """
    创建PID文件
    """
    try:
        with open(pid_file_path, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"❌ 创建PID文件失败: {e}")
        return False


def remove_pid_file(pid_file_path: str):
    """
    删除PID文件
    """
    try:
        if os.path.exists(pid_file_path):
            os.remove(pid_file_path)
    except Exception as e:
        print(f"⚠️ 删除PID文件失败: {e}")


def main():
    """
    主函数
    """
    # PID文件路径
    pid_file = "/tmp/self_reflection_daemon.pid"
    
    try:
        # 检查是否已有实例在运行
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            
            # 检查进程是否还在运行
            try:
                os.kill(old_pid, 0)  # 发送信号0检查进程是否存在
                print(f"❌ 守护进程已在运行 (PID: {old_pid})")
                print(f"如需停止现有进程，请运行: kill {old_pid}")
                sys.exit(1)
            except OSError:
                # 进程不存在，删除旧的PID文件
                os.remove(pid_file)
        
        # 创建PID文件
        if not create_pid_file(pid_file):
            sys.exit(1)
        
        # 创建并启动守护进程
        daemon = SelfReflectionDaemon(interval_minutes=30)
        
        try:
            daemon.start()
        finally:
            # 清理PID文件
            remove_pid_file(pid_file)
            
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        remove_pid_file(pid_file)
        sys.exit(1)


if __name__ == "__main__":
    main()