import pyautogui
import time
import subprocess
import pyperclip
import os
import ctypes  
import cv2        
import numpy as np 

# ==================== 1 & 2. 动态路径自适应配置 ====================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def find_jianying_path():
    """
    自动寻找剪映专业版的安装路径，防止因用户名不同或版本更新导致路径失效
    """
    local_app_data = os.environ.get('LOCALAPPDATA')
    if local_app_data:
        # 1. 尝试默认的标准路径
        default_path = os.path.join(local_app_data, r"JianyingPro\Apps\JianyingPro.exe")
        if os.path.exists(default_path):
            return default_path
        
        # 2. 如果剪映更新了版本，进行遍历查找
        apps_dir = os.path.join(local_app_data, r"JianyingPro\Apps")
        if os.path.exists(apps_dir):
            for root, dirs, files in os.walk(apps_dir):
                if "JianyingPro.exe" in files:
                    return os.path.join(root, "JianyingPro.exe")

    # 3. 尝试其他常见盘符的默认安装路径作为备选
    common_paths = [
        r"C:\Program Files\JianyingPro\Apps\JianyingPro.exe",
        r"D:\JianyingPro\Apps\JianyingPro.exe",
        r"E:\JianyingPro\Apps\JianyingPro.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
            
    return r"C:\Users\dell\AppData\Local\JianyingPro\Apps\JianyingPro.exe"

def bring_jianying_to_foreground():
    """
    利用 Windows API 寻找已经在后台运行的剪映窗口，并强行将其恢复、置顶并最大化
    """
    user32 = ctypes.windll.user32
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    hwnd_list = []

    def callback(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                if "剪映" in buf.value:
                    hwnd_list.append(hwnd)
                    return False 
        return True

    cb_func = WNDENUMPROC(callback)
    user32.EnumWindows(cb_func, 0)

    if hwnd_list:
        hwnd = hwnd_list[0]
        user32.ShowWindow(hwnd, 9)            
        user32.SetForegroundWindow(hwnd)       
        user32.ShowWindow(hwnd, 3)            
        return True
    return False

# 自动获取到的动态参数
JIANYING_PATH = find_jianying_path()
VIDEO_PATH = os.path.join(CURRENT_DIR, "video.mp4")
IMG_DIR = os.path.join(CURRENT_DIR, "img") 

# 动作间隙停顿
pyautogui.PAUSE = 0.2

def wait_and_click(image_name, confidence=0.8, timeout=30, double_click=False, right_click=False, region=None):
    """
    使用 OpenCV 矩阵精准识别静态 UI 组件，支持传入 region 缩小搜索范围
    """
    start_time = time.time()
    img_path = os.path.join(IMG_DIR, image_name)
    
    print(f"正在寻找: {image_name}...")
    
    try:
        img_bgr = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img_bgr is None:
            print(f" 【错误】无法解析图片: {image_name}")
            return None
    except Exception as e:
        print(f" 读取图片异常 {image_name}: {e}")
        return None

    while time.time() - start_time < timeout:
        try:
            if region:
                location = pyautogui.locateCenterOnScreen(img_bgr, confidence=confidence, region=region)
            else:
                location = pyautogui.locateCenterOnScreen(img_bgr, confidence=confidence)
                
            if location:
                if double_click:
                    pyautogui.doubleClick(location)
                elif right_click:
                    pyautogui.rightClick(location)
                else:
                    pyautogui.click(location)
                print(f"成功点击: {image_name}，坐标位置: ({location.x}, {location.y})")
                time.sleep(0.3) 
                return location  
        except pyautogui.ImageNotFoundException:
            pass
        time.sleep(0.2) 
        
    print(f"超时未找到图片: {image_name}")
    return None

def main():
    print("开始执行剪映自动化脚本...")
    print(f"[环境检测] 剪映路径: {JIANYING_PATH}")
    print(f"[环境检测] 视频路径: {VIDEO_PATH}")
    print(f"[环境检测] 图片目录: {IMG_DIR}\n")

    # 获取屏幕分辨率
    screen_width, screen_height = pyautogui.size()

    # 1 & 2. 智能唤醒 / 打开剪映
    print("正在检查剪映是否已经在运行...")
    if bring_jianying_to_foreground():
        print("【唤醒成功】检测到剪映已在运行，已成功将其从后台拉出并最大化！")
        time.sleep(1)
    else:
        print("【全新启动】未检测到运行中的剪映，正在重新打开...")
        if os.path.exists(JIANYING_PATH):
            subprocess.Popen(JIANYING_PATH)
            time.sleep(6) 
            wait_and_click("maximize.png", timeout=10)
        else:
            print("【严重错误】未在系统中找到剪映主程序，且后台未运行剪映，流程终止！")
            return

    # 3. 点击"智能粗剪"
    wait_and_click("smart_cut_btn.png")

    # 4. 跳出来的弹窗点击右下角"去创作"
    wait_and_click("go_create.png")
    time.sleep(1.5) 

    # 5. 导入文件
    wait_and_click("import_btn.png")
    time.sleep(1)
    pyperclip.copy(VIDEO_PATH)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    
    print("正在等待视频导入完成...")
    time.sleep(3) 

    # ==================== 6. 悬停 + 智能免图盲点加号 ====================
    print("准备将视频加入时间线...")
    video_x = int(screen_width * 0.10)
    video_y = int(screen_height * 0.16)
    
    plus_x = video_x + 32
    plus_y = video_y + 44
    
    print(f"鼠标正在移向视频右下角以唤醒加号: ({plus_x}, {plus_y})")
    pyautogui.moveTo(plus_x, plus_y, duration=0.3)
    time.sleep(0.5) 
    
    media_region = (0, 0, int(screen_width * 0.3), int(screen_height * 0.5))
    
    if wait_and_click("plus_btn.png", confidence=0.7, timeout=1.5, region=media_region):
        print("【成功】通过图片成功点击蓝色加号！")
    else:
        print("【别慌】由于视频背景改变导致图片未匹配，现在直接使用绝对坐标点击蓝色加号！")
        pyautogui.click(plus_x, plus_y)
        
    time.sleep(1.5) 

    # ==================== 7. 下半屏定位轨道 + 键盘路径绝对选择 ====================
    print("准备在时间线上右击视频轨道...")
    
    bottom_half_region = (0, int(screen_height * 0.5), screen_width, int(screen_height * 0.5))
    track_location = wait_and_click("timeline_track.png", confidence=0.8, timeout=8, right_click=True, region=bottom_half_region)
    
    if not track_location:
        print("【图片匹配失败】未找到下半屏轨道图片，使用标准全屏比例坐标兜底右击...")
        track_x = int(screen_width * 0.25)  
        track_y = int(screen_height * 0.66) 
        pyautogui.moveTo(track_x, track_y, duration=0.3)
        pyautogui.click()       
        pyautogui.rightClick()  
        
    print("已成功触发右键，正在利用键盘路径“降维狙击”智能粗剪...")
    time.sleep(0.6) # 等待右键菜单极其稳定地弹出来
    
    # 🛠️ 核心微调点：连续按 8 次向下键，完美命中高亮的“智能粗剪”项
    for i in range(8):
        pyautogui.press('down')
        time.sleep(0.08) # 极微小的物理缓冲，确保软件能完全跟上按键频率
        
    print("已精准移动到目标行，正在敲击回车唤醒粗剪面板...")
    pyautogui.press('enter')
    time.sleep(1.5) # 等待粗剪弹窗彻底加载完毕

    # 8. 点击右上角"原声剪辑"
    wait_and_click("original_audio.png", timeout=5)

    # 9. 点击右下角"开始粗剪"
    wait_and_click("start_cut.png", timeout=5)

    # 10 & 11. 等待粗剪完成并处理导出
    print(" 开始等待粗剪处理完成，这可能需要几分钟...")
    max_wait_seconds = 1200
    waited_seconds = 0
    is_export_success = False
    
    while waited_seconds < max_wait_seconds:
        print(f" 正在检查右上角蓝色导出按钮... (已等待 {waited_seconds} 秒)")
        if wait_and_click("export_blue.png", timeout=2): 
            print(" 成功点击右上角蓝色导出按钮！等待弹窗...")
            time.sleep(1.5) 
            
            print("正在验证导出弹窗...")
            if wait_and_click("export_confirm.png", timeout=5):
                print(" 验证成功：弹窗已弹出，并成功点击了底部的确认导出！")
                is_export_success = True
                break 
            else:
                print(" 弹窗没出来？移开鼠标准备重试...")
                pyautogui.moveTo(10, 10) 
                time.sleep(1)
        else:
            time.sleep(2)
            waited_seconds += 4 
            
    if not is_export_success:
        print("\n 超过20分钟仍未找到按钮，流程终止！")
        return

    # 12. 等导出结束后点击右下角的"关闭"
    print("等待视频导出完成...")
    wait_and_click("close_btn.png", timeout=1200)

    # 13. 点击右上角 X 关闭剪映软件
    print("正在关闭剪映软件...")
    wait_and_click("final_close.png", timeout=10)
    time.sleep(0.5)
    pyautogui.press('enter')

    print(" 恭喜！极速全自动化流转已顺利走通！")

if __name__ == "__main__":
    main()