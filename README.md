# 考勤助手 (Attendance Assistant)

一个基于 Python 的桌面应用程序，用于自动解析考勤图片并进行可视化展示和数据导出。

## ✨ 功能特性

- 📸 **图片自动解析**: 支持上传考勤图片，自动识别日期、时间和打卡状态
- 🔍 **OCR 文字识别**: 集成 PaddleOCR 引擎，准确识别图片中的文字信息
- 🎯 **图案识别**: 自动检测绿色圆点（正常）和灰色圆点（异常）状态
- 📅 **日历可视化**: 以直观的月历形式展示考勤数据
- ✏️ **数据编辑**: 支持手动修正 OCR 识别错误的数据
- 📊 **统计分析**: 自动计算出勤率、异常次数等统计信息
- 💾 **多格式导出**: 支持导出为 Excel、CSV 格式
- 🎨 **友好界面**: 基于 PyQt6 的现代化用户界面

## 🔧 系统要求

- Python 3.8+
- Windows 10+ / macOS 10.15+ / Linux
- 内存: 4GB 以上推荐
- 硬盘: 500MB 可用空间

## 🚀 快速开始

### 方式一：使用 uv（推荐）

```bash
# 1. 克隆项目
git clone https://gitclone.com/github.com/WeiGu-S/Attendence_Assistant.git

# 2. 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# 或 Windows PowerShell:
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. 安装依赖并运行
uv sync
uv run python -m attendance_assistant
```

### 方式二：使用 pip

```bash
# 1. 克隆项目
git clone https://gitclone.com/github.com/WeiGu-S/Attendence_Assistant.git

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -e .

# 4. 运行程序
uv run python -m attendance_assistant
```

## 使用指南

### 1. 上传考勤图片

- 点击"选择考勤图片"按钮
- 选择包含考勤信息的图片文件（支持 PNG、JPG、JPEG 等格式）
- 程序将自动处理图片并显示结果

### 2. 查看考勤数据

- 处理完成后，考勤数据将以日历形式显示
- 不同颜色表示不同的打卡状态：
  - 绿色：正常打卡
  - 橙色：异常打卡
  - 红色：未打卡
  - 灰色：休息日

### 3. 编辑数据

- 点击日历中的任意日期
- 在左侧控制面板中编辑该日的考勤信息
- 支持修改时间、状态等信息

### 4. 导出数据

- 选择导出格式（Excel 或 CSV）
- 点击"导出数据"按钮
- 选择保存位置即可完成导出

## 📁 项目结构

```
attendance-assistant/
├── attendance_assistant/          # 主应用包
│   ├── __init__.py
│   ├── __main__.py               # 主程序入口
│   ├── core/                     # 核心模块
│   │   ├── __init__.py
│   │   ├── models.py            # 数据模型
│   │   ├── exceptions.py        # 自定义异常
│   │   ├── utils.py             # 工具函数
│   │   └── config_manager.py    # 配置管理
│   ├── services/                # 服务层
│   │   ├── __init__.py
│   │   ├── image_processor.py   # 图像处理
│   │   ├── ocr_service.py       # OCR服务
│   │   └── data_exporter.py     # 数据导出
│   ├── controllers/             # 控制器层
│   │   ├── __init__.py
│   │   └── main_controller.py   # 主控制器
│   ├── gui/                     # 用户界面
│   │   ├── __init__.py
│   │   ├── main_window.py       # 主窗口
│   │   ├── attendance_calendar.py # 日历组件
│   │   └── control_panel.py     # 控制面板
│   └── resources/               # 资源文件
│       ├── __init__.py
│       ├── styles.qss           # 样式表
│       └── icons/               # 图标文件
├── pyproject.toml              # 项目配置
├── requirements.txt            # 生产依赖
├── Makefile                    # 构建脚本
└── README.md                   # 项目说明
```

## 配置说明

程序首次运行时会自动创建`config.ini`配置文件，包含以下配置项：

### OCR 配置

```ini
[OCR]
use_gpu = False              # 是否使用GPU加速
model_path = ./models        # OCR模型路径
confidence_threshold = 0.5   # 识别置信度阈值
```

### UI 配置

```ini
[UI]
language = zh_CN            # 界面语言
theme = light               # 界面主题
window_width = 1200         # 窗口宽度
window_height = 800         # 窗口高度
```

### 导出配置

```ini
[Export]
default_format = excel      # 默认导出格式
default_path = ./exports    # 默认导出路径
```

## 技术架构

- **GUI 框架**: PyQt6
- **OCR 引擎**: PaddleOCR
- **图像处理**: OpenCV
- **数据处理**: Pandas, NumPy
- **数据导出**: openpyxl (Excel), csv (CSV)

## 开发说明

### 添加新功能

1. 在相应模块中实现功能
2. 更新数据模型（如需要）
3. 修改 GUI 界面（如需要）
4. 更新配置文件（如需要）

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写详细的文档字符串
- 适当的错误处理和日志记录

## 常见问题

### Q: OCR 识别准确率不高怎么办？

A:

1. 确保图片清晰度足够
2. 调整 OCR 置信度阈值
3. 手动修正识别错误的数据

### Q: 程序运行缓慢怎么办？

A:

1. 如果有 GPU，可以在配置中启用 GPU 加速
2. 确保图片尺寸适中，过大的图片会影响处理速度
3. 关闭其他占用内存的程序

### Q: 导出的数据格式不符合要求？

A: 可以修改`data_exporter.py`中的导出逻辑，自定义导出格式和内容。

## 📦 构建和分发

### 构建 Python 包

```bash
uv run python -m build
```

### 构建可执行文件

```bash
# 使用构建脚本
python scripts/build.py --exe

# 或直接使用 PyInstaller
pyinstaller --name="AttendanceAssistant" \
            --windowed \
            --onefile \
            attendance_assistant/__main__.py
```

⭐ 如果这个项目对你有帮助，请给我们一个星标！
