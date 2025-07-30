# 超级智能体系统 - 使用说明

## 📋 系统概述

超级智能体是一个集成了面部识别、语音对话和记忆系统的完整AI解决方案。系统采用模块化设计，解决了不同Python环境的兼容性问题。

## 🏗️ 系统架构

```
┌─────────────────────┐    HTTP API    ┌──────────────────────┐
│   面部识别服务       │ ◄──────────── │   超级智能体主程序    │
│   (face环境)        │               │   (base环境)         │
│                    │               │                     │
│ - 人脸识别          │               │ - 状态管理           │
│ - 机械臂控制        │               │ - 对话系统           │
│ - 相机处理          │               │ - 记忆管理           │
└─────────────────────┘               └──────────────────────┘
        │                                        │
        │                                        │
    ┌───▼────┐                              ┌────▼────┐
    │ 硬件层  │                              │ API层   │
    │        │                              │         │
    │- 相机   │                              │- DeepSeek│
    │- 机械臂 │                              │- 语音接口│
    └────────┘                              └─────────┘
```

## 🚀 快速开始

### 1. 环境准备

**Face环境** (面部识别服务):
```bash
conda activate face
pip install flask requests
```

**Base环境** (主程序):
```bash
conda activate base  # 或使用默认环境
pip install flask requests chardet openai
```

### 2. 启动系统

**方式一: 自动启动 (推荐)**
```bash
cd /home/xuanwu/haven_ws/src
python start_system.py
```

**方式二: 手动启动**

终端1 (启动面部识别服务):
```bash
conda activate face
cd /home/xuanwu/haven_ws/src
python face_recognition_service.py
```

终端2 (启动超级智能体):
```bash
conda activate base
cd /home/xuanwu/haven_ws/src
python super_intelligent_agent.py
```

### 3. 使用流程

1. **系统启动**: 所有服务正常启动后，智能体进入休眠状态
2. **唤醒**: 输入 `wake` 命令唤醒智能体
3. **识别**: 系统自动进行面部识别
   - 如果识别到注册用户，直接开始对话
   - 如果未识别到用户，机器人将摇头寻找
4. **对话**: 输入 `chat` 开始与识别到的用户对话
5. **结束**: 说出告别语或输入 `quit` 结束

## 📁 文件结构

```
src/
├── super_intelligent_agent.py      # 主程序 - 超级智能体
├── face_recognition_service.py     # 面部识别服务 (face环境)
├── face_recognition_client.py      # 面部识别客户端 (base环境)
├── memory_agent.py                 # 记忆智能体
├── semantic_memory.py              # 语义记忆系统
├── start_system.py                 # 系统启动脚本
├── test_super_agent.py             # 系统测试脚本
├── install_dependencies.py         # 依赖安装脚本
└── myTools/
    └── recognize_oop.py             # 原始面部识别 (face环境)
```

## 🎯 核心功能

### 1. 智能状态管理
- **SLEEPING**: 休眠状态，等待唤醒
- **SCANNING**: 扫描模式，后台持续检测用户
- **SEARCHING**: 搜索模式，主动转头寻找用户
- **CHATTING**: 对话模式，与用户进行交互

### 2. 面部识别系统
- 实时人脸检测和识别
- 支持多用户注册数据库
- 智能跟随功能
- 搜索模式：-60°到+60°范围搜索

### 3. 对话和记忆系统
- 基于DeepSeek的智能对话
- 语义记忆存储和检索
- 用户画像自动更新
- 上下文记忆管理

## ⚙️ 配置说明

### 主要配置项

```python
# 面部识别配置
face_config = FaceRecognitionConfig(
    service_url="http://localhost:5001",  # 服务地址
    recognition_threshold=0.4,            # 识别阈值
    left_threshold=300,                   # 左侧跟随边界
    right_threshold=340,                  # 右侧跟随边界
    follow_delta_angle=15                 # 跟随角度步长
)

# 系统配置
super_config = SuperAgentConfig(
    face_config=face_config,
    deepseek_api_key="your-api-key",      # DeepSeek API密钥
    search_angle_range=(-60, 60),         # 搜索角度范围
    search_step=15,                       # 搜索步长
    search_delay=2.0,                     # 搜索延迟
    continuous_scan_interval=0.5,         # 扫描间隔
    unknown_user_timeout=5.0              # 未知用户超时
)
```

### 数据库配置

面部数据库位置: `/home/xuanwu/taskAgent/config/face_db.json`
记忆数据库位置: `/home/xuanwu/haven_ws/src/data/memory_tree.json`

## 🧪 测试系统

```bash
# 运行完整测试
python test_super_agent.py

# 测试服务连接
python start_system.py test

# 查看帮助
python start_system.py help
```

## 🔧 故障排除

### 常见问题

1. **面部识别服务连接失败**
   - 检查face环境是否正确激活
   - 确认端口5001未被占用
   - 检查防火墙设置

2. **相机初始化失败**
   - 确认Orbbec相机已连接
   - 检查相机驱动和权限
   - 确认相机序列号配置正确

3. **DeepSeek API调用失败**
   - 验证API密钥是否正确
   - 检查网络连接
   - 确认API额度充足

4. **记忆系统错误**
   - 检查数据目录权限
   - 确认embedding服务可用
   - 验证JSON文件格式

### 日志和调试

- 系统运行日志会显示在控制台
- 错误信息包含详细的故障原因
- 可通过修改代码中的print语句调整日志级别

## 🎨 扩展功能

系统采用模块化设计，易于扩展：

1. **添加新的识别算法**: 修改face_recognition_service.py
2. **集成语音功能**: 在super_intelligent_agent.py中添加语音接口
3. **扩展对话能力**: 修改memory_agent.py中的对话逻辑
4. **添加新的硬件控制**: 在相应的服务中添加API接口

## 📞 技术支持

- 系统基于Python 3.8+开发
- 支持Linux环境 (已在树莓派上测试)
- 模块化设计，易于维护和扩展
- 完整的API接口，支持远程调用

---

**版本**: 1.0  
**更新日期**: 2025-01-25  
**开发环境**: Python 3.8, Ubuntu/Raspbian