# PyQt6 许可证验证系统

一个完整的软件许可证验证解决方案，包含客户端控件、验证服务器和管理工具。支持机器码绑定、在线验证、过期时间设置等功能。

## 功能特点

### 客户端
- 美观的许可证激活对话框
- 支持机器码绑定
- 在线许可证验证
- 可自定义样式
- 配置文件管理
- 完整的错误处理

### 服务端
- RESTful API接口
- SQLite数据库存储
- 支持许可证过期时间
- 支持设备绑定
- 激活次数统计
- 管理员API密钥认证

### 管理工具
- 命令行许可证生成
- 许可证状态查询
- 许可证禁用功能
- 批量管理支持

## 系统架构

```
license_system/
│
├── README.md           # 说明文档
├── requirements.txt    # 依赖项
├── setup.py           # 安装配置
│
├── license_system/    # 客户端源代码
│   ├── __init__.py
│   ├── validator.py   # 验证逻辑
│   ├── config.json    # 配置文件
│   │
│   └── ui/
│       ├── __init__.py
│       ├── license_dialog.py  # 许可证对话框
│       └── styles.py         # 样式表
│
├── license_server/    # 服务端源代码
│   └── server.py      # Flask服务器实现
│
└── license_generator/ # 许可证生成工具
    ├── __init__.py
    ├── cli.py        # 命令行工具
    └── gui.py        # 图形界面工具
```

## 安装说明

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 安装客户端包：
```bash
pip install .
```

## 使用方法

### 1. 启动验证服务器

```bash
cd license_server
python server.py
```

服务器配置：
- 默认端口：5000
- 管理员密钥：在 server.py 中设置 `ADMIN_KEY`
- 数据库：自动创建 SQLite 数据库文件

### 2. 生成许可证

#### 2.1 图形界面版本

```bash
python -m license_generator.gui
```

#### 2.2 命令行版本

```bash
python -m license_generator.cli --admin-key your-admin-key --action generate --expires 365
```

### 3. 在应用中集成

```python
from PyQt6.QtWidgets import QMainWindow, QApplication
from license_system import LicenseDialog, LicenseValidator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.validator = LicenseValidator(
            server_url="http://your-license-server.com",
            config_path="config.json"
        )
        
    def check_license(self) -> bool:
        if not self.validator.validate_license():
            license_key = LicenseDialog.get_key(self)
            if license_key:
                if self.validator.save_license(license_key):
                    return self.validator.validate_license(license_key)
            return False
        return True

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    
    if window.check_license():
        window.show()
        app.exec()
```

## API文档

### 验证服务器API

1. 验证许可证
```
POST /validate
Content-Type: application/json

Request:
{
    "license_key": "xxxx-xxxx-xxxx-xxxx",
    "machine_code": "unique-machine-identifier"
}

Response:
{
    "valid": true/false,
    "message": "可选的错误消息"
}
```

2. 生成许可证（需要管理员密钥）
```
POST /admin/generate
X-Admin-Key: your-admin-key
Content-Type: application/json

Request:
{
    "expires_at": "2024-12-31 23:59:59"  // 可选
}

Response:
{
    "success": true,
    "license_key": "生成的许可证密钥"
}
```

3. 查询许可证（需要管理员密钥）
```
GET /admin/licenses
X-Admin-Key: your-admin-key

Response:
[
    {
        "license_key": "xxx",
        "machine_code": "xxx",
        "created_at": "xxx",
        "expires_at": "xxx",
        "is_active": true/false,
        "activation_count": 0
    }
]
```

4. 禁用许可证（需要管理员密钥）
```
POST /admin/deactivate
X-Admin-Key: your-admin-key
Content-Type: application/json

Request:
{
    "license_key": "要禁用的许可证密钥"
}

Response:
{
    "success": true/false
}
```

## 自定义样式

你可以通过修改 `styles.py` 文件来自定义对话框样式：

```python
from license_system.ui.styles import LICENSE_DIALOG_STYLE

# 修改样式
CUSTOM_STYLE = """
    QDialog {
        background-color: #ffffff;
    }
    /* 其他自定义样式 */
"""

# 在对话框中使用
class CustomLicenseDialog(LicenseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CUSTOM_STYLE)
```

## 安全建议

1. 服务器部署
   - 使用HTTPS
   - 修改默认管理员密钥
   - 设置防火墙规则
   - 定期备份数据库

2. 客户端配置
   - 使用加密存储配置文件
   - 实现离线验证机制
   - 添加防篡改检测

3. 许可证管理
   - 定期更换管理员密钥
   - 监控异常激活行为
   - 实施访问控制策略

## 依赖项

- Python 3.7+
- PyQt6 >= 6.4.0
- requests >= 2.28.0
- Flask (服务器)
- flask-cors (服务器)
- wmi >= 1.5.1 (仅Windows)

## 注意事项

1. 确保配置文件路径可写
2. 验证需要网络连接
3. Windows系统需要安装wmi模块
4. 建议使用HTTPS进行安全连接
5. 数据库文件需要定期备份
6. 管理员密钥需要妥善保管

## 许可证

MIT License 