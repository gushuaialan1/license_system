from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from .styles import LICENSE_DIALOG_STYLE

class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("软件激活")
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # 应用样式
        self.setStyleSheet(LICENSE_DIALOG_STYLE)
        
        # 创建布局
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加说明文本
        info_label = QLabel("请输入许可证密钥以激活软件：")
        layout.addWidget(info_label)
        
        # 添加输入框
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("请输入许可证密钥")
        layout.addWidget(self.key_input)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        self.activate_btn = QPushButton("激活")
        self.activate_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.activate_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def get_license_key(self):
        """获取输入的许可证密钥"""
        return self.key_input.text().strip()
    
    @staticmethod
    def get_key(parent=None):
        """显示对话框并获取许可证密钥"""
        dialog = LicenseDialog(parent)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return dialog.get_license_key()
        return None 