"""
电机系统配置文件
适配12V 333RPM减速电机
- 电压: 12V
- 空载转速: 333RPM  
- 额定转速: 250RPM
- 减速比: 30:1
- 霍尔脉冲: 11个/转
"""

# 电机基本参数
MOTOR_PARAMS = {
    'voltage': 12,              # 电压 (V)
    'no_load_rpm': 333,         # 空载转速 (RPM)
    'rated_rpm': 250,           # 额定转速 (RPM)
    'gear_ratio': 30,           # 减速比
    'hall_pulses_per_rev': 11,  # 电机转一圈的霍尔脉冲数
    'encoder_ppr': 11,          # 编码器每转脉冲数
}

# 计算输出轴参数
# 输出轴转速 = 电机转速 / 减速比
OUTPUT_SHAFT_PARAMS = {
    'max_no_load_rpm': MOTOR_PARAMS['no_load_rpm'] / MOTOR_PARAMS['gear_ratio'],  # 约11.1 RPM
    'rated_rpm': MOTOR_PARAMS['rated_rpm'] / MOTOR_PARAMS['gear_ratio'],            # 约8.3 RPM
    'pulses_per_rev': MOTOR_PARAMS['hall_pulses_per_rev'] * MOTOR_PARAMS['gear_ratio'],  # 11*30=330
    'degrees_per_pulse': 360 / (MOTOR_PARAMS['hall_pulses_per_rev'] * MOTOR_PARAMS['gear_ratio']),  # 约1.09度
}

# 硬件接线配置
HARDWARE_CONFIG = {
    # L298N电机驱动器连接
    'motor': {
        'pwm_pin': 25,      # PWM控制引脚 (必须支持PWM)
        'in1_pin': 26,      # 方向控制引脚1
        'in2_pin': 27,      # 方向控制引脚2  
        'freq': 1000,       # PWM频率 (Hz)
        'pwm_resolution': 16,  # PWM分辨率 (16位)
    },
    
    # 霍尔传感器连接
    'encoder': {
        'hall_a_pin': 4,    # 霍尔A相信号
        'hall_b_pin': 5,    # 霍尔B相信号
        'ppr': OUTPUT_SHAFT_PARAMS['pulses_per_rev'],  # 实际输出轴每转脉冲数
        'gear_ratio': MOTOR_PARAMS['gear_ratio'],      # 减速比
        'pull_up': True,    # 是否启用上拉电阻
    },
    
    # 电源配置
    'power': {
        'motor_voltage': 12,      # 电机工作电压
        'logic_voltage': 3.3,    # ESP32逻辑电压
        'max_current': 2.0,       # 最大电流 (A)
    }
}

# PID控制参数 - 针对你的电机优化
PID_CONFIGS = {
    # 保守参数 (适合初学者)
    'conservative': {
        'kp': 1.5,
        'ki': 0.2, 
        'kd': 0.08,
        'output_min': -60.0,
        'output_max': 60.0,
        'sample_time': 0.01,
        'description': '稳定控制，超调小'
    },
    
    # 平衡参数 (推荐使用)
    'balanced': {
        'kp': 2.0,
        'ki': 0.4,
        'kd': 0.12,
        'output_min': -75.0, 
        'output_max': 75.0,
        'sample_time': 0.01,
        'description': '快速响应，稳定性好'
    },
    
    # 激进参数 (追求速度)
    'aggressive': {
        'kp': 3.0,
        'ki': 0.6,
        'kd': 0.18,
        'output_min': -85.0,
        'output_max': 85.0, 
        'sample_time': 0.01,
        'description': '快速响应，可能超调'
    },
    
    # 精确定位参数
    'precision': {
        'kp': 2.5,
        'ki': 0.8,
        'kd': 0.15,
        'output_min': -70.0,
        'output_max': 70.0,
        'sample_time': 0.005,    # 更快的采样
        'description': '高精度定位，消除稳态误差'
    }
}

# 控制系统参数
CONTROL_CONFIG = {
    'control_loop_freq': 100,    # 控制循环频率 (Hz)
    'angle_tolerance': 2.0,      # 角度容差 (度)
    'speed_tolerance': 5.0,      # 速度容差 (RPM)
    'timeout_ms': 10000,         # 超时时间 (毫秒)
}

# 调试和监控参数
DEBUG_CONFIG = {
    'print_interval': 1000,       # 打印间隔 (毫秒)
    'log_data': False,           # 是否记录数据
    'save_to_file': False,       # 是否保存到文件
}

# 获取指定PID配置
def get_pid_config(config_name='balanced'):
    """获取指定的PID配置"""
    return PID_CONFIGS.get(config_name, PID_CONFIGS['balanced'])

# 获取完整的系统配置
def get_system_config(pid_config_name='balanced'):
    """获取完整的系统配置"""
    config = {
        'motor': HARDWARE_CONFIG['motor'],
        'encoder': HARDWARE_CONFIG['encoder'],
        'pid': get_pid_config(pid_config_name),
        'control': CONTROL_CONFIG,
        'debug': DEBUG_CONFIG,
        'motor_params': MOTOR_PARAMS,
        'output_shaft': OUTPUT_SHAFT_PARAMS
    }
    return config

# 打印系统信息
def print_system_info():
    """打印系统配置信息"""
    print("=== 电机系统配置信息 ===")
    print(f"电机参数:")
    print(f"  电压: {MOTOR_PARAMS['voltage']}V")
    print(f"  空载转速: {MOTOR_PARAMS['no_load_rpm']} RPM")
    print(f"  额定转速: {MOTOR_PARAMS['rated_rpm']} RPM") 
    print(f"  减速比: {MOTOR_PARAMS['gear_ratio']}:1")
    print(f"  霍尔脉冲: {MOTOR_PARAMS['hall_pulses_per_rev']} PPR")
    print()
    
    print(f"输出轴参数:")
    print(f"  最大转速: {OUTPUT_SHAFT_PARAMS['max_no_load_rpm']:.1f} RPM")
    print(f"  额定转速: {OUTPUT_SHAFT_PARAMS['rated_rpm']:.1f} RPM")
    print(f"  脉冲/转: {OUTPUT_SHAFT_PARAMS['pulses_per_rev']}")
    print(f"  分辨率: {OUTPUT_SHAFT_PARAMS['degrees_per_pulse']:.3f}°/脉冲")
    print()
    
    print(f"PID配置:")
    for name, config in PID_CONFIGS.items():
        print(f"  {name}: Kp={config['kp']}, Ki={config['ki']}, Kd={config['kd']}")
        print(f"    说明: {config['description']}")
    print()
    
    print(f"硬件接线:")
    print(f"  电机: PWM={HARDWARE_CONFIG['motor']['pwm_pin']}, IN1={HARDWARE_CONFIG['motor']['in1_pin']}, IN2={HARDWARE_CONFIG['motor']['in2_pin']}")
    print(f"  编码器: A={HARDWARE_CONFIG['encoder']['hall_a_pin']}, B={HARDWARE_CONFIG['encoder']['hall_b_pin']}")

# 使用示例
if __name__ == "__main__":
    # 打印系统信息
    print_system_info()
    
    # 获取平衡配置
    config = get_system_config('balanced')
    print(f"\n获取的PID配置: {config['pid']}")