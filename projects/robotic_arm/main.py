from machine import Pin, ADC
from servo import Servo  # 导入舵机库
import time

# 初始化摇杆引脚
vrx_pin = ADC(Pin(4))  # VRX - X轴摇杆 (GPIO4)
vry_pin = ADC(Pin(5))  # VRY - Y轴摇杆 (GPIO5)
sw_pin = Pin(3, Pin.IN, Pin.PULL_UP)  # SW - 按键 (GPIO3)

# 初始化舵机引脚
servo1 = Servo(Pin(11))  # 舵机1 (GPIO11)
servo2 = Servo(Pin(12))  # 舵机2 (GPIO12)
servo3 = Servo(Pin(13))  # 舵机3 (GPIO13)

# 设置ADC分辨率 (0-4095)
vrx_pin.atten(ADC.ATTN_11DB)  # 增加输入电压范围
vry_pin.atten(ADC.ATTN_11DB)  # 增加输入电压范围

def map_value(x, in_min, in_max, out_min, out_max):
    """
    将输入值从一个范围映射到另一个范围
    :param x: 输入值
    :param in_min: 输入最小值
    :param in_max: 输入最大值
    :param out_min: 输出最小值
    :param out_max: 输出最大值
    :return: 映射后的值
    """
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def control_servos():
    """
    主控制循环，读取摇杆输入并控制舵机
    """
    print("开始控制机械臂...")

    # 设置初始位置
    servo1.write_angle(90)  # 舵机1初始位置90度
    servo2.write_angle(90)  # 舵机2初始位置90度
    servo3.write_angle(0)   # 舵机3初始位置0度（松开）
    
    last_button_state = True  # 记录上次按钮状态，用于检测按下事件
    
    while True:
        # 读取摇杆X轴值 (0-4095)
        vrx_value = vrx_pin.read()
        # 将X轴值映射到0-180度范围
        servo1_angle = map_value(vrx_value, 0, 4095, 0, 180)
        # 控制舵机1转动
        servo1.write_angle(servo1_angle)
        
        # 读取摇杆Y轴值 (0-4095)
        vry_value = vry_pin.read()
        # 将Y轴值映射到0-180度范围
        servo2_angle = map_value(vry_value, 0, 4095, 0, 180)
        # 控制舵机2转动
        servo2.write_angle(servo2_angle)
        
        # 读取摇杆按键状态
        current_button_state = sw_pin.value()
        
        # 检测按键是否被按下（下降沿触发）
        if last_button_state and not current_button_state:
            print("按键按下，控制抓取舵机...")
            
            # 控制舵机3执行抓取动作
            servo3.write_angle(90)  # 抓取物品
            time.sleep(0.5)         # 短暂延迟
            servo3.write_angle(0)   # 松开物品
            time.sleep(0.5)         # 短暂延迟
        
        # 更新按钮状态
        last_button_state = current_button_state
        
        # 短暂延迟，避免过于频繁更新
        time.sleep_ms(50)
        
        # 打印当前状态（可选，调试用）
        print(f"X轴: {vrx_value}, 舵机1角度: {servo1_angle} | "
              f"Y轴: {vry_value}, 舵机2角度: {servo2_angle} | "
              f"按键: {'按下' if not current_button_state else '未按'}")

# 主程序入口
if __name__ == "__main__":
    try:
        control_servos()
    except KeyboardInterrupt:
        print("程序已停止")
        # 将所有舵机归位到安全位置
        servo1.write_angle(90)
        servo2.write_angle(90)
        servo3.write_angle(0)