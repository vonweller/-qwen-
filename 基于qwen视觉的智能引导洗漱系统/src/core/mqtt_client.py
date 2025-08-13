"""
MQTT客户端 - 处理物联网通信
"""

import json
import paho.mqtt.client as mqtt
from PyQt5.QtCore import QObject, pyqtSignal
from src.utils.config_manager import ConfigManager

class MQTTClient(QObject):
    """MQTT客户端"""
    
    # 信号定义
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    toothpaste_ready = pyqtSignal()  # 牙膏准备就绪
    message_received = pyqtSignal(str, str)  # 主题, 消息
    start_brushing_requested = pyqtSignal()  # 请求开始刷牙
    stop_brushing_requested = pyqtSignal()   # 请求停止刷牙
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.client = None
        self.is_connected = False
        
        self.setup_client()
        
    def setup_client(self):
        """设置MQTT客户端"""
        try:
            self.client = mqtt.Client()
            
            # 设置认证信息
            username = self.config.get('mqtt.username')
            password = self.config.get('mqtt.password')
            if username and password:
                self.client.username_pw_set(username, password)
            
            # 设置回调函数
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            
            # 连接到MQTT服务器
            broker = self.config.get('mqtt.broker', 'localhost')
            port = self.config.get('mqtt.port', 1883)
            
            print(f"连接MQTT服务器: {broker}:{port}")
            self.client.connect(broker, port, 60)
            self.client.loop_start()
            
        except Exception as e:
            print(f"MQTT客户端设置失败: {e}")
            
    def on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            print("MQTT连接成功")
            self.is_connected = True
            self.connected.emit()
            
            # 订阅sp主题用于刷牙控制
            client.subscribe("sp")
            print("订阅主题: sp (刷牙控制)")
            
            # 订阅配置文件中的其他主题
            topics = self.config.get('mqtt.topics', {})
            for topic_name, topic in topics.items():
                client.subscribe(topic)
                print(f"订阅主题: {topic}")
                
        else:
            print(f"MQTT连接失败，错误代码: {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        print("MQTT连接断开")
        self.is_connected = False
        self.disconnected.emit()
        
    def on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"收到MQTT消息 - 主题: {topic}, 内容: {payload}")
            
            # 处理刷牙控制消息 (sp主题)
            if topic == "sp" or topic == "siot/sp":
                self.handle_brushing_control_message(payload)
            
            # 处理特定主题的消息
            toothpaste_topic = self.config.get('mqtt.topics.toothpaste')
            if topic == toothpaste_topic:
                self.handle_toothpaste_message(payload)
            
            # 发送通用消息信号
            self.message_received.emit(topic, payload)
            
        except Exception as e:
            print(f"处理MQTT消息失败: {e}")
            
    def handle_brushing_control_message(self, payload):
        """处理刷牙控制消息"""
        try:
            message = payload.strip()
            print(f"处理刷牙控制消息: {message}")
            
            if message == "开始刷牙":
                print("MQTT收到开始刷牙指令")
                self.start_brushing_requested.emit()
            elif message == "停止刷牙":
                print("MQTT收到停止刷牙指令")
                self.stop_brushing_requested.emit()
            else:
                print(f"未识别的刷牙控制消息: {message}")
                
        except Exception as e:
            print(f"处理刷牙控制消息失败: {e}")
    
    def handle_toothpaste_message(self, payload):
        """处理牙膏相关消息"""
        try:
            # 尝试解析JSON
            data = json.loads(payload)
            
            # 检查是否是牙膏准备就绪的信号
            if data.get('action') == 'toothpaste_ready' or data.get('status') == 'ready':
                print("检测到牙膏准备就绪信号")
                self.toothpaste_ready.emit()
                
        except json.JSONDecodeError:
            # 如果不是JSON格式，检查文本内容
            if 'toothpaste' in payload.lower() or '牙膏' in payload:
                print("检测到牙膏相关消息")
                self.toothpaste_ready.emit()
                
    def publish_message(self, topic, message):
        """发布消息"""
        if not self.is_connected:
            print("MQTT未连接，无法发布消息")
            return False
            
        try:
            if isinstance(message, dict):
                message = json.dumps(message, ensure_ascii=False)
                
            result = self.client.publish(topic, message)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"消息发布成功 - 主题: {topic}, 内容: {message}")
                return True
            else:
                print(f"消息发布失败 - 错误代码: {result.rc}")
                return False
                
        except Exception as e:
            print(f"发布消息失败: {e}")
            return False
            
    def publish_status(self, status_data):
        """发布状态信息"""
        status_topic = self.config.get('mqtt.topics.status')
        if status_topic:
            return self.publish_message(status_topic, status_data)
        return False
        
    def disconnect(self):
        """断开连接"""
        if self.client and self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()
            
    def reconnect(self):
        """重新连接"""
        if self.client:
            try:
                self.client.reconnect()
            except Exception as e:
                print(f"MQTT重连失败: {e}")
                
    def get_connection_status(self):
        """获取连接状态"""
        return self.is_connected