from machine import Pin, ADC, PWM
import time

# 摇杆引脚定义
JOYSTICK_X = 26  # X轴ADC引脚
JOYSTICK_Y = 27  # Y轴ADC引脚

# 舵机引脚定义
SERVO1_PIN = 1   # 机械臂旋转舵机
SERVO2_PIN = 2   # 机械臂俯仰舵机
SERVO3_PIN = 3   # 机械臂抓取舵机

# 初始化ADC
adc_x = ADC(Pin(JOYSTICK_X), atten=ADC.ATTN_11DB)
adc_y = ADC(Pin(JOYSTICK_Y), atten=ADC.ATTN_11DB)

# 初始化PWM（50Hz频率，适合舵机）
servo1 = PWM(Pin(SERVO1_PIN), freq=50, duty=0)
servo2 = PWM(Pin(SERVO2_PIN), freq=50, duty=0)
servo3 = PWM(Pin(SERVO3_PIN), freq=50, duty=0)

# ADC值到角度的映射函数
def adc_to_angle(adc_value, min_adc=0, max_adc=4095, min_angle=0, max_angle=180):
    angle = ((adc_value - min_adc) / (max_adc - min_adc)) * (max_angle - min_angle) + min_angle
    # 确保角度在有效范围内
    angle = max(min_angle, min(max_angle, angle))
    return round(angle, 2)

# 角度到PWM占空比的映射函数（适用于大多数舵机）
def angle_to_duty(angle):
    # 50Hz PWM，20ms周期
    # 占空比范围：2.5%~12.5%对应0~180度
    # 计算公式：duty = 2.5% + (angle/180)*(12.5%-2.5%)
    # PWM占空比范围：0~1023（10位分辨率）
    duty = (2.5 + (angle / 180) * 10) / 100 * 1023
    return int(duty)

# 初始化舵机到中间位置
def init_servos():
    mid_angle = 90
    servo1.duty(angle_to_duty(mid_angle))
    servo2.duty(angle_to_duty(mid_angle))
    servo3.duty(angle_to_duty(mid_angle))
    time.sleep(1)  # 等待舵机到达位置

# 主程序
print("机械臂摇杆控制器启动...")
init_servos()

while True:
    # 读取摇杆ADC值
    adc_x_val = adc_x.read()
    adc_y_val = adc_y.read()

    # 映射到角度
    angle_x = adc_to_angle(adc_x_val)
    angle_y = adc_to_angle(adc_y_val)

    # 控制舵机
    # 摇杆X轴控制机械臂旋转（舵机1）
    servo1.duty(angle_to_duty(angle_x))

    # 摇杆Y轴控制机械臂俯仰（舵机2）
    servo2.duty(angle_to_duty(angle_y))

    # 可以根据需要添加按钮控制抓取（舵机3）
    # 这里简单实现：Y轴小于30度时抓取，大于150度时松开
    if angle_y < 30:
        servo3.duty(angle_to_duty(0))  # 抓取
    elif angle_y > 150:
        servo3.duty(angle_to_duty(180))  # 松开

    # 打印调试信息
    print(f"X轴: {adc_x_val} -> {angle_x}度, Y轴: {adc_y_val} -> {angle_y}度")

    time.sleep(0.05)  # 控制频率


