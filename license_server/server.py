from flask import Flask, request, jsonify
import sqlite3
import datetime
import logging
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE NOT NULL,
            machine_code TEXT,
            created_at DATETIME NOT NULL,
            expires_at DATETIME,
            is_active BOOLEAN DEFAULT 1,
            activation_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("数据库初始化完成")

@app.before_first_request
def setup():
    init_db()

@app.route('/validate', methods=['POST'])
def validate_license():
    """验证许可证"""
    try:
        data = request.json
        license_key = data.get('license_key')
        machine_code = data.get('machine_code')
        
        if not license_key or not machine_code:
            return jsonify({
                'valid': False,
                'message': '缺少必要参数'
            })
            
        conn = sqlite3.connect('licenses.db')
        c = conn.cursor()
        
        # 检查许可证是否存在且有效
        c.execute('''
            SELECT machine_code, expires_at, is_active, activation_count
            FROM licenses
            WHERE license_key = ?
        ''', (license_key,))
        
        result = c.fetchone()
        if not result:
            return jsonify({
                'valid': False,
                'message': '许可证不存在'
            })
            
        saved_machine_code, expires_at, is_active, activation_count = result
        
        # 检查是否已被禁用
        if not is_active:
            return jsonify({
                'valid': False,
                'message': '许可证已被禁用'
            })
            
        # 检查是否已过期
        if expires_at:
            expires_at = datetime.datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
            if expires_at < datetime.datetime.now():
                return jsonify({
                    'valid': False,
                    'message': '许可证已过期'
                })
        
        # 如果未绑定机器码，则绑定
        if not saved_machine_code:
            c.execute('''
                UPDATE licenses
                SET machine_code = ?, activation_count = 1
                WHERE license_key = ?
            ''', (machine_code, license_key))
            conn.commit()
            
        # 如果已绑定，检查是否匹配
        elif saved_machine_code != machine_code:
            return jsonify({
                'valid': False,
                'message': '许可证已绑定到其他设备'
            })
        else:
            # 更新激活次数
            c.execute('''
                UPDATE licenses
                SET activation_count = activation_count + 1
                WHERE license_key = ?
            ''', (license_key,))
            conn.commit()
            
        conn.close()
        return jsonify({'valid': True})
        
    except Exception as e:
        logging.error(f"验证许可证失败: {str(e)}")
        return jsonify({
            'valid': False,
            'message': str(e)
        })

@app.route('/admin/generate', methods=['POST'])
def generate_license():
    """生成新的许可证"""
    try:
        data = request.json
        admin_key = request.headers.get('X-Admin-Key')
        
        if not admin_key or admin_key != app.config['ADMIN_KEY']:
            return jsonify({'error': '未授权访问'}), 401
            
        # 生成许可证密钥
        import uuid
        license_key = str(uuid.uuid4())
        
        # 获取过期时间（可选）
        expires_at = data.get('expires_at')
        
        conn = sqlite3.connect('licenses.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO licenses (license_key, created_at, expires_at)
            VALUES (?, ?, ?)
        ''', (license_key, datetime.datetime.now(), expires_at))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'license_key': license_key
        })
        
    except Exception as e:
        logging.error(f"生成许可证失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/licenses', methods=['GET'])
def list_licenses():
    """列出所有许可证"""
    try:
        admin_key = request.headers.get('X-Admin-Key')
        if not admin_key or admin_key != app.config['ADMIN_KEY']:
            return jsonify({'error': '未授权访问'}), 401
            
        conn = sqlite3.connect('licenses.db')
        c = conn.cursor()
        c.execute('''
            SELECT license_key, machine_code, created_at, expires_at, is_active, activation_count
            FROM licenses
        ''')
        
        licenses = [{
            'license_key': row[0],
            'machine_code': row[1],
            'created_at': row[2],
            'expires_at': row[3],
            'is_active': row[4],
            'activation_count': row[5]
        } for row in c.fetchall()]
        
        conn.close()
        return jsonify(licenses)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/deactivate', methods=['POST'])
def deactivate_license():
    """禁用许可证"""
    try:
        admin_key = request.headers.get('X-Admin-Key')
        if not admin_key or admin_key != app.config['ADMIN_KEY']:
            return jsonify({'error': '未授权访问'}), 401
            
        license_key = request.json.get('license_key')
        if not license_key:
            return jsonify({'error': '缺少许可证密钥'}), 400
            
        conn = sqlite3.connect('licenses.db')
        c = conn.cursor()
        c.execute('''
            UPDATE licenses
            SET is_active = 0
            WHERE license_key = ?
        ''', (license_key,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.config['ADMIN_KEY'] = 'your-admin-key-here'  # 设置管理员密钥
    app.run(host='0.0.0.0', port=5000) 