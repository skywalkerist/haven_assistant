# Haven Intelligent Assistant System / Haven智能助手系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)]()

[English](#english) | [中文](#chinese)

---

## English

### 🌟 Project Overview

Haven is an intelligent assistant system that integrates facial recognition, voice interaction, robotic arm control, and cloud services. The system adopts a modular design and supports voice wake-up, face recognition, intelligent dialogue, robot control, and other functions.

The Haven Intelligent Assistant System is a comprehensive AI agent platform that integrates speech recognition, natural language dialogue, robot control, facial recognition, and personalized interaction capabilities. The system adopts a modular design, supports distributed deployment, and features powerful task scheduling and execution capabilities.

#### 🎯 Core Features

- **Voice Wake-up**: Listening for "小助小助" keyword activation
- **Face Recognition**: User identity recognition and personalized greetings
- **Intelligent Dialogue**: AI conversation system based on DeepSeek API
- **Robot Control**: Robotic arm point management, movement control, and patrol functions
- **Cloud Integration**: UniCloud functions, task queue management, audio file storage
- **Personalized Voice**: Voice cloning and custom voice generation

### 🏗️ System Architecture

#### Core Components
- **Face Recognition Service**: Runs in face environment, provides HTTP API based on InsightFace
- **Super Intelligent Agent**: Runs in base environment, supports voice wake-up and intelligent dialogue
- **Cloud Client**: Handles various task requests, supports robot control and patrol functions
- **Frontend Application**: Located in app branch, provides user interface and control panel

#### Workflow
1. **Voice Wake-up**: Listens for "小助小助" keyword
2. **Face Recognition**: Identifies user identity, personalized greeting
3. **Intelligent Dialogue**: AI conversation system based on DeepSeek API
4. **Robot Control**: Supports waypoint management, movement control, and patrol functions

### 🚀 Quick Start

#### System Requirements
- Python 3.8+
- Miniconda/Anaconda
- Hardware: Orbbec camera, robotic arm

#### Installation Steps

1. **Clone the Project**
```bash
git clone https://github.com/skywalkerist/haven_assistant.git
cd haven_ws
```

2. **Environment Setup**
```bash
# Create face environment (for face recognition)
conda create -n face python=3.8
conda activate face
pip install insightface pyorbbecsdk opencv-python

# Create base environment (for main system)
conda create -n base python=3.8
conda activate base
pip install requests flask openai psutil
```

3. **Configuration Files**
Ensure the following configuration files exist:
- `config/face_db.json` - Face database
- `config/voices.json` - Voice configuration
- `config/patrol_routes.json` - Patrol routes
- `demos/data/profiles/` - User profile directory

4. **Start System**
```bash
# Method 1: Full system startup
cd demos
python start_system.py

# Method 2: Cloud client only
python app_client.py

# Method 3: Test system connections
python start_system.py test
```

### 📝 Main Features

#### 🎤 Speech Processing System
- **Speech Recognition**: Based on iFlytek Spark ASR, supports Chinese speech-to-text
- **Speech Synthesis**: Supports personalized voice cloning and generation
- **Audio Recording**: High-quality audio capture and processing

#### 🤖 Intelligent Dialogue System
- **DeepSeek Dialogue Engine**: Intelligent conversation based on large language models
- **Context Understanding**: Maintains conversation history and user profiles
- **Personalized Response**: Customized replies based on user characteristics

#### 👁️ Face Recognition System
- **Real-time Face Detection**: High-precision face recognition based on InsightFace
- **User Identity Management**: Supports multi-user registration and identity verification
- **Face Tracking**: Intelligent face following and gaze functionality

#### 🚶 Robot Control System
- **Marker Point Management**: Dynamic addition, deletion, and navigation to specified markers
- **Path Planning**: Intelligent patrol route planning and execution
- **Motion Control**: Precise position control and navigation

#### 💾 Data Management System
- **User Profiles**: Personalized user information storage and management
- **Memory System**: Semantic memory storage and retrieval
- **Configuration Management**: Dynamic system configuration updates

### 🔧 API Configuration

#### Required API Keys
Configure the following API keys in `demos/app_client.py`:

```python
SPARK_APP_ID = 'your_spark_app_id'
SPARK_API_SECRET = 'your_spark_api_secret'
SPARK_API_KEY = 'your_spark_api_key'
DEEPSEEK_API_KEY = 'your_deepseek_api_key'
UNICLOUD_BASE_URL = 'your_unicloud_base_url'
```

#### Configuration Files

- `config/voices.json`: Voice configuration and default tone settings
- `config/patrol_routes.json`: Patrol route configuration
- `demos/data/profiles/`: User profile storage directory

### 📝 Supported Task Types

#### Voice and Dialogue
- `speech_to_text` - Speech to text conversion
- `dialogue` - AI intelligent dialogue
- `record_audio` - Audio recording function
- `train_voice` - Voice model training

#### Robot Control
- `get_marker_list` - Get marker point list
- `add_marker` - Add new marker point
- `delete_marker` - Delete marker point
- `move_to_point` - Move to specified point

#### Patrol Functions
- `get_patrol_routes` - Get patrol routes
- `save_patrol_route` - Save patrol route
- `start_patrol` - Start patrol
- `stop_patrol` - Stop patrol

#### Configuration Management
- `get_voices_config` - Get voice configuration
- `set_voices_config` - Set voice configuration
- `get_profiles_config` - Get user profiles
- `update_profile` - Update user profile

### 📱 Frontend Application

The frontend application is located in the `app` branch and provides:
- User-friendly control interface
- Real-time status monitoring
- Configuration management panel
- Task execution control

Switch to app branch to view frontend code:
```bash
git checkout app
```

### 🔄 Available Commands
- `python start_system.py` - Start complete system
- `python start_system.py test` - Test system connections
- `python start_system.py help` - Show help information
- `python start_system.py shutdown` - Safe system shutdown

### 📊 System Monitoring

#### Service Status Check
```bash
# Check face recognition service
curl http://localhost:5001/api/status

# Check system connections
python start_system.py test
```

#### Safe Shutdown
Use `Ctrl+C` or run shutdown command to safely close the system:
```bash
python start_system.py shutdown
```

#### 👁️ Facial Recognition System
- **Real-time Face Detection**: High-precision face recognition based on InsightFace
- **User Identity Management**: Supports multi-user registration and identity verification
- **Face Tracking**: Intelligent face following and gaze functionality

#### 🚶 Robot Control System
- **Marker Point Management**: Dynamic addition, deletion, and navigation to specified markers
- **Path Planning**: Intelligent patrol route planning and execution
- **Motion Control**: Precise position control and navigation

#### 💾 Data Management System
- **User Profiles**: Personalized user information storage and management
- **Memory System**: Semantic memory storage and retrieval
- **Configuration Management**: Dynamic system configuration updates

### 🔧 Configuration

#### Main Configuration Files

- `config/voices.json`: Voice configuration and default tone settings
- `config/patrol_routes.json`: Patrol route configuration
- `demos/data/profiles/`: User profile storage directory

#### API Key Configuration

Configure the following API keys in `demos/app_client.py`:

```python
SPARK_APP_ID = 'your_spark_app_id'
SPARK_API_SECRET = 'your_spark_api_secret'
SPARK_API_KEY = 'your_spark_api_key'
DEEPSEEK_API_KEY = 'your_deepseek_api_key'
```

### 💡 Usage Examples

#### Basic Voice Dialogue
```python
# After starting the client, the system automatically polls cloud tasks
# Supported task types:

# 1. Speech recognition to dialogue
task = {
    "task": "speech_to_text",
    "params": {"audioUrl": "https://example.com/audio.pcm"}
}

# 2. Text dialogue
task = {
    "task": "dialogue", 
    "params": {"text": "Hello, how's the weather today?"}
}

# 3. Robot navigation
task = {
    "task": "move_to_point",
    "params": {"marker_name": "living_room"}
}
```

#### User Profile Management
```python
# Get user profiles
task = {
    "task": "get_profiles_config"
}

# Update user profile
task = {
    "task": "update_profile",
    "params": {
        "profile_id": "user123",
        "profile_data": {
            "name": "John Doe",
            "preferences": ["music", "reading"],
            "personality": "friendly"
        }
    }
}
```

### 🔄 Task Scheduling Mechanism

The system adopts a cloud polling-based task scheduling mechanism:

1. **Task Submission**: Submit tasks to queue through UniCloud functions
2. **Task Polling**: Client periodically polls cloud for pending tasks
3. **Task Execution**: Call corresponding processing modules based on task type
4. **Status Update**: Real-time feedback of execution results to cloud
5. **Error Handling**: Comprehensive error handling and retry mechanisms

### 🧪 Testing and Debugging

#### Run Tests
```bash
# System connection test
python start_system.py test

# Voice recording test
python test_recording.py

# Dialogue system test
python test_optimization.py
```

#### Debug Mode
```bash
# Enable verbose logging
export DEBUG=1
python app_client.py
```

### 📦 Project Structure

```
xuanwu_control/
├── demos/                      # Demos and main applications
│   ├── app_client.py           # Main client program
│   ├── start_system.py         # System startup script
│   ├── data/                   # Data storage
│   │   └── profiles/           # User profiles
│   └── run_temp/               # Temporary files
├── src/                        # Source code modules
│   ├── super_intelligent_agent.py  # Super intelligent agent
│   ├── face_recognition_*.py   # Face recognition modules
│   ├── memory_agent.py         # Memory agent
│   ├── marker_manager.py       # Marker point management
│   ├── move_controller.py      # Motion control
│   ├── audio_recorder.py       # Audio recording
│   ├── spark_asr.py           # Speech recognition
│   ├── deepseek_dialog.py     # Dialogue system
│   └── voice_cloner.py        # Voice cloning
├── config/                     # Configuration files
│   ├── voices.json            # Voice configuration
│   └── patrol_routes.json     # Patrol routes
└── README.md                  # Project documentation
```

### 🤝 Contributing

Welcome to submit Issues and Pull Requests to improve the project:

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details

### 📞 Contact

- Project Maintainer: [Maintainer Name]
- Email: [Contact Email]
- Project Homepage: [Project Link]

### 🙏 Acknowledgments

Thanks to the following open source projects and services:

- [InsightFace](https://github.com/deepinsight/insightface) - Face Recognition
- [Orbbec SDK](https://github.com/orbbec/pyorbbecsdk) - Depth Camera
- [iFlytek Open Platform](https://www.xfyun.cn/) - Speech Services
- [DeepSeek](https://www.deepseek.com/) - Intelligent Dialogue
- [UniCloud](https://unicloud.dcloud.net.cn/) - Cloud Services

---

## Chinese

### 🌟 项目概述

Haven是一个集成面部识别、语音交互、机械臂控制和云端服务的智能助手系统。系统采用模块化设计，支持语音唤醒、人脸识别、智能对话、机器人控制等多种功能。

Haven智能助手系统是一个综合性AI智能体平台，集成了语音识别、自然语言对话、机器人控制、人脸识别、个性化交互等功能。系统采用模块化设计，支持分布式部署，具备强大的任务调度和执行能力。

#### 🎯 核心特性

- **语音唤醒**: 监听“小助小助”关键词激活
- **人脸识别**: 用户身份识别和个性化问候
- **智能对话**: 基于DeepSeek API的AI对话系统
- **机器人控制**: 机械臂点位管理、移动控制和巡逻功能
- **云端集成**: UniCloud云函数、任务队列管理、音频文件存储
- **个性化语音**: 语音克隆和自定义语音生成

### 🏗️ 系统架构

#### 核心组件
- **面部识别服务**: 运行在face环境，基于InsightFace提供HTTP API
- **超级智能体**: 运行在base环境，支持语音唤醒和智能对话
- **云端客户端**: 处理各种任务请求，支持机器人控制和巡逻功能
- **前端应用**: 位于app分支，提供用户界面和控制面板

#### 工作流程
1. **语音唤醒**: 监听“小助小助”关键词
2. **面部识别**: 识别用户身份，个性化问候
3. **智能对话**: 基于DeepSeek API的AI对话系统
4. **机器人控制**: 支持航点管理、移动控制和巡逻功能

### 🚀 快速开始

#### 环境要求
- Python 3.8+
- Miniconda/Anaconda
- 硬件: Orbbec相机、机械臂

#### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/skywalkerist/haven_assistant.git
cd haven_ws
```

2. **环境配置**
```bash
# 创建face环境 (人脸识别)
conda create -n face python=3.8
conda activate face
pip install insightface pyorbbecsdk opencv-python

# 创建base环境 (主系统)
conda create -n base python=3.8
conda activate base
pip install requests flask openai psutil
```

3. **配置文件**
确保以下配置文件存在:
- `config/face_db.json` - 面部数据库
- `config/voices.json` - 语音配置
- `config/patrol_routes.json` - 巡逻路线
- `demos/data/profiles/` - 用户档案目录

4. **启动系统**
```bash
# 方式1: 完整系统启动
cd demos
python start_system.py

# 方式2: 仅云端客户端
python app_client.py

# 方式3: 测试系统连接
python start_system.py test
```

### 📋 主要功能模块

#### 🎤 语音处理系统
- **语音识别**: 基于讯飞Spark ASR，支持中文语音转文字
- **语音合成**: 支持个性化语音克隆和生成
- **音频录制**: 高质量音频采集和处理

#### 🤖 智能对话系统
- **DeepSeek对话引擎**: 基于大语言模型的智能对话
- **上下文理解**: 维护对话历史和用户画像
- **个性化响应**: 根据用户特征定制回复内容

#### 👁️ 人脸识别系统
- **实时人脸检测**: 基于InsightFace的高精度人脸识别
- **用户身份管理**: 支持多用户注册和身份验证
- **人脸跟踪**: 智能人脸跟随和注视功能

#### 🚶 机器人控制系统
- **标记点管理**: 动态添加、删除、导航到指定标记点
- **路径规划**: 智能巡逻路线规划和执行
- **移动控制**: 精确的位置控制和导航

#### 💾 数据管理系统
- **用户档案**: 个性化用户信息存储和管理
- **记忆系统**: 语义记忆存储和检索
- **配置管理**: 系统配置动态更新

### 🔧 配置说明

#### 主要配置文件

- `config/voices.json`: 语音配置和默认音色设置
- `config/patrol_routes.json`: 巡逻路线配置
- `demos/data/profiles/`: 用户档案存储目录

#### API密钥配置

在 `demos/app_client.py` 中配置以下API密钥:

```python
SPARK_APP_ID = 'your_spark_app_id'
SPARK_API_SECRET = 'your_spark_api_secret'
SPARK_API_KEY = 'your_spark_api_key'
DEEPSEEK_API_KEY = 'your_deepseek_api_key'
```

### 📝 支持的任务类型

#### 语音和对话
- `speech_to_text` - 语音转文字
- `dialogue` - AI智能对话
- `record_audio` - 录音功能
- `train_voice` - 语音模型训练

#### 机器人控制
- `get_marker_list` - 获取点位列表
- `add_marker` - 添加新点位
- `delete_marker` - 删除点位
- `move_to_point` - 移动到指定点位

#### 巡逻功能
- `get_patrol_routes` - 获取巡逻路线
- `save_patrol_route` - 保存巡逻路线
- `start_patrol` - 开始巡逻
- `stop_patrol` - 停止巡逻

#### 配置管理
- `get_voices_config` - 获取语音配置
- `set_voices_config` - 设置语音配置
- `get_profiles_config` - 获取用户档案
- `update_profile` - 更新用户档案

### 📱 前端应用

前端应用位于`app`分支，提供：
- 用户友好的控制界面
- 实时状态监控
- 配置管理面板
- 任务执行控制

切换到app分支查看前端代码：
```bash
git checkout app
```

### 🔄 可用命令
- `python start_system.py` - 启动完整系统
- `python start_system.py test` - 测试系统连接
- `python start_system.py help` - 显示帮助信息
- `python start_system.py shutdown` - 安全关闭系统

### 📋 系统监控

#### 服务状态检查
```bash
# 检查面部识别服务
curl http://localhost:5001/api/status

# 检查系统连接
python start_system.py test
```

#### 安全关闭
使用`Ctrl+C`或运行关闭命令安全关闭系统：
```bash
python start_system.py shutdown
```

### 📦 项目结构

```
haven_ws/
├── demos/                      # 演示和主要应用
│   ├── app_client.py           # 主客户端程序
│   ├── start_system.py         # 系统启动脚本
│   ├── data/                   # 数据存储
│   │   └── profiles/           # 用户档案
│   └── run_temp/               # 临时文件
├── src/                        # 源代码模块
│   ├── super_intelligent_agent.py  # 超级智能体
│   ├── face_recognition_*.py   # 人脸识别模块
│   ├── memory_agent.py         # 记忆智能体
│   ├── marker_manager.py       # 标记点管理
│   ├── move_controller.py      # 移动控制
│   ├── audio_recorder.py       # 音频录制
│   ├── spark_asr.py           # 语音识别
│   ├── deepseek_dialog.py     # 对话系统
│   └── voice_cloner.py        # 语音克隆
├── config/                     # 配置文件
│   ├── voices.json            # 语音配置
│   └── patrol_routes.json     # 巡逻路线
└── README.md                  # 项目说明
```

### 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目:

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

### 🙏 致谢

感谢以下开源项目和服务:

- [InsightFace](https://github.com/deepinsight/insightface) - 人脸识别
- [Orbbec SDK](https://github.com/orbbec/pyorbbecsdk) - 深度相机
- [讯飞开放平台](https://www.xfyun.cn/) - 语音服务
- [DeepSeek](https://www.deepseek.com/) - 智能对话
- [UniCloud](https://unicloud.dcloud.net.cn/) - 云服务

---

**版本**: 2.0  
**更新日期**: 2025-07-30  
**开发环境**: Python 3.8+, Linux/macOS/Windows

---

**Haven - 让AI助手更智能，让交互更自然** 🤖✨