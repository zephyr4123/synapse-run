# 二维码登录404调试指南

## 问题描述
- test_qrcode_web.py测试正常
- 真实测试命令出现404 NOT FOUND

## 已添加的调试语句

### 1. qrcode_manager.py

#### create_qrcode_session() - Session创建
```
[QRCodeManager] 🔵 创建新会话:
  - Session ID: xxx
  - Platform: xxx
  - Image length: xxx
  - Session file: xxx
[QRCodeManager] 📂 加载现有sessions: N 个
[QRCodeManager] 💾 保存session到文件...
[QRCodeManager] ✅ Session保存成功，当前共 N 个
[QRCodeManager] ✅/❌ Session验证成功/失败
```

#### get_qrcode() - Session查询
```
[QRCodeManager] 🔍 查询Session: xxx
  - Session file: xxx
  - File exists: True/False
[QRCodeManager] 📂 加载sessions: N 个
[QRCodeManager] 📋 所有session IDs: [...]
[QRCodeManager] ✅/❌ Session找到/未找到
  - Platform: xxx
  - Created: xxx
  - Elapsed: xxx
```

### 2. crawler_util.py

#### show_qrcode() - 二维码展示
```
[show_qrcode] 🔍 Debug Info:
  - Current file: xxx
  - Project root: xxx
  - Platform: xxx
  - QR code length: xxx
  - sys.path before insert: [...]
  - sys.path after insert: [...]
[show_qrcode] 📞 Calling create_qrcode_session...
[show_qrcode] ✅ Session created: xxx
[扫码登录] Session ID (用于调试): xxx
```

### 3. app.py

#### Flask路由 /qrcode/<session_id>
```
[Flask] 🌐 访问QR页面: /qrcode/xxx
[Flask] 📞 调用get_qrcode_manager()...
[Flask] 🔍 查询session: xxx
[Flask] ✅/❌ Session找到/未找到或已过期
  - Platform: xxx
  - Image length: xxx
```

## 测试步骤

### 1. 重启Flask服务器
```bash
pkill -f "python app.py"
python app.py
```

### 2. 运行爬虫测试
```bash
cd MindSpider/DeepSentimentCrawling/MediaCrawler
python main.py --platform xhs --lt qrcode --type search --save_data_option db
```

### 3. 查看日志输出

#### 期望看到的输出流程:

**爬虫侧 (crawler_util.py):**
```
[show_qrcode] 🔍 Debug Info:
  - Platform: xhs
  - QR code length: [应该>0]
[show_qrcode] 📞 Calling create_qrcode_session...
↓
[QRCodeManager] 🔵 创建新会话:
  - Session ID: [生成的UUID]
  - Session file: [应该指向temp_qrcodes/sessions.pkl]
[QRCodeManager] 💾 保存session到文件...
[QRCodeManager] ✅ Session保存成功
[QRCodeManager] ✅ Session验证成功
↓
[show_qrcode] ✅ Session created: [UUID]
[扫码登录] http://localhost:5000/qrcode/[UUID]
```

**Flask侧 (app.py) - 访问链接时:**
```
[Flask] 🌐 访问QR页面: /qrcode/[UUID]
[Flask] 🔍 查询session: [UUID]
↓
[QRCodeManager] 🔍 查询Session: [UUID]
[QRCodeManager] 📂 加载sessions: N 个
[QRCodeManager] 📋 所有session IDs: ['UUID', ...]
[QRCodeManager] ✅ Session找到!
↓
[Flask] ✅ Session找到，返回页面
```

## 可能的问题点

### 问题1: Session文件路径不一致
**症状**: 创建时保存到A路径，查询时读取B路径
**日志特征**:
- 创建: `Session file: /path/A/sessions.pkl`
- 查询: `Session file: /path/B/sessions.pkl`
**解决**: 确保两个进程的工作目录一致

### 问题2: Session ID不匹配
**症状**: 生成的ID和访问的ID不同
**日志特征**:
- 创建: `Session created: uuid-1`
- 访问: `访问QR页面: /qrcode/uuid-2`
**解决**: 检查日志输出的完整URL

### 问题3: Session文件权限问题
**症状**: 创建成功但读取失败
**日志特征**:
- 创建: `✅ Session保存成功`
- 查询: `File exists: False`
**解决**: 检查文件权限和所有者

### 问题4: 时间过期问题
**症状**: 创建后立即过期
**日志特征**:
- 创建: `Session保存成功`
- 查询: `⏰ Session已过期`
**解决**: 检查系统时间是否正确

## 排查顺序

1. **确认Session创建成功**
   - 看到 `✅ Session保存成功`
   - 看到 `✅ Session验证成功`

2. **记录Session ID**
   - 复制日志中的完整UUID

3. **确认文件已创建**
   ```bash
   ls -la temp_qrcodes/sessions.pkl
   cat temp_qrcodes/sessions.pkl | od -c  # 查看文件内容
   ```

4. **访问链接时查看Flask日志**
   - 确认是否收到请求
   - 确认加载的session文件路径
   - 确认是否找到对应的session

5. **对比两个进程的输出**
   - Session file路径是否一致
   - Session ID是否匹配

## 快速验证命令

```bash
# 1. 确认temp_qrcodes目录存在
ls -la temp_qrcodes/

# 2. 测试创建session (test_qrcode_web.py)
python test_qrcode_web.py

# 3. 查看session文件
python -c "import pickle; print(pickle.load(open('temp_qrcodes/sessions.pkl', 'rb')))"

# 4. 运行真实测试并保存日志
cd MindSpider/DeepSentimentCrawling/MediaCrawler
python main.py --platform xhs --lt qrcode --type search --save_data_option db 2>&1 | tee /tmp/crawler.log

# 5. 在另一个终端查看Flask日志
# (Flask输出会显示在运行app.py的终端)
```

## 预期结果

成功的情况下应该看到:
1. 爬虫创建session ✅
2. Session文件存在 ✅
3. Flask收到访问请求 ✅
4. Flask找到对应session ✅
5. 浏览器显示二维码页面 ✅

如果任何一步失败，查看对应的调试日志定位问题。
