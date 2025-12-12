## ESP32 / WROOM

![img](https://micropython.org/resources/micropython-media/boards/ESP32_GENERIC/esp32_devkitc.jpg)

**Vendor:** Espressif

**Features:** BLE, External Flash, WiFi

**Source on GitHub:** [esp32/ESP32_GENERIC](https://github.com/micropython/micropython/tree/master/ports/esp32/boards/ESP32_GENERIC)

**More info:** [Website](https://www.espressif.com/en/products/modules)

以下固件适用于大多数基于ESP32且具有4MiB或更大闪存容量的开发板，包括WROOM WROVER、SOLO、PICO和MINI模块。

该电路板提供多种变体：

- 如果您的开发板基于WROVER模块，或具备SPIRAM（也称为PSRAM）功能，则建议使用"spiram"变体。请参阅标题为"SPIRAM/WROVER支持"的部分。
- 如果您的开发板搭载的是ESP32-D2WD芯片（仅配备2MiB闪存），请使用"d2wd"版本。请查找标题为ESP32 D2WD的内容。
- 如果您的开发板采用单核ESP32（例如"SOLO"模块），请选择"unicore"版本。请查找标题为ESP32 Unicore的选项。
- 若需对MicroPython固件执行空中下载更新，请选择"ota"版本。该版本因支持OTA功能，其闪存中用于存储Python文件的空间较少。请查阅标题为"OTA支持"的章节。

否则，请下载通用版本（位于下方第一个标题下）。

## Installation instructions

使用esptool.py程序对开发板进行编程，该程序可在[here](https://docs.espressif.com/projects/esptool/en/latest/esp32/)找到。Windows用户请注意：您安装的程序可能名为esptool而非esptool.py。

### Erasing

若您是首次在开发板上安装MicroPython，则应先使用以下命令擦除整个闪存：

```bash
esptool.py erase_flash
```

`esptool.py` 将尝试自动检测连接 ESP32 的串口，但若检测失败或计算机上连接了多个基于 Espressif 的设备，请使用 `--port` 选项指定目标串口名称。例如：

```bash
esptool.py --port PORTNAME erase_flash
```

- On Linux, 端口名称通常类似于 `/dev/ttyUSB` 或 `/dev/ttyACM0`。
- On Mac, the port name is usually similar to `/dev/cu.usbmodem01`.
- On Windows, the port name is usually similar to `COM4`.

### Flashing

然后将固件部署到开发板上，起始地址为`0x1000`：

```bash
esptool.py --baud 460800 write_flash 0x1000 ESP32_BOARD_NAME-DATE-VERSION.bin
```

请用从本页面下载的`.bin`文件替换`ESP32_BOARD_NAME-DATE-VERSION.bin`。如上所述，如果`esptool.py`无法自动检测串口，则可通过命令行显式指定。例如：

```bash
esptool.py --port PORTNAME --baud 460800 write_flash 0x1000 ESP32_BOARD_NAME-DATE-VERSION.bin
```

### Troubleshooting

如果刷写开始后中途失败，请尝试移除 --baud 460800 选项，改用较慢的默认速度进行刷写。

如果这些步骤无效，请参考  [MicroPython ESP32 Troubleshooting steps](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html#troubleshooting-installation-problems)  故障排除步骤和 [esptool documentation](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/basic-options.html)。

**Important**: 从以下选项中，下载适用于您开发板的 .bin 文件。