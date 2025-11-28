# ESP32 MicroPython 开发环境配置指南

## 🛠️ 环境要求

### 必需软件
1. **Python 3.8+** (建议3.9或3.10)
2. **VS Code** (推荐1.75+版本)
3. **ESPTOOL** (固件烧录)
4. **mpremote** (官方推荐工具)

## 🚀 快速配置

### 1. 安装VS Code插件
```bash
# 推荐插件列表 (已在 extensions.json 中配置)
- MicroPython (Microsoft官方)
- Python (Microsoft官方)
- Pylance
- Black Formatter
- GitLens
```

### 2. 安装Python依赖
```bash
pip install -r requirements.txt
```

### 3. 配置ESP32连接
```bash
# 1. 烧录MicroPython固件 (首次使用)
esptool.py --chip esp32 --port COM3 erase_flash
esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-20231005-v1.21.0.bin

# 2. 连接测试
mpremote connect COM3 repl

# 3. 挂载当前项目 (开发时)
mpremote connect COM3 mount .
```

## 💻 开发工作流

### 推荐工作流程

#### 方法1: 使用 mpremount (推荐)
```bash
# 1. 挂载项目到ESP32
mpremote connect COM3 mount .

# 2. 在VS Code中编辑代码，自动同步到ESP32
# 3. 连接REPL进行调试
mpremote connect COM3 repl

# 4. 在REPL中运行
import main_control
```

#### 方法2: 使用传统上传
```bash
# 1. 编辑单个文件
# 2. 上传到ESP32
ampy --port COM3 put motor_driver.py

# 3. 运行程序
ampy --port COM3 run main_control.py
```

### VS Code 快捷键

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 运行当前文件 | `Ctrl+Shift+P` → "Run Current File" | 本地测试 |
| 上传到ESP32 | `Ctrl+Shift+P` → "Upload to ESP32" | 部署代码 |
| 连接REPL | `Ctrl+Shift+P` → "Run REPL" | 调试交互 |
| 格式化代码 | `Shift+Alt+F` | 代码格式化 |

## 🔧 项目结构优化

### 开发时推荐结构
```
gear-motor-has-hall-sentor/
├── lib/                    # MicroPython标准库扩展
│   └── your_libs/
├── src/                    # 源代码
│   ├── motor_driver.py
│   ├── encoder_reader.py
│   └── pid_controller.py
├── tests/                  # 测试文件
│   ├── test_motor.py
│   └── test_encoder.py
├── tools/                  # 工具脚本
│   ├── flash_esp32.py
│   └── monitor.py
├── docs/                   # 文档
├── .vscode/               # VS Code配置
├── config.py              # 配置文件
├── main.py                # 主程序 (ESP32运行)
└── README.md              # 项目说明
```

## 🚀 实用开发技巧

### 1. 代码调试
```python
# 使用串口输出调试信息
import utime
def debug_print(msg):
    timestamp = utime.ticks_ms()
    print(f"[{timestamp}] {msg}")

# 在motor_driver.py中添加调试
debug_print(f"电机速度设置为: {speed}")
```

### 2. 模块化开发
```python
# 创建通用工具模块
# utils.py
def safe_range(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
```

### 3. 配置管理
```python
# 使用现有的config.py
from config import get_system_config

# 获取平衡配置
config = get_system_config('balanced')
motor_config = config['motor']
pid_config = config['pid']
```

## 🔍 性能优化

### 1. 代码优化建议
- 避免频繁的字符串操作
- 使用整型运算代替浮点运算
- 合理使用定时器和中断

### 2. 内存管理
```python
# 检查内存使用
import gc
def print_memory():
    print(f"可用内存: {gc.mem_free()} bytes")
    print(f"已用内存: {gc.mem_alloc()} bytes")

# 定期清理内存
gc.collect()
```

## 🐛 常见问题解决

### 1. 连接问题
```bash
# 检查串口
mpremote connect COM3

# 如果连接失败，尝试重置ESP32
mpremote connect COM3 reset
```

### 2. 上传失败
```bash
# 手动删除main.py，重新上传
mpremote connect COM3 rm main.py
mpremote connect COM3 cp main.py :
```

### 3. 内存不足
```python
# 在代码中添加内存监控
if gc.mem_free() < 10000:  # 小于10KB
    gc.collect()
```

## 📚 进阶开发

### 1. 自动化测试
创建 `tests/` 目录，编写单元测试。

### 2. 版本控制
```bash
git init
git add .
git commit -m "Initial commit"
```

### 3. 持续集成
配置 GitHub Actions 自动化测试和部署。

## 🎯 最佳实践

1. **代码规范**: 使用 Black 格式化代码
2. **注释**: 为关键函数和类添加详细注释
3. **测试**: 编写测试用例验证功能
4. **版本管理**: 使用 Git 管理代码版本
5. **文档**: 保持 README.md 和代码文档更新

## 📞 技术支持

- [MicroPython官方文档](https://docs.micropython.org/)
- [ESP32技术参考](https://docs.espressif.com/projects/esp-idf/zh_CN/latest/)
- [VS Code MicroPython插件文档](https://marketplace.visualstudio.com/items?itemName=ms-python.micropython)

---

**开始你的ESP32 MicroPython开发之旅吧！** 🚀