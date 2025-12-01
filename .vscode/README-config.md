# VSCode MicroPython ESP32 开发配置说明

## 📁 配置文件结构

### launch.json - 调试配置
- **功能**: MicroPython串口监视器
- **串口**: COM5 (需根据实际设备修改)
- **波特率**: 115200
- **退出字符**: Ctrl+C (ASCII 3)

### settings.json - VSCode环境设置
- **Python解释器**: 系统PATH中的python
- **代码补全**: MicroPython stubs位于./stubs目录
- **串口配置**: COM5, 115200波特率
- **类型检查**: 基础模式，禁用导入检查
- **格式化**: Python文件保存时自动格式化

### tasks.json - 自动化任务
- **连接管理**: 检测/断开ESP32连接
- **文件操作**: 上传/运行当前Python文件
- **REPL访问**: 打开MicroPython交互终端
- **复合任务**: 完整的开发工作流

## 🔧 使用说明

### 必需插件
1. Python扩展 (ms-python.python)
2. MicroPython扩展 (ms-vscode.micropython-preview)

### 环境要求
1. Python 3.8+
2. mpremote工具: `pip install mpremote`
3. pyserial库: `pip install pyserial`

### 串口配置
1. 在设备管理器中查看ESP32串口号
2. 修改所有配置文件中的COM5为实际串口
3. 波特率保持115200不变

### 常用任务快捷键
- `Ctrl+Shift+P` → "Tasks: Run Task" → 选择任务
- 推荐任务: "mpremote: Upload and Run Current File"

## ⚠️ 注意事项
- 确保ESP32已刷入MicroPython固件
- 单个串口只能被一个程序占用
- 任务执行前请断开其他串口监视工具
- 硬编码路径需根据实际环境调整