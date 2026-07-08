# 🎬 jianying-smart-cutter (剪映全自动智能粗剪流水线)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-orange.svg)](https://www.microsoft.com/windows)

**`jianying-smart-cutter`** 是一个基于 Python 开发的 Windows 平台桌面自动化脚本。它利用模拟鼠标键盘与高精度图像矩阵识别，彻底打通了**剪映**的“智能粗剪”功能，实现从视频导入、时间线装载、静音死节粗剪、到全自动导出的“零人工干预”全自动视频处理剪辑工作流。

特别经过高内聚设计，完美适配作为 **AI Agent (如 OpenClaw、Codex 等框架) 的自动化 Skill** 插件进行分发与调度。

---

## 🎯 项目核心亮点 (Features)

* 🌐 **全系统路径自适应**：利用系统环境变量动态深度遍历递归抓取剪映主程序，彻底摆脱死板硬编码，无视剪映版本更新或不同电脑用户名导致的路径失效问题。
* 👁️ **智能隐藏窗口唤醒**：内置 Windows API 底层拦截。运行后若检测到剪映已在后台运行或最小化，会暴力将其“揪”至前台并强行全屏最大化，无感衔接后续自动化流程。
* 🚀 **无感防干扰素材导入**：摒弃传统不稳定的拖拽模拟。采用**“精准鼠标悬停 + 智能免图绝对坐标盲点”**双保险机制，换用任何画面、任意长度的视频素材都能 100% 成功点中蓝色加号送入轨道。
* ⚡ **键盘路径降维破局**：在轨道右键菜单选择阶段，彻底移除易受软件版本微调、UI 半透明、限免图标干扰的普通图像匹配。改为**键盘方向键绝对物理导航机制**，连按 8 次 `Down` 直击目标，速度快如闪电，成功率 100%。
* 🛡️ **全方位安全边界锁**：全局操作间隙进行毫秒级高并发压榨，并在寻轨、导出等敏感地带动态划定 `Region` 局部矩阵扫描包围圈，杜绝全屏灰色背景的李鬼误触。

---

## 📁 标准项目结构 (Structure)

为了确保脚本内的自适应相对路径完美闭环，请严格保持以下目录布局结构：

```text
├── jianying-smart-cutter/       # 仓库根目录
│   ├── videocut.py              # 流水线核心自动化脚本
│   ├── README.md                # 本说明文档
│   ├── video.mp4                # 待剪辑的视频素材（用户在此放入并固定命名）
│   └── img/                     # 自动化所需的静态 UI 核心特征图切片
│       ├── maximize.png         # 最大化按钮
│       ├── smart_cut_btn.png    # 首页智能粗剪大按钮
│       ├── go_create.png        # 去创作按钮
│       ├── import_btn.png       # 编辑器导入素材按钮
│       ├── plus_btn.png         # 素材悬停亮起的蓝色+号
│       ├── timeline_track.png   # 轨道底部纯色暗青特征条
│       ├── export_blue.png      # 右上角蓝色导出
│       ├── export_confirm.png   # 弹窗确认导出
│       ├── close_btn.png        # 导出完成关闭按钮
│       └── final_close.png      # 剪映主程序右上角关闭 X

```

---

## ⚙️ 环境依赖与前置自检 (Installation)

### 1. 物理环境要求

* **操作系统**：仅支持 **Windows 10 / Windows 11**（深度依赖 Windows `user32.dll` 底层 API）。
* **宿主软件**：宿主电脑需提前下载并安装 **剪映专业版**。
* **显示要求**：运行时请确保剪映没有被其他非自动化窗口完全遮挡。

### 2. Python 依赖库

项目深度依赖以下工业级图形及自动化库，请通过终端一键静默安装：

```bash
pip install pyautogui pyperclip opencv-python numpy Pillow

```

---

## 🚀 极速使用指南 (Usage)

1. 克隆或下载本仓库至本地任意盘符（路径可包含中文）。
2. 将你想要进行粗剪的视频文件，重命名为 **`video.mp4`**，并直接丢在与 `videocut.py` 相同的文件夹下。
3. 确保你的 `img/` 文件夹里已经集齐了对应版本的剪映按钮切图。
4. 打开终端（CMD/PowerShell），直接运行：

```bash
python videocut.py

```

> ⚠️ **运行期间重要铁律**：脚本在模拟高频鼠标键盘操作时，**请务必将双手移开鼠标与键盘**，不要人为抢夺窗口焦点，静静欣赏自动化黑客工作流。

---

## 🤖 AI Agent Skill 开发者集成规范

如果你打算将本项目作为 Skill 模块接入到你的 AI Agent（如 OpenClaw 或 Codex 等）中，请遵循以下指令调度逻辑：

1. **触发场景判断**：当用户发出 “帮我剪个片子”、“帮我处理一下 video.mp4”、“跑一下剪映智能粗剪” 等语义时，Agent 自动定位至此 Skill 目录。
2. **首次调用环境检测**：Agent 在首次准备调用 `videocut.py` 之前，必须先通过宿主系统静默执行 `python -c "import pyautogui, cv2"` 检测环境。若未安装依赖，需自动代替用户在后台静默补全 `pip install -r dependencies`，随后再异步拉起主程序。

---
