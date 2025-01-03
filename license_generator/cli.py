import argparse
import requests
import json
from datetime import datetime, timedelta

class LicenseGenerator:
    def __init__(self, server_url: str, admin_key: str):
        self.server_url = server_url
        self.admin_key = admin_key
        
    def generate_license(self, expires_days: int = None) -> str:
        """
        生成新的许可证
        
        Args:
            expires_days: 许可证有效期（天数），None表示永久有效
        """
        expires_at = None
        if expires_days:
            expires_at = (datetime.now() + timedelta(days=expires_days)).strftime('%Y-%m-%d %H:%M:%S')
            
        response = requests.post(
            f"{self.server_url}/admin/generate",
            headers={'X-Admin-Key': self.admin_key},
            json={'expires_at': expires_at},
            verify=False
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result['license_key']
        raise Exception(f"生成许可证失败: {response.text}")
        
    def list_licenses(self) -> list:
        """获取所有许可证列表"""
        response = requests.get(
            f"{self.server_url}/admin/licenses",
            headers={'X-Admin-Key': self.admin_key},
            verify=False
        )
        
        if response.status_code == 200:
            return response.json()
        raise Exception(f"获取许可证列表失败: {response.text}")
        
    def deactivate_license(self, license_key: str) -> bool:
        """禁用许可证"""
        response = requests.post(
            f"{self.server_url}/admin/deactivate",
            headers={'X-Admin-Key': self.admin_key},
            json={'license_key': license_key},
            verify=False
        )
        
        if response.status_code == 200:
            return response.json().get('success', False)
        return False

def main():
    parser = argparse.ArgumentParser(description='许可证生成工具')
    parser.add_argument('--server', default='http://localhost:5000', help='许可证服务器地址')
    parser.add_argument('--admin-key', required=True, help='管理员密钥')
    parser.add_argument('--action', choices=['generate', 'list', 'deactivate'], required=True, help='操作类型')
    parser.add_argument('--expires', type=int, help='许可证有效期（天数）')
    parser.add_argument('--license-key', help='要禁用的许可证密钥')
    
    args = parser.parse_args()
    generator = LicenseGenerator(args.server, args.admin_key)
    
    try:
        if args.action == 'generate':
            license_key = generator.generate_license(args.expires)
            print(f"生成的许可证密钥: {license_key}")
            
        elif args.action == 'list':
            licenses = generator.list_licenses()
            print(json.dumps(licenses, indent=2, ensure_ascii=False))
            
        elif args.action == 'deactivate':
            if not args.license_key:
                print("错误: 需要提供要禁用的许可证密钥")
                return
            success = generator.deactivate_license(args.license_key)
            print(f"禁用许可证 {args.license_key}: {'成功' if success else '失败'}")
            
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == '__main__':
    main() 