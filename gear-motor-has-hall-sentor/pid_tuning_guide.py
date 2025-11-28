"""
PID调参向导
专门针对12V 333RPM 30:1减速电机的PID调参指导
提供从零开始的调参步骤和实时反馈
"""

import utime
from motor_driver import MotorDriver
from encoder_reader import EncoderReader
from pid_controller import PIDController
from config import get_system_config, print_system_info

class PIDTuningWizard:
    def __init__(self):
        """初始化调参向导"""
        config = get_system_config('balanced')
        
        self.motor = MotorDriver(**config['motor'])
        self.encoder = EncoderReader(**config['encoder'])
        
        # 初始PID参数 (从保守值开始)
        self.kp = 0.5
        self.ki = 0.0
        self.kd = 0.0
        
        print("PID调参向导初始化完成")
        print("电机规格: 12V, 333RPM, 30:1减速")
    
    def step_test(self, kp, ki, kd, step_angle=90.0, test_time=3.0):
        """
        执行阶跃响应测试
        
        返回测试结果字典
        """
        # 创建PID控制器
        pid = PIDController(kp=kp, ki=ki, kd=kd, setpoint=step_angle)
        
        # 重置编码器和PID
        self.encoder.reset()
        pid.reset()
        
        # 数据记录
        start_time = utime.ticks_ms()
        data = []
        max_angle = 0
        min_angle = 0
        steady_state_errors = []
        oscillation_count = 0
        last_error_sign = 0
        
        print(f"测试参数: Kp={kp}, Ki={ki}, Kd={kd}")
        print(f"目标角度: {step_angle}°")
        
        # 运行测试
        for i in range(int(test_time * 100)):  # 10ms间隔
            current_angle = self.encoder.get_angle()
            control_output = pid.update(current_angle)
            
            # 应用控制输出 (限制范围)
            control_output = max(-80, min(80, control_output))
            self.motor.set_speed(control_output)
            
            # 记录数据
            current_time = (utime.ticks_diff(utime.ticks_ms(), start_time) / 1000.0)
            data.append({
                'time': current_time,
                'angle': current_angle,
                'error': pid.error,
                'output': control_output
            })
            
            # 统计性能指标
            if current_angle > max_angle:
                max_angle = current_angle
            if current_angle < min_angle:
                min_angle = current_angle
            
            # 检测振荡
            current_error_sign = 1 if pid.error > 0 else -1
            if last_error_sign != 0 and current_error_sign != last_error_sign:
                oscillation_count += 1
            last_error_sign = current_error_sign
            
            # 记录稳态误差 (最后1秒)
            if current_time > test_time - 1.0:
                steady_state_errors.append(abs(pid.error))
            
            # 每200ms打印一次进度
            if i % 20 == 0:
                print(f"  时间:{current_time:4.1f}s | 角度:{current_angle:6.1f}° | "
                      f"误差:{pid.error:6.1f}° | 输出:{control_output:6.1f}%")
            
            utime.sleep(0.01)
        
        # 停止电机
        self.motor.stop()
        
        # 计算性能指标
        results = {
            'kp': kp, 'ki': ki, 'kd': kd,
            'max_angle': max_angle,
            'min_angle': min_angle,
            'overshoot': ((max_angle - step_angle) / step_angle * 100) if max_angle > step_angle else 0,
            'undershoot': ((step_angle - min_angle) / step_angle * 100) if min_angle < 0 else 0,
            'final_error': abs(data[-1]['error']) if data else 0,
            'steady_state_error': sum(steady_state_errors) / len(steady_state_errors) if steady_state_errors else 0,
            'oscillation_count': oscillation_count,
            'rise_time': self._calculate_rise_time(data, step_angle),
            'settling_time': self._calculate_settling_time(data, step_angle),
            'data': data
        }
        
        return results
    
    def _calculate_rise_time(self, data, target):
        """计算上升时间 (10%到90%)"""
        if not data:
            return None
        
        ten_percent = target * 0.1
        ninety_percent = target * 0.9
        
        rise_start_time = None
        for point in data:
            if point['angle'] >= ten_percent:
                rise_start_time = point['time']
                break
        
        for point in data:
            if point['angle'] >= ninety_percent:
                return point['time'] - rise_start_time if rise_start_time else None
        
        return None
    
    def _calculate_settling_time(self, data, target, tolerance=2.0):
        """计算稳定时间 (进入±2%误差范围)"""
        if not data:
            return None
        
        tolerance_band = target * 0.02  # 2%误差带
        
        for i in range(len(data)-1, 0, -1):
            if abs(data[i]['angle'] - target) > tolerance_band:
                return data[i+1]['time'] if i+1 < len(data) else data[-1]['time']
        
        return data[-1]['time']
    
    def print_results(self, results):
        """打印测试结果"""
        print("\n=== 测试结果 ===")
        print(f"超调量: {results['overshoot']:.1f}%")
        print(f"下冲量: {results['undershoot']:.1f}%")
        print(f"最终误差: {results['final_error']:.2f}°")
        print(f"稳态误差: {results['steady_state_error']:.2f}°")
        print(f"振荡次数: {results['oscillation_count']}")
        print(f"上升时间: {results['rise_time']:.2f}s" if results['rise_time'] else "上升时间: 无法计算")
        print(f"稳定时间: {results['settling_time']:.2f}s" if results['settling_time'] else "稳定时间: 无法计算")
        
        # 性能评估
        print("\n=== 性能评估 ===")
        score = 0
        max_score = 100
        
        # 超调量评分 (理想 < 20%)
        if results['overshoot'] < 10:
            score += 25
        elif results['overshoot'] < 20:
            score += 20
        elif results['overshoot'] < 30:
            score += 10
        
        # 稳态误差评分 (理想 < 2°)
        if results['steady_state_error'] < 1:
            score += 25
        elif results['steady_state_error'] < 2:
            score += 20
        elif results['steady_state_error'] < 5:
            score += 10
        
        # 振荡评分 (理想 < 2次)
        if results['oscillation_count'] <= 1:
            score += 25
        elif results['oscillation_count'] <= 2:
            score += 20
        elif results['oscillation_count'] <= 4:
            score += 10
        
        # 上升时间评分 (理想 < 2s)
        if results['rise_time'] and results['rise_time'] < 1:
            score += 25
        elif results['rise_time'] and results['rise_time'] < 2:
            score += 20
        elif results['rise_time'] and results['rise_time'] < 3:
            score += 10
        
        print(f"总体评分: {score}/{max_score}")
        
        if score >= 80:
            print("✓ 优秀 - PID参数调节很好!")
        elif score >= 60:
            print("○ 良好 - PID参数基本满足要求")
        elif score >= 40:
            print("△ 一般 - 需要进一步调参")
        else:
            print("✗ 较差 - 需要重新调参")
        
        return score
    
    def suggest_improvements(self, results):
        """根据结果提出改进建议"""
        print("\n=== 改进建议 ===")
        
        suggestions = []
        
        if results['overshoot'] > 25:
            suggestions.append("超调过大，建议减小Kp或增加Kd")
        elif results['overshoot'] < 5 and results['rise_time'] and results['rise_time'] > 2:
            suggestions.append("响应较慢，建议增加Kp")
        
        if results['steady_state_error'] > 3:
            suggestions.append("稳态误差较大，建议增加Ki")
        elif results['steady_state_error'] > 1:
            suggestions.append("可以适当增加Ki来提高精度")
        
        if results['oscillation_count'] > 3:
            suggestions.append("振荡较多，建议增加Kd提供阻尼")
        
        if results['rise_time'] and results['rise_time'] > 3:
            suggestions.append("响应太慢，建议增加Kp或增加输出限幅")
        
        if not suggestions:
            suggestions.append("参数调节良好，可以进行微调优化")
        
        for suggestion in suggestions:
            print(f"• {suggestion}")
        
        return suggestions
    
    def auto_tuning(self):
        """自动调参流程"""
        print("\n=== 自动调参流程 ===")
        print("针对12V减速电机的优化调参")
        
        best_score = 0
        best_params = {'kp': 0.5, 'ki': 0.0, 'kd': 0.0}
        
        # 第1步: 找到P的临界值
        print("\n第1步: 寻找P临界值...")
        kp_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        critical_kp = None
        
        for kp in kp_values:
            print(f"\n测试 Kp={kp}...")
            results = self.step_test(kp, 0, 0, 90.0, 2.0)
            
            if results['oscillation_count'] >= 3:
                critical_kp = kp
                print(f"找到临界点: Kp={kp}")
                break
        
        if not critical_kp:
            critical_kp = 2.5  # 默认值
        
        # 第2步: 计算初始PID参数 (Ziegler-Nichols方法)
        print(f"\n第2步: 计算初始PID参数 (基于Ku={critical_kp})")
        
        # 经典Ziegler-Nichols公式
        initial_kp = 0.6 * critical_kp
        initial_ki = 2 * initial_kp / 1.0  # 假设振荡周期为1s
        initial_kd = initial_kp * 1.0 / 8
        
        print(f"计算得出: Kp={initial_kp:.2f}, Ki={initial_ki:.2f}, Kd={initial_kd:.2f}")
        
        # 第3步: 微调优化
        print("\n第3步: 微调优化...")
        
        tuning_variants = [
            {'kp': initial_kp, 'ki': initial_ki, 'kd': initial_kd, 'name': 'ZN原始'},
            {'kp': initial_kp * 0.8, 'ki': initial_ki * 0.8, 'kd': initial_kd * 1.2, 'name': '保守调优'},
            {'kp': initial_kp * 1.2, 'ki': initial_ki * 1.2, 'kd': initial_kd * 0.8, 'name': '激进调优'},
            {'kp': 2.0, 'ki': 0.4, 'kd': 0.12, 'name': '经验值'},  # 针对该电机的经验值
        ]
        
        for variant in tuning_variants:
            print(f"\n测试 {variant['name']} 参数...")
            results = self.step_test(variant['kp'], variant['ki'], variant['kd'], 90.0, 4.0)
            score = self.print_results(results)
            
            if score > best_score:
                best_score = score
                best_params = {'kp': variant['kp'], 'ki': variant['ki'], 'kd': variant['kd']}
        
        # 第4步: 最终测试和推荐
        print(f"\n=== 自动调参完成 ===")
        print(f"最佳参数: Kp={best_params['kp']:.2f}, Ki={best_params['ki']:.2f}, Kd={best_params['kd']:.2f}")
        print(f"最佳评分: {best_score}/100")
        
        print("\n最终验证测试...")
        final_results = self.step_test(best_params['kp'], best_params['ki'], best_params['kd'], 180.0, 5.0)
        self.print_results(final_results)
        self.suggest_improvements(final_results)
        
        return best_params

def main():
    """主程序"""
    print("=== PID调参向导 ===")
    print("专为12V 333RPM 30:1减速电机优化")
    
    print_system_info()
    
    wizard = PIDTuningWizard()
    
    print("\n请选择调参模式:")
    print("1 - 自动调参 (推荐)")
    print("2 - 手动调参引导")
    print("3 - 快速验证参数")
    
    try:
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == '1':
            print("\n开始自动调参...")
            best_params = wizard.auto_tuning()
            print(f"\n推荐的PID参数: {best_params}")
            
        elif choice == '2':
            print("\n手动调参引导...")
            print("请输入要测试的PID参数:")
            
            kp = float(input("Kp (建议0.5-3.0): ") or "1.5")
            ki = float(input("Ki (建议0.0-1.0): ") or "0.2") 
            kd = float(input("Kd (建议0.0-0.3): ") or "0.1")
            
            results = wizard.step_test(kp, ki, kd, 90.0, 4.0)
            wizard.print_results(results)
            wizard.suggest_improvements(results)
            
        elif choice == '3':
            print("\n快速验证预设参数...")
            
            test_configs = [
                {'kp': 1.5, 'ki': 0.2, 'kd': 0.08, 'name': '保守'},
                {'kp': 2.0, 'ki': 0.4, 'kd': 0.12, 'name': '平衡'},
                {'kp': 2.5, 'ki': 0.6, 'kd': 0.18, 'name': '激进'},
            ]
            
            for config in test_configs:
                print(f"\n测试 {config['name']} 配置...")
                results = wizard.step_test(config['kp'], config['ki'], config['kd'], 90.0, 3.0)
                wizard.print_results(results)
                
        else:
            print("无效选择，使用自动调参")
            wizard.auto_tuning()
            
    except KeyboardInterrupt:
        print("\n调参被用户中断")
        wizard.motor.stop()
    except Exception as e:
        print(f"\n调参过程出错: {e}")
        wizard.motor.stop()
    
    print("\n调参结束")

if __name__ == "__main__":
    main()