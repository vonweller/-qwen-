from openai import OpenAI
import os
import base64


#  Base64 编码格式
def encode_video(video_path):
    with open(video_path, "rb") as video_file:
        return base64.b64encode(video_file.read()).decode("utf-8")

# 将xxxx/test.mp4替换为你本地视频的绝对路径
base64_video = encode_video("xxx/test.mp4")
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key=o"sk-5ae5e5b4e853487aac092031aa70de38",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-vl-max-latest",  
    messages=[
        {
            "role": "system",
            "content": [{"type":"text","text": "You are a helpful assistant."}]},
        {
            "role": "user",
            "content": [
                {
                    # 直接传入视频文件时，请将type的值设置为video_url
                    "type": "video_url",
                    "video_url": {"url": f"data:video/mp4;base64,{base64_video}"},
                },
                {"type": "text", "text": "这段视频描绘的是什么景象?"},
            ],
        }
    ],
)
print(completion.choices[0].message.content)