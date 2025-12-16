# -*- coding: utf-8 -*-
"""
训练数据管理路由
"""

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from models.training_record import TrainingRecordManager, SessionLocal
from utils.config_reloader import get_config_value
import json
import time

training_data_bp = Blueprint('training_data', __name__, url_prefix='/training')


def get_record_manager():
    """
    获取训练记录管理器（支持配置热重载）

    每次调用都会读取最新的TRAINING_DATA_SOURCE配置
    """
    data_source = get_config_value('TRAINING_DATA_SOURCE', 'keep')
    return TrainingRecordManager(data_source=data_source)


@training_data_bp.route('/')
def index():
    """训练数据管理主页 - 根据数据源渲染不同页面"""
    # 获取当前数据源配置
    data_source = get_config_value('TRAINING_DATA_SOURCE', 'keep')

    # 根据数据源渲染不同模板
    if data_source == 'garmin':
        return render_template('training_data_garmin.html')
    else:  # keep
        return render_template('training_data.html')


@training_data_bp.route('/api/records', methods=['GET'])
def get_records():
    """获取所有训练记录"""
    session = SessionLocal()
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # 查询总数
        total = get_record_manager().query(session).count()

        # 分页查询
        start_time_field = get_record_manager().get_field('start_time')
        records = get_record_manager().query(session)\
            .order_by(start_time_field.desc())\
            .limit(per_page)\
            .offset((page - 1) * per_page)\
            .all()

        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in records],
            'total': total,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        session.close()


@training_data_bp.route('/api/record', methods=['POST'])
def add_record():
    """添加训练记录"""
    session = SessionLocal()
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['exercise_type', 'duration_seconds', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400

        # 解析时间
        try:
            start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            return jsonify({'success': False, 'message': f'时间格式错误: {str(e)}'}), 400

        # 处理心率数据
        heart_rate_data = None
        hr_input = data.get('heart_rate_data')
        # 只有在用户实际输入了有效内容时才处理
        if hr_input and str(hr_input).strip():
            try:
                # 如果是字符串,尝试解析为列表
                if isinstance(hr_input, str):
                    heart_rate_list = json.loads(hr_input)
                else:
                    heart_rate_list = hr_input
                heart_rate_data = json.dumps(heart_rate_list)
            except Exception as e:
                return jsonify({'success': False, 'message': f'心率数据格式错误: {str(e)}'}), 400
        # 否则heart_rate_data保持为None,数据库会存储为NULL

        # 创建记录
        current_ts = int(time.time())
        record = get_record_manager().create_record(
            user_id=data.get('user_id', 'default_user'),
            exercise_type=data['exercise_type'],
            duration_seconds=int(data['duration_seconds']),
            start_time=start_time,
            end_time=end_time,
            calories=int(data['calories']) if data.get('calories') else None,
            distance_meters=float(data['distance_meters']) if data.get('distance_meters') else None,
            avg_heart_rate=int(data['avg_heart_rate']) if data.get('avg_heart_rate') else None,
            max_heart_rate=int(data['max_heart_rate']) if data.get('max_heart_rate') else None,
            heart_rate_data=heart_rate_data,
            add_ts=current_ts,
            last_modify_ts=current_ts,
            data_source=data.get('data_source', 'manual_import')
        )

        session.add(record)
        session.commit()
        session.refresh(record)

        return jsonify({
            'success': True,
            'message': '添加成功',
            'data': record.to_dict()
        })
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500
    finally:
        session.close()


@training_data_bp.route('/api/record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    """获取单个训练记录"""
    session = SessionLocal()
    try:
        Model = get_record_manager().get_model_class()
        record = get_record_manager().query(session).filter(Model.id == record_id).first()
        if not record:
            return jsonify({'success': False, 'message': '记录不存在'}), 404

        return jsonify({
            'success': True,
            'data': record.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        session.close()


@training_data_bp.route('/api/record/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    """更新训练记录"""
    session = SessionLocal()
    try:
        Model = get_record_manager().get_model_class()
        record = get_record_manager().query(session).filter(Model.id == record_id).first()
        if not record:
            return jsonify({'success': False, 'message': '记录不存在'}), 404

        data = request.get_json()

        # 更新字段
        if 'user_id' in data:
            record.user_id = data['user_id']
        if 'exercise_type' in data:
            record.exercise_type = data['exercise_type']
        if 'duration_seconds' in data:
            record.duration_seconds = int(data['duration_seconds'])
        if 'start_time' in data:
            record.start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
        if 'end_time' in data:
            record.end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')
        if 'calories' in data:
            record.calories = int(data['calories']) if data['calories'] else None
        if 'distance_meters' in data:
            record.distance_meters = float(data['distance_meters']) if data['distance_meters'] else None
        if 'avg_heart_rate' in data:
            record.avg_heart_rate = int(data['avg_heart_rate']) if data['avg_heart_rate'] else None
        if 'max_heart_rate' in data:
            record.max_heart_rate = int(data['max_heart_rate']) if data['max_heart_rate'] else None
        if 'heart_rate_data' in data:
            hr_input = data['heart_rate_data']
            # 只有在用户实际输入了有效内容时才处理
            if hr_input and str(hr_input).strip():
                if isinstance(hr_input, str):
                    heart_rate_list = json.loads(hr_input)
                else:
                    heart_rate_list = hr_input
                record.heart_rate_data = json.dumps(heart_rate_list)
            else:
                # 用户清空了心率数据,设置为None(数据库存储为NULL)
                record.heart_rate_data = None
        if 'data_source' in data:
            record.data_source = data['data_source']

        record.last_modify_ts = int(time.time())

        session.commit()
        session.refresh(record)

        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': record.to_dict()
        })
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500
    finally:
        session.close()


@training_data_bp.route('/api/record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除训练记录"""
    session = SessionLocal()
    try:
        Model = get_record_manager().get_model_class()
        record = get_record_manager().query(session).filter(Model.id == record_id).first()
        if not record:
            return jsonify({'success': False, 'message': '记录不存在'}), 404

        session.delete(record)
        session.commit()

        return jsonify({
            'success': True,
            'message': '删除成功'
        })
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500
    finally:
        session.close()


@training_data_bp.route('/api/exercise_types', methods=['GET'])
def get_exercise_types():
    """获取所有运动类型"""
    session = SessionLocal()
    try:
        # 从数据库中查询所有不同的运动类型
        exercise_type_field = get_record_manager().get_field('exercise_type')
        exercise_types = get_record_manager().query(session)\
            .with_entities(exercise_type_field)\
            .distinct()\
            .order_by(exercise_type_field)\
            .all()

        types_list = [et[0] for et in exercise_types]

        # 添加常见运动类型
        common_types = ['跑步', '骑行', '游泳', '健走', '爬山', '徒步', '瑜伽', '力量训练', '篮球', '足球', '羽毛球', '网球', '乒乓球']
        for ct in common_types:
            if ct not in types_list:
                types_list.append(ct)

        return jsonify({
            'success': True,
            'data': types_list
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        session.close()


@training_data_bp.route('/api/data_sources', methods=['GET'])
def get_data_sources():
    """获取所有数据来源"""
    sources = [
        'manual_import',
        'excel_import',
        'garmin_connect',
        'strava',
        'keep',
        'nike_run_club',
        'adidas_running',
        'apple_health',
        'xiaomi_health',
        'huawei_health'
    ]

    return jsonify({
        'success': True,
        'data': sources
    })


@training_data_bp.route('/api/current_source', methods=['GET'])
def get_current_source():
    """获取当前使用的数据源"""
    return jsonify({
        'success': True,
        'data': {
            'source': get_record_manager().data_source,
            'available_sources': list(get_record_manager().DATA_SOURCE_MAP.keys())
        }
    })


@training_data_bp.route('/api/switch_source', methods=['POST'])
def switch_source():
    """切换数据源"""
    try:
        data = request.get_json()
        new_source = data.get('source')

        if not new_source:
            return jsonify({'success': False, 'message': '缺少source参数'}), 400

        get_record_manager().switch_source(new_source)

        return jsonify({
            'success': True,
            'message': f'数据源已切换到: {new_source}',
            'data': {
                'source': get_record_manager().data_source,
                'model_class': get_record_manager().get_model_class().__name__
            }
        })
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'切换失败: {str(e)}'}), 500


@training_data_bp.route('/api/sync_garmin_data', methods=['POST'])
def sync_garmin_data():
    """同步Garmin数据 - 调用setup页面的导入逻辑"""
    try:
        # 从request body获取is_cn, 优先于config
        data = request.json or {}
        garmin_is_cn_str = data.get('garmin_is_cn')

        if garmin_is_cn_str is not None:
            # 如果从请求中获取,布尔化处理
            garmin_is_cn = str(garmin_is_cn_str).lower() in ['true', '1', 't', 'y', 'yes']
        else:
            # 否则从config读取Garmin配置
            garmin_is_cn = get_config_value('GARMIN_IS_CN', True)

        # 从config读取Garmin配置
        garmin_email = get_config_value('GARMIN_EMAIL', '')
        garmin_password = get_config_value('GARMIN_PASSWORD', '')

        if not garmin_email or not garmin_password:
            return jsonify({
                'success': False,
                'message': 'Garmin账户配置不完整,请先在config.py中配置GARMIN_EMAIL和GARMIN_PASSWORD'
            }), 400

        # 执行导入
        from scripts.training_data_importer import GarminDataImporter
        importer = GarminDataImporter(garmin_email, garmin_password, garmin_is_cn)
        result = importer.run(truncate_first=True)

        if 'error' in result:
            return jsonify({
                'success': False,
                'message': result['error']
            }), 500

        return jsonify({
            'success': True,
            'message': f'Garmin数据同步成功! 共导入{result["success"]}条记录',
            'result': result
        })

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Garmin数据同步失败: {error_detail}")

        return jsonify({
            'success': False,
            'message': f'同步失败: {str(e)}'
        }), 500
