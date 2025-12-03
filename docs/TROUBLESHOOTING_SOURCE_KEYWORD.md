# 数据库字段错误排查与修复文档

## 问题描述

**错误信息**:
```
pymysql.err.OperationalError: (1054, "Unknown column 'source_keyword' in 'field list'")
```

**发生场景**:
- Bilibili爬虫成功获取20条视频数据
- 尝试保存第一条视频到数据库时报错
- 错误发生在 `async_db.py:66` 的 `cur.execute(sql, values)` 调用

## 问题根源

### 真正的原因: **配置文件与实际数据库不匹配**

爬虫代码实际连接的数据库配置与用户初始化的数据库不是同一个!

**配置文件位置**: `MindSpider/DeepSentimentCrawling/MediaCrawler/config/db_config.py`

```python
# 原配置 (第19行)
MYSQL_DB_NAME = "mindspider"  # 爬虫实际连接的数据库

# 用户初始化的数据库
# 使用 MindSpider/schema/init_database.py 初始化的是 test3 数据库
```

**问题链**:
1. 用户运行 `init_database.py` 初始化了 `test3` 数据库 ✅
2. `test3` 数据库的表结构完整,有 `source_keyword` 字段 ✅
3. 但爬虫配置文件指向 `mindspider` 数据库 ❌
4. `mindspider` 数据库的表结构较旧,缺少 `source_keyword` 字段 ❌
5. 运行爬虫时连接到 `mindspider`,导致字段找不到 ❌

## 排查过程

### 1. 初步诊断 - 数据库表结构检查

**验证 test3 数据库** (用户初始化的数据库):
```sql
USE test3;
DESCRIBE bilibili_video;
```

**结果**: ✅ `source_keyword` 字段存在 (varchar(500))

### 2. 深入分析 - 检查实际运行配置

**检查代码实际使用的数据库名**:
```bash
python3 -c "
import sys
sys.path.insert(0, '/path/to/MediaCrawler')
import config
print(f'实际连接数据库: {config.MYSQL_DB_NAME}')
"
```

**结果**: `实际连接数据库: mindspider` ❌

**验证 mindspider 数据库表结构**:
```sql
USE mindspider;
DESCRIBE bilibili_video;
```

**结果**: ❌ `source_keyword` 字段不存在

### 3. 根因确认

**配置文件层级**:
```
MediaCrawler/
├── config/
│   ├── __init__.py          # 导入所有配置
│   ├── db_config.py         # 数据库配置 (问题源头!)
│   └── base_config.py       # 基础配置
├── db.py                    # 使用 config.MYSQL_DB_NAME
└── main.py
```

**配置导入链**:
```python
# config/__init__.py
from .db_config import *  # 导入 MYSQL_DB_NAME = "mindspider"

# db.py:36-42
pool = await aiomysql.create_pool(
    host=config.MYSQL_DB_HOST,
    user=config.MYSQL_DB_USER,
    password=config.MYSQL_DB_PWD,
    db=config.MYSQL_DB_NAME,  # 使用 "mindspider"
    autocommit=True,
)
```

## 解决方案

### 方案A: 修改配置指向正确的数据库 (推荐)

**步骤**:

1. **修改配置文件**:
   ```bash
   vim MindSpider/DeepSentimentCrawling/MediaCrawler/config/db_config.py
   ```

2. **将第19行改为**:
   ```python
   # 修改前
   MYSQL_DB_NAME = "mindspider"

   # 修改后
   MYSQL_DB_NAME = "test3"
   ```

3. **验证配置**:
   ```bash
   python3 -c "
   import sys
   sys.path.insert(0, '/home/dzs-ai-4/dzs-dev/Agent/BettaFish-main/MindSpider/DeepSentimentCrawling/MediaCrawler')
   import config
   print(f'当前数据库: {config.MYSQL_DB_NAME}')
   "
   ```

   应该输出: `当前数据库: test3` ✅

4. **重新运行爬虫**:
   ```bash
   cd MindSpider/DeepSentimentCrawling/MediaCrawler
   python main.py --platform bili --lt qrcode --type search --save_data_option db
   ```

### 方案B: 更新 mindspider 数据库表结构

如果希望继续使用 `mindspider` 数据库,可以添加缺失的字段:

```sql
USE mindspider;

-- 为各平台表添加 source_keyword 字段
ALTER TABLE bilibili_video ADD COLUMN source_keyword varchar(500) DEFAULT NULL COMMENT '搜索关键词';
ALTER TABLE douyin_aweme ADD COLUMN source_keyword varchar(500) DEFAULT NULL COMMENT '搜索关键词';
ALTER TABLE kuaishou_video ADD COLUMN source_keyword varchar(500) DEFAULT NULL COMMENT '搜索关键词';
ALTER TABLE weibo_note ADD COLUMN source_keyword varchar(500) DEFAULT NULL COMMENT '搜索关键词';
ALTER TABLE xhs_note ADD COLUMN source_keyword varchar(500) DEFAULT NULL COMMENT '搜索关键词';
ALTER TABLE tieba_note ADD COLUMN source_keyword varchar(500) DEFAULT NULL COMMENT '搜索关键词';

-- 知乎表可能已存在但长度不够,需修改
ALTER TABLE zhihu_content MODIFY COLUMN source_keyword varchar(500) DEFAULT NULL COMMENT '来源关键词';
```

**注意**: 如果某个表已经有该字段,会报错 `Duplicate column name`,这是正常的,可以忽略。

## 技术细节

### source_keyword 字段的作用

**定义位置**: `var.py:25`
```python
source_keyword_var: ContextVar[str] = ContextVar("source_keyword", default="")
```

**设置位置**: `media_platform/bilibili/core.py:172`
```python
for keyword in config.KEYWORDS.split(","):
    source_keyword_var.set(keyword)  # 设置当前搜索关键词
    # ... 爬取逻辑
```

**使用位置**: `store/bilibili/__init__.py:66`
```python
save_content_item = {
    "video_id": video_id,
    "title": video_item_view.get("title", ""),
    # ... 其他字段
    "source_keyword": source_keyword_var.get(),  # 从上下文变量获取
}
```

**存储位置**: `async_db.py:66`
```python
async def item_to_table(self, table_name: str, item: Dict[str, Any]) -> int:
    fields = list(item.keys())  # 包含 source_keyword
    values = list(item.values())
    # 动态生成 INSERT 语句
    sql = "INSERT INTO %s (%s) VALUES(%s)" % (table_name, fieldstr, valstr)
    await cur.execute(sql, values)  # 这里报错!
```

### 为什么会误判为连接池缓存问题?

在排查过程中,曾经怀疑是 aiomysql 连接池缓存了旧的表结构。这个假设看似合理:

1. ✅ MySQL 客户端确实会缓存表结构信息
2. ✅ 连接池会复用连接,避免重复建立
3. ❌ 但忽略了最基本的前提: **连接的是否是同一个数据库**

**教训**:
- 遇到数据库字段错误,首先确认**连接的是哪个数据库**
- 不要假设配置文件就是你看到的那个
- 用代码实际运行检查配置,而不是靠猜测

## 验证修复

### 检查清单

- [ ] 确认配置文件中的 `MYSQL_DB_NAME` 是否正确
- [ ] 用 Python 代码验证实际加载的数据库名
- [ ] 用 MySQL 客户端验证目标数据库的表结构
- [ ] 确认 `source_keyword` 字段在所有内容表中存在
- [ ] 运行爬虫验证数据能正常保存

### 成功标志

运行爬虫后,应该看到:

```
2025-12-02 15:42:14 MediaCrawler INFO - Begin search bilibli keywords
2025-12-02 15:42:14 MediaCrawler INFO - Current search keyword: 中国男篮再负韩国
... (成功获取视频列表)
2025-12-02 15:42:20 MediaCrawler INFO - bilibili video id:115644511094251
✅ 数据成功保存到数据库,没有报错!
```

## 相关文件清单

### 配置文件
- `MindSpider/DeepSentimentCrawling/MediaCrawler/config/db_config.py` - **核心配置文件**
- `MindSpider/DeepSentimentCrawling/MediaCrawler/config/__init__.py` - 配置导入
- `MindSpider/config.py` - MindSpider 主配置 (未被爬虫使用)

### 数据库初始化
- `MindSpider/schema/init_database.py` - 数据库初始化脚本
- `MindSpider/DeepSentimentCrawling/MediaCrawler/schema/tables.sql` - 表结构定义

### 代码逻辑
- `MindSpider/DeepSentimentCrawling/MediaCrawler/var.py` - ContextVar 定义
- `MindSpider/DeepSentimentCrawling/MediaCrawler/media_platform/bilibili/core.py` - 设置 source_keyword
- `MindSpider/DeepSentimentCrawling/MediaCrawler/store/bilibili/__init__.py` - 构造保存数据
- `MindSpider/DeepSentimentCrawling/MediaCrawler/async_db.py` - 数据库操作
- `MindSpider/DeepSentimentCrawling/MediaCrawler/db.py` - 连接池初始化

## 预防措施

### 1. 配置管理最佳实践

**统一配置源**:
```python
# 推荐: 使用环境变量或统一配置文件
import os

MYSQL_DB_NAME = os.getenv("MYSQL_DB_NAME", "mindspider")
```

**配置验证**:
```python
# db.py 初始化时打印配置
async def init_mediacrawler_db():
    utils.logger.info(f"[init_db] Connecting to database: {config.MYSQL_DB_NAME}")
    pool = await aiomysql.create_pool(...)
```

### 2. 数据库表结构版本管理

**添加表结构版本检查**:
```python
async def verify_table_schema():
    """验证必需字段是否存在"""
    required_columns = {
        'bilibili_video': ['source_keyword', 'video_id', 'title'],
        'douyin_aweme': ['source_keyword', 'aweme_id'],
        # ...
    }

    for table, columns in required_columns.items():
        result = await async_db_conn.query(
            f"SHOW COLUMNS FROM {table} LIKE 'source_keyword'"
        )
        if not result:
            raise Exception(f"表 {table} 缺少字段 source_keyword")
```

### 3. 初始化脚本改进

**在 init_database.py 中添加配置检查**:
```python
def check_config_consistency():
    """检查配置是否一致"""
    from MediaCrawler import config as crawler_config

    print(f"MediaCrawler 配置数据库: {crawler_config.MYSQL_DB_NAME}")
    print(f"初始化脚本目标数据库: {DB_NAME}")

    if crawler_config.MYSQL_DB_NAME != DB_NAME:
        print("⚠️  警告: 配置文件与初始化目标数据库不一致!")
        print(f"   请修改 MediaCrawler/config/db_config.py 中的 MYSQL_DB_NAME")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
```

## 总结

### 问题本质
- **配置管理问题**: 多个配置文件导致混淆
- **数据库选择错误**: 连接了错误的数据库
- **缺乏验证机制**: 没有在启动时检查配置一致性

### 关键教训
1. **不要假设,要验证**: 用代码实际检查配置
2. **配置要统一**: 避免多处定义相同配置
3. **错误要详细**: 日志中应包含连接的数据库名
4. **启动要检查**: 程序启动时验证关键配置

### 成功要素
- 系统性排查: 从表结构 → 配置文件 → 实际加载配置
- 实证验证: 用 MySQL 客户端和 Python 代码双重验证
- 根因定位: 找到真正的问题而不是表象

---

**文档创建时间**: 2024-12-02
**问题状态**: ✅ 已解决
**修复方法**: 修改配置文件 `db_config.py:19` 将 `MYSQL_DB_NAME` 改为 `test3`
