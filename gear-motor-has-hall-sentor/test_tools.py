"""
测试和调参工具包
包含各种测试程序和调试工具
帮助学习和理解PID控制原理
"""

import utime
import json
from motor_driver import MotorDriver
from encoder_reader import EncoderReader
from pid_controller import PIDController, PIDTuner
from config import get_system_config, print_system_info, MOTOR_PARAMS, OUTPUT_SHAFT_PARAMS

class SystemTester:
    def __init__(self, motor_config, encoder_config):
        """系统测试器"""
        self.motor = MotorDriver(**motor_config)
        self.encoder = EncoderReader(**encoder_config)
        print("系统测试器初始化完成")
    
    def test_motor_basic(self):
        """电机基础功能测试"""
        print("\n=== 电机基础功能测试 ===")
        
        # 测试正转
        print("测试正转...")
        self.motor.forward(30)  # 30%速度
        utime.sleep(2)
        
        print("停止...")
        self.motor.stop()
        utime.sleep(1)
        
        # 测试反转
        print("测试反转...")
        self.motor.backward(30)  # 30%速度
        utime.sleep(2)
        
        print("停止...")
        self.motor.stop()
        utime.sleep(1)
        
        # 测试变速
        print("测试变速...")
        for speed in [20, 40, 60, 80, 100]:
            print(f"速度: {speed}%")
            self.motor.forward(speed)
            utime.sleep(0.5)
        
        self.motor.stop()
        print("电机基础测试完成")
    
    def test_encoder_basic(self):
        """编码器基础功能测试"""
        print("\n=== 编码器基础功能测试 ===")
        print("请手动旋转电机轴...")
        
        self.encoder.reset()
        start_time = utime.ticks_ms()
        
        for i in range(100):  # 测试10秒
            if i % 10 == 0:  # 每秒打印一次
                count = self.encoder.get_count()
                angle = self.encoder.get_angle()
                revs = self.encoder.get_revolutions()
                rpm = self.encoder.get_speed_rpm()
                
                print(f"时间:{i}s | 计数:{count} | 角度:{angle:.1f}° | "
                      f"转数:{revs:.2f} | 速度:{rpm:.1f}RPM")
            
            utime.sleep(0.1)
        
        print("编码器基础测试完成")
    
    def test_system_response(self):
        """系统响应测试"""
        print("\n=== 系统响应测试 ===")
        
        self.encoder.reset()
        
        # 测试开环响应
        print("测试开环响应...")
        self.motor.forward(50)
        
        start_time = utime.ticks_ms()
        data = []
        
        for i in range(200):  # 20秒
            current_time = utime.ticks_diff(utime.ticks_ms(), start_time) / 1000.0
            angle = self.encoder.get_angle()
            rpm = self.encoder.get_speed_rpm()
            
            data.append({
                'time': current_time,
                'angle': angle,
                'rpm': rpm
            })
            
            if i % 20 == 0:  # 每2秒打印一次
                print(f"时间:{current_time:4.1f}s | 角度:{angle:6.1f}° | 速度:{rpm:6.1f}RPM")
            
            utime.sleep(0.1)
        
        self.motor.stop()
        
        # 计算平均速度
        avg_rpm = sum(d['rpm'] for d in data[-50:]) / 50  # 最后5秒的平均速度
        print(f"平均速度: {avg_rpm:.1f}RPM")
        print("系统响应测试完成")


class PIDLearningTool:
    def __init__(self, motor_config, encoder_config):
        """PID学习工具"""
        self.motor = MotorDriver(**motor_config)
        self.encoder = EncoderReader(**encoder_config)
        print("PID学习工具初始化完成")
    
    def explain_pid_terms(self):
        """解释PID各参数的作用"""
        print("\n=== PID参数解释 ===")
        print("P (比例项):")
        print("  - 作用: 根据当前误差产生响应")
        print("  - 效果: P越大，响应越快，但可能产生振荡")
        print("  - 过小: 响应慢，跟踪效果差")
        print("  - 过大: 系统振荡，不稳定")
        print()
        
        print("I (积分项):")
        print("  - 作用: 累积历史误差，消除稳态误差")
        print("  - 效果: 消除系统静差，提高精度")
        print("  - 过小: 存在稳态误差")
        print("  - 过大: 产生积分饱和，系统振荡")
        print()
        
        print("D (微分项):")
        print("  - 作用: 预测未来误差趋势，提供阻尼")
        print("  - 效果: 减少超调，提高稳定性")
        print("  - 过小: 超调大，振荡多")
        print("  - 过大: 响应变慢，对噪声敏感")
    
    def demonstrate_p_control(self, kp_values=[0.5, 1.0, 2.0, 4.0]):
        """演示P控制器的作用"""
        print("\n=== P控制器演示 ===")
        
        for kp in kp_values:
            print(f"\n测试 Kp={kp}")
            
            pid = PIDController(kp=kp, ki=0.0, kd=0.0, setpoint=90.0)
            
            self.encoder.reset()
            pid.reset()
            
            start_time = utime.ticks_ms()
            max_angle = 0
            overshoot = 0
            steady_state_reached = False
            
            for i in range(500):  # 5秒测试
                current_angle = self.encoder.get_angle()
                control_output = pid.update(current_angle)
                
                # 限制输出范围
                control_output = max(-80, min(80, control_output))
                self.motor.set_speed(control_output)
                
                # 记录最大角度
                if current_angle > max_angle:
                    max_angle = current_angle
                
                # 检查稳态
                if i > 100 and abs(pid.error) < 2.0:
                    steady_state_reached = True
                    steady_time = utime.ticks_diff(utime.ticks_ms(), start_time) / 1000.0
                
                utime.sleep(0.01)
            
            self.motor.stop()
            
            # 计算超调
            overshoot = ((max_angle - 90.0) / 90.0) * 100 if max_angle > 90 else 0
            
            print(f"  最大角度: {max_angle:.1f}°")
            print(f"  超调量: {overshoot:.1f}%")
            print(f"  稳态误差: {abs(pid.error):.1f}°")
            print(f"  稳态到达: {'是' if steady_state_reached else '否'}")
    
    def demonstrate_i_control(self, ki_values=[0.1, 0.5, 1.0, 2.0]):
        """演示I控制器的作用"""
        print("\n=== I控制器演示 ===")
        
        for ki in ki_values:
            print(f"\n测试 Ki={ki} (固定 Kp=1.0)")
            
            pid = PIDController(kp=1.0, ki=ki, kd=0.0, setpoint=90.0)
            
            self.encoder.reset()
            pid.reset()
            
            # 测试稳态误差消除能力
            # 模拟一个有摩擦的系统，使用较小的P值
            test_time = 8000  # 8秒
            
            for i in range(test_time):
                current_angle = self.encoder.get_angle()
                
                # 添加模拟摩擦阻力
                if abs(pid.error) < 5 and ki > 0:
                    friction_compensation = ki * pid.integral * 0.1
                else:
                    friction_compensation = 0
                
                control_output = pid.update(current_angle) + friction_compensation
                control_output = max(-80, min(80, control_output))
                self.motor.set_speed(control_output)
                
                utime.sleep(0.01)
            
            self.motor.stop()
            
            print(f"  最终误差: {abs(pid.error):.2f}°")
            print(f"  积分值: {pid.integral:.2f}")
    
    def demonstrate_d_control(self, kd_values=[0.0, 0.1, 0.5, 1.0]):
        """演示D控制器的作用"""
        print("\n=== D控制器演示 ===")
        
        for kd in kd_values:
            print(f"\n测试 Kd={kd} (固定 Kp=2.0)")
            
            pid = PIDController(kp=2.0, ki=0.0, kd=kd, setpoint=90.0)
            
            self.encoder.reset()
            pid.reset()
            
            max_angle = 0
            overshoot = 0
            oscillation_count = 0
            last_error_sign = 0
            
            for i in range(300):  # 3秒测试
                current_angle = self.encoder.get_angle()
                control_output = pid.update(current_angle)
                control_output = max(-80, min(80, control_output))
                self.motor.set_speed(control_output)
                
                # 记录振荡
                current_error_sign = 1 if pid.error > 0 else -1
                if last_error_sign != 0 and current_error_sign != last_error_sign:
                    oscillation_count += 1
                last_error_sign = current_error_sign
                
                if current_angle > max_angle:
                    max_angle = current_angle
                
                utime.sleep(0.01)
            
            self.motor.stop()
            
            overshoot = ((max_angle - 90.0) / 90.0) * 100 if max_angle > 90 else 0
            
            print(f"  超调量: {overshoot:.1f}%")
            print(f"  振荡次数: {oscillation_count}")
            print(f"  阻尼效果: {'强' if oscillation_count < 2 else '弱'}")
    
    def interactive_tuning(self):
        """交互式调参"""
        print("\n=== 交互式PID调参 ===")
        print("使用方法:")
        print("- 输入 'kp value' 调整比例增益")
        print("- 输入 'ki value' 调整积分增益")
        print("- 输入 'kd value' 调整微分增益")
        print("- 输入 'test angle' 测试阶跃响应")
        print("- 输入 'quit' 退出")
        
        # 初始PID参数
        kp, ki, kd = 1.0, 0.1, 0.1
        pid = PIDController(kp=kp, ki=ki, kd=kd, setpoint=90.0)
        
        print(f"\n当前参数: Kp={kp}, Ki={ki}, Kd={kd}")
        
        # 模拟交互式调参 (在实际应用中可以使用串口输入)
        # 这里演示几个预设的调参步骤
        tuning_steps = [
            (1.0, 0.0, 0.0, "纯P控制"),
            (1.0, 0.1, 0.0, "加入I控制"),
            (1.0, 0.1, 0.1, "加入D控制"),
            (2.0, 0.2, 0.1, "增强P控制"),
            (3.0, 0.3, 0.2, "最终参数")
        ]
        
        for step_kp, step_ki, step_kd, description in tuning_steps:
            print(f"\n{description}: Kp={step_kp}, Ki={step_ki}, Kd={step_kd}")
            
            pid.set_tunings(step_kp, step_ki, step_kd)
            self.encoder.reset()
            pid.reset()
            
            # 阶跃响应测试
            start_time = utime.ticks_ms()
            data_points = []
            
            for i in range(500):  # 5秒测试
                current_angle = self.encoder.get_angle()
                control_output = pid.update(current_angle)
                control_output = max(-80, min(80, control_output))
                self.motor.set_speed(control_output)
                
                current_time = utime.ticks_diff(utime.ticks_ms(), start_time) / 1000.0
                data_points.append((current_time, current_angle, pid.error, control_output))
                
                utime.sleep(0.01)
            
            self.motor.stop()
            
            # 分析结果
            max_angle = max(point[1] for point in data_points)
            overshoot = ((max_angle - 90.0) / 90.0) * 100 if max_angle > 90 else 0
            final_error = abs(data_points[-1][2])
            
            print(f"  结果: 超调={overshoot:.1f}%, 稳态误差={final_error:.2f}°")


def main():
    """主测试程序"""
    # 打印系统信息
    print_system_info()
    
    # 获取系统配置
    system_config = get_system_config('balanced')
    motor_config = system_config['motor']
    encoder_config = system_config['encoder']
    
    # 创建测试工具
    system_tester = SystemTester(motor_config, encoder_config)
    learning_tool = PIDLearningTool(motor_config, encoder_config)
    
    print(f"
使用优化参数进行测试")
    print(f"电机规格: {MOTOR_PARAMS['voltage']}V, {MOTOR_PARAMS['rated_rpm']}RPM, {MOTOR_PARAMS['gear_ratio']}:1减速")
    print(f"输出轴: {OUTPUT_SHAFT_PARAMS['rated_rpm']:.1f}RPM, {OUTPUT_SHAFT_PARAMS['degrees_per_pulse']:.3f}°/脉冲")
    
    print("=== PID学习和测试工具 ===")
    print("选择测试项目:")
    print("1 - 电机基础测试")
    print("2 - 编码器基础测试") 
    print("3 - 系统响应测试")
    print("4 - PID参数学习")
    print("5 - P控制器演示")
    print("6 - I控制器演示")
    print("7 - D控制器演示")
    print("8 - 交互式调参演示")
    
    try:
        # 这里演示所有测试项目
        system_tester.test_motor_basic()
        utime.sleep(2)
        
        system_tester.test_encoder_basic()
        utime.sleep(2)
        
        system_tester.test_system_response()
        utime.sleep(2)
        
        learning_tool.explain_pid_terms()
        utime.sleep(2)
        
        learning_tool.demonstrate_p_control()
        utime.sleep(2)
        
        learning_tool.demonstrate_i_control()
        utime.sleep(2)
        
        learning_tool.demonstrate_d_control()
        utime.sleep(2)
        
        learning_tool.interactive_tuning()
        
        print("\n所有测试完成!")
        
    except KeyboardInterrupt:
        print("\n测试中断")
    except Exception as e:
        print(f"\n测试错误: {e}")


if __name__ == "__main__":
    main()