LICENSE_DIALOG_STYLE = """
    QDialog {
        background-color: #f5f5f5;
    }
    QLabel {
        font-size: 11pt;
        color: #333333;
    }
    QLineEdit {
        padding: 5px;
        border: 1px solid #cccccc;
        border-radius: 4px;
        font-size: 11pt;
        min-width: 250px;
        background-color: white;
    }
    QLineEdit:focus {
        border: 1px solid #2196F3;
    }
    QPushButton {
        background-color: #2196F3;
        color: white;
        border: none;
        padding: 6px 15px;
        border-radius: 4px;
        min-width: 80px;
        font-size: 11pt;
    }
    QPushButton:hover {
        background-color: #1976D2;
    }
    QPushButton:pressed {
        background-color: #1565C0;
    }
    QPushButton[text="取消"] {
        background-color: #757575;
    }
    QPushButton[text="取消"]:hover {
        background-color: #616161;
    }
""" 