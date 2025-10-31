#!/usr/bin/env python3
"""
鼠标自动点击工具
功能：
1. 获取鼠标点击位置的坐标
2. 自动点击多个配置的位置，支持时间间隔和热键控制
"""

import pyautogui
import time
import json
import os
from pynput import mouse, keyboard
from typing import List, Tuple
import threading


class MouseCoordinateRecorder:
    """记录鼠标点击坐标"""
    
    def __init__(self):
        self.coordinates = []
        self.recording = False
        self.listener = None
    
    def on_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if pressed and button == mouse.Button.left:
            self.coordinates.append((x, y))
            print(f"已记录坐标: ({x}, {y}) - 总共 {len(self.coordinates)} 个点")
    
    def start_recording(self):
        """开始记录坐标"""
        print("\n=== 开始记录鼠标坐标 ===")
        print("请点击你想要自动点击的位置")
        print("按 ESC 键停止记录")
        
        self.recording = True
        self.coordinates = []
        
        with mouse.Listener(on_click=self.on_click) as self.listener:
            with keyboard.Listener(on_press=self._on_key_press) as key_listener:
                key_listener.join()
    
    def _on_key_press(self, key):
        """按键事件处理"""
        try:
            if key == keyboard.Key.esc:
                print("\n记录已停止")
                return False
        except AttributeError:
            pass
    
    def get_coordinates(self) -> List[Tuple[int, int]]:
        """获取记录的坐标"""
        return self.coordinates
    
    def save_to_file(self, filename='coordinates.json'):
        """保存坐标到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.coordinates, f, ensure_ascii=False, indent=2)
        print(f"坐标已保存到 {filename}")


class AutoClicker:
    """自动点击器"""
    
    def __init__(self, coordinates: List[Tuple[int, int]], interval: float = 1.0):
        """
        初始化自动点击器
        
        Args:
            coordinates: 要点击的坐标列表
            interval: 每次点击之间的时间间隔（秒）
        """
        self.coordinates = coordinates
        self.interval = interval
        self.running = False
        self.paused = False
        self.click_thread = None
    
    def start(self):
        """开始自动点击"""
        if self.running:
            print("自动点击已在运行中")
            return
        
        self.running = True
        self.paused = False
        self.click_thread = threading.Thread(target=self._click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()
        print("自动点击已启动")
    
    def stop(self):
        """停止自动点击"""
        self.running = False
        print("\n自动点击已停止")
    
    def pause(self):
        """暂停自动点击"""
        if self.running and not self.paused:
            self.paused = True
            print("\n自动点击已暂停")
    
    def resume(self):
        """恢复自动点击"""
        if self.running and self.paused:
            self.paused = False
            print("\n自动点击已恢复")
    
    def _click_loop(self):
        """点击循环"""
        click_count = 0
        while self.running:
            if not self.paused:
                for i, (x, y) in enumerate(self.coordinates):
                    if not self.running:
                        break
                    
                    while self.paused and self.running:
                        time.sleep(0.1)
                    
                    if not self.running:
                        break
                    
                    pyautogui.click(x, y)
                    click_count += 1
                    print(f"点击位置 {i+1}/{len(self.coordinates)}: ({x}, {y}) - 第 {click_count} 次点击", end='\r')
                    
                    time.sleep(self.interval)
            else:
                time.sleep(0.1)


class HotkeyController:
    """热键控制器"""
    
    def __init__(self, auto_clicker: AutoClicker):
        self.auto_clicker = auto_clicker
        self.listener = None
    
    def start_listening(self):
        """开始监听热键"""
        print("\n=== 热键说明 ===")
        print("F1: 开始/恢复自动点击")
        print("F2: 暂停自动点击")
        print("F3: 停止自动点击并退出")
        print("ESC: 退出程序")
        print("================\n")
        
        with keyboard.Listener(on_press=self._on_key_press) as self.listener:
            self.listener.join()
    
    def _on_key_press(self, key):
        """按键事件处理"""
        try:
            if key == keyboard.Key.f1:
                if not self.auto_clicker.running:
                    self.auto_clicker.start()
                else:
                    self.auto_clicker.resume()
            elif key == keyboard.Key.f2:
                self.auto_clicker.pause()
            elif key == keyboard.Key.f3:
                self.auto_clicker.stop()
                return False
            elif key == keyboard.Key.esc:
                self.auto_clicker.stop()
                return False
        except AttributeError:
            pass


def load_coordinates(filename='coordinates.json') -> List[Tuple[int, int]]:
    """从文件加载坐标"""
    if not os.path.exists(filename):
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        return [tuple(coord) for coord in json.load(f)]


def main():
    """主函数"""
    print("=" * 50)
    print("鼠标自动点击工具")
    print("=" * 50)
    
    while True:
        print("\n请选择功能：")
        print("1. 记录鼠标点击坐标")
        print("2. 使用已保存的坐标进行自动点击")
        print("3. 手动输入坐标进行自动点击")
        print("4. 退出")
        
        choice = input("\n请输入选项 (1-4): ").strip()
        
        if choice == '1':
            recorder = MouseCoordinateRecorder()
            recorder.start_recording()
            
            if recorder.get_coordinates():
                print(f"\n共记录了 {len(recorder.get_coordinates())} 个坐标点:")
                for i, (x, y) in enumerate(recorder.get_coordinates(), 1):
                    print(f"  {i}. ({x}, {y})")
                
                save = input("\n是否保存这些坐标? (y/n): ").strip().lower()
                if save == 'y':
                    recorder.save_to_file()
        
        elif choice == '2':
            coordinates = load_coordinates()
            if not coordinates:
                print("错误: 未找到已保存的坐标文件 coordinates.json")
                continue
            
            print(f"\n已加载 {len(coordinates)} 个坐标点:")
            for i, (x, y) in enumerate(coordinates, 1):
                print(f"  {i}. ({x}, {y})")
            
            try:
                interval = float(input("\n请输入点击间隔时间（秒）[默认1.0]: ").strip() or "1.0")
            except ValueError:
                interval = 1.0
            
            auto_clicker = AutoClicker(coordinates, interval)
            controller = HotkeyController(auto_clicker)
            controller.start_listening()
        
        elif choice == '3':
            print("\n请输入坐标（格式：x,y），每行一个，输入空行结束：")
            coordinates = []
            while True:
                coord_input = input().strip()
                if not coord_input:
                    break
                try:
                    x, y = map(int, coord_input.split(','))
                    coordinates.append((x, y))
                    print(f"已添加坐标: ({x}, {y})")
                except ValueError:
                    print("格式错误，请输入 x,y 格式的坐标")
            
            if not coordinates:
                print("未输入任何坐标")
                continue
            
            try:
                interval = float(input("\n请输入点击间隔时间（秒）[默认1.0]: ").strip() or "1.0")
            except ValueError:
                interval = 1.0
            
            auto_clicker = AutoClicker(coordinates, interval)
            controller = HotkeyController(auto_clicker)
            controller.start_listening()
        
        elif choice == '4':
            print("\n退出程序")
            break
        
        else:
            print("无效的选项，请重新选择")


if __name__ == '__main__':
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    main()
