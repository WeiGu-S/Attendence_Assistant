# 考勤助手（Attendance Assistant）详细设计文档

## 1. 引言

### 1.1 文档目的
本文档旨在为"考勤助手"桌面应用程序的开发提供详细的技术指导和实现方案，基于之前的产品需求文档(PRD)，确保开发团队能够按照统一的标准和架构进行开发工作。

### 1.2 范围
本文档涵盖系统的整体架构、模块设计、接口定义、数据结构和关键技术实现细节。

### 1.3 目标读者
Python开发人员、测试工程师、项目管理人员及相关利益方。

## 2. 系统架构设计

### 2.1 整体架构
```
┌─────────────────────────────────────────────────┐
│                  表示层 (Presentation)          │
│  ┌─────────────────────────────────────────┐    │
│  │                GUI界面                  │    │
│  │   ┌─────────────┐  ┌────────────────┐   │    │
│  │   │   日历视图   │  │   控制面板     │   │    │
│  │   └─────────────┘  └────────────────┘   │    │
│  └─────────────────────────────────────────┘    │
├─────────────────────────────────────────────────┤
│                业务逻辑层 (Business Logic)      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  图像处理   │  │  考勤分析   │  │ 数据导出 │ │
│  └─────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────┤
│                数据访问层 (Data Access)         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  OCR服务    │  │  文件IO     │  │ 配置管理 │ │
│  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────┘
```

### 2.2 技术栈选择
- **GUI框架**: PyQt5 (版本5.15.x)
- **OCR引擎**: PaddleOCR (版本2.6.x)
- **图像处理**: OpenCV (版本4.6.x)
- **数据处理**: Pandas (版本1.5.x), NumPy (版本1.23.x)
- **数据导出**: openpyxl (用于Excel导出)
- **日志管理**: logging (Python标准库)
- **配置管理**: configparser (Python标准库)

### 2.3 开发环境要求
- Python 3.8+
- 包管理工具：uv
- 支持的操作系统: Windows 10+, macOS 10.15+

## 3. 模块详细设计

### 3.1 图像处理模块 (ImageProcessor)

#### 3.1.1 类设计
```python
class ImageProcessor:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def load_image(self, image_path: str) -> np.ndarray:
        """加载图片并返回numpy数组"""
        pass
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理流程:
        1. 灰度化
        2. 高斯模糊去噪
        3. 二值化(OTSU)
        4. 形态学操作(闭运算)
        """
        pass
        
    def detect_table_cells(self, processed_image: np.ndarray) -> List[Dict]:
        """
        检测表格单元格位置
        返回: [{x, y, width, height, row, col}, ...]
        """
        pass
        
    def extract_cell_image(self, original_image: np.ndarray, cell_info: Dict) -> np.ndarray:
        """提取单个单元格图像"""
        pass
        
    def detect_dots(self, cell_image: np.ndarray) -> List[Dict]:
        """
        检测单元格内的圆点
        返回: [{x, y, color, radius}, ...]
        颜色分类: 绿色(正常), 灰色(异常)
        """
        pass
```

### 3.2 OCR服务模块 (OCRService)

#### 3.2.1 类设计
```python
class OCRService:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        # 初始化PaddleOCR实例
        self.ocr_engine = None
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """初始化OCR引擎"""
        from paddleocr import PaddleOCR
        self.ocr_engine = PaddleOCR(
            use_angle_cls=True,
            lang="ch",
            use_gpu=self.config.getboolean('OCR', 'use_gpu', fallback=False),
            ocr_version='PP-OCRv3'
        )
    
    def recognize_text(self, image: np.ndarray) -> List[str]:
        """识别图像中的文本"""
        pass
        
    def extract_date_info(self, text_results: List[str]) -> Dict:
        """从OCR结果中提取日期信息"""
        pass
        
    def extract_time_info(self, text_results: List[str]) -> Dict:
        """从OCR结果中提取时间信息"""
        pass
```

### 3.3 考勤数据模型 (AttendanceDataModel)

#### 3.3.1 数据结构
```python
@dataclass
class ClockRecord:
    time: str  # 时间字符串 "HH:MM"
    status: str  # 状态: "正常", "异常", "未打卡"
    
@dataclass
class DailyAttendance:
    date: str  # 日期字符串 "YYYY-MM-DD"
    day_of_week: str  # 星期几: "周一" - "周日"
    day_type: str  # 日期类型: "工作日", "休息日", "节假日"
    clock_in: ClockRecord  # 上班打卡记录
    clock_out: ClockRecord  # 下班打卡记录
    is_confirmed: bool = False  # 是否已确认
    
@dataclass
class MonthlyAttendance:
    year_month: str  # 年月标识 "YYYY-MM"
    data: List[DailyAttendance]  # 每日考勤数据
    statistics: Dict[str, int]  # 统计信息
```

### 3.4 主控制器模块 (MainController)

#### 3.4.1 类设计
```python
class MainController:
    def __init__(self, view):
        self.view = view
        self.config = ConfigManager()
        self.image_processor = ImageProcessor(self.config)
        self.ocr_service = OCRService(self.config)
        self.current_data = None
        
    def process_uploaded_image(self, image_path: str):
        """处理上传的图片完整流程"""
        # 1. 加载图像
        # 2. 预处理
        # 3. 检测表格单元格
        # 4. 提取文本和图案信息
        # 5. 构建数据模型
        # 6. 更新视图
        
    def export_to_excel(self, file_path: str):
        """导出数据到Excel"""
        pass
        
    def update_attendance_record(self, date: str, field: str, value: str):
        """更新考勤记录"""
        pass
        
    def confirm_attendance(self, date: str):
        """确认考勤记录"""
        pass
```

### 3.5 用户界面模块 (GUI)

#### 3.5.1 主窗口设计 (MainWindow)
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = MainController(self)
        self._setup_ui()
        
    def _setup_ui(self):
        """初始化UI界面"""
        # 主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # 左侧控制面板
        control_panel = self._create_control_panel()
        
        # 右侧日历视图
        calendar_view = self._create_calendar_view()
        
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(calendar_view, 3)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def _create_control_panel(self) -> QWidget:
        """创建控制面板"""
        pass
        
    def _create_calendar_view(self) -> QWidget:
        """创建日历视图"""
        pass
        
    def update_calendar_display(self, data: MonthlyAttendance):
        """更新日历显示"""
        pass
        
    def show_statistics(self, stats: Dict[str, int]):
        """显示统计信息"""
        pass
```

#### 3.5.2 自定义日历部件 (AttendanceCalendar)
```python
class AttendanceCalendar(QWidget):
    """自定义日历部件，显示考勤状态"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.attendance_data = None
        self.current_year_month = None
        
    def set_attendance_data(self, data: MonthlyAttendance):
        """设置考勤数据并刷新显示"""
        pass
        
    def paintEvent(self, event):
        """自定义绘制日历"""
        pass
        
    def mousePressEvent(self, event):
        """处理鼠标点击事件，用于数据编辑"""
        pass
```

## 4. 数据流设计

### 4.1 图片处理流程
```
1. 用户上传图片 → 
2. 图像加载和预处理 → 
3. 表格单元格检测 → 
4. 单元格内容提取(OCR文本识别 + 圆点检测) → 
5. 数据关联和结构化 → 
6. 生成考勤数据模型 → 
7. 界面显示更新
```

### 4.2 数据导出流程
```
1. 用户点击导出按钮 → 
2. 选择导出路径和格式 → 
3. 将考勤数据模型转换为DataFrame → 
4. 生成统计信息 → 
5. 写入文件(CSV/Excel) → 
6. 完成提示
```

## 5. 接口定义

### 5.1 模块间接口

#### 5.1.1 图像处理接口
```python
def process_attendance_image(image_path: str) -> MonthlyAttendance:
    """处理考勤图片并返回结构化数据"""
    pass
```

#### 5.1.2 数据导出接口
```python
def export_attendance_data(data: MonthlyAttendance, 
                          file_path: str, 
                          format: str = 'excel') -> bool:
    """导出考勤数据到指定格式文件"""
    pass
```

### 5.2 配置文件接口
```ini
[OCR]
use_gpu = False
model_path = ./models

[UI]
language = zh_CN
theme = light

[Export]
default_format = excel
default_path = ./exports
```

## 6. 数据库设计

### 6.1 本地数据存储
由于是桌面应用程序，使用JSON文件进行数据持久化：

```json
{
  "version": "1.0",
  "processed_images": [
    {
      "image_path": "/path/to/image.jpg",
      "process_date": "2023-10-15T14:30:00",
      "attendance_data": { ... }
    }
  ],
  "user_settings": {
    "language": "zh_CN",
    "export_default_path": "./exports"
  }
}
```

## 7. 错误处理与日志

### 7.1 异常分类
- **ImageLoadError**: 图片加载失败
- **OCRProcessingError**: OCR识别错误
- **DataValidationError**: 数据验证错误
- **ExportError**: 数据导出错误

### 7.2 日志配置
```python
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'detailed'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
})
```

## 8. 部署与打包

### 8.1 打包脚本
使用PyInstaller进行打包：
```bash
pyinstaller --name="AttendanceAssistant" \
            --windowed \
            --icon=assets/icon.ico \
            --add-data="models;models" \
            --hidden-import=paddle \
            main.py
```

### 8.2 依赖管理
使用requirements.txt管理依赖：
```
PyQt5==5.15.7
paddleocr==2.6.1.3
opencv-python==4.6.0.66
pandas==1.5.0
numpy==1.23.4
openpyxl==3.0.10
```


## 附录

### A. 参考资料
- PyQt5官方文档
- PaddleOCR使用指南
- OpenCV图像处理教程

### B. 开发规范
- PEP 8代码风格规范
- 使用类型注解
- 文档字符串要求
- 要求项目工程化结构

---

本详细设计文档为开发工作提供了全面的技术指导，开发团队应严格按照此文档进行实现。如有任何设计变更，应及时更新本文档并通知所有相关人员。