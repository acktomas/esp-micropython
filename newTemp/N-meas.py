from machine import Pin
import time

# 替换为你的实际 GPIO 号
PIN_A = 4
PIN_B = 5

pinA = Pin(PIN_A, Pin.IN, Pin.PULL_UP)
pinB = Pin(PIN_B, Pin.IN, Pin.PULL_UP)

# 全局计数与前一状态
count = 0
prev = (pinA.value() << 1) | pinB.value()

# 四倍频方向查找表（索引 = (prev << 2) | curr）
# 有效序列：00->01->11->10->00 为 +1；反向为 -1；其他或抖动为 0
lookup = [
    0,  +1, -1,  0,
   -1,  0,  0, +1,
   +1,  0,  0, -1,
    0, -1, +1,  0
]

def irq_handler(pin):
    global count, prev
    curr = (pinA.value() << 1) | pinB.value()
    idx = (prev << 2) | curr
    count += lookup[idx]
    prev = curr

# 双边沿触发，实现四倍频
pinA.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=irq_handler)
pinB.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=irq_handler)

def reset_count():
    global count, prev
    count = 0
    prev = (pinA.value() << 1) | pinB.value()

def read_count():
    return count

# 测试流程示例：
reset_count()
print("开始，count=0")
# 手动缓慢转动输出轴一整圈，回到标记位置
time.sleep(20)  # 仅占位，实际请在完成一圈后再读取
print("N_meas =", abs(read_count()))
if read_count() >= 0:
    print("方向为正（约定为顺时针）")
else:
    print("方向为负（约定为逆时针）")

# 根据 N_meas 计算换算与阈值
N_meas = abs(read_count())
deg_per_count = 360.0 / N_meas
epsilon_counts = max(1, round(N_meas / 360.0))
print("每计数角度(°) =", deg_per_count)
print("±1°对应计数阈值 =", epsilon_counts)