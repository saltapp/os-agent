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
import keyboard  # 用于检测键盘按键

# 导入配置加载函数
from utils import load_config

# 通过 pip install openai 安装OpenAI SDK
from openai import OpenAI


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

        # 修复在原始输出中出现换行的情况
    action_text = action_text.replace('\n', ' ').strip()
    # 只在debug模式下打印详细信息，减少日志输出提升性能
    if os.environ.get('DEBUG_MODE') == '1':
        print(f"处理的操作文本: {action_text}")  # 调试信息
    
    # 检查是否有额外的操作行
    if '\n' in output_text and 'Action:' in output_text.split('\n')[-1]:
        extra_action = output_text.split('\n')[-1].replace('Action:', '').strip()
        if extra_action and len(extra_action) > len(action_text):
            action_text = extra_action
            print(f"使用额外的操作文本: {action_text}")  # 调试信息

    # 直接匹配常见操作类型
    action_types = ["click", "left_double", "right_single", "drag", "hotkey", "type", "cltype", "scroll", "wait", "finished"]
    for action_type in action_types:
        if action_text.lower().startswith(action_type.lower()):
            result["action"] = action_type
            break
    
    # 如果没有找到有效的action类型，尝试更灵活的提取
    if not result["action"]:
        # 特殊处理 'cltype'，需要先检查这个，避免被下面的'type'捕获
        if "cltype" in action_text.lower():
            result["action"] = "cltype"
        # 特殊处理 'hotkey'
        elif "hotkey" in action_text.lower():
            result["action"] = "hotkey"
        # 特殊处理 'type'
        elif "type" in action_text.lower():
            result["action"] = "type"
    
    # 现在解析参数，先尝试标准格式
    params_match = re.search(r'\((.*)\)', action_text)
    if params_match:
        params_text = params_match.group(1)
        
        # 处理键值对参数
        for param in params_text.split(','):
            param = param.strip()
            if '=' in param:
                key, value = param.split('=', 1)
                key = key.strip()
                value = value.strip().strip('\'"')

                # 处理bbox格式
                if 'box' in key:
                    # 先处理方括号格式 [x, y] 或 [x1, y1, x2, y2]
                    if '[' in value and ']' in value:
                        # 提取方括号内的内容
                        bracket_content = re.search(r'\[(.*?)\]', value)
                        if bracket_content:
                            numbers = re.findall(r'\d+', bracket_content.group(1))
                            if numbers:
                                coords = [int(num) for num in numbers]
                                # 如果只有2个值，复制为4个值(x1,y1,x1,y1)
                                if len(coords) == 2:
                                    coords = coords + coords
                                if len(coords) == 4:
                                    if key == 'start_box':
                                        result["start_box"] = coords
                                    elif key == 'end_box':
                                        result["end_box"] = coords
                    else:
                        # 处理常规数字格式
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
    else:
        # 如果没有找到参数，但有操作类型，打印警告
        if result["action"]:
            print(f"警告: '{result['action']}' 操作没有提供任何参数，这可能会导致执行失败")
            # 检查操作类型是否需要必要参数
            required_params = {
                "click": ["start_box"],
                "left_double": ["start_box"],
                "right_single": ["start_box"],
                "drag": ["start_box", "end_box"],
                "hotkey": ["key"],
                "type": ["content"],
                "cltype": ["start_box", "content"],
                "scroll": ["start_box", "direction"]
            }
            if result["action"] in required_params:
                missing = [param for param in required_params[result["action"]] 
                          if result.get(param) is None]
                if missing:
                    print(f"错误: 缺少 {result['action']} 操作的必要参数: {', '.join(missing)}")

    # 特殊处理hotkey，确保有key参数
    if result["action"] == "hotkey":
        # 如果还没有key，尝试更多方式提取
        if result["key"] is None:
            # 尝试1: key='value'格式
            key_match = re.search(r'key=[\'"]([^\'"]*)[\'"]', action_text)
            if key_match:
                result["key"] = key_match.group(1)
            else:
                # 尝试2: hotkey('value')格式
                direct_match = re.search(r'hotkey\([\'"]([^\'"]*)[\'"]', action_text)
                if direct_match:
                    result["key"] = direct_match.group(1)
                else:
                    # 尝试3: 直接在括号中的内容
                    bracket_match = re.search(r'hotkey\(([^\'"\)]+)\)', action_text)
                    if bracket_match:
                        # 尝试提取不带引号的key值
                        key_content = bracket_match.group(1).strip()
                        if key_content and not '=' in key_content:
                            result["key"] = key_content
        
        # 检查是否找到了键值
        if result["key"] is None or result["key"] == '':
            # 检查是否有明显的键名
            for common_key in ['enter', 'return', 'esc', 'escape', 'tab', 'space', 'ctrl', 'alt', 'shift', 'win']:
                if common_key in action_text.lower():
                    result["key"] = common_key
                    break
            
            # 如果是空字符串，设置为更直观的名称
            if result["key"] == '':
                result["key"] = "enter"  # 默认为回车键，这是最常见的情况
    
    # 特殊处理type，确保有content参数
    if result["action"] == "type" and result["content"] is None:
        # 尝试从action_text中提取content
        content_match = re.search(r'content=[\'"]([^\'"]*)[\'"]', action_text)
        if content_match:
            content = content_match.group(1)
            # 处理转义字符
            content = content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
            result["content"] = content
        else:
            # 尝试提取括号中的内容作为输入内容
            # 例如：type('hello')
            direct_match = re.search(r'type\([\'"]([^\'"]*)[\'"]', action_text)
            if direct_match:
                result["content"] = direct_match.group(1)
                
    # 特殊处理cltype，确保有start_box和content参数
    if result["action"] == "cltype":
        # 如果没有content参数，尝试提取
        if result["content"] is None:
            content_match = re.search(r'content=[\'"]([^\'"]*)[\'"]', action_text)
            if content_match:
                content = content_match.group(1)
                # 处理转义字符
                content = content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
                result["content"] = content
                
        # 检查是否缺少start_box
        if result["start_box"] is None:
            # 尝试查找bbox格式的坐标
            bbox_match = re.search(r'<bbox>(.*?)</bbox>', action_text)
            if bbox_match:
                bbox_values = bbox_match.group(1).strip().split()
                if bbox_values:
                    coords = [int(num) for num in bbox_values]
                    # 如果只有2个值，复制为4个值(x1,y1,x1,y1)
                    if len(coords) == 2:
                        coords = coords + coords
                    if len(coords) == 4:
                        result["start_box"] = coords
            else:
                # 尝试查找方括号格式的坐标
                bracket_match = re.search(r'\[([^\]]+)\]', action_text)
                if bracket_match:
                    bracket_content = bracket_match.group(1)
                    numbers = re.findall(r'\d+', bracket_content)
                    if numbers and len(numbers) >= 4:
                        coords = [int(num) for num in numbers[:4]]
                        result["start_box"] = coords
    
    print(f"解析结果: {result}")  # 调试信息
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

    # 计算绝对坐标，使用round而非int以提高精度
    abs_x1 = round(relative_bbox[0] * img_width / 1000)
    abs_y1 = round(relative_bbox[1] * img_height / 1000)
    abs_x2 = round(relative_bbox[2] * img_width / 1000)
    abs_y2 = round(relative_bbox[3] * img_height / 1000)
    
    """ # 处理点击点而非区域的情况 (x1=x2, y1=y2)
    if abs_x1 == abs_x2:
        # 确保有一个有效的方框，宽度至少为1像素
        abs_x2 = abs_x1 + 1
    if abs_y1 == abs_y2:
        # 确保有一个有效的方框，高度至少为1像素
        abs_y2 = abs_y1 + 1 """

    return [abs_x1, abs_y1, abs_x2, abs_y2]


def draw_box_and_show(image, start_box=None, end_box=None, direction=None, show_image=True):
    """
    在图片上绘制两个边界框和指向箭头

    参数:
        image: PIL.Image对象或图片路径
        start_box: 起始框坐标 [x1,y1,x2,y2] (绝对坐标)
        end_box: 结束框坐标 [x1,y1,x2,y2] (绝对坐标)
        direction: 操作方向 ('up', 'down', 'left', 'right' 或 None)
        show_image: 是否显示图像
    """
    box_color = "red"
    arrow_color = "blue"
    box_width = 7
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
    if show_image:
        plt.imshow(image)
        plt.axis('on')  # 不显示坐标轴
        plt.show()
    
    return image  # 返回图像以便保存


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
    # 创建一个全局OpenAI客户端实例，避免重复创建
    global _openai_client

    # 从配置文件加载API信息
    try:
        config = load_config()
        api_key = config["api"]["key"]
        base_url = config["api"]["base_url"] if config["api"]["base_url"] != "your_base_url_here" else None
        model_id = config["api"]["model_id"]
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        print("请确保 codes/config.json 文件存在并正确配置")
        return f"错误: 配置加载失败 - {e}"

    # 从Markdown文件加载系统提示词
    try:
        with open("codes/system_prompt.md", "r", encoding="utf-8") as f:
            sp = f.read()
    except Exception as e:
        print(f"读取系统提示词文件时出错: {e}")

    # 添加历史记录
    prompt = f"{sp}\n{user_prompt}"
    if history_text:
        # 构建完整提示
        prompt = f"{sp}\n\n## Action History\n{history_text}\n\n## User Instruction\n{user_prompt}"

    try:
        # 如果全局客户端不存在，创建新客户端
        if '_openai_client' not in globals() or _openai_client is None:
            if base_url:
                _openai_client = OpenAI(api_key=api_key, base_url=base_url)
            else:
                _openai_client = OpenAI(api_key=api_key)
            print("已创建新的OpenAI客户端")

        # 准备图像数据
        image_data = image_to_base64(img_path)

        # 调用API
        response = _openai_client.chat.completions.create(
            model=model_id,  # 使用配置文件中的模型ID
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
                                "url": image_data
                            }
                        }
                    ]
                }
            ],
        )

        # 输出和返回结果
        print("【结果】\n", response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        print(f"API错误: {e}")
        # 重置客户端以便下次重新创建
        globals()['_openai_client'] = None
        return f"错误: {e}"  # 返回错误信息字符串，而不是None


def execute_action(parsed_output, img_size, speed_factor=0.3, screenshot_dir=None, step_count=None):
    """
    执行模型输出的操作
    
    参数:
        parsed_output: 解析后的操作字典
        img_size: 图片尺寸 (width, height)
        speed_factor: 速度调整因子，值越大操作越快
        screenshot_dir: 截图保存目录，如果提供将保存操作后截图
        step_count: 当前步骤计数，用于命名截图文件
        
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
        
        # 根据速度因子调整持续时间
        drag_duration = max(0.1, 0.5 / speed_factor)  # 最小0.1秒
        key_interval = max(0.01, 0.05 / speed_factor)  # 最小0.01秒
        
        result = f"执行操作: {action}"
        
        if action == "click":
            if not start_box:
                result = "错误: click操作缺少必要的start_box坐标参数"
                print(f"警告: 尝试执行click操作但没有start_box参数。完整操作字典: {parsed_output}")
            else:
                # 将相对坐标转换为实际屏幕坐标
                start_abs = coordinates_convert(start_box, img_size)
                # 使用浮点数除法计算中心点，然后四舍五入到整数，提高精度
                center_x = round((start_abs[0] + start_abs[2]) / 2)
                center_y = round((start_abs[1] + start_abs[3]) / 2)
                
                # 点击操作
                pyautogui.click(center_x, center_y)
                result = f"点击坐标: ({center_x}, {center_y})"
            
        elif action == "left_double":
            if not start_box:
                result = "错误: left_double操作缺少必要的start_box坐标参数"
                print(f"警告: 尝试执行left_double操作但没有start_box参数。完整操作字典: {parsed_output}")
            else:
                # 双击操作
                start_abs = coordinates_convert(start_box, img_size)
                # 使用精确的浮点数除法和四舍五入
                center_x = round((start_abs[0] + start_abs[2]) / 2)
                center_y = round((start_abs[1] + start_abs[3]) / 2)
                
                pyautogui.doubleClick(center_x, center_y)
                result = f"双击坐标: ({center_x}, {center_y})"
            
        elif action == "right_single":
            if not start_box:
                result = "错误: right_single操作缺少必要的start_box坐标参数"
                print(f"警告: 尝试执行right_single操作但没有start_box参数。完整操作字典: {parsed_output}")
            else:
                # 右键点击
                start_abs = coordinates_convert(start_box, img_size)
                # 使用精确的浮点数除法和四舍五入
                center_x = round((start_abs[0] + start_abs[2]) / 2)
                center_y = round((start_abs[1] + start_abs[3]) / 2)
                
                pyautogui.rightClick(center_x, center_y)
                result = f"右键点击坐标: ({center_x}, {center_y})"
            
        elif action == "drag":
            if not start_box or not end_box:
                missing = []
                if not start_box:
                    missing.append("start_box")
                if not end_box:
                    missing.append("end_box")
                result = f"错误: drag操作缺少必要的参数: {', '.join(missing)}"
                print(f"警告: 尝试执行drag操作但参数不完整。完整操作字典: {parsed_output}")
            else:
                # 拖拽操作
                start_abs = coordinates_convert(start_box, img_size)
                end_abs = coordinates_convert(end_box, img_size)
                
                # 使用精确的浮点数除法和四舍五入
                start_x = round((start_abs[0] + start_abs[2]) / 2)
                start_y = round((start_abs[1] + start_abs[3]) / 2)
                end_x = round((end_abs[0] + end_abs[2]) / 2)
                end_y = round((end_abs[1] + end_abs[3]) / 2)
                
                pyautogui.moveTo(start_x, start_y)
                pyautogui.dragTo(end_x, end_y, duration=drag_duration)
                result = f"拖拽从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})"
            
        elif action == "hotkey":
            # 快捷键操作
            key = parsed_output.get("key")
            if key:  # 确保key不为None或空字符串
                print(f"执行hotkey操作，按键: {key}")
                if "+" in key:
                    keys = key.split("+")
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(key)
                result = f"按下快捷键: {key}"
            else:
                result = "hotkey操作缺少key参数"
                print(f"警告: 尝试执行hotkey操作但没有key参数。完整操作字典: {parsed_output}")
            
        elif action == "type":
            # 输入文本
            content = parsed_output.get("content")
            if content is not None:  # 允许空字符串输入
                # 处理文本，检查是否需要按回车
                need_enter = False
                if content.endswith('\n'):
                    content = content[:-1]
                    need_enter = True
                
                print(f"执行文本输入: '{content}'")
                
                # 尝试多种方法自动输入文本
                success = False
                error_messages = []
                
                # 方法1: 使用pyperclip+快捷键
                try:
                    import pyperclip
                    original_clipboard = pyperclip.paste()  # 保存原始剪贴板内容
                    
                    # 将文本复制到剪贴板
                    pyperclip.copy(content)
                    time.sleep(key_interval)  # 等待复制完成
                    
                    # 模拟Ctrl+V粘贴
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(key_interval)  # 等待粘贴完成
                    
                    # 可选: 恢复原始剪贴板内容
                    if original_clipboard:
                        pyperclip.copy(original_clipboard)
                    
                    success = True
                    print("使用剪贴板+Ctrl+V方法成功输入")
                except Exception as e:
                    error_msg = f"剪贴板方法失败: {str(e)}"
                    print(error_msg)
                    error_messages.append(error_msg)
                
                # 方法2: 如果方法1失败，尝试直接输入
                if not success:
                    try:
                        # 对于中文和特殊字符，逐字符输入可能更可靠
                        if any(ord(c) > 127 for c in content):  # 包含非ASCII字符
                            # 中文等非ASCII字符，尝试write
                            pyautogui.write(content)
                        else:
                            # ASCII字符，使用typewrite
                            pyautogui.typewrite(content)
                        
                        time.sleep(key_interval)
                        success = True
                        print("使用直接输入方法成功")
                    except Exception as e:
                        error_msg = f"直接输入方法失败: {str(e)}"
                        print(error_msg)
                        error_messages.append(error_msg)
                
                # 方法3: 使用Windows API - 如果前两种方法都失败
                if not success and os.name == 'nt':
                    try:
                        # 尝试导入需要的Windows模块
                        import win32com.client
                        
                        # 创建一个Shell对象
                        shell = win32com.client.Dispatch("WScript.Shell")
                        # 激活当前窗口
                        shell.SendKeys('%')
                        time.sleep(key_interval)
                        
                        # 直接输入文本
                        for char in content:
                            shell.SendKeys(char)
                            time.sleep(0.02)  # 减少字符间的等待时间，从0.05降低到0.02
                        
                        success = True
                        print("使用Windows API方法成功输入")
                    except Exception as e:
                        error_msg = f"Windows API方法失败: {str(e)}"
                        print(error_msg)
                        error_messages.append(error_msg)
                
                # 如果需要按回车键
                if need_enter and success:
                    try:
                        time.sleep(key_interval)  # 等待输入完成
                        pyautogui.press('enter')
                        print("已按下回车键")
                    except Exception as e:
                        print(f"按回车键失败: {str(e)}")
                
                # 生成结果消息
                if success:
                    result = f"输入文本: '{content}'"
                    if need_enter:
                        result += " 并按下回车"
                else:
                    result = f"所有输入方法均失败: {'; '.join(error_messages)}"
                    print("="*50)
                    print("由于自动输入失败，建议手动执行以下操作:")
                    print(f"1. 点击要输入文字的位置")
                    print(f"2. 输入或粘贴文本: {content}")
                    if need_enter:
                        print(f"3. 按回车键提交")
                    print("操作完成后按任意键继续...")
                    input()
                    print("="*50)
                
                # 仅在type操作后截图并保存
                if success and screenshot_dir and step_count:
                    try:
                        # 获取输入文本后的屏幕状态
                        post_action_screenshot = pyautogui.screenshot()
                        
                        # 保存为标记图片
                        marked_screenshot_path = f"{screenshot_dir}/marked_step_{step_count}.png"
                        post_action_screenshot.save(marked_screenshot_path)
                        print(f"已保存文本输入后的截图: {marked_screenshot_path}")
                    except Exception as screenshot_error:
                        print(f"保存文本输入后截图失败: {str(screenshot_error)}")
            else:
                result = "type操作缺少content参数"
                print(f"警告: 尝试执行type操作但没有content参数。完整操作字典: {parsed_output}")
            
        elif action == "scroll":
            missing = []
            if not start_box:
                missing.append("start_box")
            if not parsed_output.get("direction"):
                missing.append("direction")
                
            if missing:
                result = f"错误: scroll操作缺少必要的参数: {', '.join(missing)}"
                print(f"警告: 尝试执行scroll操作但参数不完整。完整操作字典: {parsed_output}")
            else:
                # 滚动操作
                start_abs = coordinates_convert(start_box, img_size)
                # 使用精确的浮点数除法和四舍五入
                center_x = round((start_abs[0] + start_abs[2]) / 2)
                center_y = round((start_abs[1] + start_abs[3]) / 2)
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
            
        elif action == "cltype":
            # 点击并输入操作
            if not start_box or parsed_output.get("content") is None:
                missing = []
                if not start_box:
                    missing.append("start_box")
                if parsed_output.get("content") is None:
                    missing.append("content")
                result = f"错误: cltype操作缺少必要的参数: {', '.join(missing)}"
                print(f"警告: 尝试执行cltype操作但参数不完整。完整操作字典: {parsed_output}")
            else:
                # 先点击文本框
                start_abs = coordinates_convert(start_box, img_size)
                # 使用精确的浮点数除法和四舍五入
                center_x = round((start_abs[0] + start_abs[2]) / 2)
                center_y = round((start_abs[1] + start_abs[3]) / 2)
                
                # 点击操作
                pyautogui.click(center_x, center_y)
                
                # 缩短点击后的等待时间
                time.sleep(key_interval * 2)
                
                # 然后输入文本
                content = parsed_output.get("content")
                
                # 处理文本，检查是否需要按回车
                need_enter = False
                if content.endswith('\n'):
                    content = content[:-1]
                    need_enter = True
                
                print(f"执行点击并文本输入: '{content}'")
                
                # 尝试多种方法自动输入文本
                success = False
                error_messages = []
                
                # 方法1: 使用pyperclip+快捷键
                try:
                    import pyperclip
                    original_clipboard = pyperclip.paste()  # 保存原始剪贴板内容
                    
                    # 将文本复制到剪贴板
                    pyperclip.copy(content)
                    time.sleep(key_interval)  # 等待复制完成
                    
                    # 模拟Ctrl+V粘贴
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(key_interval)  # 等待粘贴完成
                    
                    # 可选: 恢复原始剪贴板内容
                    if original_clipboard:
                        pyperclip.copy(original_clipboard)
                    
                    success = True
                    print("使用剪贴板+Ctrl+V方法成功输入")
                except Exception as e:
                    error_msg = f"剪贴板方法失败: {str(e)}"
                    print(error_msg)
                    error_messages.append(error_msg)
                
                # 方法2: 如果方法1失败，尝试直接输入
                if not success:
                    try:
                        # 对于中文和特殊字符，逐字符输入可能更可靠
                        if any(ord(c) > 127 for c in content):  # 包含非ASCII字符
                            # 中文等非ASCII字符，尝试write
                            pyautogui.write(content)
                        else:
                            # ASCII字符，使用typewrite
                            pyautogui.typewrite(content)
                        
                        time.sleep(key_interval)
                        success = True
                        print("使用直接输入方法成功")
                    except Exception as e:
                        error_msg = f"直接输入方法失败: {str(e)}"
                        print(error_msg)
                        error_messages.append(error_msg)
                
                # 方法3: 使用Windows API - 如果前两种方法都失败
                if not success and os.name == 'nt':
                    try:
                        # 尝试导入需要的Windows模块
                        import win32com.client
                        
                        # 创建一个Shell对象
                        shell = win32com.client.Dispatch("WScript.Shell")
                        # 激活当前窗口
                        shell.SendKeys('%')
                        time.sleep(key_interval)
                        
                        # 直接输入文本
                        for char in content:
                            shell.SendKeys(char)
                            time.sleep(0.02)  # 减少字符间的等待时间，从0.05降低到0.02
                        
                        success = True
                        print("使用Windows API方法成功输入")
                    except Exception as e:
                        error_msg = f"Windows API方法失败: {str(e)}"
                        print(error_msg)
                        error_messages.append(error_msg)
                
                # 如果需要按回车键
                if need_enter and success:
                    try:
                        time.sleep(key_interval)  # 等待输入完成
                        pyautogui.press('enter')
                        print("已按下回车键")
                    except Exception as e:
                        print(f"按回车键失败: {str(e)}")
                
                # 生成结果消息
                if success:
                    result = f"点击坐标: ({center_x}, {center_y}) 并输入文本: '{content}'"
                    if need_enter:
                        result += " 并按下回车"
                else:
                    result = f"点击成功，但所有输入方法均失败: {'; '.join(error_messages)}"
                    print("="*50)
                    print("由于自动输入失败，建议手动执行以下操作:")
                    print(f"1. 点击要输入文字的位置")
                    print(f"2. 输入或粘贴文本: {content}")
                    if need_enter:
                        print(f"3. 按回车键提交")
                    print("操作完成后按任意键继续...")
                    input()
                    print("="*50)

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
            print(f"警告: 不支持的操作类型 '{action}'。完整操作字典: {parsed_output}")
            
        # 执行结果
        execution_result = result

        return execution_result
    
    except Exception as e:
        error_msg = f"执行操作时出错: {str(e)}"
        print(f"错误: {error_msg}，操作: {action}，完整操作字典: {parsed_output}")
        return error_msg


def auto_execute_task(user_prompt, max_steps=20, screenshot_dir="data/auto_screenshots", debug=True, save_history=True, show_screenshots=False, wait_time=1):
    """
    自动执行多步骤任务

    参数:
        user_prompt: 用户的复杂指令
        max_steps: 最大执行步骤数，防止无限循环
        screenshot_dir: 截图保存目录
        debug: 是否显示调试信息
        save_history: 是否保存历史记录到文件
        show_screenshots: 是否显示带边界框的截图弹窗
        wait_time: 操作之间的等待时间(秒)，可调整以平衡速度和稳定性

    返回:
        执行结果描述
    """

    # 定义ESC键按下时的回调函数
    is_interrupted = [False]  # 使用列表作为可变对象

    def on_esc_press(e):
        if e.name == 'esc':
            print("\n" + "="*50)
            print("检测到ESC键，准备中断流程...")
            print("="*50 + "\n")
            is_interrupted[0] = True

    # 注册ESC键回调
    keyboard.on_press(on_esc_press)

    # 创建截图目录
    os.makedirs(screenshot_dir, exist_ok=True)

    # 初始化历史记录
    history_text = ""
    step_count = 0
    history_file = None

    # 用于检测重复操作和判断任务完成
    recent_actions = []
    no_progress_count = 0  # 连续无进展的步数

    # 创建历史记录文件
    if save_history:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        history_file_path = f"{screenshot_dir}/history_{timestamp}.txt"
        history_file = open(history_file_path, "w", encoding="utf-8")
        history_file.write(f"任务: {user_prompt}\n\n")

    try:
        # 执行循环直到任务完成或达到最大步骤数
        while step_count < max_steps:
            step_count += 1
            print(f"\n===== 执行步骤 {step_count} =====")

            # 获取屏幕截图
            screenshot = pyautogui.screenshot()
            screenshot_path = f"{screenshot_dir}/step_{step_count}.png"
            screenshot.save(screenshot_path)

            try:
                # 运行模型获取操作指令
                model_response = run(screenshot_path, user_prompt, history_text)

                # 检查是否有错误响应
                if model_response.startswith("错误:"):
                    error_msg = f"模型调用失败: {model_response}"
                    print(error_msg)
                    if save_history and history_file:
                        history_file.write(f"步骤 {step_count} 失败: {error_msg}\n\n")

                    # 如果是API错误，尝试等待一段时间后重试
                    if "API错误" in model_response:
                        retry_time = max(10, wait_time * 5)  # 至少等待10秒
                        print(f"等待{retry_time}秒后重试...")
                        time.sleep(retry_time)
                        continue
                    else:
                        break

                parsed_json = parse_action_output(model_response)
                parsed_output = json.loads(parsed_json)

                # 打印思考过程和操作指令
                thought = parsed_output.get('thought', '无')
                action = parsed_output.get('action', '无')
                print(f"操作指令: {action}")

                # 记录当前操作，用于检测重复操作和任务完成状态
                current_operation = {
                    'action': action,
                    'start_box': parsed_output.get('start_box'),
                    'end_box': parsed_output.get('end_box'),
                    'content': parsed_output.get('content'),
                    'key': parsed_output.get('key'),
                    'direction': parsed_output.get('direction')
                }

                # 写入历史记录
                if save_history and history_file:
                    history_file.write(f"步骤 {step_count}:\n思考: {thought}\n操作: {action}\n\n")

                # 检查是否完成任务
                if parsed_output.get("action") == "finished":
                    finish_message = f"任务完成: {parsed_output.get('content', '任务结束')}"
                    print(finish_message)
                    if save_history and history_file:
                        history_file.write(f"{finish_message}\n")
                    return f"任务成功完成，共执行 {step_count} 步"

                # 将当前操作添加到最近操作列表
                recent_actions.append(current_operation)
                if len(recent_actions) > 5:  # 只保留最近5个操作
                    recent_actions.pop(0)

                # 检查操作是否有效
                if not parsed_output.get("action"):
                    print("警告: 模型没有返回有效的操作指令")
                    if save_history and history_file:
                        history_file.write("警告: 模型没有返回有效的操作指令\n\n")
                    # 等待一段时间后继续
                    time.sleep(wait_time)

                    # 检测连续无操作的次数
                    no_progress_count += 1
                    if no_progress_count >= 3:  # 如果连续3次没有操作，认为任务完成
                        warning_msg = f"连续{no_progress_count}次没有有效操作，认为任务已完成"
                        print(warning_msg)
                        if save_history and history_file:
                            history_file.write(f"{warning_msg}\n")
                        return f"任务成功完成，共执行 {step_count} 步（检测到无进展，自动结束）"
                    continue
                else:
                    # 如果有操作，重置无进展计数
                    no_progress_count = 0
                
                # 调试模式：处理边界框
                if debug and parsed_output.get("start_box"):
                    image = Image.open(screenshot_path)
                    start_abs = coordinates_convert(parsed_output["start_box"], image.size) if parsed_output["start_box"] else None
                    end_abs = coordinates_convert(parsed_output["end_box"], image.size) if parsed_output["end_box"] else None
                    direction = parsed_output["direction"] if parsed_output["direction"] else None
                    
                    # 如果是cltype操作，添加文本标注
                    if parsed_output.get("action") == "cltype" and parsed_output.get("content"):
                        # 绘制边界框并根据设置决定是否显示
                        image_with_box = draw_box_and_show(image, start_abs, end_abs, direction, show_image=False)
                        
                        # 添加输入文本的标注
                        draw = ImageDraw.Draw(image_with_box)
                        content = parsed_output.get("content", "")
                        # 截断过长的文本显示
                        display_text = content if len(content) < 30 else content[:27] + "..."
                        try:
                            # 尝试添加文本标签
                            draw.text((start_abs[0], start_abs[1] - 20), f"输入: {display_text}", fill="blue")
                        except Exception as e:
                            print(f"添加文本标注失败: {e}")
                        
                        # 显示图像
                        if show_screenshots:
                            plt.imshow(image_with_box)
                            plt.axis('on')
                            plt.show()
                    else:
                        # 绘制边界框并根据设置决定是否显示
                        draw_box_and_show(image, start_abs, end_abs, direction, show_image=show_screenshots)
                    
                    # 保存带边界框的图像
                    marked_screenshot_path = f"{screenshot_dir}/marked_step_{step_count}.png"
                    image.save(marked_screenshot_path)
                
                # 执行操作
                img_size = screenshot.size
                # 使用与wait_time相对应的速度因子
                speed_factor = 2.0 / wait_time if wait_time > 0 else 2.0 
                execution_result = execute_action(
                    parsed_output, 
                    img_size, 
                    speed_factor,
                    screenshot_dir=screenshot_dir,
                    step_count=step_count
                )
                print(f"执行结果: {execution_result}")
                
                # 写入执行结果
                if save_history and history_file:
                    history_file.write(f"执行结果: {execution_result}\n\n")
                
                # 更新历史记录
                history_text += f"Step {step_count}:\nThought: {thought}\nAction: {action}\nResult: {execution_result}\n\n"                
                
                # 检查是否重复执行相同操作
                if len(recent_actions) >= 3:
                    # 检查最近3个操作是否相同（除了步骤计数外）
                    last_three = recent_actions[-3:]
                    if (last_three[0]['action'] == last_three[1]['action'] == last_three[2]['action'] and
                        last_three[0]['start_box'] == last_three[1]['start_box'] == last_three[2]['start_box'] and
                        last_three[0]['content'] == last_three[1]['content'] == last_three[2]['content']):
                        # 如果连续3次执行相同操作，认为任务已完成或无法继续
                        repeated_msg = f"检测到连续3次重复操作，认为任务已完成或无法继续"
                        print(repeated_msg)
                        if save_history and history_file:
                            history_file.write(f"{repeated_msg}\n")
                        return f"任务成功完成，共执行 {step_count} 步（检测到重复操作，自动结束）"

                # 根据操作类型动态调整等待时间，提高执行效率
                if action in ["click", "left_double", "right_single"]:
                    # 简单点击操作可以使用更短的等待时间
                    time.sleep(wait_time * 0.8)
                elif action in ["type", "cltype"]:
                    # 文本输入操作需要更长等待确保完成
                    time.sleep(wait_time * 0.8)
                elif action == "drag":
                    # 拖拽操作需要等待界面更新
                    time.sleep(wait_time * 0.8)
                else:
                    # 默认等待时间
                    time.sleep(wait_time * 0.8)

                # 检查是否按下ESC键中断流程
                if is_interrupted[0]:
                    interrupted_msg = f"用户按下ESC键中断任务，在执行完步骤 {step_count} 后停止"
                    print("\n" + "="*50)
                    print(interrupted_msg)
                    print("="*50 + "\n")
                    if save_history and history_file:
                        history_file.write(f"{interrupted_msg}\n\n")
                    return f"任务被用户中断，共执行 {step_count} 步"
                
            except Exception as e:
                error_msg = f"步骤 {step_count} 执行过程中出错: {str(e)}"
                print(f"错误: {error_msg}")
                if save_history and history_file:
                    history_file.write(f"{error_msg}\n\n")
                
                # 错误后等待较长时间再继续
                time.sleep(wait_time * 2)
                
                # 检查是否按下ESC键中断流程
                if is_interrupted[0]:
                    return f"任务被用户中断，共执行 {step_count} 步"
            
            # 检查是否中断
            if is_interrupted[0]:
                break
        
        if is_interrupted[0]:
            max_steps_msg = f"任务中断，共执行 {step_count} 步"
        else:
            # 检查最后几步是否都没有有效操作，以判断是否实际上已完成任务
            if no_progress_count >= 2:  # 如果最后几步都没有进展
                max_steps_msg = f"达到最大步骤数 {max_steps}，但检测到连续无进展，可能任务已完成"
                print("检测到连续无进展，认为任务可能已完成")
                if save_history and history_file:
                    history_file.write("检测到连续无进展，认为任务可能已完成\n")
                return f"任务成功完成，共执行 {step_count} 步（检测到无进展，自动结束）"
            else:
                max_steps_msg = f"达到最大步骤数 {max_steps}，任务未完成"

        if save_history and history_file:
            history_file.write(f"{max_steps_msg}\n")
        return max_steps_msg
    
    finally:
        # 注销键盘回调
        keyboard.unhook_all()
        
        # 确保历史记录文件被关闭
        if save_history and history_file:
            history_file.close()
            print(f"历史记录已保存到: {history_file.name}")


if __name__ == "__main__":
    # 自动执行多步骤任务
    try:
        # 设置结果保存目录为data/results
        base_results_dir = "data/results"
        os.makedirs(base_results_dir, exist_ok=True)
        
        # 查找下一个可用的结果目录编号
        existing_dirs = [d for d in os.listdir(base_results_dir) if os.path.isdir(os.path.join(base_results_dir, d)) and d.startswith("results")]
        next_num = 1
        
        # 从已有目录名称中提取数字，找到当前最大值
        for dir_name in existing_dirs:
            try:
                # 尝试从目录名中提取数字
                num = int(dir_name.replace("results", ""))
                next_num = max(next_num, num + 1)
            except ValueError:
                # 如果提取失败，跳过
                continue
        
        # 创建新目录
        results_dir = f"{base_results_dir}/results{next_num}"
        os.makedirs(results_dir, exist_ok=True)
        print(f"结果将保存到: {results_dir}")
        
        # 从Markdown文件读取用户提示词
        try:
            with open("codes/user_prompt.md", "r", encoding="utf-8") as f:
                user_prompt = f.read().strip()
            print(f"已从文件加载用户提示词")
        except Exception as e:
            # 如果文件读取失败，使用默认提示词
            print(f"读取用户提示词文件失败: {e}，使用默认提示词")
            user_prompt = ""
        
        # 设置执行速度(越小越快，但可能影响稳定性)
        execution_speed = 1  # 默认为1秒等待，值越小速度越快
        
        result = auto_execute_task(
            user_prompt, 
            max_steps=50, 
            screenshot_dir=results_dir,
            debug=True,
            save_history=True,
            show_screenshots=False,  # 设置为False以不显示截图弹窗
            wait_time=execution_speed  # 设置等待时间
        )
        print(result)
    except Exception as e:
        print(f"执行任务时出现严重错误: {str(e)}")