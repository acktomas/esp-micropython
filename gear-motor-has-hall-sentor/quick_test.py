"""
快速测试脚本
适配你的12V 333RPM 30:1减速电机
包含电机基本测试和PID控制演示
"""

import utime
from motor_driver import MotorDriver
from encoder_reader import EncoderReader
from pid_controller import PIDController
from config import get_system_config, print_system_info

def test_motor_basics():
    """测试电机基础功能"""
    print("\n=== 电机基础功能测试 ===")
    
    # 获取配置
    config = get_system_config('balanced')
    motor = MotorDriver(**config['motor'])
    
    print("1. 测试正转 (30% 速度)")
    motor.forward(30)
    utime.sleep(2)
    
    print("2. 测试反转 (30% 速度)")
    motor.backward(30)
    utime.sleep(2)
    
    print("3. 测试变速")
    for speed in [20, 40, 60, 80]:
        print(f"   速度: {speed}%")
        motor.forward(speed)
        utime.sleep(1)
    
    print("4. 测试停止")
    motor.stop()
    
    print("电机基础测试完成")
    return motor

def test_encoder():
    """测试编码器"""
    print("\n=== 编码器测试 ===")
    
    config = get_system_config('balanced')
    encoder = EncoderReader(**config['encoder'])
    
    encoder.reset()
    print("请手动旋转电机轴，观察编码器读数...")
    print("按Ctrl+C停止测试")
    
    try:
        for i in range(100):  # 测试10秒
            if i % 10 == 0:  # 每秒打印一次
                count = encoder.get_count()
                angle = encoder.get_angle()
                rpm = encoder.get_speed_rpm()
                
                print(f"时间:{i:2d}s | 计数:{count:4d} | 角度:{angle:5.1f}° | 速度:{rpm:4.1f}RPM")
            
            utime.sleep(0.1)
    except KeyboardInterrupt:
        print("编码器测试停止")
    
    print(f"最终位置: {encoder.get_angle():.1f}°")
    return encoder

def test_pid_control():
    """测试PID控制"""
    print("\n=== PID控制测试 ===")
    
    config = get_system_config('balanced')
    
    motor = MotorDriver(**config['motor'])
    encoder = EncoderReader(**config['encoder'])
    pid = PIDController(**config['pid'])
    
    print(f"PID参数: Kp={pid.kp}, Ki={pid.ki}, Kd={pid.kd}")
    
    # 测试多个角度
    test_angles = [90, 180, 270, 0]  # 测试角度
    
    for target_angle in test_angles:
        print(f"\n--- 测试目标角度: {target_angle}° ---")
        
        # 设置目标
        pid.set_setpoint(target_angle)
        encoder.reset()
        pid.reset()
        
        start_time = utime.ticks_ms()
        max_error = 0
        
        # 运行5秒或到达目标
        for i in range(500):  # 5秒
            current_angle = encoder.get_angle()
            control_output = pid.update(current_angle)
            
            # 应用控制
            motor.set_speed(control_output)
            
            # 记录最大误差
            if abs(pid.error) > max_error:
                max_error = abs(pid.error)
            
            # 每秒打印状态
            if i % 100 == 0:
                print(f"时间:{i//100}s | 目标:{target_angle:5.1f}° | 当前:{current_angle:5.1f}° | "
                      f"误差:{pid.error:5.1f}° | 输出:{control_output:5.1f}%")
            
            # 检查是否到达目标
            if abs(pid.error) < 2.0 and i > 50:
                elapsed_time = utime.ticks_diff(utime.ticks_ms(), start_time) / 1000.0
                print(f"✓ 到达目标! 用时: {elapsed_time:.1f}s")
                break
            
            utime.sleep(0.01)
        
        else:  # 5秒超时
            print(f"✗ 超时，未到达目标")
        
        # 最终状态
        print(f"最终角度: {encoder.get_angle():.1f}°")
        print(f"最大误差: {max_error:.1f}°")
        
        utime.sleep(1)  # 间隔1秒
    
    motor.stop()
    print("PID控制测试完成")

def calibrate_encoder():
    """编码器校准"""
    print("\n=== 编码器校准 ===")
    
    config = get_system_config('balanced')
    encoder = EncoderReader(**config['encoder'])
    
    print("校准前位置: {:.1f}°".format(encoder.get_angle()))
    encoder.reset()
    print("校准完成，当前位置设为 0.0°")
    
    # 测试分辨率
    print("请缓慢旋转电机一圈...")
    start_count = encoder.get_count()
    
    try:
        for i in range(200):  # 20秒
            current_count = encoder.get_count()
            angle = encoder.get_angle()
            
            print(f"计数: {current_count} | 角度: {angle:.1f}° | "
                  f"理论圈数: {current_count/config['encoder']['ppr']:.2f}")
            
            if abs(current_count - start_count) >= config['encoder']['ppr']:
                print(f"✓ 检测到一圈! 实际脉冲数: {abs(current_count - start_count)}")
                break
            
            utime.sleep(0.1)
    except KeyboardInterrupt:
        pass

def main():
    """主测试程序"""
    print("=== 12V减速电机快速测试 ===")
    print("电机规格: 12V, 333RPM, 30:1减速, 11霍尔脉冲")
    
    # 打印系统信息
    print_system_info()
    
    print("\n请选择测试项目:")
    print("1 - 电机基础测试")
    print("2 - 编码器测试")
    print("3 - PID控制测试") 
    print("4 - 编码器校准")
    print("5 - 完整测试流程")
    
    try:
        choice = input("请输入选择 (1-5): ").strip()
        
        if choice == '1':
            test_motor_basics()
        elif choice == '2':
            test_encoder()
        elif choice == '3':
            test_pid_control()
        elif choice == '4':
            calibrate_encoder()
        elif choice == '5':
            print("\n开始完整测试流程...")
            
            # 步骤1: 电机测试
            test_motor_basics()
            utime.sleep(2)
            
            # 步骤2: 编码器测试
            test_encoder()
            utime.sleep(2)
            
            # 步骤3: 编码器校准
            calibrate_encoder()
            utime.sleep(2)
            
            # 步骤4: PID控制测试
            test_pid_control()
            
            print("\n✓ 完整测试流程完成!")
        else:
            print("无效选择，运行PID控制测试")
            test_pid_control()
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
    
    print("\n测试结束")

if __name__ == "__main__":
    main()