# 智能洗漱台系统

基于Python的智能刷牙引导系统，集成QwenVLM训练模型、OpenCV和PyQt5。

## 功能特性

### 🦷 核心功能
- **智能定时提醒**: 自定义刷牙时间，定时语音提醒
- **MQTT物联网通信**: 接收硬件设备信号，如牙膏准备就绪
- **AI视觉刷牙引导**: 使用QwenVLM实时分析刷牙动作规范性
- **互动式刷牙教学**: 科学刷牙动作指导和步骤追踪
- **成就记录系统**: 刷牙数据统计和成就徽章系统
- **智能天气提醒**: 集成天气查询和生活建议

### 🎨 界面特色
- 现代简约设计风格
- 薄荷绿主色调，清新健康
- 实时摄像头显示
- 动态进度追踪
- 卡片式信息展示

## 系统要求

- Python 3.10+
- Windows 10/11
- 摄像头设备
- 网络连接（用于AI分析和天气查询）

## 安装运行

1. 确保使用正确的Python环境：
```bash
"D:\Do\Codes\PythonProject\PythonENV\Tool\python.exe"
```

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python main.py
```

## 配置说明

### 配置文件位置
- 主配置：`config/config.json`
- 用户数据：`data/user_data.json`
- 刷牙记录：`data/brush_records.json`

### QwenVLM配置
在 `config/config.json` 中配置您的API密钥：
```json
{
  "qwen": {
    "api_key": "your-api-key-here",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-vl-max-latest"
  }
}
```

### MQTT配置
```json
{
  "mqtt": {
    "broker": "your-mqtt-broker",
    "port": 1883,
    "username": "your-username",
    "password": "your-password"
  }
}
```

## 使用指南

### 首次使用
1. 启动程序后，点击"启动摄像头"按钮
2. 在设置中配置您的刷牙时间偏好
3. 确保QwenVLM API密钥已正确配置

### 开始刷牙
1. 点击"🦷 开始刷牙"按钮
2. 按照屏幕指示完成各个刷牙步骤
3. 系统会实时分析您的刷牙动作
4. 完成后查看评分和建议

### 查看记录
- 点击"📊 查看记录"查看历史数据
- 查看获得的成就徽章
- 分析刷牙习惯趋势

## 故障排除

### 常见问题

**摄像头无法启动**
- 检查摄像头是否被其他程序占用
- 在设置中尝试不同的设备ID

**MQTT连接失败**
- 检查网络连接
- 确认MQTT服务器地址和端口
- 验证用户名和密码

**语音播放失败**
- 确保系统音频设备正常
- 检查音量设置
- Windows系统需要SAPI语音引擎

**AI分析失败**
- 检查网络连接
- 验证QwenVLM API密钥
- 确认API配额充足

## 技术架构

### 核心模块
- `src/ui/`: 用户界面模块
- `src/core/`: 核心业务逻辑
- `src/utils/`: 工具类和配置管理
- `config/`: 配置文件
- `data/`: 数据存储

### 主要依赖
- PyQt5: GUI框架
- OpenCV: 计算机视觉
- OpenAI: QwenVLM API客户端
- paho-mqtt: MQTT通信
- pygame: 音频播放
- pyttsx3: 文本转语音

## 开发说明

### 项目结构
```
智能洗漱台系统/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖包列表
├── config/
│   └── config.json        # 主配置文件
├── src/
│   ├── ui/                # 界面模块
│   ├── core/              # 核心功能
│   └── utils/             # 工具类
└── data/                  # 数据存储
```

### 扩展开发
- 添加新的刷牙动作检测算法
- 集成更多硬件设备
- 扩展成就系统
- 添加数据导出功能

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址：基于qwen视觉的智能引导洗漱系统
- 技术支持：请查看代码注释和文档