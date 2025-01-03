import os
import json
import requests
import logging
import platform
import uuid
import wmi
from typing import Optional

class LicenseValidator:
    def __init__(self, server_url: str, config_path: str = "config.json"):
        """
        初始化许可证验证器
        
        Args:
            server_url: 验证服务器地址
            config_path: 配置文件路径
        """
        self.server_url = server_url
        self.config_file = config_path
        
    def get_machine_code(self) -> str:
        """获取机器唯一标识码"""
        try:
            c = wmi.WMI()
            # 获取CPU序列号
            cpu = c.Win32_Processor()[0].ProcessorId.strip()
            # 获取主板序列号
            board = c.Win32_BaseBoard()[0].SerialNumber.strip()
            # 获取BIOS序列号
            bios = c.Win32_BIOS()[0].SerialNumber.strip()
            
            # 组合信息并生成唯一标识
            machine_info = f"{cpu}-{board}-{bios}"
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, machine_info))
            
        except Exception as e:
            logging.error(f"获取机器码失败: {str(e)}")
            # 如果获取硬件信息失败，使用系统信息生成备用标识
            system_info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, system_info))
    
    def load_license(self) -> Optional[str]:
        """从配置文件加载许可证"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('license_key')
            return None
        except Exception as e:
            logging.error(f"加载许可证失败: {str(e)}")
            return None
    
    def save_license(self, license_key: str) -> bool:
        """保存许可证到配置文件"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['license_key'] = license_key
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
            
        except Exception as e:
            logging.error(f"保存许可证失败: {str(e)}")
            return False
            
    def validate_license(self, license_key: Optional[str] = None) -> bool:
        """
        验证许可证
        
        Args:
            license_key: 可选的许可证密钥，如果不提供则从配置文件加载
        """
        try:
            if not license_key:
                license_key = self.load_license()
                if not license_key:
                    return False
                
            machine_code = self.get_machine_code()
            
            response = requests.post(
                f"{self.server_url}/validate",
                json={
                    'license_key': license_key,
                    'machine_code': machine_code
                },
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('valid', False)
            return False
            
        except Exception as e:
            logging.error(f"验证许可证失败: {str(e)}")
            return False 