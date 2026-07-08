# 剪映专业版智能粗剪全自动流水线 Skill

## 1. Skill 概述与触发场景 (Triggers)
当用户发出以下类似意图的主动指令时，Agent 应当自动调用并触发此 Skill：
* **核心场景**：自动剪辑、批量粗剪、视频去噪/去死节、全自动视频导出。
* **典型用户指令**：
  * “帮我把刚下载的视频用剪映处理一下”
  * “帮我把目录下的 video.mp4 跑一遍智能粗剪流水线”
  * “自动化运行剪映粗剪并导出视频”

---

## 2. 目录结构规范 (File Structure)
为了确保脚本中的动态路径自适应机制完美生效，本 Skill 的文件及文件夹必须严格按照以下结构存放在同一个 Agent Skill 目录下：
```text
├── your_skill_folder/           # 本 Skill 的专属目录
│   ├── videocut.py              # 自动化核心 Python 脚本
│   ├── SKILL.md                 # 本说明文档
│   ├── video.mp4                # 用户放入的待剪辑视频（固定命名）
│   └── img/                     # 自动化所需的静态 UI 特征图文件夹
│       ├── go_create.png
│       ├── smart_cut_menu.png
│       ├── timeline_track.png
│       ├── final_close.png
│       ├── close_btn.png
│       ├── export_confirm.png
│       ├── export_blue.png
│       ├── start_cut.png
│       ├── original_audio.png
│       ├── import_btn.png
│       ├── smart_cut_btn.png
│       └── maximize.png

```

---

## 3. 环境依赖与首次运行检查 (Dependencies & Verification)

### 3.1 核心依赖库

本 Skill 依赖以下 Python 第三方库以实现系统唤醒、图像离线解码与高精度模拟鼠标键盘：

* `pyautogui`：图形界面自动化鼠标键盘控制
* `pyperclip`：系统剪贴板管理（用于完美规避中文字符路径乱码）
* `opencv-python` (cv2)：工业级图形矩阵解码与高匹配度对齐
* `numpy`：处理底层图形数据流
* `Pillow` (PIL)：辅助图形处理

### 3.2 Agent 首次运行自检逻辑 (Execution Flow for Agent)

**【重要命令】** Agent 机器人在**第一次**接收到启动指令、或在准备执行 `videocut.py` 之前，必须先在宿主计算机的终端（Terminal/PowerShell）中执行以下前置检查与安装动作：

1. **环境静默检查**：
Agent 应尝试在后台运行以下环境探针指令，确认依赖是否存在：
```bash
python -c "import pyautogui, pyperclip, cv2, numpy, PIL"

```


2. **自动补全依赖**：
如果上述指令抛出 `ModuleNotFoundError` 异常，Agent **必须优先且自动**在控制台执行以下静默安装命令。未完成依赖安装前，严禁直接运行主脚本：
```bash
pip install pyautogui pyperclip opencv-python numpy Pillow

```



---

## 4. 关键运行前置条件 (Prerequisites)

在 Agent 替用户执行此 Skill 前，需引导或确保宿主系统满足以下环境：

1. **Windows 系统环境**：本脚本深度使用了 Windows API (`ctypes`)，仅支持在 Windows 10/11 操作系统上运行。
2. **剪映已安装**：宿主电脑上必须已安装“剪映专业版”。脚本会自动扫描系统的 `%LOCALAPPDATA%` 及各大常见盘符的默认路径，若剪映为非标准路径安装，请确保剪映程序在后台处于运行或最小化状态。
3. **视频文件就位**：待处理的视频文件必须命名为 `video.mp4` 并放置在与 `videocut.py` 相同的根目录下。
4. **禁止人工干扰**：流水线运行期间（特别是涉及键盘快捷键和右键菜单选择时），用户请勿人为移动鼠标或敲击键盘，以免丢失当前窗口焦点导致流水线错位。

```
