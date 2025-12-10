# -*- coding: utf-8 -*-
"""
系统配置路由 - 提供健康检查和配置管理接口
"""

from flask import Blueprint, render_template, request, jsonify
import os
import re
from pathlib import Path
from werkzeug.utils import secure_filename

# 创建Blueprint
setup_bp = Blueprint('setup', __name__)

# 导入健康检查模块
from utils.health_check import run_health_check

# 导入训练数据导入器
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.training_data_importer import KeepDataImporter


@setup_bp.route('/setup')
def setup_page():
    """配置页面"""
    return render_template('setup.html')


@setup_bp.route('/api/health_check')
def api_health_check():
    """健康检查API"""
    try:
        results = run_health_check()
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'健康检查失败: {str(e)}'
        }), 500


@setup_bp.route('/api/get_config')
def get_config():
    """获取当前配置"""
    try:
        config_file = Path('config.py')
        if not config_file.exists():
            return jsonify({
                'success': False,
                'message': '配置文件不存在'
            }), 404

        # 读取配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析配置项
        config_data = {
            'llm_api_key': extract_config_value(content, 'LLM_API_KEY'),
            'llm_base_url': extract_config_value(content, 'LLM_BASE_URL'),
            'default_model': extract_config_value(content, 'DEFAULT_MODEL_NAME'),
            'report_model': extract_config_value(content, 'REPORT_MODEL_NAME'),
            'tavily_api_key': extract_config_value(content, 'TAVILY_API_KEY'),
            'bocha_api_key': extract_config_value(content, 'BOCHA_WEB_SEARCH_API_KEY'),
            'db_host': extract_config_value(content, 'DB_HOST'),
            'db_port': extract_config_value(content, 'DB_PORT'),
            'db_user': extract_config_value(content, 'DB_USER'),
            'db_password': extract_config_value(content, 'DB_PASSWORD'),
            'db_name': extract_config_value(content, 'DB_NAME'),
            'training_data_source': extract_config_value(content, 'TRAINING_DATA_SOURCE'),
            'garmin_email': extract_config_value(content, 'GARMIN_EMAIL'),
            'garmin_password': extract_config_value(content, 'GARMIN_PASSWORD')
        }

        return jsonify({
            'success': True,
            'data': config_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'读取配置失败: {str(e)}'
        }), 500


@setup_bp.route('/api/save_config', methods=['POST'])
def save_config():
    """保存配置"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': '无效的请求数据'
            }), 400

        # 读取现有配置文件
        config_file = Path('config.py')
        if not config_file.exists():
            return jsonify({
                'success': False,
                'message': '配置文件不存在'
            }), 404

        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 更新配置项
        updates = {
            'LLM_API_KEY': data.get('llm_api_key'),
            'LLM_BASE_URL': data.get('llm_base_url'),
            'DEFAULT_MODEL_NAME': data.get('default_model'),
            'REPORT_MODEL_NAME': data.get('report_model'),
            'TAVILY_API_KEY': data.get('tavily_api_key'),
            'BOCHA_WEB_SEARCH_API_KEY': data.get('bocha_api_key'),
            'DB_HOST': data.get('db_host'),
            'DB_PORT': data.get('db_port'),
            'DB_USER': data.get('db_user'),
            'DB_PASSWORD': data.get('db_password'),
            'DB_NAME': data.get('db_name'),
            'TRAINING_DATA_SOURCE': data.get('training_data_source'),
            'GARMIN_EMAIL': data.get('garmin_email'),
            'GARMIN_PASSWORD': data.get('garmin_password')
        }

        # 替换配置值
        for key, value in updates.items():
            if value is not None:
                content = update_config_value(content, key, value)

        # 备份原配置文件
        backup_file = config_file.with_suffix('.py.bak')
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(config_file, 'r', encoding='utf-8') as original:
                f.write(original.read())

        # 写入新配置
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # 重新加载配置
        try:
            import importlib
            import config
            importlib.reload(config)
        except Exception as reload_error:
            # 配置重载失败,恢复备份
            with open(backup_file, 'r', encoding='utf-8') as f:
                with open(config_file, 'w', encoding='utf-8') as original:
                    original.write(f.read())
            return jsonify({
                'success': False,
                'message': f'配置保存成功但重载失败: {str(reload_error)}'
            }), 500

        return jsonify({
            'success': True,
            'message': '配置保存成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'保存配置失败: {str(e)}'
        }), 500


def extract_config_value(content: str, key: str) -> str:
    """从配置文件内容中提取配置值"""
    # 匹配形如 KEY = "value" 或 KEY = 'value' 或 KEY = value 的配置行
    pattern = rf'^{key}\s*=\s*["\']?([^"\']*)["\']?'
    match = re.search(pattern, content, re.MULTILINE)

    if match:
        value = match.group(1).strip()
        # 移除可能的注释
        if '#' in value:
            value = value.split('#')[0].strip()
        return value

    return ''


def update_config_value(content: str, key: str, value: str) -> str:
    """更新配置文件中的配置值"""
    # 转义特殊字符
    escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')

    # 匹配配置行
    pattern = rf'^({key}\s*=\s*)["\']?[^"\'#]*["\']?(.*)$'

    def replace_func(match):
        prefix = match.group(1)
        suffix = match.group(2).strip()

        # 保留数字类型不加引号
        if key in ['DB_PORT'] and value.isdigit():
            return f'{prefix}{value}{" " + suffix if suffix else ""}'
        else:
            return f'{prefix}"{escaped_value}"{" " + suffix if suffix else ""}'

    new_content = re.sub(pattern, replace_func, content, flags=re.MULTILINE)

    return new_content


@setup_bp.route('/api/test_llm_connection', methods=['POST'])
def test_llm_connection():
    """测试LLM API连接"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        base_url = data.get('base_url')
        model_name = data.get('model_name', 'qwen-plus-latest')

        if not api_key or not base_url:
            return jsonify({
                'success': False,
                'message': 'API Key和Base URL不能为空'
            })

        # 测试连接
        import openai
        client = openai.OpenAI(api_key=api_key, base_url=base_url)

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5,
            timeout=10
        )

        return jsonify({
            'success': True,
            'message': 'API连接成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'API连接失败: {str(e)}'
        })


@setup_bp.route('/api/test_mysql_connection', methods=['POST'])
def test_mysql_connection():
    """测试MySQL连接"""
    try:
        import pymysql

        data = request.get_json()
        host = data.get('host')
        port = int(data.get('port', 3306))
        user = data.get('user')
        password = data.get('password')
        database = data.get('database')

        if not all([host, user, password, database]):
            return jsonify({
                'success': False,
                'message': '所有数据库配置项不能为空'
            })

        # 测试连接
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            connect_timeout=5
        )

        # 检查数据库是否存在
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW DATABASES LIKE '{database}'")
            db_exists = cursor.fetchone() is not None

        connection.close()

        if db_exists:
            return jsonify({
                'success': True,
                'message': f'MySQL连接成功,数据库"{database}"已存在'
            })
        else:
            return jsonify({
                'success': True,
                'message': f'MySQL连接成功,但数据库"{database}"不存在',
                'warning': True
            })

    except Exception as e:
        error_msg = str(e)
        if '2003' in error_msg:
            return jsonify({
                'success': False,
                'message': f'无法连接到MySQL服务器({host}:{port}),请检查MySQL是否已启动'
            })
        elif '1045' in error_msg:
            return jsonify({
                'success': False,
                'message': '认证失败,请检查用户名和密码是否正确'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'MySQL连接失败: {error_msg}'
            })


@setup_bp.route('/api/upload_training_excel', methods=['POST'])
def upload_training_excel():
    """
    上传并导入训练数据Excel

    请求参数:
    - file: Excel文件(multipart/form-data)

    返回:
    - success: 是否成功
    - message: 提示信息
    - result: 导入统计 {'success': int, 'failed': int, 'total': int}
    """
    try:
        # 检查文件是否存在
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '请选择Excel文件'
            }), 400

        file = request.files['file']

        # 检查文件名
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '未选择文件'
            }), 400

        # 检查文件扩展名
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'message': '只支持Excel文件(.xlsx/.xls)'
            }), 400

        # 确保data目录存在
        data_dir = Path(__file__).parent.parent / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)

        # 安全文件名处理
        filename = secure_filename(file.filename)
        # 统一使用keep_data.xlsx作为标准文件名
        filepath = data_dir / 'keep_data.xlsx'

        # 保存文件(覆盖旧文件)
        file.save(str(filepath))

        # 执行导入(覆盖写入模式)
        importer = KeepDataImporter(str(filepath))
        result = importer.run(truncate_first=True)

        return jsonify({
            'success': True,
            'message': f'导入成功! 共{result["success"]}条记录',
            'result': result
        })

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Excel导入失败: {error_detail}")

        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        }), 500


@setup_bp.route('/api/init_database', methods=['POST'])
def init_database():
    """初始化数据库"""
    try:
        import pymysql

        data = request.get_json()
        host = data.get('host')
        port = int(data.get('port', 3306))
        user = data.get('user')
        password = data.get('password')
        database = data.get('database')

        if not all([host, user, password, database]):
            return jsonify({
                'success': False,
                'message': '所有数据库配置项不能为空'
            })

        # 连接MySQL
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE {database}")

            # 读取SQL文件
            sql_file = Path('scripts/training_tables.sql')
            if not sql_file.exists():
                connection.close()
                return jsonify({
                    'success': False,
                    'message': 'SQL文件不存在: scripts/training_tables.sql'
                })

            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # 分割并执行SQL语句
            sql_statements = sql_content.split(';')
            for statement in sql_statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)

            connection.commit()

        connection.close()

        return jsonify({
            'success': True,
            'message': f'数据库"{database}"初始化成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'数据库初始化失败: {str(e)}'
        })


@setup_bp.route('/api/test_garmin_login', methods=['POST'])
def test_garmin_login():
    """测试Garmin登录"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        is_cn = data.get('is_cn', True)

        if not email or not password:
            return jsonify({
                'success': False,
                'message': '邮箱和密码不能为空'
            })

        # 测试登录
        from scripts.training_data_importer import GarminDataImporter
        importer = GarminDataImporter(email, password, is_cn)
        importer.login()

        return jsonify({
            'success': True,
            'message': 'Garmin登录成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Garmin登录失败: {str(e)}'
        })


@setup_bp.route('/api/import_garmin_data', methods=['POST'])
def import_garmin_data():
    """导入Garmin数据"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        is_cn = data.get('is_cn', True)

        if not email or not password:
            return jsonify({
                'success': False,
                'message': '邮箱和密码不能为空'
            }), 400

        # 执行导入
        from scripts.training_data_importer import GarminDataImporter
        importer = GarminDataImporter(email, password, is_cn)
        result = importer.run(truncate_first=True)

        if 'error' in result:
            return jsonify({
                'success': False,
                'message': result['error']
            }), 500

        return jsonify({
            'success': True,
            'message': f'Garmin数据导入成功! 共{result["success"]}条记录',
            'result': result
        })

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Garmin数据导入失败: {error_detail}")

        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        }), 500
