### 一、PWM 核心硬件配置

#### 1. **LEDC（常用 PWM）**

   - 通道数：**8 个独立通道**，可同时输出 8 路不同参数的 PWM 信号。
   - 支持引脚：**所有可输出的 GPIO 都能配置为 PWM 引脚**（需通过代码绑定通道 + 定时器）。
   - 特性：
     - 仅支持**低速模式**（`LEDC_LOW_SPEED_MODE`）。
     - 可配置频率（与占空比分辨率关联：频率越高，分辨率越低）、占空比（0~100%）。
     - 支持硬件渐变（无需 CPU 干预）、中断触发等功能。
#### 2.**MCPWM（进阶 PWM）**

   - 通道数：**2 个 MCPWM 单元，共 12 路 PWM 输出**（每个单元 3 对互补通道）。
   - 特性：
     - 支持互补输出、死区控制、故障保护、脉宽捕获等功能。
     - 适用于电机驱动、数字电源等需要高精度控制的场景。

#### 3、LEDC 与 MCPWM 的区别

| 特性           | LEDC（LED PWM 控制器）                     | MCPWM（电机控制 PWM）                      |
| -------------- | ------------------------------------------ | ------------------------------------------ |
| **核心用途**   | 通用 PWM（LED 调光、呼吸灯、简单外设控制） | 高精度 PWM（电机驱动、数字电源、舵机控制） |
| **通道数**     | 8 个独立通道                               | 2 个单元共 12 路（含互补输出）             |
| **功能特性**   | 支持硬件渐变、占空比调节                   | 支持互补输出、死区控制、故障保护、脉宽捕获 |
| **配置复杂度** | 简单（适合入门）                           | 复杂（适合进阶场景）                       |

#### 4、MicroPython 配置 PWM 的代码示例

##### LEDC 配置（以板载 RGB LED 为例）

```python
from machine import Pin, PWM
import time

# 配置RGB LED的3个引脚为PWM（假设RGB对应GPIO48、GPIO47、GPIO46）
red = PWM(Pin(48), freq=1000, duty=0)  # 频率1kHz，占空比0（熄灭）
green = PWM(Pin(47), freq=1000, duty=0)
blue = PWM(Pin(46), freq=1000, duty=0)

# 呼吸灯效果（以红色为例）
while True:
    for duty in range(0, 1024):
        red.duty(duty)
        time.sleep_ms(1)
    for duty in range(1023, -1, -1):
        red.duty(duty)
        time.sleep_ms(1)
```

#### 5. MCPWM 配置（以舵机控制为例）

MicroPython 对 MCPWM 的支持需依赖`machine`模块的`MCPWM`类（部分版本需手动导入）：

```python
from machine import Pin, MCPWM
import time

# 配置MCPWM单元0，通道0，引脚GPIO1
mcpwm = MCPWM(0, 0, Pin(1))
mcpwm.freq(50)  # 舵机常用频率50Hz

# 舵机角度控制（0°→1ms脉宽，180°→2ms脉宽）
def set_servo_angle(angle):
    duty = (angle / 180) * 1023 * (2/20) + (1023 * (1/20))  # 50Hz对应周期20ms
    mcpwm.duty(int(duty))

# 测试舵机转动
set_servo_angle(0)
time.sleep(1)
set_servo_angle(90)
time.sleep(1)
set_servo_angle(180)
```

### 二、PWM 频率精度

ESP32-S3 的 PWM 频率精度由**时钟源**和**分频系数**决定：

- LEDC 默认使用**APB_CLK（80MHz）**，频率计算为：`freq = APB_CLK / (分频系数 * (分辨率+1))`。

  

  例：分辨率 10 位（0~1023）时，最小频率约 76Hz，最大频率约 78kHz（实际精度误差 < 1%）。

- MCPWM 支持更高精度的时钟分频，频率误差可控制在 0.1% 以内。

### 三、项目应用场景

1. **LED 相关**：RGB 灯带调光、呼吸灯、LED 点阵屏驱动。
2. **电机控制**：直流电机调速（MCPWM）、舵机角度控制（LEDC/MCPWM）。
3. **电源控制**：数字电源的电压 / 电流调节（MCPWM）。
4. **信号模拟**：模拟红外遥控信号（LEDC）、简易波形发生器（如方波）。

#### 1、PWM 配置步骤（以 LEDC 为例）

1. **配置定时器**：指定 PWM 频率、占空比分辨率、时钟源（如 APB_CLK 80MHz）。
2. **绑定通道与 GPIO**：将 LEDC 通道绑定到指定 GPIO 引脚。
3. **设置 / 更新占空比**：通过代码调整占空比，并生效配置。

### 四、**ESP32-S3-DevKitC-1 常用 GPIO 功能兼容表，

表格聚焦实际开发中高频使用的引脚，标注了核心功能兼容性和使用注意事项：

| GPIO 编号 | 板载硬件关联 | LEDC 支持 | MCPWM 支持 | 其他核心功能                 | 使用注意事项                                          |
| --------- | ------------ | --------- | ---------- | ---------------------------- | ----------------------------------------------------- |
| GPIO0     | 启动模式引脚 | ✅         | ✅          | UART0_RX、触摸输入、ADC1_CH0 | 下拉为正常启动，建议仅作输出 / 输入，避免频繁电平变化 |
| GPIO1     | -            | ✅         | ✅          | UART0_TX、触摸输入、ADC1_CH1 | 常用扩展引脚，适合舵机 / 电机 PWM 输出                |
| GPIO2     | -            | ✅         | ✅          | SPI_CS0、ADC1_CH2、I2C_SDA   | 兼容多协议，适合通用 PWM / 数据传输                   |
| GPIO3     | -            | ✅         | ✅          | SPI_CLK、ADC1_CH3、I2C_SCL   | 与 GPIO2 配对，适合 I2C/PWM 组合使用                  |
| GPIO4     | -            | ✅         | ✅          | SPI_MOSI、ADC1_CH4           | 高速数据 + PWM 场景（如灯带驱动）                     |
| GPIO5     | -            | ✅         | ✅          | SPI_MISO、ADC1_CH5           | 同上，适合双向数据 + PWM                              |
| GPIO10    | -            | ✅         | ✅          | UART1_TX、ADC1_CH6           | 推荐 MCPWM 专用引脚（电机 / 舵机）                    |
| GPIO11    | -            | ✅         | ✅          | UART1_RX、ADC1_CH7           | 与 GPIO10 配对，适合双路 MCPWM 输出                   |
| GPIO12    | -            | ✅         | ✅          | 触摸输入、ADC2_CH0           | 低噪声，适合高精度 PWM（如模拟波形输出）              |
| GPIO46    | 板载 RGB-B   | ✅         | ❌          | 仅通用 IO/LEDC               | 板载蓝色 LED 专属，优先用于 RGB 调光                  |
| GPIO47    | 板载 RGB-G   | ✅         | ❌          | 仅通用 IO/LEDC               | 板载绿色 LED 专属，优先用于 RGB 调光                  |
| GPIO48    | 板载 RGB-R   | ✅         | ❌          | 仅通用 IO/LEDC               | 板载红色 LED 专属，优先用于 RGB 调光                  |
| GPIO35    | -            | ✅         | ✅          | ADC2_CH1、触摸输入           | 仅输入模式（无输出能力），不可作 PWM 输出             |
| GPIO36    | -            | ✅         | ✅          | ADC2_CH2、触摸输入           | 仅输入模式，不可作 PWM 输出                           |

### 五、关键补充说明

1. **LEDC/MCPWM 通用规则**：
   - 上表中标注`✅`的引脚，均可通过 MicroPython 代码直接映射为 LEDC/MCPWM 输出；
   - GPIO46/47/48 仅支持 LEDC（板载 RGB 优化），不支持 MCPWM；
   - GPIO35/36 为输入专用引脚，无法输出 PWM，仅可作信号采集。
2. **开发板硬件限制**：
   - 板载 RGB LED（GPIO46/47/48）为**共阳 / 共阴设计**，PWM 占空比逻辑需匹配硬件（如占空比 0 为熄灭，1023 为最亮）；
   - 所有 GPIO 均支持**软件 PWM**，但 LEDC/MCPWM 为硬件 PWM，精度更高、占用 CPU 更少。
3. **选型建议**：
   - 简单 PWM（呼吸灯 / 调光）：优先选 GPIO46/47/48（板载）、GPIO1/2（扩展）；
   - 高精度 PWM（电机 / 舵机）：优先选 GPIO10/11/12（MCPWM 优化）；
   - 避免用 GPIO0 作高频 PWM，防止影响设备启动稳定性。

### DevKitC-1 常用 PWM 引脚示例（仅为推荐，非固定）

| 功能      | 推荐 GPIO 引脚         | 说明                      |
| --------- | ---------------------- | ------------------------- |
| LEDC PWM  | GPIO1、GPIO2、GPIO48   | 板载 RGB、常用扩展引脚    |
| MCPWM PWM | GPIO10、GPIO11、GPIO12 | 适合电机 / 舵机的扩展引脚 |

简单说：**LEDC 和 MCPWM 可以映射到 ESP32-S3-DevKitC-1 的任意 GPIO（只要是输出引脚），无固定专属接口**。

以下是**ESP32-S3-DevKitC-1**的 MicroPython PWM（LEDC+MCPWM）详细测试代码，包含注释说明：

#### 1. LEDC 通用 PWM 测试（呼吸灯 + 多通道输出）

```python
from machine import Pin, PWM
import time

# --------------------------
# LEDC PWM 初始化配置
# --------------------------
# 示例1：控制板载RGB LED（假设RGB对应GPIO48/47/46，具体以实际硬件为准）
rgb_red = PWM(Pin(48), freq=1000, duty=0)  # 通道1：GPIO48，频率1kHz，初始占空比0
rgb_green = PWM(Pin(47), freq=1000, duty=0) # 通道2：GPIO47
rgb_blue = PWM(Pin(46), freq=1000, duty=0)  # 通道3：GPIO46

# 示例2：独立PWM输出引脚（如GPIO10）
pwm_out = PWM(Pin(10), freq=2000, duty=512) # 通道4：GPIO10，频率2kHz，占空比50%（10位分辨率下512=50%）


# --------------------------
# LEDC 功能测试函数
# --------------------------
def test_rgb_breathing():
    """RGB呼吸灯测试：红色渐变→绿色渐变→蓝色渐变"""
    print("=== 开始RGB呼吸灯测试 ===")
    # 红色呼吸
    for duty in range(0, 1024, 2):  # 10位分辨率：0~1023，步长2（加快渐变速度）
        rgb_red.duty(duty)
        time.sleep_ms(5)
    for duty in range(1023, -1, -2):
        rgb_red.duty(duty)
        time.sleep_ms(5)
    rgb_red.duty(0)  # 关闭红色
    
    # 绿色呼吸
    for duty in range(0, 1024, 2):
        rgb_green.duty(duty)
        time.sleep_ms(5)
    for duty in range(1023, -1, -2):
        rgb_green.duty(duty)
        time.sleep_ms(5)
    rgb_green.duty(0)  # 关闭绿色
    
    # 蓝色呼吸
    for duty in range(0, 1024, 2):
        rgb_blue.duty(duty)
        time.sleep_ms(5)
    for duty in range(1023, -1, -2):
        rgb_blue.duty(duty)
        time.sleep_ms(5)
    rgb_blue.duty(0)  # 关闭蓝色


def test_pwm_freq_duty():
    """PWM频率/占空比动态调整测试（GPIO10）"""
    print("=== 开始频率/占空比调整测试 ===")
    # 测试不同频率（100Hz→1kHz→10kHz）
    for freq in [100, 1000, 10000]:
        pwm_out.freq(freq)  # 调整频率
        print(f"当前频率：{freq}Hz")
        # 占空比从0→100%渐变
        for duty in range(0, 1024, 10):
            pwm_out.duty(duty)
            time.sleep_ms(100)
    pwm_out.duty(0)  # 停止输出


# --------------------------
# 执行测试
# --------------------------
if __name__ == "__main__":
    test_rgb_breathing()   # 先运行RGB呼吸灯测试
    time.sleep(2)          # 间隔2秒
    test_pwm_freq_duty()   # 再运行频率/占空比测试
```

#### 2. MCPWM 电机 / 舵机控制测试

```python
from machine import Pin, MCPWM
import time

# --------------------------
# MCPWM 初始化配置（舵机控制）
# --------------------------
# MCPWM单元0，通道0，绑定GPIO1（舵机信号线）
servo_mcpwm = MCPWM(0, 0, Pin(1))
servo_mcpwm.freq(50)  # 舵机标准频率：50Hz（周期20ms）


# --------------------------
# MCPWM 功能测试函数
# --------------------------
def servo_angle_control(angle):
    """将角度转换为MCPWM占空比（0°→1ms脉宽，180°→2ms脉宽）"""
    # 50Hz对应周期20ms，脉宽范围1ms~2ms → 占空比范围5%~10%
    # MCPWM默认10位分辨率（0~1023），占空比计算：duty = (脉宽/周期)*1023
    pulse_width_ms = 1 + (angle / 180) * 1  # 1ms + (角度/180)*1ms
    duty = int((pulse_width_ms / 20) * 1023)
    servo_mcpwm.duty(duty)
    print(f"舵机角度：{angle}°，脉宽：{pulse_width_ms}ms，占空比：{duty}")


def test_servo_move():
    """舵机角度测试：0°→90°→180°→90°→0°"""
    print("=== 开始舵机控制测试 ===")
    angles = [0, 90, 180, 90, 0]
    for angle in angles:
        servo_angle_control(angle)
        time.sleep(1.5)  # 等待舵机转动到位


# --------------------------
# 执行测试
# --------------------------
if __name__ == "__main__":
    test_servo_move()
```

#### 使用说明：

1. **LEDC 代码**：直接运行后，板载 RGB 会依次呼吸渐变，GPIO10 会动态调整频率和占空比。
2. **MCPWM 代码**：需将舵机信号线接 GPIO1，运行后舵机会按角度转动。
3. 若硬件引脚与示例不符，需根据实际**ESP32-S3-DevKitC-1 引脚图**修改`Pin()`参数。

**ESP32-S3-DevKitC-1 3 路舵机**和**灯带驱动**场景的引脚分配方案已整理完成，方案兼顾硬件 PWM 精度、引脚兼容性和开发便利性，附详细说明和代码示例：

------

#### 3、3 路舵机驱动引脚分配方案

##### 核心设计原则

- 优先使用**MCPWM 硬件通道**（高精度、低 CPU 占用），适配舵机 50Hz 标准频率；
- 避开启动引脚（GPIO0）、板载 RGB 引脚，选择独立扩展引脚；
- 预留 I2C/UART 等扩展接口，方便叠加传感器等外设。

##### 最终引脚分配

| 舵机编号 | 控制引脚 | PWM 类型 | 备用引脚 | 功能说明                                    |
| -------- | -------- | -------- | -------- | ------------------------------------------- |
| 舵机 1   | GPIO10   | MCPWM    | GPIO1    | MCPWM 单元 0 - 通道 0，主舵机（如云台水平） |
| 舵机 2   | GPIO11   | MCPWM    | GPIO2    | MCPWM 单元 0 - 通道 1，副舵机（如云台垂直） |
| 舵机 3   | GPIO12   | MCPWM    | GPIO3    | MCPWM 单元 1 - 通道 0，辅助舵机（如机械爪） |

##### 配套代码示例（MicroPython）


```python
from machine import Pin, MCPWM
import time

# 初始化3路MCPWM舵机引脚
servo1 = MCPWM(0, 0, Pin(10))  # 单元0-通道0 → GPIO10
servo2 = MCPWM(0, 1, Pin(11))  # 单元0-通道1 → GPIO11
servo3 = MCPWM(1, 0, Pin(12))  # 单元1-通道0 → GPIO12

# 统一设置舵机频率（50Hz）
for servo in [servo1, servo2, servo3]:
    servo.freq(50)

# 舵机角度控制函数（0°→1ms脉宽，180°→2ms脉宽）
def set_servo_angle(servo, angle):
    pulse_width = 1 + (angle / 180) * 1  # 1ms ~ 2ms
    duty = int((pulse_width / 20) * 1023)  # 20ms为50Hz周期，10位分辨率
    servo.duty(duty)
    print(f"舵机角度：{angle}°，占空比：{duty}")

# 测试3路舵机同步转动
if __name__ == "__main__":
    angles = [0, 90, 180, 90, 0]
    for angle in angles:
        set_servo_angle(servo1, angle)
        set_servo_angle(servo2, angle)
        set_servo_angle(servo3, angle)
        time.sleep(1)
```

##### 使用注意事项

1. 舵机需外接 5V 电源（开发板 3.3V 引脚电流不足），仅信号线接 GPIO；
2. 若需更多舵机，可复用 LEDC（精度略低但足够），如 GPIO4/5/6；
3. 避免将舵机引脚与高速数据引脚（如 SPI）复用，防止信号干扰。

------

#### 3、灯带驱动引脚分配方案

##### 核心设计原则

- 优先使用**LEDC 硬件通道**（支持高频 PWM、渐变效果），适配 WS2812/APA102 等灯带；
- 单路灯带用独立引脚，多路 RGB 灯带按颜色分通道；
- 选择高驱动能力引脚，支持高频（800kHz）信号输出。

##### 最终引脚分配

| 灯带类型         | 控制引脚                    | PWM 类型 | 备用引脚      | 功能说明                        |
| ---------------- | --------------------------- | -------- | ------------- | ------------------------------- |
| 单路 WS2812 灯带 | GPIO48                      | LEDC     | GPIO4         | 板载 RGB 引脚（复用），高频 PWM |
| RGB 灯带（红）   | GPIO48                      | LEDC     | GPIO1         | 独立红色通道                    |
| RGB 灯带（绿）   | GPIO47                      | LEDC     | GPIO2         | 独立绿色通道                    |
| RGB 灯带（蓝）   | GPIO46                      | LEDC     | GPIO3         | 独立蓝色通道                    |
| APA102 灯带      | GPIO4（CLK）+ GPIO5（DATA） | LEDC     | GPIO10+GPIO11 | 时钟 + 数据双通道               |

##### 配套代码示例（MicroPython）


```python
from machine import Pin, PWM
import time

# 方案1：单路WS2812灯带（GPIO48）
led_strip = PWM(Pin(48), freq=800000, duty=0)  # WS2812标准频率800kHz

# 方案2：RGB三色灯带（GPIO48/47/46）
rgb_r = PWM(Pin(48), freq=1000, duty=0)  # 红色通道
rgb_g = PWM(Pin(47), freq=1000, duty=0)  # 绿色通道
rgb_b = PWM(Pin(46), freq=1000, duty=0)  # 蓝色通道

# RGB灯带渐变效果测试
def rgb_gradient():
    print("=== RGB灯带渐变测试 ===")
    # 红→绿→蓝循环渐变
    for i in range(0, 1024, 5):
        rgb_r.duty(i)
        rgb_g.duty(1023-i)
        rgb_b.duty(512-i%512)
        time.sleep_ms(10)

# 单路灯带亮度调节
def strip_brightness():
    print("=== 单路灯带亮度测试 ===")
    for duty in range(0, 1024, 10):
        led_strip.duty(duty)
        time.sleep_ms(50)
    for duty in range(1023, -1, -10):
        led_strip.duty(duty)
        time.sleep_ms(50)

if __name__ == "__main__":
    rgb_gradient()
    time.sleep(2)
    strip_brightness()
```

##### 使用注意事项

1. WS2812 灯带需高频 PWM（800kHz），优先选 GPIO48/4/5（高频输出稳定）；
2. 灯带建议外接 5V 电源，信号线串 100Ω 电阻后接 GPIO，防止电流冲击损坏引脚；
3. 多路灯带避免共用同一 LEDC 通道，否则会出现亮度同步问题。

------

##### 总结

1. **3 路舵机**：优先选 GPIO10/11/12（MCPWM），高精度适配舵机 50Hz 频率，需外接电源；
2. **灯带驱动**：单路选 GPIO48（LEDC），RGB 分路选 GPIO48/47/46，高频灯带适配 800kHz 频率；
3. 两种场景的引脚无重叠，可同时使用（如云台 + 灯带联动），兼容性最优。

#### 4.ESP32-S3-DevKitC-1 云台 + RGB 灯带联动 综合引脚分配方案

该方案兼顾**3 路舵机云台**的高精度 MCPWM 控制和**RGB 灯带**的 LEDC 渐变效果，引脚无冲突、无复用，同时预留扩展接口，适配云台灯带联动的典型场景（如云台转向时灯带同步变色）。

##### 核心设计原则

1. **功能隔离**：舵机 MCPWM 与灯带 LEDC 使用独立引脚，避免信号干扰；
2. **优先级适配**：舵机用 MCPWM（高精度），灯带用 LEDC（高频渐变）；
3. **扩展预留**：保留 UART/I2C 引脚，方便叠加传感器（如云台避障）；
4. **硬件兼容**：避开启动引脚（GPIO0）、输入专用引脚（GPIO35/36）。

##### 最终综合引脚分配表

| 功能模块 | 设备 / 通道 | 控制引脚 | PWM 类型 | 功能说明                                         | 联动逻辑参考                |
| -------- | ----------- | -------- | -------- | ------------------------------------------------ | --------------------------- |
| 云台舵机 | 水平舵机    | GPIO10   | MCPWM    | MCPWM 单元 0 - 通道 0，50Hz 标准频率             | 水平转向→灯带蓝色通道渐变   |
| 云台舵机 | 垂直舵机    | GPIO11   | MCPWM    | MCPWM 单元 0 - 通道 1，50Hz 标准频率             | 垂直转向→灯带绿色通道渐变   |
| 云台舵机 | 辅助舵机    | GPIO12   | MCPWM    | MCPWM 单元 1 - 通道 0，50Hz 标准频率（如机械爪） | 机械爪开合→灯带红色通道渐变 |
| RGB 灯带 | 红色通道    | GPIO48   | LEDC     | 板载 RGB 引脚复用，1kHz 频率（渐变流畅）         | 跟随云台水平角度变化        |
| RGB 灯带 | 绿色通道    | GPIO47   | LEDC     | 板载 RGB 引脚复用，1kHz 频率                     | 跟随云台垂直角度变化        |
| RGB 灯带 | 蓝色通道    | GPIO46   | LEDC     | 板载 RGB 引脚复用，1kHz 频率                     | 跟随辅助舵机状态变化        |
| 扩展预留 | UART_TX     | GPIO1    | -        | 可接串口传感器（如角度反馈）                     | 传感器数据→灯带亮度调节     |
| 扩展预留 | UART_RX     | GPIO2    | -        | 同上                                             | -                           |

##### 联动场景代码示例（MicroPython）

该代码实现核心联动逻辑：**云台水平舵机转动时，灯带红色通道亮度同步变化；垂直舵机转动时，绿色通道同步变化**，直接适配上述引脚方案。

```python
from machine import Pin, PWM, MCPWM
import time

# ==================== 硬件初始化 ====================
# 1. 云台舵机（MCPWM）初始化
servo_horizontal = MCPWM(0, 0, Pin(10))  # 水平舵机→GPIO10
servo_vertical = MCPWM(0, 1, Pin(11))    # 垂直舵机→GPIO11
servo_aux = MCPWM(1, 0, Pin(12))         # 辅助舵机→GPIO12
# 舵机频率统一设置为50Hz（标准舵机周期20ms）
for servo in [servo_horizontal, servo_vertical, servo_aux]:
    servo.freq(50)

# 2. RGB灯带（LEDC）初始化
rgb_r = PWM(Pin(48), freq=1000, duty=0)  # 红→GPIO48
rgb_g = PWM(Pin(47), freq=1000, duty=0)  # 绿→GPIO47
rgb_b = PWM(Pin(46), freq=1000, duty=0)  # 蓝→GPIO46

# ==================== 核心联动函数 ====================
def set_servo_angle(servo, angle):
    """舵机角度控制：0°→1ms脉宽，180°→2ms脉宽"""
    pulse_width = 1 + (angle / 180) * 1  # 脉宽范围1~2ms
    duty = int((pulse_width / 20) * 1023)  # 转换为10位占空比
    servo.duty(duty)
    return duty  # 返回占空比，用于灯带联动

def servo_rgb_linkage(horiz_angle, vert_angle):
    """云台-灯带联动核心逻辑：角度→占空比→灯带亮度"""
    # 1. 控制云台舵机转动
    horiz_duty = set_servo_angle(servo_horizontal, horiz_angle)
    vert_duty = set_servo_angle(servo_vertical, vert_angle)
    
    # 2. 联动调节灯带：舵机占空比映射为灯带亮度（0~1023）
    rgb_r.duty(horiz_duty)  # 水平角度→红色亮度
    rgb_g.duty(vert_duty)   # 垂直角度→绿色亮度
    rgb_b.duty(512)         # 蓝色固定中等亮度（可扩展为辅助舵机联动）
    
    print(f"云台水平{horiz_angle}°→红灯亮度{horiz_duty} | 垂直{vert_angle}°→绿灯亮度{vert_duty}")

# ==================== 联动测试 ====================
if __name__ == "__main__":
    # 云台从0°→90°→180°转动，灯带同步变色
    for angle in range(0, 181, 10):
        servo_rgb_linkage(angle, 90 - angle//2)  # 水平递增，垂直递减
        time.sleep(0.5)
    
    # 复位云台和灯带
    servo_rgb_linkage(90, 90)
    rgb_r.duty(0)
    rgb_g.duty(0)
    rgb_b.duty(0)
```

##### 使用注意事项

1. **电源供电**：
   - 云台舵机需外接 5V/2A 电源（开发板 3.3V 引脚电流不足），仅信号线接 GPIO；
   - RGB 灯带建议外接 5V 电源，信号线串 100Ω 电阻后接 GPIO，防止电流冲击。
2. **信号干扰**：
   - 舵机和灯带的电源线分开布线，避免 PWM 信号被电源纹波干扰；
   - 高频灯带（如 WS2812）需将频率设为 800kHz，替换代码中`freq=1000`为`freq=800000`。
3. **扩展优化**：
   - 若需添加角度传感器（如电位器），可接 GPIO35（ADC 输入），读取角度后反向控制灯带；
   - 如需更多舵机 / 灯带通道，可复用 GPIO4/5（LEDC）、GPIO3（MCPWM 备用）。

##### 总结

1. 核心引脚分配：云台用 GPIO10/11/12（MCPWM），灯带用 GPIO46/47/48（LEDC），功能隔离无冲突；
2. 联动逻辑：通过舵机占空比与灯带亮度的直接映射，实现 “云台转向→灯带变色” 的核心需求；
3. 扩展性：预留 GPIO1/2（UART）可叠加传感器，适配更复杂的联动场景（如避障时灯带闪烁）。