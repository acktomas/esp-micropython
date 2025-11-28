"""
霍尔编码器读取模块
用于读取带霍尔传感器的直流减速电机信号
计算位置、角度和速度
"""

from machine import Pin
import utime
from micropython import schedule

class EncoderReader:
    def __init__(self, hall_a_pin, hall_b_pin, ppr=11, gear_ratio=1):
        """
        初始化编码器读取器
        
        参数:
        - hall_a_pin: 霍尔传感器A相引脚
        - hall_b_pin: 霍尔传感器B相引脚  
        - ppr: 编码器每转脉冲数 (通常是霍尔传感器数量×2)
        - gear_ratio: 减速比 (例如 30:1 减速器输入 30)
        """
        self.hall_a = Pin(hall_a_pin, Pin.IN, Pin.PULL_UP)
        self.hall_b = Pin(hall_b_pin, Pin.IN, Pin.PULL_UP)
        
        # 编码器参数
        self.ppr = ppr  # 每转脉冲数
        self.gear_ratio = gear_ratio  # 减速比
        self.total_ppr = ppr * gear_ratio  # 总脉冲数
        
        # 计数器
        self.count = 0  # 原始计数
        self.last_count = 0
        self.total_count = 0  # 累计计数
        self.overflow_count = 0
        
        # 速度计算
        self.last_time = utime.ticks_ms()
        self.speed = 0  # RPM
        self.angle_speed = 0  # 角速度 (度/秒)
        
        # 中断处理标志
        self._last_a_state = self.hall_a.value()
        self._last_b_state = self.hall_b.value()
        
        # 设置中断
        self.hall_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._encoder_irq)
        self.hall_b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._encoder_irq)
        
        print(f"编码器初始化完成 - A:{hall_a_pin}, B:{hall_b_pin}, PPR:{ppr}, 减速比:{gear_ratio}")
    
    def _encoder_irq(self, pin):
        """编码器中断处理"""
        current_a = self.hall_a.value()
        current_b = self.hall_b.value()
        
        # 简化的四倍频解码
        if current_a != self._last_a_state:
            if current_a != current_b:
                self.count += 1
            else:
                self.count -= 1
        elif current_b != self._last_b_state:
            if current_b == current_a:
                self.count += 1
            else:
                self.count -= 1
        
        self._last_a_state = current_a
        self._last_b_state = current_b
        
        # 累计计数（用于多圈计算）
        self.total_count += 1
    
    def get_count(self):
        """获取当前计数"""
        return self.count
    
    def reset(self):
        """重置计数器"""
        self.count = 0
        self.total_count = 0
        self.overflow_count = 0
        self.last_count = 0
        self.speed = 0
        self.angle_speed = 0
        print("编码器计数器已重置")
    
    def get_angle(self):
        """获取当前角度 (度)"""
        return (self.count / self.total_ppr) * 360.0
    
    def get_revolutions(self):
        """获取当前转数"""
        return self.count / self.total_ppr
    
    def get_angular_position(self):
        """获取角位置 (弧度)"""
        return (self.count / self.total_ppr) * 2 * 3.14159265359
    
    def update_speed(self):
        """更新速度计算"""
        current_time = utime.ticks_ms()
        time_diff = utime.ticks_diff(current_time, self.last_time)
        
        if time_diff >= 50:  # 每50ms更新一次速度
            count_diff = self.count - self.last_count
            
            if time_diff > 0:
                # 计算RPM (转/分钟)
                self.speed = (count_diff / self.total_ppr) * 60000 / time_diff
                
                # 计算角速度 (度/秒)
                self.angle_speed = self.speed * 360.0 / 60.0
            
            self.last_count = self.count
            self.last_time = current_time
    
    def get_speed_rpm(self):
        """获取速度 (RPM)"""
        self.update_speed()
        return self.speed
    
    def get_speed_deg_per_sec(self):
        """获取角速度 (度/秒)"""
        self.update_speed()
        return self.angle_speed
    
    def get_speed_rad_per_sec(self):
        """获取角速度 (弧度/秒)"""
        return self.get_speed_deg_per_sec() * 3.14159265359 / 180.0
    
    def test(self):
        """编码器测试程序"""
        print("开始编码器测试...")
        print("请手动旋转电机轴...")
        
        last_angle = 0
        last_time = utime.ticks_ms()
        
        for i in range(100):  # 测试10秒
            current_time = utime.ticks_ms()
            time_diff = utime.ticks_diff(current_time, last_time)
            
            if time_diff >= 1000:  # 每秒打印一次
                angle = self.get_angle()
                rpm = self.get_speed_rpm()
                revs = self.get_revolutions()
                
                print(f"时间:{i}s | 计数:{self.count:6d} | 角度:{angle:6.1f}° | "
                      f"转数:{revs:6.2f} | 速度:{rpm:6.1f}RPM")
                
                last_time = current_time
            
            utime.sleep(0.1)
        
        print("编码器测试完成")


# 使用示例和测试
if __name__ == "__main__":
    try:
        # 根据实际接线修改引脚号
        # 假设霍尔传感器连接到引脚 4 和 5
        # ppr=11 (11个霍尔信号)
        # gear_ratio=30 (30:1减速比)
        
        encoder = EncoderReader(hall_a_pin=4, hall_b_pin=5, ppr=11, gear_ratio=30)
        encoder.test()
        
    except Exception as e:
        print(f"编码器错误: {e}")
        print("请检查引脚接线是否正确")