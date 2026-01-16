from machine import Pin
from neopixel import NeoPixel
import time

# --------------------------
# 关键配置（根据开发板版本选择）
# --------------------------
# 1. ESP32-S3-DevKitC-1 v1.0：板载RGB LED接GPIO48（J3-16）
# 2. ESP32-S3-DevKitC-1 v1.1：板载RGB LED接GPIO38（J3-10）
# 3. 外接灯带：推荐GPIO21（J3-18）
RGB_PIN = 48  # 此处以v1.0为例，v1.1需改为38
NUM_LEDS = 1  # 板载仅1个RGB LED

# 初始化NeoPixel（WS2812需GRB颜色顺序，文档未明确，补充实战要点）
np = NeoPixel(Pin(RGB_PIN, Pin.OUT), NUM_LEDS)

def set_rgb(red, green, blue):
    """设置RGB颜色（WS2812为GRB顺序，非RGB）"""
    np[0] = (green, red, blue)  # 关键：文档未提，必须按GRB顺序
    np.write()  # 发送数据到LED

def breath_effect(color, step=5, delay=20):
    """呼吸灯效果（渐变明暗）"""
    r, g, b = color
    # 渐亮
    for brightness in range(0, 256, step):
        set_rgb(int(r*brightness/255), int(g*brightness/255), int(b*brightness/255))
        time.sleep_ms(delay)
    # 渐暗
    for brightness in range(255, -1, -step):
        set_rgb(int(r*brightness/255), int(g*brightness/255), int(b*brightness/255))
        time.sleep_ms(delay)

try:
    print(f"RGB LED测试（引脚GPIO{RGB_PIN}）")
    while True:
        set_rgb(255, 0, 0)  # 红色
        time.sleep(1)
        set_rgb(0, 255, 0)  # 绿色
        time.sleep(1)
        set_rgb(0, 0, 255)  # 蓝色
        time.sleep(1)
        breath_effect((255, 255, 255))  # 白色呼吸灯
except KeyboardInterrupt:
    set_rgb(0, 0, 0)  # 退出时关闭LED
    print("测试结束")