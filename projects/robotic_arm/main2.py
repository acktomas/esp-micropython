"""
ESP32-S3 主控 + 1 遥感（摇杆）+ 3 个 MG90S 舵机 控制脚本

连接说明：
 - 摇杆 X（VRX） -> GPIO4 (ADC)    控制 舵机1 (GPIO11) 角度 0-180
 - 摇杆 Y（VRY） -> GPIO5 (ADC)    控制 舵机2 (GPIO12) 角度 0-180
 - 摇杆 Z（按键） -> GPIO3 (数字)  控制 舵机3 (GPIO13) 抓取（按下抓起，松开放开）

使用库：基于仓库内的 micropython-servo（`lib/servo/__init__.py`），通过 `Servo` 类控制舵机

中文注释：方便快速理解和修改
"""

import machine
import time
from servo import Servo

# --- 硬件引脚定义（按用户要求）
ADC_PIN_X = 4    # 摇杆 X -> GPIO4
ADC_PIN_Y = 5    # 摇杆 Y -> GPIO5
BTN_PIN_Z = 3    # 摇杆按键 Z -> GPIO3

SERVO1_PIN = 11  # 舵机1 控制 X
SERVO2_PIN = 12  # 舵机2 控制 Y
SERVO3_PIN = 13  # 舵机3 抓取

# 舵机抓取角度设定（按需调整）
SERVO3_GRAB_ANGLE = 30    # 抓取时的角度（举例：30°）
SERVO3_RELEASE_ANGLE = 90 # 释放时的角度（举例：90°）

# ADC 读数范围（ESP32 常见 12-bit）
ADC_MIN = 0
ADC_MAX = 4095


def map_range(x, in_min, in_max, out_min, out_max):
    # 将 x 从 [in_min, in_max] 线性映射到 [out_min, out_max]
    if in_max == in_min:
        return out_min
    # 限幅
    if x < in_min:
        x = in_min
    if x > in_max:
        x = in_max
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def read_adc_avg(adc, samples=8, delay_ms=2):
    # 读取 ADC 并做简单平均以平滑抖动
    s = 0
    for _ in range(samples):
        s += adc.read()
        time.sleep_ms(delay_ms)
    return s // samples


def main():
    # 初始化 ADC
    adc_x = machine.ADC(machine.Pin(ADC_PIN_X))
    adc_y = machine.ADC(machine.Pin(ADC_PIN_Y))
    # 尝试设置宽度和衰减（不同端口可能不支持，故加 try）
    try:
        adc_x.width(machine.ADC.WIDTH_12BIT)
        adc_y.width(machine.ADC.WIDTH_12BIT)
    except Exception:
        pass
    try:
        adc_x.atten(machine.ADC.ATTN_11DB)
        adc_y.atten(machine.ADC.ATTN_11DB)
    except Exception:
        pass

    # 按键引脚，假设按键接地（按下拉低），使用上拉
    btn = machine.Pin(BTN_PIN_Z, machine.Pin.IN, machine.Pin.PULL_UP)

    # 初始化舵机（使用 lib/servo 提供的 Servo 类）
    srv1 = Servo(SERVO1_PIN)
    srv2 = Servo(SERVO2_PIN)
    srv3 = Servo(SERVO3_PIN)

    # 初始位置：将舵机1/2 移到 90°（居中），舵机3 释放位置
    srv1.write(90)
    srv2.write(90)
    srv3.write(SERVO3_RELEASE_ANGLE)

    last_btn_state = btn.value()
    # 简单去抖时间
    last_debounce = time.ticks_ms()
    DEBOUNCE_MS = 50

    print("主循环启动：按住 Z 键抓取，移动摇杆控制舵机1/2")

    while True:
        # 读取并平滑 ADC
        x_raw = read_adc_avg(adc_x, samples=6)
        y_raw = read_adc_avg(adc_y, samples=6)

        # 将 ADC 映射到 0-180°
        angle_x = int(map_range(x_raw, ADC_MIN, ADC_MAX, 0, 180))
        angle_y = int(map_range(y_raw, ADC_MIN, ADC_MAX, 0, 180))

        # 写入舵机 1/2
        srv1.write(angle_x)
        srv2.write(angle_y)

        # 读取按键并去抖
        cur = btn.value()
        now = time.ticks_ms()
        if cur != last_btn_state:
            last_debounce = now
        if time.ticks_diff(now, last_debounce) > DEBOUNCE_MS:
            # 稳定后判断按键状态：假设按下为 0
            if cur == 0:
                # 按下 -> 抓取位置
                srv3.write(SERVO3_GRAB_ANGLE)
            else:
                # 松开 -> 释放位置
                srv3.write(SERVO3_RELEASE_ANGLE)

        last_btn_state = cur

        # 循环等待，控制更新频率
        time.sleep_ms(50)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # 出现异常打印，便于调试
        print('发生异常:', e)
        raise
