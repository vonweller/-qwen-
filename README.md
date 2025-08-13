# 🦷 智能洗漱引导系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.10-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**基于QwenVL视觉模型的智能刷牙引导系统**

集成AI视觉分析、YOLO姿态检测、MQTT物联网通信的现代化洗漱解决方案

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [系统架构](#-系统架构) • [配置说明](#️-配置说明) • [开发文档](#-开发文档)

</div>

---

## 📋 项目概述

智能洗漱引导系统是一个基于Python开发的现代化刷牙引导应用，通过集成**QwenVL视觉大模型**、**YOLO11姿态检测**和**PyQt5界面框架**，为用户提供科学、智能的刷牙指导体验。

### 🎯 核心亮点

- 🤖 **AI视觉分析**: 基于QwenVL大模型实时分析刷牙动作规范性
- 🎯 **姿态检测**: YOLO11精准识别刷牙姿势和位置
- 🌐 **物联网集成**: MQTT协议连接智能硬件设备
- 📊 **数据追踪**: 完整的刷牙记录和成就系统
- 🎨 **现代界面**: 薄荷绿主题的清新UI设计

## ✨ 功能特性

### 🦷 智能刷牙引导
- **实时动作分析**: QwenVL模型分析刷牙技巧和覆盖度
- **姿态检测**: YOLO11检测刷牙姿势是否标准
- **步骤指导**: 科学的刷牙步骤引导和时间管理
- **语音提醒**: 智能语音播报和定时提醒

### 📱 用户界面
- **摄像头实时预览**: 高清摄像头画面显示
- **动态进度追踪**: 可视化刷牙进度和评分
- **成就系统**: 刷牙徽章和里程碑记录
- **数据统计**: 详细的刷牙历史和趋势分析

### 🌐 物联网功能
- **MQTT通信**: 与智能牙刷、水龙头等设备联动
- **硬件集成**: 支持多种智能洗漱设备
- **天气集成**: 智能天气查询和生活建议

### 📊 数据管理
- **用户档案**: 个性化设置和偏好管理
- **刷牙记录**: 完整的历史数据存储
- **评分系统**: 科学的刷牙质量评估

## 🚀 快速开始

### 系统要求

- **操作系统**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python版本**: 3.10 或更高版本
- **硬件要求**: 摄像头设备, 4GB+ RAM
- **网络**: 稳定的互联网连接（用于AI分析）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/vonweller/-qwen-.git
cd -qwen-
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置API密钥**
```bash
# 编辑 config/config.json
# 添加你的QwenVL API密钥
```

5. **启动应用**
```bash
python main.py
```

### 快速配置

首次运行需要配置以下信息：

```json
{
  "qwen": {
    "api_key": "your-qwen-api-key",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-vl-max-latest"
  },
  "mqtt": {
    "broker": "your-mqtt-broker",
    "port": 1883,
    "username": "your-username",
    "password": "your-password"
  }
}
```

## 🏗️ 系统架构

```
智能洗漱引导系统/
├── 📁 src/
│   ├── 🎨 ui/                    # 用户界面模块
│   │   ├── main_window.py        # 主窗口
│   │   ├── camera_widget.py      # 摄像头组件
│   │   ├── rating_widget.py      # 评分组件
│   │   └── records_widget.py     # 记录组件
│   ├── 🧠 core/                  # 核心业务逻辑
│   │   ├── qwen_analyzer.py      # QwenVL分析器
│   │   ├── yolo_pose_detector.py # YOLO姿态检测
│   │   ├── brush_controller.py   # 刷牙控制器
│   │   ├── mqtt_client.py        # MQTT客户端
│   │   └── audio_player.py       # 音频播放器
│   └── 🛠️ utils/                 # 工具类
│       ├── config_manager.py     # 配置管理
│       ├── data_manager.py       # 数据管理
│       └── weather_api.py        # 天气API
├── 📁 config/                    # 配置文件
├── 📁 data/                      # 数据存储
├── 📁 assets/                    # 资源文件
└── 📄 main.py                    # 程序入口
```

### 核心技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **PyQt5** | 5.15.10 | GUI框架 |
| **OpenCV** | 4.8.1 | 计算机视觉 |
| **QwenVL** | Latest | AI视觉分析 |
| **YOLO11** | 8.0.196 | 姿态检测 |
| **MQTT** | 1.6.1 | 物联网通信 |
| **PyTorch** | 1.9.0+ | 深度学习框架 |

## ⚙️ 配置说明

### QwenVL API配置

获取API密钥：[阿里云DashScope](https://dashscope.aliyuncs.com/)

```json
{
  "qwen": {
    "api_key": "sk-xxxxxxxxxx",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-vl-max-latest",
    "max_tokens": 1000,
    "temperature": 0.7
  }
}
```

### MQTT设备配置

```json
{
  "mqtt": {
    "broker": "mqtt.example.com",
    "port": 1883,
    "username": "device_user",
    "password": "device_pass",
    "topics": {
      "toothpaste_ready": "smart_bathroom/toothpaste/ready",
      "water_flow": "smart_bathroom/faucet/flow",
      "brush_status": "smart_bathroom/toothbrush/status"
    }
  }
}
```

### 摄像头设置

```json
{
  "camera": {
    "device_id": 0,
    "resolution": [1280, 720],
    "fps": 30,
    "auto_focus": true
  }
}
```

## 📖 使用指南

### 1. 启动系统
- 运行 `python main.py`
- 点击"启动摄像头"按钮
- 确认摄像头画面正常显示

### 2. 开始刷牙
- 点击"🦷 开始刷牙"按钮
- 按照屏幕提示完成各个步骤
- 系统实时分析并给出指导

### 3. 查看结果
- 刷牙完成后查看评分
- 获得成就徽章
- 查看改进建议

### 4. 历史记录
- 点击"📊 查看记录"
- 分析刷牙趋势
- 设定个人目标

## 🔧 开发文档

### 环境搭建

```bash
# 开发环境
pip install -r requirements-dev.txt

# 代码格式化
black src/
flake8 src/

# 类型检查
mypy src/
```

### 项目结构说明

- **UI层**: PyQt5界面组件，负责用户交互
- **业务层**: 核心算法和逻辑处理
- **数据层**: 配置管理和数据存储
- **硬件层**: MQTT通信和设备控制

### API接口

#### QwenVL分析接口
```python
from src.core.qwen_analyzer import QwenAnalyzer

analyzer = QwenAnalyzer()
result = analyzer.analyze_brushing_action(image_frame)
```

#### YOLO姿态检测
```python
from src.core.yolo_pose_detector import YoloPoseDetector

detector = YoloPoseDetector()
poses = detector.detect_pose(image_frame)
```

### 扩展开发

1. **添加新的检测算法**
   - 继承 `BaseDetector` 类
   - 实现 `detect()` 方法
   - 注册到检测器管理器

2. **集成新硬件设备**
   - 扩展 `MQTTClient` 类
   - 添加设备特定的消息处理
   - 更新配置文件格式

3. **自定义UI组件**
   - 继承 `QWidget` 基类
   - 实现自定义绘制逻辑
   - 集成到主窗口布局

## 🐛 故障排除

### 常见问题

<details>
<summary><strong>摄像头无法启动</strong></summary>

**可能原因**:
- 摄像头被其他程序占用
- 设备ID配置错误
- 驱动程序问题

**解决方案**:
```python
# 检查可用摄像头
import cv2
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i} is available")
        cap.release()
```
</details>

<details>
<summary><strong>QwenVL API调用失败</strong></summary>

**可能原因**:
- API密钥无效或过期
- 网络连接问题
- API配额不足

**解决方案**:
- 检查API密钥有效性
- 验证网络连接
- 查看API使用配额
</details>

<details>
<summary><strong>MQTT连接失败</strong></summary>

**可能原因**:
- 服务器地址错误
- 认证信息无效
- 防火墙阻止连接

**解决方案**:
```bash
# 测试MQTT连接
mosquitto_pub -h your-broker -p 1883 -u username -P password -t test -m "hello"
```
</details>

## 📊 性能优化

### 系统性能

- **CPU使用率**: < 30% (Intel i5 8代+)
- **内存占用**: < 500MB
- **摄像头延迟**: < 100ms
- **AI分析响应**: < 2s

### 优化建议

1. **降低摄像头分辨率**提升帧率
2. **调整AI分析频率**平衡精度和性能
3. **启用GPU加速**提升YOLO检测速度
4. **优化UI刷新率**减少CPU占用

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献方式

1. **Fork** 项目到你的GitHub
2. **创建** 功能分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **创建** Pull Request

### 开发规范

- 遵循 PEP 8 代码风格
- 添加适当的注释和文档
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [QwenVL](https://github.com/QwenLM/Qwen-VL) - 强大的视觉语言模型
- [YOLO](https://github.com/ultralytics/ultralytics) - 实时目标检测框架
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 跨平台GUI框架
- [OpenCV](https://opencv.org/) - 计算机视觉库

## 📞 联系我们

- **项目地址**: [GitHub Repository](https://github.com/vonweller/-qwen-)
- **问题反馈**: [Issues](https://github.com/vonweller/-qwen-/issues)
- **功能建议**: [Discussions](https://github.com/vonweller/-qwen-/discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个星标！**

Made with ❤️ by [vonweller](https://github.com/vonweller)

</div>