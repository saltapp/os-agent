<!-- <p align="center">
  <img alt="UI-TARS"  width="260" src="figures/icon.png">
</p>

# UI-TARS：原生智能体驱动的自动化GUI交互 -->
![本地图像](figures/writer.png)
<p align="center">
        🤗 <a href="https://huggingface.co/bytedance-research/UI-TARS-7B-DPO">Hugging Face 模型</a>&nbsp&nbsp | &nbsp&nbsp🤖 <a href="https://www.modelscope.cn/models/bytedance-research/UI-TARS-7B-DPO">ModelScope</a>&nbsp&nbsp | &nbsp&nbsp 📑 <a href="https://arxiv.org/abs/2501.12326">论文</a> &nbsp&nbsp  |&nbsp&nbsp</a>
🖥️ <a href="https://github.com/bytedance/UI-TARS-desktop">UI-TARS-desktop</a>&nbsp&nbsp  <br>🏄 <a href="https://github.com/web-infra-dev/Midscene">Midscene（浏览器自动化）</a>&nbsp&nbsp | &nbsp&nbsp🤗 <a href="https://huggingface.co/spaces/bytedance-research/UI-TARS">Space</a>&nbsp&nbsp | &nbsp&nbsp🫨 <a href="https://discord.gg/pTXwYVjfcs">Discord</a>&nbsp&nbsp
</p>

我们还提供了 **UI-TARS-desktop** 版本，可在您的**本地个人设备**上运行。请访问 [https://github.com/bytedance/UI-TARS-desktop](https://github.com/bytedance/UI-TARS-desktop)。如需在网页自动化中使用 UI-TARS，可参考开源项目 [Midscene.js](https://github.com/web-infra-dev/Midscene)。
### ⚠️ 重要公告：GGUF 模型性能

**GGUF 模型**已完成量化，但其性能无法保证。因此我们决定**降级**该模型。

💡 **替代方案**：  
你可以使用**[云端部署](#cloud-deployment)**或**[本地部署 [vLLM]](#local-deployment-vllm)**（如果你有足够的GPU资源）。

感谢你的理解和耐心，我们会持续优化体验。

## 更新日志
- ✨ 我们更新了来自官方 [OSWorld 仓库](https://github.com/xlang-ai/OSWorld/blob/main/run_uitars.py) 的 OSWorld 推理脚本。现在你可以用官方推理脚本进行部署，并提供了 [OSWorld 轨迹示例](https://drive.google.com/file/d/1N9dYzAB9xSiHwE9VSdEi9xSpB9eXfVZT/view?usp=sharing) 以帮助你快速上手。
- 🚀 01.25: 我们在中文版 [GUI模型部署教程](https://bytedance.sg.larkoffice.com/docx/TCcudYwyIox5vyxiSDLlgIsTgWf#U94rdCxzBoJMLex38NPlHL21gNb) 的**[云端部署](#cloud-deployment)**部分，补充了 ModelScope 平台相关内容。你现在可以用 ModelScope 平台进行部署。

## 概述
UI-TARS 是新一代原生 GUI 智能体模型，具备类人感知、推理和动作能力，可无缝与图形用户界面（GUI）交互。与传统模块化框架不同，UI-TARS 将感知、推理、定位和记忆等关键能力集成于单一视觉-语言模型（VLM）中，实现端到端任务自动化，无需预定义流程或手工规则。
![本地图像](figures/UI-TARS-vs-Previous-SOTA.png)
![本地图像](figures/UI-TARS.png)

## 核心特性
### 感知
- **全面GUI理解**：处理多模态输入（文本、图像、交互），构建对界面的整体理解。
- **实时交互**：持续监控动态GUI，实时响应界面变化。

### 动作
- **统一动作空间**：跨平台（桌面、移动、网页）标准化动作定义。
- **平台特定动作**：支持如快捷键、长按、平台手势等额外动作。

### 推理
- **系统1&2推理**：结合快速直觉反应与高阶规划，胜任复杂任务。
- **任务分解与反思**：支持多步规划、反思与纠错，提升任务鲁棒性。

### 记忆
- **短期记忆**：捕捉任务上下文，增强情境感知。
- **长期记忆**：保留历史交互与知识，优化决策。

## 能力
- **跨平台交互**：统一动作框架支持桌面、移动、网页环境。
- **多步任务执行**：训练于多步轨迹与推理，胜任复杂任务。
- **融合真实与合成数据学习**：结合大规模标注与合成数据，提升泛化与鲁棒性。

## 性能
**感知能力评测**
| 模型 | VisualWebBench | WebSRC  | SQAshort |
|------|---------------|---------|----------|
| Qwen2-VL-7B | 73.3 | 81.8 | 84.9 |
| Qwen-VL-Max | 74.1 | 91.1 | 78.6 |
| Gemini-1.5-Pro | 75.4 | 88.9 | 82.2 |
| UIX-Qwen2-7B | 75.9 | 82.9 | 78.8 |
| Claude-3.5-Sonnet | 78.2 | 90.4 | 83.1 |
| GPT-4o | 78.5 | 87.7 | 82.3 |
| **UI-TARS-2B** | 72.9 | 89.2 | 86.4 |
| **UI-TARS-7B** | 79.7 | **93.6** | 87.7 |
| **UI-TARS-72B** | **82.8** | 89.3 | **88.6** |

**定位能力评测**
- **ScreenSpot Pro**

| 智能体模型 | Dev-Text | Dev-Icon | Dev-Avg | Creative-Text | Creative-Icon | Creative-Avg | CAD-Text | CAD-Icon | CAD-Avg | Scientific-Text | Scientific-Icon | Scientific-Avg | Office-Text | Office-Icon | Office-Avg | OS-Text | OS-Icon | OS-Avg | Avg-Text | Avg-Icon | Avg |
|------|----------|----------|----------|--------------|--------------|--------------|---------|---------|---------|---------------|---------------|---------------|------------|------------|------------|--------|--------|--------|---------|---------|------|
| QwenVL-7B | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 | 0.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | **0.1** |
| GPT-4o | 1.3 | 0.0 | 0.7 | 1.0 | 0.0 | 0.6 | 2.0 | 0.0 | 1.5 | 2.1 | 0.0 | 1.2 | 1.1 | 0.0 | 0.9 | 0.0 | 0.0 | 0.0 | 1.3 | 0.0 | **0.8** |
| SeeClick | 0.6 | 0.0 | 0.3 | 1.0 | 0.0 | 0.6 | 2.5 | 0.0 | 1.9 | 3.5 | 0.0 | 2.0 | 1.1 | 0.0 | 0.9 | 2.8 | 0.0 | 1.5 | 1.8 | 0.0 | **1.1** |
| Qwen2-VL-7B | 2.6 | 0.0 | 1.3 | 1.5 | 0.0 | 0.9 | 0.5 | 0.0 | 0.4 | 6.3 | 0.0 | 3.5 | 3.4 | 1.9 | 3.0 | 0.9 | 0.0 | 0.5 | 2.5 | 0.2 | **1.6** |
| OS-Atlas-4B | 7.1 | 0.0 | 3.7 | 3.0 | 1.4 | 2.3 | 2.0 | 0.0 | 1.5 | 9.0 | 5.5 | 7.5 | 5.1 | 3.8 | 4.8 | 5.6 | 0.0 | 3.1 | 5.0 | 1.7 | **3.7** |
| ShowUI-2B | 16.9 | 1.4 | 9.4 | 9.1 | 0.0 | 5.3 | 2.5 | 0.0 | 1.9 | 13.2 | 7.3 | 10.6 | 15.3 | 7.5 | 13.5 | 10.3 | 2.2 | 6.6 | 10.8 | 2.6 | **7.7** |
| CogAgent-18B | 14.9 | 0.7 | 8.0 | 9.6 | 0.0 | 5.6 | 7.1 | 3.1 | 6.1 | 22.2 | 1.8 | 13.4 | 13.0 | 0.0 | 10.0 | 5.6 | 0.0 | 3.1 | 12.0 | 0.8 | **7.7** |
| Aria-UI | 16.2 | 0.0 | 8.4 | 23.7 | 2.1 | 14.7 | 7.6 | 1.6 | 6.1 | 27.1 | 6.4 | 18.1 | 20.3 | 1.9 | 16.1 | 4.7 | 0.0 | 2.6 | 17.1 | 2.0 | **11.3** |
| UGround-7B | 26.6 | 2.1 | 14.7 | 27.3 | 2.8 | 17.0 | 14.2 | 1.6 | 11.1 | 31.9 | 2.7 | 19.3 | 31.6 | 11.3 | 27.0 | 17.8 | 0.0 | 9.7 | 25.0 | 2.8 | **16.5** |
| Claude Computer Use | 22.0 | 3.9 | 12.6 | 25.9 | 3.4 | 16.8 | 14.5 | 3.7 | 11.9 | 33.9 | 15.8 | 25.8 | 30.1 | 16.3 | 26.9 | 11.0 | 4.5 | 8.1 | 23.4 | 7.1 | **17.1** |
| OS-Atlas-7B | 33.1 | 1.4 | 17.7 | 28.8 | 2.8 | 17.9 | 12.2 | 4.7 | 10.3 | 37.5 | 7.3 | 24.4 | 33.9 | 5.7 | 27.4 | 27.1 | 4.5 | 16.8 | 28.1 | 4.0 | **18.9** |
| UGround-V1-7B | - | - | 35.5 | - | - | 27.8 | - | - | 13.5 | - | - | 38.8 | - | - | 48.8 | - | - | 26.1 | - | - | **31.1** |
| **UI-TARS-2B** | 47.4 | 4.1 | 26.4 | 42.9 | 6.3 | 27.6 | 17.8 | 4.7 | 14.6 | 56.9 | 17.3 | 39.8 | 50.3 | 17.0 | 42.6 | 21.5 | 5.6 | 14.3 | 39.6 | 8.4 | **27.7** |
| **UI-TARS-7B** | 58.4 | 12.4 | 36.1 | 50.0 | 9.1 | 32.8 | **20.8**| 9.4 | **18.0**| 63.9 | **31.8** | **50.0** | **63.3** | 20.8 | 53.5 | 30.8 | **16.9**| 24.5 | 47.8 | 16.2 | **35.7** |
| **UI-TARS-72B** | **63.0** | **17.3** | **40.8** | **57.1** | **15.4** | **39.6** | 18.8 | **12.5**| 17.2 | **64.6** | 20.9 | 45.7 | **63.3** | **26.4** | **54.8** | **42.1**| 15.7 | **30.1**| **50.9**| **17.5**| **38.1**  |

- **ScreenSpot**

| 方法 |  Mobile-Text | Mobile-Icon/Widget | Desktop-Text | Desktop-Icon/Widget | Web-Text | Web-Icon/Widget | Avg |
|------|-------------|-------------|-------------|-------------|-------------|---------|---------|
| **Agent Framework**  | | | | | | | |
| GPT-4 (SeeClick) |  76.6 | 55.5 | 68.0 | 28.6 | 40.9 | 23.3 | **48.8** |
| GPT-4 (OmniParser)  | 93.9 | 57.0 | 91.3 | 63.6 | 81.3 | 51.0 | **73.0** |
| GPT-4 (UGround-7B)  | 90.1 | 70.3 | 87.1 | 55.7 | 85.7 | 64.6 | **75.6** |
| GPT-4o (SeeClick)  | 81.0 | 59.8 | 69.6 | 33.6 | 43.9 | 26.2 | **52.3** |
| GPT-4o (UGround-7B)  | 93.4 | 76.9 | 92.8 | 67.9 | 88.7 | 68.9 | **81.4** |
| **Agent Model**   | | | | | | | |
| GPT-4  | 22.6 | 24.5 | 20.2 | 11.8 | 9.2 | 8.8 | **16.2** |
| GPT-4o  | 20.2 | 24.9 | 21.1 | 23.6 | 12.2 | 7.8 | **18.3** |
| CogAgent  | 67.0 | 24.0 | 74.2 | 20.0 | 70.4 | 28.6 | **47.4** |
| SeeClick  | 78.0 | 52.0 | 72.2 | 30.0 | 55.7 | 32.5 | **53.4** |
| Qwen2-VL  | 75.5 | 60.7 | 76.3 | 54.3 | 35.2 | 25.7 | **55.3** |
| UGround-7B  | 82.8 | 60.3 | 82.5 | 63.6 | 80.4 | 70.4 | **73.3** |
| Aguvis-G-7B  | 88.3 | 78.2 | 88.1 | 70.7 | 85.7 | 74.8 | **81.8** |
| OS-Atlas-7B | 93.0 | 72.9 | 91.8 | 62.9 | 90.9 | 74.3 | **82.5** |
| Claude Computer Use  | - | - | - | - | - | - | **83.0** |
| Gemini 2.0 (Project Mariner)  | - | - | - | - | - | - | **84.0** |
| Aguvis-7B  | **95.6** | 77.7 | 93.8 | 67.1 | 88.3 | 75.2 | **84.4** |
| Aguvis-72B  | 94.5 | **85.2** | 95.4 | 77.9 | **91.3** | **85.9** | **89.2** |
| **Our Model**   | | | | | | | |
| **UI-TARS-2B**  | 93.0 | 75.5 | 90.7 | 68.6 | 84.3 | 74.8 | **82.3** |
| **UI-TARS-7B**  | 94.5 | **85.2** | **95.9** | 85.7 | 90.0 | 83.5 | **89.5** |
| **UI-TARS-72B**  | 94.9 | 82.5 | 89.7 | **88.6** | 88.7 | 85.0 | **88.4** |

- **ScreenSpot v2**

| 方法 |  Mobile-Text | Mobile-Icon/Widget | Desktop-Text | Desktop-Icon/Widget | Web-Text | Web-Icon/Widget | Avg |
|------|-------------|-------------|-------------|-------------|-------------|---------|---------|
| **Agent Framework**  | | | | | | | |
| GPT-4o (SeeClick)  | 85.2 | 58.8 | 79.9 | 37.1 | 72.7 | 30.1 | **63.6** |
| GPT-4o (OS-Atlas-4B)  | 95.5 | 75.8 | 79.4 | 49.3 | 90.2 | 66.5 | **79.1** |
| GPT-4o (OS-Atlas-7B)  | 96.2 | 83.4 | 89.7 | 69.3 | **94.0** | 79.8 | **87.1** |
| **Agent Model**  | | | | | | | |
| SeeClick  | 78.4 | 50.7 | 70.1 | 29.3 | 55.2 | 32.5 | **55.1** |
| OS-Atlas-4B  | 87.2 | 59.7 | 72.7 | 46.4 | 85.9 | 63.1 | **71.9** |
| OS-Atlas-7B  | 95.2 | 75.8 | 90.7 | 63.6 | 90.6 | 77.3 | **84.1** |
| **Our Model**  | | | | | | | |
| **UI-TARS-2B**  | 95.2 | 79.1 | 90.7 | 68.6 | 87.2 | 78.3 | **84.7** |
| **UI-TARS-7B** | **96.9** | **89.1** | **95.4** | 85.0 | 93.6 | 85.2 | **91.6** |
| **UI-TARS-72B**  | 94.8 | 86.3 | 91.2 | **87.9** | 91.5 | **87.7** | **90.3** |

**离线智能体能力评测**
- **Multimodal Mind2Web**

| 方法 |  Cross-Task Ele.Acc | Cross-Task Op.F1 | Cross-Task Step SR | Cross-Website Ele.Acc | Cross-Website Op.F1 | Cross-Website Step SR | Cross-Domain Ele.Acc | Cross-Domain Op.F1 | Cross-Domain Step SR |
|------|----------------------|-------------------|--------------------|----------------------|--------------------|-------------------|--------------------|-------------------|-------------------|
| **Agent Framework**  | | | | | | | | | |
| GPT-4o (SeeClick)  | 32.1 | - | - | 33.1 | - | - | 33.5 | - | - |
| GPT-4o (UGround)  | 47.7 | - | - | 46.0 | - | - | 46.6 | - | - |
| GPT-4o (Aria-UI)  | 57.6 | - | - | 57.7 | - | - | 61.4 | - | - |
| GPT-4V (OmniParser)  | 42.4 | 87.6 | 39.4 | 41.0 | 84.8 | 36.5 | 45.5 | 85.7 | 42.0 |
| **Agent Model** |  | | | | | | | | |
| GPT-4o  | 5.7 | 77.2 | 4.3 | 5.7 | 79.0 | 3.9 | 5.5 | 86.4 | 4.5 |
| GPT-4 (SOM)  | 29.6 | - | 20.3 | 20.1 | - | 13.9 | 27.0 | - | 23.7 |
| GPT-3.5 (Text-only)  | 19.4 | 59.2 | 16.8 | 14.9 | 56.5 | 14.1 | 25.2 | 57.9 | 24.1 |
| GPT-4 (Text-only)  | 40.8 | 63.1 | 32.3 | 30.2 | 61.0 | 27.0 | 35.4 | 61.9 | 29.7 |
| Claude  | 62.7 | 84.7 | 53.5 | 59.5 | 79.6 | 47.7 | 64.5 | 85.4 | 56.4 |
| Aguvis-7B  | 64.2 | 89.8 | 60.4 | 60.7 | 88.1 | 54.6 | 60.4 | 89.2 | 56.6 |
| CogAgent  | - | - | 62.3 | - | - | 54.0 | - | - | 59.4 |
| Aguvis-72B  | 69.5 | 90.8 | 64.0 | 62.6 | 88.6 | 56.5 | 63.5 | 88.5 | 58.2 |
| **Our Model**  | | | | | | | | | |
| **UI-TARS-2B**  | 62.3 | 90.0 | 56.3 | 58.5 | 87.2 | 50.8 | 58.8 | 89.6 | 52.3 |
| **UI-TARS-7B**  | 73.1 | 92.2 | 67.1 | 68.2 | 90.9 | 61.7 | 66.6 | 90.9 | 60.5 |
| **UI-TARS-72B**  | **74.7** | **92.5** | **68.6** | **72.4** | **91.2** | **63.5** | **68.9** | **91.8** | **62.1** |

- **Android Control and GUI Odyssey**

| 智能体模型 | AndroidControl-Low Type | AndroidControl-Low Grounding | AndroidControl-Low SR | AndroidControl-High Type | AndroidControl-High Grounding | AndroidControl-High SR | GUIOdyssey Type | GUIOdyssey Grounding | GUIOdyssey SR |
|------|----------------------|----------------------|----------------|----------------------|----------------------|----------------|----------------|----------------|----------------|
| Claude | 74.3 | 0.0 | 19.4 | 63.7 | 0.0 | 12.5 | 60.9 | 0.0 | 3.1 |
| GPT-4o | 74.3 | 0.0 | 19.4 | 66.3 | 0.0 | 20.8 | 34.3 | 0.0 | 3.3 |
| SeeClick | 93.0 | 73.4 | 75.0 | 82.9 | 62.9 | 59.1 | 71.0 | 52.4 | 53.9 |
| InternVL-2-4B | 90.9 | 84.1 | 80.1 | 84.1 | 72.7 | 66.7 | 82.1 | 55.5 | 51.5 |
| Qwen2-VL-7B | 91.9 | 86.5 | 82.6 | 83.8 | 77.7 | 69.7 | 83.5 | 65.9 | 60.2 |
| Aria-UI | -- | 87.7 | 67.3 | -- | 43.2 | 10.2 | -- | 86.8 | 36.5 |
| OS-Atlas-4B | 91.9 | 83.8 | 80.6 | 84.7 | 73.8 | 67.5 | 83.5 | 61.4 | 56.4 |
| OS-Atlas-7B | 93.6 | 88.0 | 85.2 | 85.2 | 78.5 | 71.2 | 84.5 | 67.8 | 62.0 |
| Aguvis-7B | -- | -- | 80.5 | -- | -- | 61.5 | -- | -- | -- |
| Aguvis-72B | -- | -- | 84.4 | -- | -- | 66.4 | -- | -- | -- |
| **UI-TARS-2B** | **98.1** | 87.3 | 89.3 | 81.2 | 78.4 | 68.9 | 93.9 | 86.8 | 83.4 |
| **UI-TARS-7B** | 98.0 | 89.3 | 90.8 | 83.7 | 80.5 | 72.5 | 94.6 | 90.1 | 87.0 |
| **UI-TARS-72B** | **98.1** | **89.9** | **91.3** | **85.2** | **81.5** | **74.7** | **95.4** | **91.4** | **88.6** |

**在线智能体能力评测**

| 方法 |  OSWorld (Online) | AndroidWorld (Online) |
|------|-------------------|------------------|
| **Agent Framework**  | | |
| GPT-4o (UGround)  | - | 32.8 |
| GPT-4o (Aria-UI)  | 15.2 | 44.8 |
| GPT-4o (Aguvis-7B)  | 14.8 | 37.1 |
| GPT-4o (Aguvis-72B)  | 17.0 | - |
| GPT-4o (OS-Atlas-7B)  | 14.6 | - |
| **Agent Model**  | | |
| GPT-4o  | 5.0 | 34.5 (SoM) |
| Gemini-Pro-1.5  | 5.4 | 22.8 (SoM) |
| Aguvis-72B  | 10.3 | 26.1 |
| Claude Computer-Use  | 14.9 (15步) | 27.9 |
| Claude Computer-Use  | 22.0 (50步) | - |
| **Our Model**  | | |
| **UI-TARS-7B-SFT**  | 17.7 (15步) | 33.0 |
| **UI-TARS-7B-DPO**  | 18.7 (15步) | - |
| **UI-TARS-72B-SFT**  | 18.8 (15步) | **46.6** |
| **UI-TARS-72B-DPO**  | **22.7** (15步) | - |
| **UI-TARS-72B-DPO**  | **24.6** (50步) | - |

## 部署

### 云端部署
推荐使用 HuggingFace Inference Endpoints 进行快速部署。
我们提供两份文档供参考：

英文版: [GUI Model Deployment Guide](https://juniper-switch-f10.notion.site/GUI-Model-Deployment-Guide-17b5350241e280058e98cea60317de71)

中文版: [GUI模型部署教程](https://bytedance.sg.larkoffice.com/docx/TCcudYwyIox5vyxiSDLlgIsTgWf#U94rdCxzBoJMLex38NPlHL21gNb)

### 本地部署 [Transformers]
与 Qwen2-VL 部署方式一致。详情见 [教程](https://github.com/QwenLM/Qwen2-VL?tab=readme-ov-file#using---transformers-to-chat)。

### 本地部署 [vLLM]
推荐使用 vLLM 进行快速部署与推理。需使用 `vllm>=0.6.1`。
```bash
pip install -U transformers
VLLM_VERSION=0.6.6
CUDA_VERSION=cu124
pip install vllm==${VLLM_VERSION} --extra-index-url https://download.pytorch.org/whl/${CUDA_VERSION}

```
#### 下载模型
Hugging Face 提供三种模型规模：**2B**、**7B**、**72B**。为获得最佳性能，推荐使用 **7B-DPO** 或 **72B-DPO**（视GPU配置而定）：

- [2B-SFT](https://huggingface.co/bytedance-research/UI-TARS-2B-SFT)
- [7B-SFT](https://huggingface.co/bytedance-research/UI-TARS-7B-SFT)
- [7B-DPO](https://huggingface.co/bytedance-research/UI-TARS-7B-DPO)
- [72B-SFT](https://huggingface.co/bytedance-research/UI-TARS-72B-SFT)
- [72B-DPO](https://huggingface.co/bytedance-research/UI-TARS-72B-DPO)


#### 启动 OpenAI API 服务
运行如下命令启动 OpenAI 协议兼容的 API 服务。7B 模型建议 `-tp=1`，72B 模型建议 `-tp=4`。

```bash
python -m vllm.entrypoints.openai.api_server --served-model-name ui-tars \
    --model <path to your model> --limit-mm-per-prompt image=5 -tp <tp>
```

然后你可以用如下方式调用 chat API，配合 GUI 提示词（可选移动或电脑场景）和本地图片 base64 编码（详见 [OpenAI API 协议文档](https://platform.openai.com/docs/guides/vision/uploading-base-64-encoded-images)），也可用于 [UI-TARS-desktop](https://github.com/bytedance/UI-TARS-desktop)：
```python
import base64
from openai import OpenAI


instruction = "search for today's weather"
screenshot_path = "screenshot.png"
client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="empty",
)

## 以下为移动端提示词
template = r"""你是一个GUI智能体。你会获得任务、动作历史和截图。你需要执行下一个动作以完成任务。

## 输出格式
```
Thought: ...
Action: ...
```

## 动作空间
click(start_box='<|box_start|>(x1,y1)<|box_end|>')
left_double(start_box='<|box_start|>(x1,y1)<|box_end|>')
right_single(start_box='<|box_start|>(x1,y1)<|box_end|>')
drag(start_box='<|box_start|>(x1,y1)<|box_end|>', end_box='<|box_start|>(x3,y3)<|box_end|>')
hotkey(key='')
type(content='') #如需提交输入，在content结尾加"\n"
scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', direction='down or up or right or left')
wait() #休眠5秒并截图检查变化
finished()
call_user() #任务无法解决或需用户协助时提交任务

## 注意
- Thought部分用中文。
- 用一句话总结下一个动作及目标元素。

## 用户指令
"""

with open(screenshot_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
response = client.chat.completions.create(
    model="ui-tars",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": template + instruction},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_string}"}},
            ],
        },
    ],
    frequency_penalty=1,
    max_tokens=128,
)
print(response.choices[0].message.content)
```

单步定位任务或在如 Seeclick 等定位数据集上推理，请参考如下脚本：
```python
import base64
from openai import OpenAI


instruction = "search for today's weather"
screenshot_path = "screenshot.png"
client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="empty",
)

## 以下为移动端提示词
template = r"""只输出一个点的坐标。哪个元素匹配如下任务： """

with open(screenshot_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
response = client.chat.completions.create(
    model="ui-tars",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_string}"}},
                {"type": "text", "text": template + instruction}
            ],
        },
    ],
    frequency_penalty=1,
    max_tokens=128,
)
print(response.choices[0].message.content)
```

### 提示词模板
目前我们提供两种稳定运行和高性能的提示词模板，分别适用于移动端和个人电脑场景。
- 移动端模板：
```python
## 以下为移动端提示词
template = r"""你是一个GUI智能体。你会获得任务、动作历史和截图。你需要执行下一个动作以完成任务。

## 输出格式
```
Thought: ...
Action: ...
```

## 动作空间
click(start_box='<|box_start|>(x1,y1)<|box_end|>')
long_press(start_box='<|box_start|>(x1,y1)<|box_end|>', time='')
type(content='')
scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', end_box='<|box_start|>(x3,y3)<|box_end|>')
press_home()
press_back()
finished(content='') #无论成功与否都提交任务

## 注意
- Thought部分用英文。
- 写一个小计划，最后用一句话总结下一个动作及目标元素。

## 用户指令
"""
```

- 电脑端模板：
```python
## 以下为电脑端提示词
template = r"""你是一个GUI智能体。你会获得任务、动作历史和截图。你需要执行下一个动作以完成任务。

## 输出格式
```
Thought: ...
Action: ...
```

## 动作空间
click(start_box='<|box_start|>(x1,y1)<|box_end|>')
left_double(start_box='<|box_start|>(x1,y1)<|box_end|>')
right_single(start_box='<|box_start|>(x1,y1)<|box_end|>')
drag(start_box='<|box_start|>(x1,y1)<|box_end|>', end_box='<|box_start|>(x3,y3)<|box_end|>')
hotkey(key='')
type(content='') #如需提交输入，在content结尾加"\n"
scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', direction='down or up or right or left')
wait() #休眠5秒并截图检查变化
finished()
call_user() #任务无法解决或需用户协助时提交任务

## 注意
- Thought部分用中文。
- 用一句话总结下一个动作及目标元素。

## 用户指令
"""
```

### 本地部署 [Ollama]
<!-- Ollama 可通过 gguf 格式部署模型。safetensors 存在bug。 -->Ollama 即将上线，敬请期待~ 😊
<!-- #### 获取 GGUF 格式模型
我们提供 2B 和 7B GGUF 格式模型：

2B: https://huggingface.co/bytedance-research/UI-TARS-2B-gguf

7B: https://huggingface.co/bytedance-research/UI-TARS-7B-gguf

用户可用 [llama.cpp](https://github.com/ggerganov/llama.cpp/blob/master/convert_hf_to_gguf.py) 脚本将模型转为 GGUF 格式：

```bash
python3 convert_hf_to_gguf.py <path to your model>
```

GGUF 文件会生成在指定路径下。

#### 部署 GGUF 模型
参考 Ollama [教程](https://github.com/ollama/ollama?tab=readme-ov-file#customize-a-model) 部署：

```bash
# 创建 Modelfile，Windows 用户可直接创建名为 Modelfile 的文件
echo "FROM ./path/to/model.gguf" > Modelfile

# 用 Ollama 创建模型
ollama create ui-tars -f Modelfile

# 运行模型
ollama run ui-tars

```

测试脚本与 vLLM 相同，仅需两处更改：

```python
...
client = OpenAI(
    base_url="http://127.0.0.1:11434/v1/",
    ...
)
...
response = client.chat.completions.create(
    model="ui-tars" # 用 Ollama cli 创建的模型名
    ...
)

``` -->

### 推理结果说明

#### 坐标映射
模型输出二维坐标，表示相对位置。将每个分量除以1000，得到[0,1]区间的相对值。Action所需绝对坐标计算方式：
- X绝对 = X相对 × 图像宽度
- Y绝对 = Y相对 × 图像高度

例如，屏幕尺寸为1920×1080，模型输出坐标(235, 512)。X绝对为 `round(1920*235/1000)=451`，Y绝对为 `round(1080*512/1000)=553`，绝对坐标为(451, 553)

## 桌面与网页自动化体验

如需体验桌面端 UI-TARS 智能体，可参考 [UI-TARS-desktop](https://github.com/bytedance/UI-TARS-desktop)。推荐桌面端使用 **7B/72B DPO模型**。

[Midscene.js](https://github.com/web-infra-dev/Midscene) 是支持 UI-TARS 的开源网页自动化 SDK。开发者可用 JavaScript 和自然语言控制浏览器。详见[模型接入指南](https://midscenejs.com/choose-a-model)。

## 许可证

UI-TARS 遵循 Apache License 2.0。

## 鸣谢
本项目基于并扩展了 Qwen2-VL 能力，Qwen2-VL 是强大的视觉-语言模型，也是 UI-TARS 的基础架构。感谢 Qwen2-VL 团队在多模态AI领域的开创性工作，为进一步发展提供了坚实基础。

同时感谢开源社区的数据集、工具和见解，推动了 UI-TARS 的发展。大家的协作不断拓展了 GUI 自动化和 AI 智能体的边界。

## 引用
如果你觉得我们的论文和代码对你的研究有帮助，欢迎 star :star: 和引用 :pencil:

```BibTeX
@article{qin2025ui,
  title={UI-TARS: Pioneering Automated GUI Interaction with Native Agents},
  author={Qin, Yujia and Ye, Yining and Fang, Junjie and Wang, Haoming and Liang, Shihao and Tian, Shizuo and Zhang, Junda and Li, Jiahao and Li, Yunxin and Huang, Shijue and others},
  journal={arXiv preprint arXiv:2501.12326},
  year={2025}
}
```
