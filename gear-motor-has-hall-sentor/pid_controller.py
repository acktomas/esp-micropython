"""
PID控制器模块
实现经典PID控制算法
包含详细的参数调节和学习功能
"""

import utime
import math

class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, setpoint=0.0, 
                 output_min=-100.0, output_max=100.0, sample_time=0.01):
        """
        初始化PID控制器
        
        参数:
        - kp: 比例增益 (P)
        - ki: 积分增益 (I)  
        - kd: 微分增益 (D)
        - setpoint: 目标值
        - output_min: 输出最小值
        - output_max: 输出最大值
        - sample_time: 采样时间 (秒)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.output_min = output_min
        self.output_max = output_max
        self.sample_time = sample_time
        
        # 内部状态变量
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = utime.ticks_ms()
        
        # 输出限制
        self.output = 0.0
        
        # 调试信息
        self.error = 0.0
        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0
        
        # 抗积分饱和
        self.integral_limit = output_max * 0.8  # 积分项限制
        
        # 微分项平滑滤波
        self.derivative_filter_alpha = 0.1
        self.last_derivative = 0.0
        
        print(f"PID控制器初始化 - Kp:{kp}, Ki:{ki}, Kd:{kd}, 目标:{setpoint}")
    
    def update(self, current_value):
        """
        更新PID控制器
        
        参数:
        - current_value: 当前测量值
        
        返回:
        - output: 控制输出
        """
        current_time = utime.ticks_ms()
        
        # 检查采样时间
        if utime.ticks_diff(current_time, self.last_time) < int(self.sample_time * 1000):
            return self.output
        
        # 计算误差
        self.error = self.setpoint - current_value
        
        # P项 (比例)
        self.p_term = self.kp * self.error
        
        # I项 (积分) - 带抗饱和
        self.integral += self.error * self.sample_time
        
        # 限制积分项范围
        if self.integral > self.integral_limit:
            self.integral = self.integral_limit
        elif self.integral < -self.integral_limit:
            self.integral = -self.integral_limit
        
        self.i_term = self.ki * self.integral
        
        # D项 (微分) - 带滤波
        derivative = (self.error - self.last_error) / self.sample_time
        
        # 低通滤波平滑微分项
        filtered_derivative = (self.derivative_filter_alpha * derivative + 
                              (1 - self.derivative_filter_alpha) * self.last_derivative)
        
        self.d_term = self.kd * filtered_derivative
        self.last_derivative = filtered_derivative
        
        # 计算总输出
        self.output = self.p_term + self.i_term + self.d_term
        
        # 输出限制
        if self.output > self.output_max:
            self.output = self.output_max
        elif self.output < self.output_min:
            self.output = self.output_min
        
        # 更新状态
        self.last_error = self.error
        self.last_time = current_time
        
        return self.output
    
    def set_tunings(self, kp, ki, kd):
        """设置PID参数"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
        print(f"PID参数更新 - Kp:{kp}, Ki:{ki}, Kd:{kd}")
    
    def set_setpoint(self, setpoint):
        """设置目标值"""
        self.setpoint = setpoint
        # 清除积分项以避免冲击
        self.integral = 0.0
    
    def reset(self):
        """重置PID控制器"""
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = utime.ticks_ms()
        self.output = 0.0
        self.last_derivative = 0.0
        print("PID控制器已重置")
    
    def get_debug_info(self):
        """获取调试信息"""
        return {
            'error': self.error,
            'p_term': self.p_term,
            'i_term': self.i_term, 
            'd_term': self.d_term,
            'output': self.output,
            'setpoint': self.setpoint
        }
    
    def print_debug(self):
        """打印调试信息"""
        debug = self.get_debug_info()
        print(f"误差:{debug['error']:6.2f} | "
              f"P:{debug['p_term']:6.2f} | "
              f"I:{debug['i_term']:6.2f} | "
              f"D:{debug['d_term']:6.2f} | "
              f"输出:{debug['output']:6.2f} | "
              f"目标:{debug['setpoint']:6.2f}")


# PID调参助手类
class PIDTuner:
    def __init__(self, pid_controller):
        """
        PID调参助手
        
        参数:
        - pid_controller: PID控制器实例
        """
        self.pid = pid_controller
        self.tuning_data = []
        
    def auto_tune_step_response(self, motor, encoder, step_size=90.0, duration=5.0):
        """
        阶跃响应自动调参
        
        参数:
        - motor: 电机驱动器
        - encoder: 编码器
        - step_size: 阶跃幅度 (度)
        - duration: 测试时间 (秒)
        """
        print("开始阶跃响应测试...")
        
        # 记录初始位置
        initial_angle = encoder.get_angle()
        target_angle = initial_angle + step_size
        
        # 设置目标
        self.pid.set_setpoint(target_angle)
        
        # 记录数据
        start_time = utime.ticks_ms()
        data_points = []
        
        while utime.ticks_diff(utime.ticks_ms(), start_time) < int(duration * 1000):
            current_angle = encoder.get_angle()
            current_time = utime.ticks_diff(utime.ticks_ms(), start_time) / 1000.0
            
            # 更新PID
            control_output = self.pid.update(current_angle)
            
            # 应用控制输出
            motor.set_speed(control_output)
            
            # 记录数据点
            data_points.append({
                'time': current_time,
                'setpoint': target_angle,
                'actual': current_angle,
                'error': self.pid.error,
                'output': control_output
            })
            
            # 打印进度
            if int(current_time * 10) % 10 == 0:  # 每秒打印一次
                print(f"时间:{current_time:4.1f}s | "
                      f"目标:{target_angle:6.1f}° | "
                      f"实际:{current_angle:6.1f}° | "
                      f"误差:{self.pid.error:6.1f}°")
            
            utime.sleep(0.01)  # 10ms采样周期
        
        motor.stop()
        
        # 计算性能指标
        self._analyze_step_response(data_points)
        
        return data_points
    
    def _analyze_step_response(self, data):
        """分析阶跃响应数据"""
        if not data:
            return
        
        print("\n=== 阶跃响应分析 ===")
        
        # 找到稳态值 (最后10%数据平均值)
        steady_state_size = len(data) // 10
        steady_state_values = [d['actual'] for d in data[-steady_state_size:]]
        steady_state_value = sum(steady_state_values) / len(steady_state_values)
        
        # 超调量
        max_value = max(d['actual'] for d in data)
        target_value = data[0]['setpoint']
        overshoot = ((max_value - target_value) / target_value) * 100 if target_value != 0 else 0
        
        # 稳态误差
        steady_state_error = abs(target_value - steady_state_value)
        
        # 上升时间 (10%到90%)
        ten_percent = target_value * 0.1
        ninety_percent = target_value * 0.9
        
        rise_start = None
        rise_end = None
        
        for d in data:
            if rise_start is None and d['actual'] >= ten_percent:
                rise_start = d['time']
            if rise_end is None and d['actual'] >= ninety_percent:
                rise_end = d['time']
                break
        
        rise_time = (rise_end - rise_start) if (rise_start and rise_end) else None
        
        print(f"超调量: {overshoot:.1f}%")
        print(f"稳态误差: {steady_state_error:.2f}°")
        print(f"上升时间: {rise_time:.2f}s" if rise_time else "上升时间: 无法计算")
        print(f"稳态值: {steady_state_value:.2f}°")
        
        # 调参建议
        print("\n=== 调参建议 ===")
        if overshoot > 20:
            print("超调量过大，建议减小Kp或增加Kd")
        elif overshoot < 5:
            print("响应较慢，建议增加Kp")
        
        if steady_state_error > 5:
            print("稳态误差较大，建议增加Ki")
        
        if rise_time and rise_time > 2:
            print("上升时间过长，建议增加Kp")


# 使用示例
if __name__ == "__main__":
    # 创建PID控制器示例
    pid = PIDController(kp=2.0, ki=0.5, kd=0.1, setpoint=90.0)
    tuner = PIDTuner(pid)
    
    print("PID控制器和调参工具初始化完成")
    print("示例参数:")
    print(f"- Kp: {pid.kp}")
    print(f"- Ki: {pid.ki}") 
    print(f"- Kd: {pid.kd}")
    print(f"- 目标: {pid.setpoint}°")
    
    # 简单测试
    print("\n简单测试...")
    for i in range(10):
        output = pid.update(i * 10)  # 模拟从0到90的过程
        pid.print_debug()
        utime.sleep(0.1)