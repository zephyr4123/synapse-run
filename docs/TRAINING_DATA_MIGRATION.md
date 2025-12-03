# 训练数据迁移文档

## 概述

本文档记录了将InsightAgent从"舆情分析系统"改造为"中长跑训练计划定制助手"的数据库迁移过程。

## 迁移内容

### 1. 数据库表结构变更

#### 旧表结构 (已弃用)
- `bilibili_video`, `douyin_aweme`, `weibo_note` 等社交媒体内容表
- `*_comment` 系列评论表
- `daily_news` 新闻表

#### 新表结构
- **`training_records`**: 训练记录主表

**字段说明**:
```sql
- id: 自增主键
- user_id: 用户ID (预留多用户支持)
- exercise_type: 运动类型 (跑步/骑行/游泳等)
- duration_seconds: 运动时长(秒)
- start_time: 开始时间
- end_time: 结束时间
- calories: 消耗卡路里
- distance_meters: 运动距离(米)
- avg_heart_rate: 平均心率
- max_heart_rate: 最大心率
- heart_rate_data: 心率记录数组 (JSON格式)
- add_ts: 记录添加时间戳
- last_modify_ts: 最后修改时间戳
- data_source: 数据来源 (manual_import/wearable_device/app)
```

**索引优化**:
- `idx_training_user_id`: 支持多用户查询
- `idx_training_start_time`: 支持时间范围查询
- `idx_training_exercise_type`: 支持按运动类型筛选

### 2. 工具类变更

#### 旧工具类 (已弃用)
- **MediaCrawlerDB** (`InsightEngine/tools/search.py`)
  - 5种工具: 热点搜索、全局话题搜索、按日期搜索、评论获取、平台定向搜索

#### 新工具类
- **TrainingDataDB** (`InsightEngine/tools/training_search.py`)
  - 6种工具,专为训练数据分析设计

**工具列表**:

1. **search_recent_trainings**: 查询最近N天的训练记录
   - 参数: `days`, `exercise_type`, `limit`
   - 用途: 查看最近一周/一个月的训练情况

2. **search_by_date_range**: 按日期范围查询训练记录
   - 参数: `start_date`, `end_date`, `exercise_type`, `limit`
   - 用途: 分析特定时间段的训练数据

3. **get_training_stats**: 获取训练统计数据
   - 参数: `start_date`, `end_date`, `exercise_type`
   - 用途: 计算总距离、平均配速、总时长等指标

4. **search_by_distance_range**: 按距离范围查询
   - 参数: `min_distance_km`, `max_distance_km`, `exercise_type`, `limit`
   - 用途: 查找长距离训练(如10公里以上)

5. **search_by_heart_rate**: 按心率区间查询
   - 参数: `min_avg_hr`, `max_avg_hr`, `exercise_type`, `limit`
   - 用途: 分析不同心率区间的训练

6. **get_exercise_type_summary**: 按运动类型汇总
   - 参数: `start_date`, `end_date`
   - 用途: 按跑步/骑行等类型统计

### 3. Agent代码变更

#### 文件修改清单

**InsightEngine/agent.py**:
```python
# 修改前
from .tools import MediaCrawlerDB, DBResponse, ...
self.search_agency = MediaCrawlerDB()

# 修改后
from .tools import TrainingDataDB, DBResponse, ...
self.search_agency = TrainingDataDB()
```

**InsightEngine/tools/__init__.py**:
```python
# 修改前
from .search import MediaCrawlerDB, QueryResult, DBResponse

# 修改后
from .training_search import TrainingDataDB, TrainingRecord, DBResponse
```

## 使用指南

### 步骤1: 创建数据库表

```bash
cd /home/dzs-ai-4/dzs-dev/Agent/multiRunningAgents

# 连接MySQL并执行SQL
mysql -u your_user -p your_database < MindSpider/DeepSentimentCrawling/MediaCrawler/schema/training_tables.sql
```

或使用Python脚本(自动创建表):
```bash
# 导入脚本会自动检测并创建表
python scripts/import_training_data.py
```

### 步骤2: 导入训练数据

**前提条件**:
- Excel文件 `406099.xlsx` 位于项目根目录
- 已设置数据库环境变量

**执行导入**:
```bash
# 设置环境变量
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=your_database

# 运行导入脚本
python scripts/import_training_data.py
```

**脚本功能**:
- 自动读取Excel文件
- 排除"运动轨迹"列
- 数据清洗(处理NaN值、转换类型)
- 批量插入数据库
- 自动创建表(如果不存在)

### 步骤3: 验证导入结果

```bash
# 进入Python REPL
python

# 测试工具类
>>> from InsightEngine.tools import TrainingDataDB
>>> db = TrainingDataDB()
>>> response = db.search_recent_trainings(days=7, exercise_type='跑步', limit=5)
>>> print(f"找到 {response.results_count} 条记录")
```

### 步骤4: 使用InsightAgent

```python
from InsightEngine import DeepSearchAgent

# 初始化Agent
agent = DeepSearchAgent()

# Agent会自动使用TrainingDataDB工具集
# 提示词应改为训练相关的查询,例如:
# "分析用户最近一个月的跑步训练数据"
# "制定下周的中长跑训练计划"
```

## 数据结构对比

### 旧系统 (舆情分析)
```
话题 → 多平台内容 → 评论 → 情感分析
```

### 新系统 (训练分析)
```
用户 → 训练记录 → 运动指标 → 训练计划
```

## 注意事项

### 1. 数据备份
- 旧表数据已由用户备份,无需保留
- 新系统使用独立的 `training_records` 表

### 2. 配速计算
- 配速自动计算: `duration_seconds / (distance_meters / 1000)`
- 单位: 秒/公里
- 展示格式: `5'30"` (5分30秒每公里)

### 3. 心率数据
- 存储格式: JSON数组字符串 `["108","109","110",...]`
- 解析: `TrainingDataDB._parse_heart_rate_data()`
- 用于分析心率变化趋势

### 4. 多用户支持
- `user_id` 字段预留,当前默认 `'default_user'`
- 扩展时可区分多个用户的训练数据

### 5. 数据来源追踪
- `data_source` 字段记录数据来源
- 当前值: `'excel_import'`
- 未来可扩展: `'wearable_device'`, `'mobile_app'` 等

## 文件清单

### 新增文件
1. `MindSpider/DeepSentimentCrawling/MediaCrawler/schema/training_tables.sql`
   - 训练记录表SQL定义

2. `InsightEngine/tools/training_search.py`
   - TrainingDataDB工具类 (460行)

3. `scripts/import_training_data.py`
   - Excel数据导入脚本 (200行)

4. `docs/TRAINING_DATA_MIGRATION.md`
   - 本文档

### 修改文件
1. `InsightEngine/agent.py`
   - 第22行: 导入语句
   - 第51行: 工具初始化
   - 第67行: 打印信息

2. `InsightEngine/tools/__init__.py`
   - 完全重写,导出TrainingDataDB

### 保留文件
- `InsightEngine/tools/search.py` (旧工具类,可删除或保留作参考)
- `InsightEngine/tools/keyword_optimizer.py` (关键词优化器,保留)
- `InsightEngine/tools/sentiment_analyzer.py` (情感分析器,保留)

## 下一步优化建议

1. **提示词改造**:
   - 修改 `InsightEngine/prompts/prompts.py`
   - 从舆情分析话术改为训练计划话术

2. **节点逻辑优化**:
   - `FirstSearchNode`: 适配训练数据搜索逻辑
   - `ReflectionNode`: 反思训练计划合理性
   - `SummaryNode`: 总结训练成效

3. **新增分析功能**:
   - 配速趋势分析
   - 心率区间训练建议
   - 训练负荷监测
   - 周期化训练计划生成

4. **可视化增强**:
   - 训练日历热力图
   - 配速曲线图
   - 心率区间分布图

## 常见问题

### Q1: 导入时提示"表不存在"?
**A**: 确保先执行SQL文件创建表,或让导入脚本自动创建。

### Q2: 如何查看已导入的数据?
**A**: 使用 `TrainingDataDB.search_recent_trainings()` 或直接SQL查询。

### Q3: 可以导入多次吗?
**A**: 可以,脚本使用 `INSERT IGNORE` 避免重复。

### Q4: 如何添加新的查询工具?
**A**: 在 `TrainingDataDB` 类中添加新方法,参考现有工具的实现模式。

### Q5: 情感分析器还需要吗?
**A**: 对训练数据不适用,可在后续版本移除或改为"训练状态分析器"。

## 版本历史

- **v1.0** (2025-12-03): 初始迁移完成
  - 创建训练数据表结构
  - 实现TrainingDataDB工具类
  - 完成数据导入脚本
  - 更新Agent代码

## 联系信息

如有问题或建议,请在项目issue中提出。
