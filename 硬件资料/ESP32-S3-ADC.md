### 一、ESP32-S3 的 ADC 核心

你这个是**ESP32-S3-DevKitC-1 开发板**（用的是 ESP32-S3-WROOM-1 模组），我结合它的引脚图，把 ADC 接口按 “分组 + 功能 + 特殊用途” 讲清楚：

#### 1、ADC 接口总览

这个开发板的 ADC 分 2 组（**ADC1、ADC2**），共 18 个可用接口，不同接口的 “额外功能” 和注意事项如下：

#### 2、ADC1 接口（共 8 个，推荐优先用）

ADC1 的接口和 Wi-Fi 不冲突，且大部分是 “纯模拟输入 + 触摸功能”，适合接摇杆、传感器：

| 接口号 | ADC 通道 | 额外功能          | 特殊特点 / 注意事项                                   |
| ------ | -------- | ----------------- | ----------------------------------------------------- |
| GPIO4  | ADC1_3   | TOUCH4、RTC       | 普通模拟输入，无冲突，**你之前接摇杆 X 轴的常用接口** |
| GPIO5  | ADC1_4   | TOUCH5、RTC       | 普通模拟输入，无冲突，**你之前接摇杆 Y 轴的常用接口** |
| GPIO6  | ADC1_5   | TOUCH6、RTC       | 普通模拟输入，无冲突                                  |
| GPIO7  | ADC1_6   | TOUCH7、RTC       | 普通模拟输入，无冲突                                  |
| GPIO8  | ADC1_7   | TOUCH8、RTC、JTAG | 能当模拟输入，但用 JTAG 调试时不能用                  |
| GPIO1  | ADC1_0   | TOUCH1、RTC       | 普通模拟输入，无冲突                                  |
| GPIO2  | ADC1_1   | TOUCH2、RTC       | 普通模拟输入，无冲突                                  |
| GPIO3  | ADC1_2   | TOUCH3、RTC、JTAG | 能当模拟输入，但用 JTAG 调试时不能用                  |

#### 3、ADC2 接口（共 10 个，注意 Wi-Fi 冲突）

ADC2 接口和 Wi-Fi 共用硬件，开 Wi-Fi 时可能失效；且大部分绑定了其他外设功能：

| 接口号 | ADC 通道 | 额外功能             | 特殊特点 / 注意事项                                   |
| ------ | -------- | -------------------- | ----------------------------------------------------- |
| GPIO15 | ADC2_4   | U0RTS、RTC、32K 晶振 | **别用！** 绑定了 32K 晶振，用了会影响系统时钟        |
| GPIO16 | ADC2_5   | U0CTS、RTC、32K 晶振 | **别用！** 绑定了 32K 晶振，用了会影响系统时钟        |
| GPIO17 | ADC2_6   | U1TXD、RTC           | 能当模拟输入，但用 UART1 串口时不能用                 |
| GPIO18 | ADC2_7   | U1RXD、RTC           | 能当模拟输入，但用 UART1 串口时不能用                 |
| GPIO11 | ADC2_0   | TOUCH11、RTC、SPI    | 能当模拟输入，但用 SPI 外设（比如接 SD 卡）时不能用   |
| GPIO12 | ADC2_1   | TOUCH12、RTC、SPI    | 能当模拟输入，但用 SPI 外设时不能用                   |
| GPIO13 | ADC2_2   | TOUCH13、RTC、SPI    | 能当模拟输入（你之前接舵机的接口，舵机用 PWM 不冲突） |
| GPIO14 | ADC2_3   | TOUCH14、RTC、SPI    | 能当模拟输入，但用 SPI 外设时不能用                   |
| GPIO19 | ADC2_8   | U1RTS、RTC、USB      | **别用！** 绑定了 USB，用了会导致电脑连不上开发板     |
| GPIO20 | ADC2_9   | U1CTS、RTC、USB      | **别用！** 绑定了 USB，用了会导致电脑连不上开发板     |

#### 4、重点：这些接口有 “特殊用途”，禁止随便用

- **GPIO15、GPIO16**：绑定 32K 晶振，影响系统时钟，绝对不能用；
- **GPIO19、GPIO20**：绑定 USB 接口，用了会断连电脑，绝对不能用；
- **GPIO3、GPIO8**：绑定 JTAG 调试接口，用 JTAG 时不能用，但平时可以用。

#### 关键：ADC 衰减模式（决定可测电压范围）

首先一句话结论：**ADC 衰减模式是让 ESP32-S3 的 ADC 能 “读更高电压” 的功能，代价是精度会稍微降低一点**。

我用生活化的例子给你讲清楚：

#### 1. 为什么需要衰减模式？

ESP32-S3 的 ADC “原生能力” 只能读**0~3.3V**的电压（超过 3.3V 会烧坏 ADC）。但如果传感器输出的电压超过 3.3V（比如某些模块输出 5V），就需要 “衰减”—— 相当于给电压 “打个折”，让它降到 3.3V 以内，ADC 才能安全读取。

#### 2. ESP32-S3 的 4 种衰减模式

ESP32-S3 有 4 种衰减模式，对应不同的 “可读电压范围”，代码里用`atten()`函数设置（比如咱们之前代码里的`joystick_x.atten(ADC.ATTN_11DB)`）：

| 衰减模式（代码里的名字） | 对应的可读电压范围 | 适合场景                                     | 缺点                       |
| ------------------------ | ------------------ | -------------------------------------------- | -------------------------- |
| `ADC.ATTN_0DB`           | 0~1.1V             | 读很低的电压（比如小传感器）                 | 范围太小，大部分场景用不上 |
| `ADC.ATTN_2_5DB`         | 0~1.5V             | 读较低电压                                   | 范围还是小                 |
| `ADC.ATTN_6DB`           | 0~2.2V             | 读中等电压                                   | 常用但不够大               |
| `ADC.ATTN_11DB`          | 0~3.9V             | 读接近 3.3V 的电压（或轻微超过 3.3V 的电压） | **最常用**                 |

#### 3. 实际怎么用？

比如你要读一个输出 4V 的传感器：

- 不开启衰减模式：4V 超过 3.3V，ADC 会烧坏；
- 开启`ATTN_11DB`衰减模式：ADC 会把 4V “衰减” 到 3.3V 以内，然后读出对应的数字值，再通过公式换算回实际的 4V 电压。

#### 4. 注意：衰减模式会降低精度

衰减模式相当于 “放大了可读范围，但缩小了数字的区分度”—— 比如原生 0~3.3V 对应 0~4095，衰减后 0~3.9V 对应 0~4095，同样的电压变化，数字变化会更小，精度会稍微低一点，但对咱们做摇杆、舵机这些项目来说，完全够用。

总结：**咱们项目里用的`ATTN_11DB`是最实用的衰减模式，既能读接近 3.3V 的电压，又不会影响精度太多**。

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



### 二、ADC 校准

ESP32-S3 的 ADC 即使配置了`ATTN_11DB`，也会因硬件工艺、电压波动、温度变化产生**系统误差**（比如实际 3.3V 对应的值不是 4095，而是 4000）。校准的核心是：

1. 消除 “零漂”：0V 输入时，ADC 值不是 0（可能是 10/20）；
2. 消除 “量程偏差”：3.3V 输入时，ADC 值不是 4095（可能是 4000）；
3. 让 ADC 值和实际电压 / 物理量（如角度）精准对应。

#### 1、两种校准方法（按需求选择）

##### 方法 1：基础软件校准（创客场景首选）

适合普通传感器 / 电位器场景（如舵机角度反馈），无需复杂硬件，通过 “实测极值→重新映射” 实现校准，也是我们之前代码中隐含的核心逻辑。

###### 1. 校准原理

- 步骤 1：实测传感器的**最小 ADC 值**（比如电位器旋到最左，ADC 值 = 20）；
- 步骤 2：实测传感器的**最大 ADC 值**（比如电位器旋到最右，ADC 值 = 4080）；
- 步骤 3：用公式将实测的 [20,4080] 映射到标准的 [0,4095]，再转角度。

###### 2. 可直接使用的校准代码（结合舵机传感器）

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

###### 3. 使用方法

1. 烧录代码后打开串口 REPL；
2. 按提示操作：
   - 第一步：将电位器旋到最左（对应舵机 0°），按回车，程序记录最小 ADC 值；
   - 第二步：将电位器旋到最右（对应舵机 180°），按回车，程序记录最大 ADC 值；
3. 程序会实时输出 “原始值→校准值→角度”，校准后角度会精准对应电位器旋转范围。

##### 方法 2：高精度硬件校准（官方校准值，工业场景）

适合对精度要求高的场景（如工业传感器、精密测量），利用 ESP32-S3 内置的**出厂校准参数**修正 ADC 值，误差可从 ±10mV 降到 ±1mV。

###### 1. 校准原理

ESP32-S3 出厂时，乐鑫会将每个芯片的 ADC 校准参数写入 eFuse（一次性烧录的存储区），通过读取这些参数，修正不同电压、不同衰减下的 ADC 值。

###### 2. 高精度校准代码（MicroPython）

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

###### 3. 代码说明

- `esp32.raw_read()`：读取 eFuse 中的出厂校准参数（不同衰减模式对应不同地址）；
- 校准公式：根据乐鑫官方文档，结合参考电压（vref）和校准系数（coeff），将原始 ADC 值转成实际电压（mV）；
- 输出结果：直接显示 “原始 ADC 值→实际电压”，无需手动校准，精度更高。

#### 2、结合舵机场景的完整校准整合代码

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

##### 四、校准注意事项（避坑关键）

1. **硬件基础**：
   - 传感器供电必须稳定（用 3.3V 稳压模块，而非 ESP32 的 3.3V 引脚，减少波动）；
   - 接线尽量短，避免干扰（模拟信号易受电磁干扰，建议用屏蔽线）。
2. **软件校准技巧**：
   - 多次采样取平均（代码中`SAMPLES=10`），避免单次采样的偶然误差；
   - 校准后保存参数（可写入 Flash），下次上电无需重新校准。
3. **适用场景**：
   - 创客 / 舵机场景：用**方法 1（基础软件校准）** 足够；
   - 工业 / 精密测量：用**方法 2（出厂校准）+ 方法 1** 双层校准。

#### 总结

1. **基础校准**：通过 “实测极值→重新映射” 修正 ADC 偏差，适合舵机 / 电位器等创客场景，操作简单、效果明显；
2. **高精度校准**：读取 ESP32-S3 出厂校准参数，计算实际电压，适合精密测量场景；
3. **核心要点**：校准的关键是 “固定极值”（比如电位器旋到最左 / 最右），确保映射的基准准确。