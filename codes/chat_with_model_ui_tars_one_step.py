from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import base64
import re
import json
import math
from pathlib import Path
import os
import time
import pyautogui  # 添加pyautogui库

# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime._exceptions import ArkAPIError
from volcenginesdkarkruntime import Ark


def parse_action_output(output_text):
    # 提取Thought部分
    thought_match = re.search(r'Thought:(.*?)\nAction:', output_text, re.DOTALL)
    thought = thought_match.group(1).strip() if thought_match else ""

    # 提取Action部分
    action_match = re.search(r'Action:(.*?)(?:\n|$)', output_text, re.DOTALL)
    action_text = action_match.group(1).strip() if action_match else ""

    # 初始化结果字典
    result = {
        "thought": thought,
        "action": "",
        "key": None,
        "content": None,
        "start_box": None,
        "end_box": None,
        "direction": None
    }

    if not action_text:
        return json.dumps(result, ensure_ascii=False)

    # 解析action类型
    action_parts = action_text.split('(')
    action_type = action_parts[0]
    result["action"] = action_type

    # 解析参数
    if len(action_parts) > 1:
        params_text = action_parts[1].rstrip(')')
        params = {}

        # 处理键值对参数
        for param in params_text.split(','):
            param = param.strip()
            if '=' in param:
                key, value = param.split('=', 1)
                key = key.strip()
                value = value.strip().strip('\'"')

                # 处理bbox格式
                if 'box' in key:
                    # 提取坐标数字
                    numbers = re.findall(r'\d+', value)
                    if numbers:
                        coords = [int(num) for num in numbers]
                        if len(coords) == 4:
                            if key == 'start_box':
                                result["start_box"] = coords
                            elif key == 'end_box':
                                result["end_box"] = coords
                elif key == 'key':
                    result["key"] = value
                elif key == 'content':
                    # 处理转义字符
                    value = value.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
                    result["content"] = value
                elif key == 'direction':
                    result["direction"] = value

    return json.dumps(result, ensure_ascii=False, indent=2)


def coordinates_convert(relative_bbox, img_size):
    """
       将相对坐标[0,1000]转换为图片上的绝对像素坐标

       参数:
           relative_bbox: 相对坐标列表/元组 [x1, y1, x2, y2] (范围0-1000)
           img_size: 图片尺寸元组 (width, height)

       返回:
           绝对坐标列表 [x1, y1, x2, y2] (单位:像素)

       示例:
           >>> coordinates_convert([500, 500, 600, 600], (1000, 2000))
           [500, 1000, 600, 1200]  # 对于2000高度的图片，y坐标×2
       """
    # 参数校验
    if len(relative_bbox) != 4 or len(img_size) != 2:
        raise ValueError("输入参数格式应为: relative_bbox=[x1,y1,x2,y2], img_size=(width,height)")

    # 解包图片尺寸
    img_width, img_height = img_size

    # 计算绝对坐标
    abs_x1 = int(relative_bbox[0] * img_width / 1000)
    abs_y1 = int(relative_bbox[1] * img_height / 1000)
    abs_x2 = int(relative_bbox[2] * img_width / 1000)
    abs_y2 = int(relative_bbox[3] * img_height / 1000)

    return [abs_x1, abs_y1, abs_x2, abs_y2]


def draw_box_and_show(image, start_box=None, end_box=None, direction=None):
    """
    在图片上绘制两个边界框和指向箭头

    参数:
        image: PIL.Image对象或图片路径
        start_box: 起始框坐标 [x1,y1,x2,y2] (绝对坐标)
        end_box: 结束框坐标 [x1,y1,x2,y2] (绝对坐标)
        direction: 操作方向 ('up', 'down', 'left', 'right' 或 None)
    """
    box_color = "red"
    arrow_color = "blue"
    box_width = 10
    drag_arrow_length = 150  # drag操作箭头长度

    draw = ImageDraw.Draw(image)

    # 绘制起始框
    if start_box is not None:
        draw.rectangle(start_box, outline=box_color, width=box_width)

    # 绘制结束框
    if end_box is not None:
        draw.rectangle(end_box, outline=box_color, width=box_width)

    # 处理不同类型的操作
    if start_box is not None:
        start_center = ((start_box[0] + start_box[2]) / 2, (start_box[1] + start_box[3]) / 2)

        if end_box is not None:
            # 绘制两个框之间的连接线和箭头
            end_center = ((end_box[0] + end_box[2]) / 2, (end_box[1] + end_box[3]) / 2)
            draw.line([start_center, end_center], fill=arrow_color, width=box_width)
            draw_arrow_head(draw, start_center, end_center, arrow_color, box_width * 3)
        elif direction is not None:
            # 处理drag操作（只有start_box和direction）
            end_point = calculate_drag_endpoint(start_center, direction, drag_arrow_length)
            draw.line([start_center, end_point], fill=arrow_color, width=box_width)
            draw_arrow_head(draw, start_center, end_point, arrow_color, box_width * 3)

    # 显示结果图片
    plt.imshow(image)
    plt.axis('on')  # 不显示坐标轴
    plt.show()


def draw_arrow_head(draw, start, end, color, size):
    """
    绘制箭头头部
    """
    # 计算角度
    angle = math.atan2(end[1] - start[1], end[0] - start[0])

    # 计算箭头三个点的位置
    p1 = end
    p2 = (
        end[0] - size * math.cos(angle + math.pi / 6),
        end[1] - size * math.sin(angle + math.pi / 6)
    )
    p3 = (
        end[0] - size * math.cos(angle - math.pi / 6),
        end[1] - size * math.sin(angle - math.pi / 6)
    )

    # 绘制箭头
    draw.polygon([p1, p2, p3], fill=color)


def calculate_drag_endpoint(start_point, direction, length):
    """
    计算drag操作的箭头终点

    参数:
        start_point: 起点坐标 (x, y)
        direction: 方向 ('up', 'down', 'left', 'right')
        length: 箭头长度

    返回:
        终点坐标 (x, y)
    """
    x, y = start_point
    if direction == 'up':
        return (x, y - length)
    elif direction == 'down':
        return (x, y + length)
    elif direction == 'left':
        return (x - length, y)
    elif direction == 'right':
        return (x + length, y)
    else:
        return (x, y)  # 默认不移动

def image_to_base64(image_path):
    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.svg': 'image/svg+xml',
    }
    with open(image_path, "rb") as image_file:
        binary_data = image_file.read()
        base64_data = base64.b64encode(binary_data).decode("utf-8")
    return f"data:{mime_types.get(ext, 'image/png')};base64,{base64_data}"


def run(img_path, user_prompt, history_text=""):
    """
    运行模型分析图像
    
    参数:
        img_path: 图像路径
        user_prompt: 用户指令
        history_text: 历史操作记录，默认为空
        
    返回:
        模型的响应内容
    """
    # 直接使用API密钥
    api_key = "b92c9fcf-b2eb-497e-80cb-69aa7b347876"  # 请替换为您的有效API密钥
    
    # 系统提示词
    sp = "You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task.\n## Output Format\n```\nThought: ...\nAction: ...\n```\n## Action Space\nclick(start_box='[x1, y1, x2, y2]')\nleft_double(start_box='[x1, y1, x2, y2]')\nright_single(start_box='[x1, y1, x2, y2]')\ndrag(start_box='[x1, y1, x2, y2]', end_box='[x3, y3, x4, y4]')\nhotkey(key='')\ntype(content='') #If you want to submit your input, use \"\\n\" at the end of `content`.\nscroll(start_box='[x1, y1, x2, y2]', direction='down or up or right or left')\nwait() #Sleep for 5s and take a screenshot to check for any changes.\nfinished(content='xxx') # Use escape characters \\\\', \\\\\", and \\\\n in content part to ensure we can parse the content in normal python string format.\n## Note\n- Use Chinese in `Thought` part.\n- Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.\n## User Instruction"

    # 添加历史记录
    prompt = f"{sp}\n{user_prompt}"
    if history_text:
        prompt = f"{sp}\n\n## Action History\n{history_text}\n\n## User Instruction\n{user_prompt}"
    
    try:
        # 创建Ark客户端，直接使用API密钥
        client = Ark(api_key=api_key, base_url="https://ark.cn-beijing.volces.com/api/v3")
        
        # 调用API
        response = client.chat.completions.create(
            model="ep-20250418113739-lgjh4",  # 模型ID
            temperature=0,  # 控制随机性，0表示最确定的输出
            messages=[
                {
                    "role": "system",
                    "content": prompt  # 系统提示词
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": ""  # 用户指令已包含在系统提示中
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_to_base64(img_path)  # 将图像转换为base64
                            }
                        }
                    ]
                }
            ],
        )
        
        # 输出和返回结果
        print("【结果】\n", response.choices[0].message.content)
        return response.choices[0].message.content
    except ArkAPIError as e:
        print(f"API错误: {e}")
        return f"错误: {e}"  # 返回错误信息字符串，而不是None
    except Exception as e:
        print(f"发生错误: {e}")
        return f"错误: {e}"  # 返回错误信息字符串，而不是None


def execute_action(parsed_output, img_size):
    """
    执行模型输出的操作
    
    参数:
        parsed_output: 解析后的操作字典
        img_size: 图片尺寸 (width, height)
        
    返回:
        执行结果描述
    """
    action = parsed_output.get("action", "")
    if not action:
        return "没有操作指令"
    
    try:
        # 转换相对坐标为绝对坐标
        start_box = parsed_output.get("start_box")
        end_box = parsed_output.get("end_box")
        
        # 获取屏幕宽高
        screen_width, screen_height = pyautogui.size()
        
        result = f"执行操作: {action}"
        
        if action == "click" and start_box:
            # 将相对坐标转换为实际屏幕坐标
            start_abs = coordinates_convert(start_box, img_size)
            center_x = (start_abs[0] + start_abs[2]) // 2
            center_y = (start_abs[1] + start_abs[3]) // 2
            
            # 点击操作
            pyautogui.click(center_x, center_y)
            result = f"点击坐标: ({center_x}, {center_y})"
            
        elif action == "left_double" and start_box:
            # 双击操作
            start_abs = coordinates_convert(start_box, img_size)
            center_x = (start_abs[0] + start_abs[2]) // 2
            center_y = (start_abs[1] + start_abs[3]) // 2
            
            pyautogui.doubleClick(center_x, center_y)
            result = f"双击坐标: ({center_x}, {center_y})"
            
        elif action == "right_single" and start_box:
            # 右键点击
            start_abs = coordinates_convert(start_box, img_size)
            center_x = (start_abs[0] + start_abs[2]) // 2
            center_y = (start_abs[1] + start_abs[3]) // 2
            
            pyautogui.rightClick(center_x, center_y)
            result = f"右键点击坐标: ({center_x}, {center_y})"
            
        elif action == "drag" and start_box and end_box:
            # 拖拽操作
            start_abs = coordinates_convert(start_box, img_size)
            end_abs = coordinates_convert(end_box, img_size)
            
            start_x = (start_abs[0] + start_abs[2]) // 2
            start_y = (start_abs[1] + start_abs[3]) // 2
            end_x = (end_abs[0] + end_abs[2]) // 2
            end_y = (end_abs[1] + end_abs[3]) // 2
            
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, duration=0.5)
            result = f"拖拽从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})"
            
        elif action == "hotkey" and parsed_output.get("key"):
            # 快捷键操作
            key = parsed_output.get("key")
            if "+" in key:
                keys = key.split("+")
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)
            result = f"按下快捷键: {key}"
            
        elif action == "type" and parsed_output.get("content") is not None:
            # 输入文本
            content = parsed_output.get("content")
            pyautogui.typewrite(content)
            result = f"输入文本: {content}"
            
        elif action == "scroll" and start_box and parsed_output.get("direction"):
            # 滚动操作
            start_abs = coordinates_convert(start_box, img_size)
            center_x = (start_abs[0] + start_abs[2]) // 2
            center_y = (start_abs[1] + start_abs[3]) // 2
            direction = parsed_output.get("direction")
            
            # 移动到滚动区域
            pyautogui.moveTo(center_x, center_y)
            
            # 根据方向滚动
            clicks = 5  # 滚动的单位数
            if direction == "up":
                pyautogui.scroll(clicks)
            elif direction == "down":
                pyautogui.scroll(-clicks)
            elif direction == "left":
                pyautogui.hscroll(-clicks)
            elif direction == "right":
                pyautogui.hscroll(clicks)
                
            result = f"在位置 ({center_x}, {center_y}) 向{direction}方向滚动"
            
        elif action == "wait":
            # 等待操作
            time.sleep(5)
            result = "等待5秒"
            
        elif action == "finished":
            # 完成操作
            content = parsed_output.get("content", "任务完成")
            result = f"任务结束: {content}"
            
        else:
            result = f"不支持的操作: {action}"
            
        return result
    
    except Exception as e:
        return f"执行操作时出错: {str(e)}"


if __name__ == "__main__":
    image_path = "data/屏幕截图 2025-05-20 155419.png"
    user_prompt = "将鼠标挪到END文本右侧绿色圆点圆心，拖拽（drag）到UI文本左侧红色点来连接"
    
    # 获取屏幕截图
    screenshot = pyautogui.screenshot()
    screenshot_path = "data/screenshot.png"
    screenshot.save(screenshot_path)
    
    # 运行模型获取操作指令
    model_response = run(screenshot_path, user_prompt)
    parsed_output = json.loads(parse_action_output(model_response))
    print("解析后的输出:", json.dumps(parsed_output, ensure_ascii=False, indent=2))
    
    # 显示边界框
    image = Image.open(screenshot_path)
    start_abs = coordinates_convert(parsed_output["start_box"], image.size) if parsed_output["start_box"] else None
    end_abs = coordinates_convert(parsed_output["end_box"], image.size) if parsed_output["end_box"] else None
    direction = parsed_output["direction"] if parsed_output["direction"] else None
    
    # 绘制边界框和显示
    draw_box_and_show(image, start_abs, end_abs, direction)
    
    # 执行操作
    execution_result = execute_action(parsed_output, image.size)
    print("执行结果:", execution_result)