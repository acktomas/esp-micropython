"""
兼容性更强的 Servo 控制类（MicroPython，ESP32 系列）
特性：
- 角度 <-> 脉冲(us) 映射，支持自定义角度范围和反向
- 自动兼容多种 PWM 接口：duty_u16、duty_ns、duty（旧接口）
- attach/detach（释放 PWM 以节省资源）
- 校准、居中、扫动等常用方法
- 简单异常与安全停止处理
"""
from machine import Pin, PWM
import time


class Servo:
    def __init__(
        self,
        pin,
        freq: int = 50,
        min_us: int = 500,
        max_us: int = 2500,
        angle_min: int = 0,
        angle_max: int = 180,
        invert: bool = False,
        start_attached: bool = True,
    ):
        """
        pin: GPIO 编号或 machine.Pin 对象
        freq: PWM 频率（Hz），舵机通常 50Hz
        min_us/max_us: 分别对应 angle_min/angle_max 的脉冲宽度（微秒）
        angle_min/angle_max: 可设置不同的角度范围
        invert: True 则角度映射翻转（0<->180）
        start_attached: 是否在构造时立即 attach（创建 PWM）
        """
        if isinstance(pin, Pin):
            self._pin_obj = pin
        else:
            self._pin_obj = Pin(pin, Pin.OUT)
        self.freq = int(freq)
        self.min_us = int(min_us)
        self.max_us = int(max_us)
        self.angle_min = int(angle_min)
        self.angle_max = int(angle_max)
        self.invert = bool(invert)
        self._pwm = None
        self._period_us = 1_000_000 / self.freq
        self._attached = False

        if start_attached:
            self.attach(self._pin_obj)

    # --- attach / detach ---
    def attach(self, pin=None):
        """关联到一个引脚并启用 PWM（若已 attach，会先 deinit 再 attach）"""
        if pin is not None:
            if isinstance(pin, Pin):
                self._pin_obj = pin
            else:
                self._pin_obj = Pin(pin, Pin.OUT)
        if self._attached:
            self.deinit()
        # 兼容不同 port 的 PWM 构造签名：
        # 优先尝试直接传 freq；若抛 TypeError，则回退为先创建再设置 freq。
        try:
            self._pwm = PWM(self._pin_obj, freq=self.freq)
        except TypeError as e:
            # 构造签名不接受 freq，尝试回退方式
            try:
                self._pwm = PWM(self._pin_obj)
                # 有些实现没有 freq 方法，故用 hasattr 先检查
                if hasattr(self._pwm, "freq"):
                    self._pwm.freq(self.freq)
            except Exception as e2:
                # 回退也失败：抛出更清晰的信息，包含两个异常上下文以便调试
                raise RuntimeError("无法创建 PWM：尝试带 freq 和不带 freq 的构造均失败。 原始错误: {}, 回退错误: {}".format(e, e2))
        except Exception as e:
            # 非签名问题（如 pin 类型错误），直接向上抛出以便定位
            raise
        self._attached = True

    def deinit(self):
        """释放 PWM，舵机失去控制信号（可断电节能）"""
        if self._pwm:
            try:
                self._pwm.deinit()
            except Exception:
                pass
        self._pwm = None
        self._attached = False

    # --- 映射与写入 ---
    def _clip_angle(self, angle):
        a = float(angle)
        if a < self.angle_min:
            a = float(self.angle_min)
        if a > self.angle_max:
            a = float(self.angle_max)
        return a

    def _angle_to_pulse_us(self, angle):
        """将 angle 映射为脉冲宽度（us）"""
        a = self._clip_angle(angle)
        # 标准化到 0..1
        span_angle = self.angle_max - self.angle_min
        if span_angle == 0:
            frac = 0.0
        else:
            frac = (a - self.angle_min) / span_angle
        if self.invert:
            frac = 1.0 - frac
        span_us = self.max_us - self.min_us
        return int(self.min_us + frac * span_us)

    def _pulse_us_to_duty(self, pulse_us):
        """尝试多种方式返回 PWM 设置值：
           - 优先返回 (mode='u16', value)
           - 其次尝试 (mode='ns', value)
           - 最后返回 (mode='old', value) 对应 0..1023/1024
        """
        period_us = self._period_us
        period_ns = period_us * 1000  # 转换为纳秒

        duty_ns = int(pulse_us * 1000)
        if duty_ns < 0:
            duty_ns = 0
        if duty_ns > period_ns:
            duty_ns = period_ns

        # 以纳秒为基准计算占空比（避免 float 反复量化导致误差）
        duty_frac = (duty_ns / period_ns) if period_ns else 0.0

        # duty_u16 0..65535
        duty_u16 = int(duty_frac * 65535)
        if duty_u16 < 0:
            duty_u16 = 0
        if duty_u16 > 65535:
            duty_u16 = 65535

        # 推荐直接用 duty_frac 计算旧接口值，或用整数运算基于纳秒
        # 更准确：duty_old = int(duty_frac * 1023)
        # 更稳健（无浮点）：duty_old = int(duty_ns * 1023 // period_ns)
        duty_old = int(duty_frac * 1023)
        if duty_old < 0:
            duty_old = 0
        if duty_old > 1023:
            duty_old = 1023

        return ("u16", duty_u16, duty_ns, duty_old)

    def write_pulse_us(self, pulse_us):
        """直接设置脉冲宽度（微秒），会自动选择可用接口"""
        if not self._attached:
            self.attach()
        mode, duty_u16, duty_ns, duty_old = self._pulse_us_to_duty(pulse_us)
        # 优先尝试 duty_u16
        try:
            self._pwm.duty_u16(duty_u16)
            return
        except AttributeError:
            pass
        except Exception:
            # 如果报错（例如硬件不支持），继续尝试其他方式
            pass
        # 尝试 duty_ns（某些 port 支持）
        try:
            self._pwm.duty_ns(duty_ns)
            return
        except AttributeError:
            pass
        except Exception:
            pass
        # 旧接口 duty(0..1023)
        try:
            self._pwm.duty(duty_old)
            return
        except Exception:
            # 如果所有接口都失败，则抛出异常以便用户调试
            raise RuntimeError("无法设置 PWM 输出：此端口的 PWM 接口未知或不可用")

    def write_angle(self, angle):
        """将舵机移动到指定角度（自动 clip）"""
        pulse = self._angle_to_pulse_us(angle)
        self.write_pulse_us(pulse)

    # --- 便捷动作 ---
    def center(self):
        """移动到中位"""
        mid = (self.angle_min + self.angle_max) / 2
        self.write_angle(mid)

    def sweep(self, start=None, end=None, step=5, delay=0.02):
        """
        线性扫动：从 start 到 end。
        若 start/end 为 None，则使用 angle_min/angle_max。
        """
        if start is None:
            start = self.angle_min
        if end is None:
            end = self.angle_max
        start = int(start)
        end = int(end)
        step = abs(int(step)) or 1
        if start <= end:
            rng = range(start, end + 1, step)
        else:
            rng = range(start, end - 1, -step)
        for a in rng:
            self.write_angle(a)
            time.sleep(delay)

    def jog(self, delta, delay=0.2):
        """相对移动 delta 度并在结束后短暂停留"""
        # 读取当前角度未知，需应用端记录或传入。如果没有存储，就假设中位起始。
        # 为简单起见，这里不保存状态；建议上层应用自行保存当前位置。
        raise NotImplementedError("jog 需要保存当前位置，建议上层实现位置跟踪或使用 write_angle")

    def calibrate(self, min_us=None, max_us=None, angle_min=None, angle_max=None):
        """运行时更新校准参数"""
        if min_us is not None:
            self.min_us = int(min_us)
        if max_us is not None:
            self.max_us = int(max_us)
        if angle_min is not None:
            self.angle_min = int(angle_min)
        if angle_max is not None:
            self.angle_max = int(angle_max)
        self._period_us = 1_000_000 / self.freq

    # --- 资源管理支持 ---
    def __enter__(self):
        if not self._attached:
            self.attach()
        return self

    def __exit__(self, exc_type, exc, tb):
        # 尝试回到中位并释放
        try:
            self.center()
            time.sleep(0.2)
        except Exception:
            pass
        self.deinit()