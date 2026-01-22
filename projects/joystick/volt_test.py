from machine import ADC, Pin
import time

# 初始化摇杆X/Y轴ADC（与项目引脚一致）
# GPIO4 = VRX（X轴），GPIO5 = VRY（Y轴）
vrx_adc = ADC(Pin(4))
vry_adc = ADC(Pin(5))

# 关键配置：11dB衰减（支持0-3.9V量程），12位采样（0-4095）
vrx_adc.atten(ADC.ATTN_11DB)
vrx_adc.width(ADC.WIDTH_12BIT)
vry_adc.atten(ADC.ATTN_11DB)
vry_adc.width(ADC.WIDTH_12BIT)

# 存储极值的变量
vrx_min = 4095  # 初始化为最大值
vrx_max = 0     # 初始化为最小值
vry_min = 4095
vry_max = 0

print("开始校准摇杆（持续10秒）：")
print("请缓慢、完整地拨动X轴（左右）和Y轴（上下），覆盖所有位置！")

start_time = time.time()
# 持续采样10秒，记录极值
while time.time() - start_time < 10:
    # 读取ADC原始值
    vrx_val = vrx_adc.read()
    vry_val = vry_adc.read()

    # 更新X轴极值
    if vrx_val < vrx_min:
        vrx_min = vrx_val
    if vrx_val > vrx_max:
        vrx_max = vrx_val

    # 更新Y轴极值
    if vry_val < vry_min:
        vry_min = vry_val
    if vry_val > vry_max:
        vry_max = vry_val

    # 实时打印当前值（方便观察）
    # ADC值转电压：电压 = ADC值 * 3.3 / 4095
    vrx_volt = vrx_val * 3.3 / 4095
    vry_volt = vry_val * 3.3 / 4095
    print(f"X轴：ADC={vrx_val} | 电压={vrx_volt:.2f}V | Y轴：ADC={vry_val} | 电压={vry_volt:.2f}V")
    time.sleep(0.05)

# 打印最终校准结果
print("\n=== 摇杆校准结果 ===")
print(f"X轴（VRX）：")
print(f"  ADC极值：{vrx_min} ~ {vrx_max}")
print(f"  电压极值：{vrx_min*3.3/4095:.2f}V ~ {vrx_max*3.3/4095:.2f}V")
print(f"Y轴（VRY）：")
print(f"  ADC极值：{vry_min} ~ {vry_max}")
print(f"  电压极值：{vry_min*3.3/4095:.2f}V ~ {vry_max*3.3/4095:.2f}V")
