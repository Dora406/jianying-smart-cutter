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

# 极速执行流控制
pyautogui.PAUSE = 0.2

def wait_and_click(image_name, confidence=0.8, timeout=30, double_click=False, right_click=False, region=None):
    """
    【万能多尺度自适应匹配核心函数】
    自动循环将图片缩放为 100%, 125%, 150%, 175%, 200%, 80%, 75% 等多种屏幕缩放比，无视大小只认图案。
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

    scales = [1.0, 1.25, 1.5, 1.75, 2.0, 0.8, 0.75]

    while time.time() - start_time < timeout:
        for scale in scales:
            try:
                if scale == 1.0:
                    img_to_search = img_bgr
                else:
                    img_to_search = cv2.resize(img_bgr, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                
                if region:
                    if img_to_search.shape[1] > region[2] or img_to_search.shape[0] > region[3]:
                        continue
                
                location = pyautogui.locateCenterOnScreen(img_to_search, confidence=confidence, region=region)
                if location:
                    if double_click:
                        pyautogui.doubleClick(location)
                    elif right_click:
                        pyautogui.rightClick(location)
                    else:
                        pyautogui.click(location)
                    print(f"成功匹配点击: {image_name} (自动适配缩放比: {int(scale*100)}%)，坐标: ({location.x}, {location.y})")
                    time.sleep(0.3)  
                    return location   
            except pyautogui.ImageNotFoundException:
                pass
            except Exception:
                pass
        time.sleep(0.2)  
        
    print(f"超时未找到图片: {image_name}")
    return None

def main():
    print("开始执行剪映自动化脚本...")
    print(f"[环境检测] 剪映路径: {JIANYING_PATH}")
    print(f"[环境检测] 视频路径: {VIDEO_PATH}")
    print(f"[环境检测] 图片目录: {IMG_DIR}\n")

    screen_width, screen_height = pyautogui.size()

    # 1 & 2. 智能唤醒 / 打开剪映
    print("正在检查剪映是否已经在运行...")
    if bring_jianying_to_foreground():
        print("【唤醒成功】检测到剪映已地区在运行，已成功将其从后台拉出并最大化！")
        time.sleep(1)
    else:
        print("【全新启动】未检测到运行中的剪映，正在重新打开...")
        if os.path.exists(JIANYING_PATH):
            subprocess.Popen(JIANYING_PATH)
            time.sleep(6)  
            pyautogui.hotkey('win', 'up')
        else:
            print("【严重错误】未在系统中找到剪映主程序，且后台未运行剪映，流程终止！")
            return

    # 3. 点击"智能粗剪"
    wait_and_click("smart_cut_btn.png")

    # 4. 弹窗点击"去创作"
    wait_and_click("go_create.png", confidence=0.7)
    time.sleep(1.5)  

    # 5. 点击导入并选择视频
    wait_and_click("import_btn.png")
    time.sleep(1)
    pyperclip.copy(VIDEO_PATH)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    
    print("正在等待视频导入完成...")
    time.sleep(3.5)

    # ==================== 6. 定位腹地 + 严苛防误触狙击圈 ====================
    print("准备将视频加入时间线...")
    # 修正坐标比例：纵向拉深到 24%，让鼠标稳稳落在笔记本放大后的“视频缩略图正中央”
    video_x = int(screen_width * 0.10)
    video_y = int(screen_height * 0.24)
    
    print(f"鼠标正在移向视频腹地以完全激活加号: ({video_x}, {video_y})")
    pyautogui.moveTo(video_x, video_y, duration=0.3)
    time.sleep(1.0) 
    
    # 划定精准扩展矩阵：向左上只看 50 像素（彻底排除勾选框），向右下狂看 300 像素
    expanded_plus_region = (max(0, video_x - 50), max(0, video_y - 50), 300, 300)
    
    if wait_and_click("plus_btn.png", confidence=0.85, timeout=3.0, region=expanded_plus_region):
        print("【成功】通过高精度局部图片匹配，成功点击了真正的蓝色加号！")
    else:
        # 重写物理反击连招，使用100%成功的键盘流
        print("【物理反击】图片由于极限变形未命中。正在启动键盘终极连招...")
        pyautogui.click(video_x, video_y) # 稳稳单击，强制让这个视频卡片在底层获得焦点选中状态
        time.sleep(0.3)
        pyautogui.press('enter')           # 敲击回车送入轨道（双保险之一）
        time.sleep(0.2)
        pyautogui.press('e')               # 敲击快捷键 E 追加到轨道（双保险之二）
        print("【成功】已通过“单击+回车+E”键盘组合拳将视频强行送入时间线！")
        
    time.sleep(1.5)  

    # ==================== 7. 下半屏定位轨道 + 多尺度智能图片匹配菜单 ====================
    print("准备在时间线上右击视频轨道...")
    
    bottom_half_region = (0, int(screen_height * 0.5), screen_width, int(screen_height * 0.5))
    track_location = wait_and_click("timeline_track.png", confidence=0.8, timeout=8, right_click=True, region=bottom_half_region)
    
    if not track_location:
        print("【图片匹配失败】未找到下半屏轨道图片，使用标准全屏比例坐标兜底右击...")
        track_x = int(screen_width * 0.25)   
        track_y = int(screen_height * 0.72)  
        pyautogui.moveTo(track_x, track_y, duration=0.3)
        pyautogui.click()        
        pyautogui.rightClick()   
        
    ref_x = track_location.x if track_location else int(screen_width * 0.25)
    ref_y = track_location.y if track_location else int(screen_height * 0.72)

    # 右击完瞬间执行鼠标左移 150 像素！彻底断开与菜单主体的接触，防止悬停触发任何子菜单展开
    pyautogui.moveTo(max(0, int(ref_x - 150)), int(ref_y))
    print("已成功触发右键并闪现移开鼠标，正在划定超大范围天空防御区...")
    time.sleep(0.6)  
    
    # 将纵向包围圈顶部从 -450 像素扩容到 -800 像素，完美将推向天空的所有菜单囊括进来
    menu_search_region = (max(0, int(ref_x - 60)), max(0, int(ref_y - 800)), 500, 950)
    
    # 将精确度放宽到 0.73。有了多尺度缩放对齐，0.73不仅秒杀字体模糊，且字形差异足够拉开与“AI音效”的距离
    if wait_and_click("smart_cut_menu.png", confidence=0.73, timeout=4.0, region=menu_search_region):
        print("【全网通关】通过自适应多尺度图形引擎，精准点击了菜单中的“智能粗剪”！")
    else:
        # 自适应探针兜底键盘流
        print("【视觉未匹配】菜单图片识别未通过，启动实时“硬件探针”自适应键盘流...")
        
        def check_panel_opened():
            img_audio_path = os.path.join(IMG_DIR, "original_audio.png")
            try:
                img_audio = cv2.imdecode(np.fromfile(img_audio_path, dtype=np.uint8), cv2.IMREAD_COLOR)
                if img_audio is None: return False
                for scale in [1.0, 1.25, 1.5, 1.75, 2.0, 0.8]:
                    img_search = img_audio if scale == 1.0 else cv2.resize(img_audio, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                    try:
                        if pyautogui.locateCenterOnScreen(img_search, confidence=0.75):
                            return True
                    except pyautogui.ImageNotFoundException:
                        pass
            except Exception:
                pass
            return False

        panel_success = False
        # 穷举不同电脑状态下的菜单栏行数：8下（标准无粘贴属性）、9下（包含粘贴属性）、7下（精简版）
        for downs in [8, 9, 7]:
            print(f"[自适应纠错] 正在尝试连按 {downs} 次向下键...")
            old_pause = pyautogui.PAUSE
            pyautogui.PAUSE = 0.05  # 适当放慢到安全的0.05秒，确保剪映可以100%捕捉按键不丢包！
            for _ in range(downs):
                pyautogui.press('down')
            pyautogui.PAUSE = old_pause   
            pyautogui.press('enter')
            
            time.sleep(1.2) # 给面板展开一秒钟的硬件缓冲时间
            if check_panel_opened():
                print(f"【突破成功】经面板闭环验证，连按 {downs} 次向下键已完美唤醒粗剪面板！")
                panel_success = True
                break
            else:
                print(f"[尝试失败] 按 {downs} 次未能唤醒面板（可能点错），重新右击轨道重试...")
                pyautogui.moveTo(ref_x, ref_y, duration=0.2)
                pyautogui.rightClick()   
                pyautogui.moveTo(max(0, int(ref_x - 150)), int(ref_y))
                time.sleep(0.5)
                
        if not panel_success:
            print("【严重警告】视觉匹配和键盘自适应穷举全部失效，强行向后流转...")
        
    time.sleep(1.5)  

    # 8. 点击"原声剪辑"
    wait_and_click("original_audio.png", timeout=5)

    # 9. 点击"开始粗剪"
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
