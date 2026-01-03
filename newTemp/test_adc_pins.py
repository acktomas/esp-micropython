from machine import ADC, Pin
import time

# Test common ADC pins for ESP32 boards
possible_pins = [35, 36, 37, 38, 39,40,41,42,45,46,47,48]

print("Testing ADC pins...")
for pin_num in possible_pins:
    try:
        # Try to create ADC with this pin
        adc = ADC(Pin(pin_num), atten=ADC.ATTN_11DB)
        value = adc.read()
        print(f"✓ Pin {pin_num}: Valid ADC pin, value={value}")
        time.sleep(0.1)
    except Exception as e:
        print(f"✗ Pin {pin_num}: Error - {e}")

# Test ADC2 pins for ESP32
adc2_pins = [0, 1, 2,3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,16,17,18 ,19,20, 21, 25, 26, 27]
print("\nTesting ADC2 pins...")
for pin_num in adc2_pins:
    try:
        # ADC2 requires different initialization on some boards
        adc = ADC(Pin(pin_num))
        value = adc.read()
        print(f"✓ Pin {pin_num}: Valid ADC2 pin, value={value}")
        time.sleep(0.1)
    except Exception as e:
        print(f"✗ Pin {pin_num}: Error - {e}")
