"""
直流减速电机驱动模块
使用L298N或类似电机驱动器控制电机
支持PWM调速和方向控制
"""

from machine import Pin, PWM
import utime


class MotorDriver:
    def __init__(self, pwm_pin, in1_pin, in2_pin, freq=1000):
        """
        初始化电机驱动器
        
        参数:
        - pwm_pin: PWM引脚号 (ESP32: 0-39, 支持PWM的引脚)
        - in1_pin: 方向控制引脚1
        - in2_pin: 方向控制引脚2  
        - freq: PWM频率 (Hz)
        """
        self.pwm = PWM(Pin(pwm_pin), freq)
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
        self.freq = freq
        
        # 初始状态: 电机停止
        self.speed = 0
        self.stop()
        
        print(f"电机驱动器初始化完成 - PWM:{pwm_pin}, IN1:{in1_pin}, IN2:{in2_pin}")
    
    def set_speed(self, speed):
        """
        设置电机速度 (-100 到 100)
        正数: 正转，负数: 反转
        
        参数:
        - speed: 速度百分比 (-100 到 100)
        """
        # 限制速度范围
        speed = max(-100, min(100, speed))
        self.speed = speed
        
        # 计算PWM占空比 (0-65535)
        duty = int(abs(speed) * 65535 / 100)
        
        if speed > 0:
            # 正转
            self.in1.value(1)
            self.in2.value(0)
            self.pwm.duty_u16(duty)
        elif speed < 0:
            # 反转
            self.in1.value(0)
            self.in2.value(1)
            self.pwm.duty_u16(duty)
        else:
            # 停止
            self.stop()
    
    def forward(self, speed=50):
        """正转"""
        self.set_speed(abs(speed))
    
    def backward(self, speed=50):
        """反转"""
        self.set_speed(-abs(speed))
    
    def stop(self):
        """停止电机 (刹车)"""
        self.in1.value(1)
        self.in2.value(1)
        self.pwm.duty_u16(65535)  # 最大占空比刹车
        self.speed = 0
    
    def coast(self):
        """惰性停止 (不刹车)"""
        self.in1.value(0)
        self.in2.value(0)
        self.pwm.duty_u16(0)
        self.speed = 0
    
    def get_speed(self):
        """获取当前速度"""
        return self.speed
    
    def test(self):
        """电机测试程序"""
        print("开始电机测试...")
        
        # 测试正转
        print("正转 50% 速度")
        self.forward(50)
        utime.sleep(2)
        
        # 测试停止
        print("停止")
        self.stop()
        utime.sleep(1)
        
        # 测试反转
        print("反转 50% 速度")
        self.backward(50)
        utime.sleep(2)
        
        # 测试不同速度
        print("变速测试: 25% -> 50% -> 75% -> 100%")
        for speed in [25, 50, 75, 100]:
            print(f"正转 {speed}% 速度")
            self.forward(speed)
            utime.sleep(1)
        
        # 最终停止
        self.stop()
        print("电机测试完成")


# 使用示例和测试
if __name__ == "__main__":
    # 根据实际接线修改引脚号
    # 假设使用以下引脚 (请根据实际接线修改):
    # PWM: 引脚 25 (支持PWM)
    # IN1: 引脚 26
    # IN2: 引脚 27
    
    try:
        motor = MotorDriver(pwm_pin=25, in1_pin=26, in2_pin=27, freq=1000)
        motor.test()
        
    except Exception as e:
        print(f"电机驱动错误: {e}")
        print("请检查引脚接线是否正确")