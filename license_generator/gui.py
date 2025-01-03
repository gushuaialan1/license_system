import sys
import requests
import logging
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QTextEdit, QLabel, QLineEdit, QMessageBox,
                            QDateTimeEdit, QHBoxLayout, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDateTime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('license_generator.log'),
        logging.StreamHandler()
    ]
)

class GenerateThread(QThread):
    """后台生成许可证的线程"""
    success = pyqtSignal(dict)  # 成功信号
    error = pyqtSignal(str)     # 错误信号
    
    def __init__(self, server_url, admin_key, expires_at=None):
        super().__init__()
        self.server_url = server_url
        self.admin_key = admin_key
        self.expires_at = expires_at
        
    def run(self):
        try:
            # 准备请求数据
            json_data = {}
            if self.expires_at:
                json_data['expires_at'] = self.expires_at.strftime("%Y-%m-%d %H:%M:%S")
            
            logging.info(f"准备发送请求到: {self.server_url}")
            logging.info(f"请求数据: {json_data}")
            
            # 设置请求会话
            session = requests.Session()
            session.verify = False
            
            # 设置重试次数
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 发送请求
                    response = session.post(
                        f'{self.server_url}/admin/generate',
                        headers={'X-Admin-Key': self.admin_key},
                        json=json_data,
                        timeout=30  # 增加超时时间
                    )
                    
                    logging.info(f"服务器响应状态码: {response.status_code}")
                    logging.info(f"服务器响应内容: {response.text}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            self.success.emit(result)
                            return
                        else:
                            self.error.emit(f"生成失败: {result.get('error', '未知错误')}")
                            return
                    else:
                        self.error.emit(f"服务器响应错误: {response.status_code}\n{response.text}")
                        return
                        
                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logging.warning(f"请求失败，正在进行第 {retry_count} 次重试: {str(e)}")
                        continue
                    else:
                        logging.error(f"重试 {max_retries} 次后仍然失败")
                        if isinstance(e, requests.exceptions.ConnectionError):
                            self.error.emit("无法连接到服务器，请检查服务器地址和网络连接")
                        elif isinstance(e, requests.exceptions.Timeout):
                            self.error.emit("请求超时，请检查网络连接")
                        else:
                            self.error.emit(f"请求失败: {str(e)}")
                        return
                        
        except Exception as e:
            logging.error(f"生成许可证失败: {str(e)}")
            self.error.emit(f"生成许可证失败: {str(e)}")

class LicenseGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("许可证生成器")
        self.setMinimumSize(800, 600)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 服务器地址输入
        server_layout = QHBoxLayout()
        server_label = QLabel("服务器地址:")
        server_label.setMinimumWidth(100)
        self.server_input = QLineEdit()
        self.server_input.setText("http://localhost:5000")
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_input)
        layout.addLayout(server_layout)
        
        # 管理员密钥输入
        admin_key_layout = QHBoxLayout()
        admin_key_label = QLabel("管理员密钥:")
        admin_key_label.setMinimumWidth(100)
        self.admin_key_input = QLineEdit()
        self.admin_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        admin_key_layout.addWidget(admin_key_label)
        admin_key_layout.addWidget(self.admin_key_input)
        layout.addLayout(admin_key_layout)
        
        # 有效期设置
        expiry_layout = QHBoxLayout()
        expiry_label = QLabel("有效期设置:")
        expiry_label.setMinimumWidth(100)
        expiry_layout.addWidget(expiry_label)
        
        self.enable_expiry = QCheckBox("启用")
        self.enable_expiry.stateChanged.connect(self.toggle_expiry)
        expiry_layout.addWidget(self.enable_expiry)
        
        self.expiry_date = QDateTimeEdit()
        self.expiry_date.setDateTime(QDateTime.currentDateTime().addYears(1))
        self.expiry_date.setEnabled(False)
        expiry_layout.addWidget(self.expiry_date)
        expiry_layout.addStretch()
        layout.addLayout(expiry_layout)
        
        # 生成按钮
        self.generate_btn = QPushButton("生成新的许可证")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_license)
        layout.addWidget(self.generate_btn)
        
        # 结果显示区域
        result_label = QLabel("生成记录:")
        layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 10px;
                font-family: Consolas, Monaco, monospace;
            }
        """)
        layout.addWidget(self.result_text)
        
        # 底部按钮布局
        bottom_layout = QHBoxLayout()
        
        # 清空按钮
        clear_btn = QPushButton("清空记录")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        clear_btn.clicked.connect(self.clear_results)
        bottom_layout.addWidget(clear_btn)
        
        # 打开日志按钮
        open_log_btn = QPushButton("查看日志")
        open_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        open_log_btn.clicked.connect(self.open_log)
        bottom_layout.addWidget(open_log_btn)
        
        layout.addLayout(bottom_layout)
        
        logging.info("许可证生成器界面初始化完成")
        
    def toggle_expiry(self, state):
        self.expiry_date.setEnabled(state == Qt.CheckState.Checked)
        
    def generate_license(self):
        # 验证输入
        server_url = self.server_input.text().strip()
        admin_key = self.admin_key_input.text().strip()
        
        if not server_url:
            QMessageBox.warning(self, "错误", "请输入服务器地址")
            return
        if not admin_key:
            QMessageBox.warning(self, "错误", "请输入管理员密钥")
            return
            
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("正在生成...")
        
        # 获取过期时间
        expires_at = None
        if self.enable_expiry.isChecked():
            expires_at = self.expiry_date.dateTime().toPyDateTime()
        
        logging.info(f"开始生成许可证，服务器地址: {server_url}")
        
        # 创建并启动生成线程
        self.generate_thread = GenerateThread(server_url, admin_key, expires_at)
        self.generate_thread.success.connect(self.handle_success)
        self.generate_thread.error.connect(self.handle_error)
        self.generate_thread.finished.connect(self.handle_finished)
        self.generate_thread.start()
    
    def handle_success(self, result):
        license_key = result['license_key']
        expires_at = "永久有效"
        if self.enable_expiry.isChecked():
            expires_at = self.expiry_date.dateTime().toString("yyyy-MM-dd hh:mm:ss")
            
        success_msg = (f"许可证生成成功！\n"
                      f"许可证密钥: {license_key}\n"
                      f"有效期至: {expires_at}\n")
        self.result_text.append(success_msg)
        
        # 保存到文件
        with open('license_keys.txt', 'a', encoding='utf-8') as f:
            f.write(f"密钥: {license_key} | 有效期至: {expires_at}\n")
        self.result_text.append("密钥已保存到 license_keys.txt 文件\n")
        self.result_text.append("-" * 50 + "\n")
        
        logging.info(f"许可证生成成功: {license_key}")
    
    def handle_error(self, error_msg):
        QMessageBox.warning(self, "错误", error_msg)
        logging.error(f"生成失败: {error_msg}")
    
    def handle_finished(self):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("生成新的许可证")
        logging.info("生成过程结束")
            
    def clear_results(self):
        self.result_text.clear()
        logging.info("清空显示记录")
        
    def open_log(self):
        import os
        import platform
        
        log_file = "license_generator.log"
        if platform.system() == "Windows":
            os.system(f"notepad {log_file}")
        else:
            os.system(f"xdg-open {log_file}")

def main():
    logging.info("启动许可证生成器")
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = LicenseGeneratorWindow()
    window.show()
    sys.exit(app.exec()) 