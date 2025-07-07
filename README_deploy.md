# UI-TARS 1.5 HuggingFace Endpoint 部署指南

## 1. HuggingFace Inference Endpoints 云端部署

我们使用 HuggingFace 的 Inference Endpoints 平台来快速部署云端模型。

### 部署步骤

1. **进入部署界面**  
    - 点击 [从 Hugging Face 部署](https://endpoints.huggingface.co/catalog)  
    ![从 Hugging Face 部署](https://huggingface.co/datasets/JjjFangg/Demo_video/resolve/main/deployment_1_formal.png?download=true)  
    - 选择模型 `UI-TARS 1.5 7B` 并点击 **Import Model**  
    ![导入模型](https://huggingface.co/datasets/JjjFangg/Demo_video/resolve/main/deployment_2_formal.png?download=true)  

2. **配置设置**
    - **硬件配置**  
        - 在 `Hardware Configuration` 部分，选择 GPU 实例。不同模型大小推荐如下：  
            - 7B 模型请选择 `GPU L40S 1GPU 48G`（推荐：Nvidia L4 / Nvidia A100）。  
        ![硬件配置](https://huggingface.co/datasets/JjjFangg/Demo_video/resolve/main/deployment_3_formal.png?download=true)

    - **容器配置**  
        - 设置如下参数：  
            - `Max Number of Tokens (per Query)`: 65536  
            - `Max Batch Prefill Tokens`: 65536  
            - `Max Input Length (per Query)`: 65537  
        ![容器配置](https://huggingface.co/datasets/JjjFangg/Demo_video/resolve/main/deployment_4_formal.png?download=true)

    - **环境变量**  
        - 添加如下环境变量：  
            - `CUDA_GRAPHS=0` 避免部署失败。详情见 [issue 2875](https://github.com/huggingface/text-generation-inference/issues/2875)。  
            - `PAYLOAD_LIMIT=8000000` 防止大图片请求失败。详情见 [issue 1802](https://github.com/huggingface/text-generation-inference/issues/1802)。  
        ![环境变量](https://huggingface.co/datasets/JjjFangg/Demo_video/resolve/main/deployment_5_formal.png?download=true)

    - **创建 Endpoint**  
        - 点击 **Create** 创建端点。  
        ![创建 Endpoint](https://huggingface.co/datasets/JjjFangg/Demo_video/resolve/main/deployment_6_formal.png?download=true)

    - **进入设置**  
        - 部署完成后会看到确认页面，需要进入设置页面。  
        ![完成](https://huggingface.co/datasets/JjjFangg/Demo_video/resolve/main/deployment_7_formal.png?download=true)
    
    - **更新 URI** -
        - 进入 Container 页面，将 Container URI 设置为 ghcr.io/huggingface/text-generation-inference:3.2.1，并**点击 Update Endpoint 应用更改**。 
        ![完成](https://huggingface.co/datasets/JjjFangg/Demo_video/resolve/main/deployment_8_formal.png?download=true)


## 2. API 使用示例

### **Python 测试代码**  
```python
# pip install openai
import io
import re
import json
import base64
from PIL import Image
from io import BytesIO
from openai import OpenAI

def add_box_token(input_string):
    # 步骤1：将字符串拆分为单独动作
    if "Action: " in input_string and "start_box=" in input_string:
        suffix = input_string.split("Action: ")[0] + "Action: "
        actions = input_string.split("Action: ")[1:]
        processed_actions = []
        for action in actions:
            action = action.strip()
            # 步骤2：用正则提取坐标（start_box 或 end_box）
            coordinates = re.findall(r"(start_box|end_box)='\((\d+),\s*(\d+)\)'", action)
            
            updated_action = action  # 以原始动作为起点
            for coord_type, x, y in coordinates:
                # 转换 x 和 y 为整数
                updated_action = updated_action.replace(f"{coord_type}='({x},{y})'", f"{coord_type}='<|box_start|>({x},{y})<|box_end|>'")
            processed_actions.append(updated_action)
        
        # 步骤5：重组最终字符串
        final_string = suffix + "\n\n".join(processed_actions)
    else:
        final_string = input_string
    return final_string

client = OpenAI(
    base_url="https:xxx",
    api_key="hf_xxx"
)

result = {}
messages = json.load(open("./data/test_messages.json"))
for message in messages:
    if message["role"] == "assistant":
        message["content"] = add_box_token(message["content"])
        print(message["content"])

chat_completion = client.chat.completions.create(
    model="tgi",
    messages=messages,
    top_p=None,
    temperature=0.0,
    max_tokens=400,
    stream=True,
    seed=None,
    stop=None,
    frequency_penalty=None,
    presence_penalty=None
)

response = ""
for message in chat_completion:
    response += message.choices[0].delta.content
print(response)
```

### **期望输出** ###
```python
Thought: 我看到Preferences窗口已经打开了，但这里显示的都是系统资源相关的设置。要设置图片的颜色模式，我得先看看左侧的选项列表。嗯，"Color Management"这个选项看起来很有希望，应该就是处理颜色管理的地方。让我点击它看看里面有什么选项。
Action: click(start_box='(177,549)')
```