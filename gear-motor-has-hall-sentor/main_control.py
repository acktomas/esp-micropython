"""
主控制程序
整合电机驱动、编码器读取和PID控制
实现精确的角度控制功能
"""

import utime
from motor_driver import MotorDriver
from encoder_reader import EncoderReader  
from pid_controller import PIDController, PIDTuner
from config import get_system_config, print_system_info

class MotorAngleController:
    def __init__(self, motor_config, encoder_config, pid_config):
        """
        电机角度控制器主类
        
        参数:
        - motor_config: 电机配置字典
        - encoder_config: 编码器配置字典
        - pid_config: PID配置字典
        """
        # 初始化硬件模块
        self.motor = MotorDriver(**motor_config)
        self.encoder = EncoderReader(**encoder_config)
        
        # 初始化PID控制器
        self.pid = PIDController(**pid_config)
        self.tuner = PIDTuner(self.pid)
        
        # 控制状态
        self.is_running = False
        self.current_mode = "IDLE"  # IDLE, MANUAL, AUTO
        
        # 控制目标
        self.target_angle = 0.0
        
        # 性能监控
        self.last_update_time = utime.ticks_ms()
        self.control_loop_time = 0.01  # 10ms控制周期
        
        print("电机角度控制器初始化完成")
    
    def set_target_angle(self, angle):
        """设置目标角度"""
        self.target_angle = angle
        self.pid.set_setpoint(angle)
        print(f"目标角度设置为: {angle}°")
    
    def start_control(self):
        """启动控制循环"""
        if self.is_running:
            print("控制已在运行中")
            return
        
        self.is_running = True
        self.current_mode = "AUTO"
        print("启动自动控制模式")
    
    def stop_control(self):
        """停止控制循环"""
        self.is_running = False
        self.current_mode = "IDLE"
        self.motor.stop()
        print("停止控制，电机已停止")
    
    def manual_control(self, speed):
        """手动控制模式"""
        self.current_mode = "MANUAL"
        self.motor.set_speed(speed)
        print(f"手动控制模式，速度: {speed}%")
    
    def update(self):
        """主控制循环更新"""
        if not self.is_running or self.current_mode != "AUTO":
            return
        
        # 检查控制周期
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, self.last_update_time) < int(self.control_loop_time * 1000):
            return
        
        # 获取当前角度
        current_angle = self.encoder.get_angle()
        
        # 更新PID控制器
        control_output = self.pid.update(current_angle)
        
        # 应用控制输出
        self.motor.set_speed(control_output)
        
        # 更新时间
        self.last_update_time = current_time
        
        # 打印状态 (可选)
        if utime.ticks_diff(current_time, self.last_update_time) % 1000 == 0:  # 每秒打印一次
            self.print_status()
    
    def print_status(self):
        """打印当前状态"""
        current_angle = self.encoder.get_angle()
        error = self.pid.error
        output = self.pid.output
        
        print(f"模式:{self.current_mode} | "
              f"目标:{self.target_angle:6.1f}° | "
              f"当前:{current_angle:6.1f}° | "
              f"误差:{error:6.1f}° | "
              f"输出:{output:6.1f}%")
    
    def get_position_info(self):
        """获取位置信息"""
        return {
            'target_angle': self.target_angle,
            'current_angle': self.encoder.get_angle(),
            'error': self.pid.error,
            'output': self.pid.output,
            'mode': self.current_mode,
            'rpm': self.encoder.get_speed_rpm()
        }
    
    def calibrate(self):
        """校准编码器"""
        print("开始编码器校准...")
        self.encoder.reset()
        print("校准完成，当前位置设为0°")
    
    def auto_tune(self, step_size=90.0, duration=5.0):
        """自动调参"""
        if self.is_running:
            self.stop_control()
        
        print("开始自动调参...")
        data = self.tuner.auto_tune_step_response(self.motor, self.encoder, step_size, duration)
        return data


def main():
    """主程序入口"""
    
    # 打印系统配置信息
    print_system_info()
    
    # 获取优化的系统配置 (默认使用平衡配置)
    system_config = get_system_config('balanced')
    
    motor_config = system_config['motor']
    encoder_config = system_config['encoder'] 
    pid_config = system_config['pid']
    
    # 创建控制器
    controller = MotorAngleController(motor_config, encoder_config, pid_config)
    
    print(f"
使用PID配置: {pid_config['description']}")
    print(f"参数: Kp={pid_config['kp']}, Ki={pid_config['ki']}, Kd={pid_config['kd']}")
    
    # 校准
    controller.calibrate()
    
    print("\n=== 电机角度控制演示程序 ===")
    print("命令说明:")
    print("1 - 转到 90°")
    print("2 - 转到 180°") 
    print("3 - 转到 270°")
    print("4 - 转到 360° (一圈)")
    print("0 - 停止控制")
    print("c - 校准编码器")
    print("t - 自动调参")
    print("m - 手动控制测试")
    print("q - 退出程序")
    
    try:
        while True:
            # 更新控制循环
            controller.update()
            
            # 简单的命令接口 (在实际应用中可以使用串口或Web界面)
            # 这里用定时器模拟不同阶段的控制目标
            
            # 演示序列
            controller.start_control()
            
            # 阶段1: 转到90度
            print("\n阶段1: 转到90度")
            controller.set_target_angle(90.0)
            
            # 等待到达目标 (误差小于2度)
            for i in range(500):  # 5秒超时
                controller.update()
                if abs(controller.pid.error) < 2.0:
                    print("到达目标!")
                    break
                utime.sleep(0.01)
            
            utime.sleep(1)
            
            # 阶段2: 转到180度
            print("\n阶段2: 转到180度")
            controller.set_target_angle(180.0)
            
            for i in range(500):
                controller.update()
                if abs(controller.pid.error) < 2.0:
                    print("到达目标!")
                    break
                utime.sleep(0.01)
            
            utime.sleep(1)
            
            # 阶段3: 转到270度
            print("\n阶段3: 转到270度")
            controller.set_target_angle(270.0)
            
            for i in range(500):
                controller.update()
                if abs(controller.pid.error) < 2.0:
                    print("到达目标!")
                    break
                utime.sleep(0.01)
            
            utime.sleep(1)
            
            # 阶段4: 回到0度
            print("\n阶段4: 回到0度")
            controller.set_target_angle(0.0)
            
            for i in range(500):
                controller.update()
                if abs(controller.pid.error) < 2.0:
                    print("到达目标!")
                    break
                utime.sleep(0.01)
            
            print("\n演示完成! 5秒后重新开始...")
            controller.stop_control()
            utime.sleep(5)
            
    except KeyboardInterrupt:
        print("\n用户中断")
        controller.stop_control()
    except Exception as e:
        print(f"\n程序错误: {e}")
        controller.stop_control()


if __name__ == "__main__":
    main()