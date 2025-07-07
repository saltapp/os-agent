# UI-TARS: 智能UI自动化任务执行系统

![Local Image](figures/writer.png)
<p align="center">
        🌐 <a href="https://seed-tars.com/">Website</a>&nbsp&nbsp | 🤗 <a href="https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B">Hugging Face Models</a>&nbsp&nbsp 
        | &nbsp&nbsp 🔧 <a href="README_deploy.md">Deployment</a> &nbsp&nbsp  | &nbsp&nbsp 📑 <a href="https://arxiv.org/abs/2501.12326">Paper</a> &nbsp&nbsp  |&nbsp&nbsp</a>
🖥️ <a href="https://github.com/bytedance/UI-TARS-desktop">UI-TARS-desktop</a>&nbsp&nbsp
</p>

## 简介

UI-TARS (User Interface Task Automation with Reasoning System) 是一个基于AI视觉理解的智能UI自动化任务执行系统，能够通过分析屏幕截图并执行相应的操作来完成复杂的用户界面任务。

本仓库是UI-TARS的改进版本，增加了配置文件管理，提高了代码的安全性和可移植性，适合本地化部署和个人使用。

## 🌟 主要特点

- **AI驱动的视觉理解**：通过先进的视觉模型分析屏幕界面，无需传统的元素定位
- **自动化操作执行**：支持点击、双击、右键点击、拖拽、文本输入、快捷键等多种操作
- **多步骤任务处理**：能够连续执行多个步骤以完成复杂任务
- **操作历史记录**：自动记录每一步操作及其结果，便于回溯和调试
- **可视化结果展示**：为每个操作生成带有标记的截图，直观展示执行过程
- **安全的配置系统**：通过配置文件管理API密钥和其他敏感信息，防止隐私泄露
- **用户友好的中断机制**：支持通过ESC键随时中断执行流程

## 🚀 快速开始

### 系统要求

- Python 3.7+
- Windows/macOS/Linux (主要在Windows上测试)
- 必要的Python库：PIL, matplotlib, pyautogui, keyboard等

### 安装

1. 克隆此仓库：
   ```
   git clone https://github.com/yourusername/UI-TARS-github.git
   cd UI-TARS-github
   ```

2. 安装依赖：
   ```
   pip install volcengine-python-sdk[ark] pillow matplotlib pyautogui keyboard
   ```

### ⚙️ 配置

项目使用配置文件管理敏感信息，以防止API密钥等数据意外泄露：

1. 在`codes`目录下找到`config.template.json`模板文件
2. 复制该文件并重命名为`config.json`
3. 编辑`config.json`，填入您的实际API密钥和其他信息：
   ```json
   {
     "api": {
       "key": "your_api_key_here",
       "base_url": "your_base_url_here",
       "model_id": "your_model_id_here"
     }
   }
   ```

4. 更多详细配置说明请参考[配置文档](codes/README_config.md)

### 使用方法

1. 在`codes/user_prompt.md`文件中编写您的任务指令，描述需要自动完成的操作
2. 运行主程序：
   ```
   python codes/chat_with_model_ui_tars.py
   ```
3. 系统会自动截取屏幕，分析界面，并执行相应的操作
4. 操作过程中可随时按ESC键中断执行流程

### 执行结果

- 所有执行步骤的截图将保存在`data/results/resultsX/`目录下
- 操作历史记录将保存为文本文件，记录每一步的思考过程和执行结果

## 📊 示例

项目包含一些示例执行结果，位于`data/results/results1/`目录下，展示了系统如何执行多步骤UI操作任务。

## 📄 文档

- [配置说明](codes/README_config.md) - 详细的配置文件设置说明
- [坐标系统说明](README_coordinates.md) - 了解系统如何处理屏幕坐标
- [部署指南](README_deploy.md) - 如何在不同环境中部署此系统

## Prompt使用指南

根据不同设备环境和任务复杂度，以下三种提示模板位于<a href="codes/prompts.py">codes/prompts.py</a>，可指导GUI代理生成适当的操作。请选择最适合您使用场景的模板：

### 🖥️ `COMPUTER_USE`

**推荐用于**：桌面环境（Windows、Linux或macOS）的GUI任务。

**特点**：
- 支持常见桌面操作：鼠标点击（单击、双击、右键）、拖拽操作、键盘快捷键、文本输入、滚动等。
- 适用于浏览器导航、办公软件交互、文件管理等桌面任务。

### 📱 `MOBILE_USE`

**推荐用于**：移动设备或Android模拟器的GUI任务。

**特点**：
- 包含移动设备特定操作：`long_press`、`open_app`、`press_home`、`press_back`。
- 适用于启动应用、滚动视图、填写输入字段以及在移动应用内导航。

### 📌 `GROUNDING`

**推荐用于**：仅专注于动作输出的轻量级任务，或用于模型训练和评估。

**特点**：
- 仅输出`Action`，不包含任何推理过程（`Thought`）。
- 适用于评估模型定位能力。

## 引用

本项目基于UI-TARS开发，如果您在研究中使用，请引用原论文：

```BibTeX
@article{qin2025ui,
  title={UI-TARS: Pioneering Automated GUI Interaction with Native Agents},
  author={Qin, Yujia and Ye, Yining and Fang, Junjie and Wang, Haoming and Liang, Shihao and Tian, Shizuo and Zhang, Junda and Li, Jiahao and Li, Yunxin and Huang, Shijue and others},
  journal={arXiv preprint arXiv:2501.12326},
  year={2025}
}
```

## 许可证

本项目基于[LICENSE](LICENSE)开源许可证。 