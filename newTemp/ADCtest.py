from machine import ADC, Pin
import time

def read_adc_avg(adc, samples=10):
    """多次采样取平均，提高稳定性"""
    total = 0
    for _ in range(samples):
        total += adc.read()
        time.sleep_ms(1)
    return total // samples

try:
    # Try common valid ADC pins for ESP32
    # ADC1 pins (usually available): 32-39
    adc_x = ADC(Pin(34), atten=ADC.ATTN_11DB)  # Changed from 36 to 34
    adc_y = ADC(Pin(35), atten=ADC.ATTN_11DB)  # Changed from 37 to 35

    print("ADC initialized successfully!")
    print("Using ADC pins: X=34, Y=35")

    while True:
        adc_x_value = read_adc_avg(adc_x)
        adc_y_value = read_adc_avg(adc_y)
        print("ADC Value:", adc_x_value, adc_y_value)
        time.sleep(0.1)

except ValueError as e:
    print(f"Error: {e}")
    print("Please check if the pins are valid ADC pins for your board.")
    print("Common valid ADC pins for ESP32:")
    print("- ADC1: 32, 33, 34, 35, 36, 37, 38, 39")
    print("- ADC2: 0, 2, 4, 12, 13, 14, 15, 25, 26, 27")
    print("Note: Some ADC2 pins may be unavailable when Wi-Fi is active.")
