### ESP32-S3 的 ADC 核心

#### 1. 推荐优先使用的 ADC 引脚（无冲突、稳定）

| ADC 单元 | 引脚号 | 特点                                   |
| -------- | ------ | -------------------------------------- |
| ADC1     | GPIO34 | 仅输入，无其他功能冲突，推荐传感器使用 |
| ADC1     | GPIO35 | 仅输入，无烧录 / 通信冲突              |
| ADC1     | GPIO36 | 仅输入，适合电位器 / 模拟传感器        |
| ADC1     | GPIO37 | 仅输入，稳定                           |
| ADC1     | GPIO38 | 仅输入，稳定                           |
| ADC1     | GPIO39 | 仅输入，稳定                           |

GPIO34~39 是**纯输入引脚**（无输出功能），只能用来采集模拟信号，不能用来输出 PWM / 数字信号（比如驱动 LED）

#### 关键：ADC 衰减模式（决定可测电压范围）

ESP32-S3 的 ADC 默认只能测 0~1.1V，需通过**衰减配置**扩展量程，常用模式：

| 衰减模式         | 可测电压范围 | 适用场景                     |
| ---------------- | ------------ | ---------------------------- |
| `ADC.ATTN_0DB`   | 0~1.1V       | 高精度小电压测量（如传感器） |
| `ADC.ATTN_6DB`   | 0~1.5V       | 较少用                       |
| `ADC.ATTN_11DB`  | 0~3.3V       | 最常用（电位器、普通传感器） |
| `ADC.ATTN_2_5DB` | 0~1.2V       | 较少用                       |

👉 之前代码中用`adc.atten(ADC.ATTN_11DB)`，就是为了让电位器的 0~3.3V 电压能完整转换成 0~4095 的数字值。

**采样稳定性优化**采集模拟信号时，建议多次采样取平均值，减少干扰：

```python
def read_adc_avg(adc, samples=10):
    """多次采样取平均，提高稳定性"""
    total = 0
    for _ in range(samples):
        total += adc.read()
        time.sleep_ms(1)
    return total // samples
```



### ADC 校准

ESP32-S3 的 ADC 即使配置了`ATTN_11DB`，也会因硬件工艺、电压波动、温度变化产生**系统误差**（比如实际 3.3V 对应的值不是 4095，而是 4000）。校准的核心是：

1. 消除 “零漂”：0V 输入时，ADC 值不是 0（可能是 10/20）；
2. 消除 “量程偏差”：3.3V 输入时，ADC 值不是 4095（可能是 4000）；
3. 让 ADC 值和实际电压 / 物理量（如角度）精准对应。

### 二、两种校准方法（按需求选择）

#### 方法 1：基础软件校准（创客场景首选）

适合普通传感器 / 电位器场景（如舵机角度反馈），无需复杂硬件，通过 “实测极值→重新映射” 实现校准，也是我们之前代码中隐含的核心逻辑。

##### 1. 校准原理

- 步骤 1：实测传感器的**最小 ADC 值**（比如电位器旋到最左，ADC 值 = 20）；
- 步骤 2：实测传感器的**最大 ADC 值**（比如电位器旋到最右，ADC 值 = 4080）；
- 步骤 3：用公式将实测的 [20,4080] 映射到标准的 [0,4095]，再转角度。

##### 2. 可直接使用的校准代码（结合舵机传感器）

```python
from machine import Pin, ADC
import time

# 传感器配置
SENSOR_PIN = 34  # 校准的ADC引脚
ADC_ATTEN = ADC.ATTN_11DB  # 0-3.3V量程
SAMPLES = 10  # 多次采样取平均，减少干扰

# 存储校准参数（实测的最小/最大ADC值）
calib_min = 0
calib_max = 4095

def read_adc_avg(adc, samples=SAMPLES):
    """多次采样取平均，提高稳定性"""
    total = 0
    for _ in range(samples):
        total += adc.read()
        time.sleep_ms(1)
    return total // samples

def calibrate_adc():
    """ADC校准流程（手动交互）"""
    global calib_min, calib_max
    adc = ADC(Pin(SENSOR_PIN))
    adc.atten(ADC_ATTEN)
    
    print("===== ADC校准 =====")
    print("步骤1：将传感器调到最小值（如电位器旋到最左），然后按回车")
    input()  # 等待用户操作
    calib_min = read_adc_avg(adc)
    print(f"实测最小值：{calib_min}")
    
    print("步骤2：将传感器调到最大值（如电位器旋到最右），然后按回车")
    input()  # 等待用户操作
    calib_max = read_adc_avg(adc)
    print(f"实测最大值：{calib_max}")
    
    # 防呆：如果最小值≥最大值，重置为默认
    if calib_min >= calib_max:
        print("校准失败！最小值≥最大值，使用默认参数")
        calib_min = 0
        calib_max = 4095
    else:
        print(f"校准完成！校准范围：[{calib_min}, {calib_max}]")
    return adc

def get_calibrated_value(adc):
    """获取校准后的ADC值（映射到0-4095）"""
    raw_value = read_adc_avg(adc)
    # 核心校准公式：将[calib_min, calib_max]映射到[0, 4095]
    if raw_value <= calib_min:
        calibrated = 0
    elif raw_value >= calib_max:
        calibrated = 4095
    else:
        calibrated = int((raw_value - calib_min) * 4095 / (calib_max - calib_min))
    return calibrated

def adc_to_angle(calibrated_value, min_angle=0, max_angle=180):
    """校准后的ADC值转角度"""
    return int((calibrated_value / 4095) * (max_angle - min_angle) + min_angle)

# 主流程
if __name__ == "__main__":
    # 第一步：执行校准
    adc = calibrate_adc()
    
    # 第二步：实时读取校准后的值
    print("\n===== 实时校准结果 =====")
    while True:
        raw = read_adc_avg(adc)
        calibrated = get_calibrated_value(adc)
        angle = adc_to_angle(calibrated)
        print(f"原始值：{raw} → 校准值：{calibrated} → 角度：{angle}°")
        time.sleep(0.5)
```

##### 3. 使用方法

1. 烧录代码后打开串口 REPL；
2. 按提示操作：
   - 第一步：将电位器旋到最左（对应舵机 0°），按回车，程序记录最小 ADC 值；
   - 第二步：将电位器旋到最右（对应舵机 180°），按回车，程序记录最大 ADC 值；
3. 程序会实时输出 “原始值→校准值→角度”，校准后角度会精准对应电位器旋转范围。

#### 方法 2：高精度硬件校准（官方校准值，工业场景）

适合对精度要求高的场景（如工业传感器、精密测量），利用 ESP32-S3 内置的**出厂校准参数**修正 ADC 值，误差可从 ±10mV 降到 ±1mV。

##### 1. 校准原理

ESP32-S3 出厂时，乐鑫会将每个芯片的 ADC 校准参数写入 eFuse（一次性烧录的存储区），通过读取这些参数，修正不同电压、不同衰减下的 ADC 值。

##### 2. 高精度校准代码（MicroPython）

```python
from machine import Pin, ADC
import esp32
import time

# 读取ESP32-S3的ADC出厂校准参数
def get_adc_calib_params(atten=ADC.ATTN_11DB):
    """
    读取ADC校准参数
    atten: 衰减模式（ATTN_0DB/ATTN_6DB/ATTN_11DB）
    返回：校准参数（vref: 参考电压，coeff: 校准系数）
    """
    # 读取eFuse中的校准参数（不同衰减对应不同参数）
    if atten == ADC.ATTN_0DB:
        calib = esp32.raw_read(0x3FF75040)  # 0dB衰减校准值
        vref = (calib >> 8) & 0xFF
        coeff = calib & 0xFF
    elif atten == ADC.ATTN_6DB:
        calib = esp32.raw_read(0x3FF75044)  # 6dB衰减校准值
        vref = (calib >> 8) & 0xFF
        coeff = calib & 0xFF
    elif atten == ADC.ATTN_11DB:
        calib = esp32.raw_read(0x3FF75048)  # 11dB衰减校准值
        vref = (calib >> 8) & 0xFF
        coeff = calib & 0xFF
    else:
        vref = 1100  # 默认参考电压(mV)
        coeff = 0
    return vref, coeff

def calibrated_adc_read(adc, atten=ADC.ATTN_11DB):
    """读取校准后的ADC值（转成实际电压，单位：mV）"""
    vref, coeff = get_adc_calib_params(atten)
    raw = adc.read()
    
    # 官方校准公式（修正ADC值）
    if atten == ADC.ATTN_11DB:
        # 11dB衰减下的电压计算（0-3300mV）
        voltage = (raw * vref * 3.0) / (coeff * 4095)
    elif atten == ADC.ATTN_6DB:
        # 6dB衰减下的电压计算（0-1500mV）
        voltage = (raw * vref * 1.5) / (coeff * 4095)
    else:
        # 0dB衰减下的电压计算（0-1100mV）
        voltage = (raw * vref) / (coeff * 4095)
    
    return int(voltage)  # 转成整数mV

# 测试代码
if __name__ == "__main__":
    # 初始化ADC
    adc = ADC(Pin(34))
    adc.atten(ADC.ATTN_11DB)  # 0-3.3V量程
    
    # 读取校准参数
    vref, coeff = get_adc_calib_params(ADC.ATTN_11DB)
    print(f"出厂校准参数：参考电压={vref}mV，校准系数={coeff}")
    
    # 实时读取校准后的电压
    print("\n实时校准电压（mV）：")
    while True:
        raw = adc.read()
        calibrated_voltage = calibrated_adc_read(adc)
        print(f"原始ADC值：{raw} → 校准后电压：{calibrated_voltage}mV")
        time.sleep(0.5)
```

##### 3. 代码说明

- `esp32.raw_read()`：读取 eFuse 中的出厂校准参数（不同衰减模式对应不同地址）；
- 校准公式：根据乐鑫官方文档，结合参考电压（vref）和校准系数（coeff），将原始 ADC 值转成实际电压（mV）；
- 输出结果：直接显示 “原始 ADC 值→实际电压”，无需手动校准，精度更高。

### 三、结合舵机场景的完整校准整合代码

将 “基础软件校准” 整合到之前的舵机控制代码中，实现 “出厂硬件校准 + 手动软件校准” 双层校准，角度反馈精度拉满：

```python
from machine import Pin, PWM, ADC
import time

# 配置区
SERVO_PIN = 5
SENSOR_PIN = 34
MIN_ANGLE = 0
MAX_ANGLE = 180
# 校准参数（初始化默认值）
calib_min = 0
calib_max = 4095

# 初始化舵机
servo = PWM(Pin(SERVO_PIN), freq=50, duty=0)

# 初始化ADC（带出厂校准）
adc = ADC(Pin(SENSOR_PIN))
adc.atten(ADC.ATTN_11DB)

def read_calibrated_voltage():
    """读取出厂校准后的电压（mV）"""
    vref = (esp32.raw_read(0x3FF75048) >> 8) & 0xFF
    coeff = esp32.raw_read(0x3FF75048) & 0xFF
    raw = adc.read()
    voltage = (raw * vref * 3.0) / (coeff * 4095)
    return int(voltage)

def calibrate_sensor():
    """传感器-舵机手动校准"""
    global calib_min, calib_max
    print("步骤1：将舵机转到0°，电位器固定，按回车")
    input()
    calib_min = adc.read()
    print(f"0°对应ADC值：{calib_min}")
    
    print("步骤2：将舵机转到180°，电位器固定，按回车")
    input()
    calib_max = adc.read()
    print(f"180°对应ADC值：{calib_max}")

def get_sensor_angle():
    """获取校准后的角度"""
    raw = adc.read()
    # 软件校准：映射到0-4095
    if raw <= calib_min:
        calibrated = 0
    elif raw >= calib_max:
        calibrated = 4095
    else:
        calibrated = int((raw - calib_min) * 4095 / (calib_max - calib_min))
    # 转角度
    angle = int((calibrated / 4095) * (MAX_ANGLE - MIN_ANGLE) + MIN_ANGLE)
    return angle

# 主流程
if __name__ == "__main__":
    # 第一步：执行校准
    calibrate_sensor()
    
    # 第二步：实时读取角度
    print("\n实时角度反馈：")
    while True:
        voltage = read_calibrated_voltage()
        angle = get_sensor_angle()
        print(f"电压：{voltage}mV → 角度：{angle}°")
        time.sleep(0.5)
```

### 四、校准注意事项（避坑关键）

1. **硬件基础**：
   - 传感器供电必须稳定（用 3.3V 稳压模块，而非 ESP32 的 3.3V 引脚，减少波动）；
   - 接线尽量短，避免干扰（模拟信号易受电磁干扰，建议用屏蔽线）。
2. **软件校准技巧**：
   - 多次采样取平均（代码中`SAMPLES=10`），避免单次采样的偶然误差；
   - 校准后保存参数（可写入 Flash），下次上电无需重新校准。
3. **适用场景**：
   - 创客 / 舵机场景：用**方法 1（基础软件校准）** 足够；
   - 工业 / 精密测量：用**方法 2（出厂校准）+ 方法 1** 双层校准。

### 总结

1. **基础校准**：通过 “实测极值→重新映射” 修正 ADC 偏差，适合舵机 / 电位器等创客场景，操作简单、效果明显；
2. **高精度校准**：读取 ESP32-S3 出厂校准参数，计算实际电压，适合精密测量场景；
3. **核心要点**：校准的关键是 “固定极值”（比如电位器旋到最左 / 最右），确保映射的基准准确。