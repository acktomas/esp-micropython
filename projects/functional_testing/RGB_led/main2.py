# 导入必要的库
from machine import Pin
import neopixel
import time

# --- 配置部分 ---
# 定义RGB LED连接的引脚和数量
PIN_NUM = 48      # 推荐使用GPIO38
NUM_LEDS = 1      # 假设只驱动1个RGB LED，如果是灯带，请修改此值

# 创建NeoPixel对象
# Pin(PIN_NUM, Pin.OUT) 创建一个输出引脚
# neopixel.NeoPixel() 初始化NeoPixel库
np = neopixel.NeoPixel(Pin(PIN_NUM, Pin.OUT), NUM_LEDS)

# --- 基础函数 ---
def set_color(r, g, b):
    """
    设置所有LED为指定颜色
    :param r: 红色分量 (0-255)
    :param g: 绿色分量 (0-255)
    :param b: 蓝色分量 (0-255)
    """
    for i in range(NUM_LEDS):
        np[i] = (r, g, b)
    np.write() # 将颜色数据发送到LED

def breathing_effect(color=(0, 0, 255), cycles=3):
    """
    实现呼吸灯效果
    :param color: 基础颜色 (r, g, b)
    :param cycles: 呼吸循环次数
    """
    r_base, g_base, b_base = color
    for _ in range(cycles):
        # 逐渐变亮
        for brightness in range(0, 256, 5):
            r = int(r_base * (brightness / 255))
            g = int(g_base * (brightness / 255))
            b = int(b_base * (brightness / 255))
            set_color(r, g, b)
            time.sleep_ms(10) # 控制呼吸速度
        
        # 逐渐变暗
        for brightness in range(255, -1, -5):
            r = int(r_base * (brightness / 255))
            g = int(g_base * (brightness / 255))
            b = int(b_base * (brightness / 255))
            set_color(r, g, b)
            time.sleep_ms(10)

# --- 主程序 ---
if __name__ == "__main__":
    print("ESP32-S3 RGB LED Demo")
    
    # 效果1: 依次显示红、绿、蓝
    print("显示纯色...")
    set_color(255, 0, 0)  # 红色
    time.sleep(1)
    set_color(0, 255, 0)  # 绿色
    time.sleep(1)
    set_color(0, 0, 255)  # 蓝色
    time.sleep(1)
    
    # 效果2: 显示白色
    set_color(255, 255, 255) # 白色
    time.sleep(1)
    
    # 效果3: 关闭LED
    set_color(0, 0, 0)
    time.sleep(0.5)
    
    # 效果4: 呼吸灯 (蓝色)
    print("启动呼吸灯效果...")
    breathing_effect(color=(0, 0, 255), cycles=5)
    
    # 最终关闭
    set_color(0, 0, 0)
    print("Demo结束")