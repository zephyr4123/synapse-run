# BettaFish 多智能体协作系统学习指南

> 本指南旨在帮助你系统化学习"微舆"多智能体舆情分析系统的架构设计与实现思想

## 📋 项目概览

BettaFish是一个基于多智能体架构的舆情分析系统，核心特点：

- **四个专业化Agent**：QueryEngine（搜索）、MediaEngine（多模态）、InsightEngine（数据挖掘）、ReportEngine（报告生成）
- **ForumEngine协作机制**：通过"论坛式"辩论实现集体智能
- **统一架构范式**：所有Agent遵循相同的nodes/tools/state/prompts结构
- **LLM接口标准化**：统一使用OpenAI兼容格式，支持灵活切换

**学习时长**：预计3-5天深度学习

---

## 🎯 核心框架思想

在开始学习之前，理解以下六个核心设计原则：

### 1. 专业分工原则
每个Agent专注特定领域，使用最适合的LLM：
- QueryEngine → DeepSeek Reasoner（推理能力）
- MediaEngine → Gemini 2.5 Pro（多模态理解）
- InsightEngine → Kimi K2（长上下文处理）
- ReportEngine → Gemini 2.5 Pro（生成能力）

**思考**：为什么不用一个超强LLM处理所有任务？

### 2. 统一架构范式
所有Agent遵循相同的模块化结构：
- `agent.py` - 主类，编排workflow
- `state/` - 状态管理
- `nodes/` - 处理节点（FirstSearch → Reflection → Summary → Formatting）
- `tools/` - 外部能力封装
- `llms/` - 统一LLM客户端
- `prompts/` - 提示词模板管理

**价值**：降低学习曲线，提高可维护性和可扩展性

### 3. 协作增强智能
通过ForumEngine实现Agent间的"思维碰撞"：
- Agent将分析结果写入共享论坛日志
- 监控模块实时提取关键信息
- LLM主持人生成总结和引导
- 各Agent读取论坛内容，循环迭代

**思考**：如何避免单一LLM的思维局限？

### 4. 接口标准化
统一使用OpenAI兼容格式（api_key + base_url + model_name）：
- 降低集成复杂度
- 便于切换LLM提供商
- 避免vendor lock-in风险

### 5. 反思机制
每个Agent都实现ReflectionNode：
- 分析已有结果
- 识别信息缺口
- 生成优化建议
- 返回下一轮策略

**价值**：自我优化能力，提高结果质量

### 6. 模块化设计
工具、节点、状态独立管理：
- 易于单元测试
- 便于功能扩展
- 降低耦合度

---

## 🗺️ 学习路径总览

```
第一阶段：理解设计理念（0.5天）
    ↓
第二阶段：学习统一架构（1天）
    ↓
第三阶段：学习各个Agent（1.5天）
    ↓
第四阶段：学习协作机制（1天）
    ↓
第五阶段：学习辅助系统（0.5-1天）
```

**学习原则**：从宏观到微观，从简单到复杂，从基础到应用

---

## 📖 第一阶段：理解设计理念

**目标**：理解为什么这样设计，建立架构全局观

### 阅读顺序

#### 1. 项目总览文档
**文件**：`CLAUDE.md`

**重点关注**：
- "项目概述"和"系统架构"部分
- "架构决策"部分（最重要！）
  - 为何选择Flask + Streamlit组合？
  - 为何使用论坛机制？
  - 为何所有LLM使用OpenAI格式？
- "扩展指南"部分（了解设计的可扩展性）

**思考问题**：
- 多智能体架构相比单一LLM有什么优势？
- ForumEngine的"论坛机制"解决了什么问题？
- 为什么需要四个不同的Agent？

#### 2. 系统入口文件
**文件**：`app.py`

**重点关注**：
- 整体流程编排（不需要看具体实现）
- 各Agent如何被调用
- ForumEngine如何启动和监控
- Flask路由和Streamlit应用的关系

**学习目标**：理解系统启动流程和Agent调度逻辑

#### 3. ForumEngine简介
**文件**：`ForumEngine/monitor.py`（浏览结构，暂不深入）

**重点关注**：
- 文件开头的模块说明注释
- 主要类和方法的命名（理解职责）

### 阶段验证

能够回答以下问题：
- [ ] 为什么不用单一超强LLM处理所有任务？
- [ ] ForumEngine的论坛机制有什么价值？
- [ ] 四个Agent的职责分工是什么？
- [ ] 系统如何从用户请求到生成报告？

---

## 📖 第二阶段：学习统一架构

**目标**：通过一个Agent（QueryEngine）理解所有Agent的通用模式

**为何选择QueryEngine**：功能相对简单，工具集清晰，是学习统一架构的最佳范例

### 阅读顺序

#### 1. 状态管理系统
**文件**：`QueryEngine/state/state.py`

**重点关注**：
- State类的属性定义
- 状态字段的含义（query、search_results、summary等）
- 状态如何在节点间传递

**学习目标**：理解Agent如何维护执行状态

#### 2. LLM统一客户端
**文件**：`QueryEngine/llms/base.py`

**重点关注**：
- LLMClient类的初始化参数（api_key、base_url、model_name）
- `create_completion()`方法的实现
- `acreate_completion()`异步方法
- 错误处理机制

**学习目标**：理解如何统一调用不同LLM提供商

#### 3. 节点基础类
**文件**：`QueryEngine/nodes/base_node.py`

**重点关注**：
- BaseNode抽象类的设计
- `execute()`方法的约定
- 节点如何接收和返回State

**学习目标**：理解节点系统的设计模式

#### 4. 具体节点实现
**按顺序阅读**：
1. `QueryEngine/nodes/search_node.py` - 首轮搜索节点
2. `QueryEngine/nodes/reflection_node.py` - 反思优化节点
3. `QueryEngine/nodes/summary_node.py` - 总结归纳节点
4. `QueryEngine/nodes/formatting_node.py` - 格式化输出节点

**重点关注**：
- 每个节点的`execute()`方法
- 节点如何调用LLM客户端
- 节点如何使用tools
- 节点如何更新State
- Reflection节点的自我优化逻辑

**学习目标**：理解FirstSearch → Reflection → Summary → Formatting的处理流程

#### 5. Agent主类
**文件**：`QueryEngine/agent.py`

**重点关注**：
- Agent类的初始化（LLM、tools、nodes）
- `run()`方法的workflow编排
- 节点之间的调用顺序
- 如何判断是否需要多轮优化

**学习目标**：理解Agent如何编排完整workflow

#### 6. 工具集成
**文件**：`QueryEngine/tools/`目录下的工具文件

**重点关注**：
- 工具类的设计模式
- Tavily API的封装方式
- 工具如何被Agent调用

**学习目标**：理解如何封装外部能力为工具

#### 7. 提示词管理
**文件**：`QueryEngine/prompts/prompts.py`

**重点关注**：
- 提示词模板的组织方式
- 如何使用Python字符串格式化
- 不同节点使用不同的提示词模板

**学习目标**：理解提示词的模板化管理

### 阶段验证

能够回答以下问题并绘制流程图：
- [ ] State在节点间如何传递和更新？
- [ ] LLMClient如何实现LLM提供商的切换？
- [ ] FirstSearch → Reflection → Summary → Formatting的完整流程是什么？
- [ ] Reflection节点如何识别信息缺口？
- [ ] 如果要添加新节点，需要做什么？

**实践任务**：
- 绘制QueryEngine的workflow流程图
- 标注每个节点的输入和输出

---

## 📖 第三阶段：学习各个Agent

**目标**：理解各Agent的差异化实现和工具选择逻辑

**学习顺序**：QueryEngine → MediaEngine → InsightEngine → ReportEngine

### 1. QueryEngine - 广度搜索能力

**已在第二阶段学习完毕**

**核心特点回顾**：
- 工具：Tavily API的6种搜索工具（新闻搜索、网页搜索等）
- 推荐LLM：DeepSeek Reasoner（推理能力强）
- 应用场景：互联网信息检索、事件追踪、新闻监控

### 2. MediaEngine - 多模态分析能力

**文件路径**：`MediaEngine/`

**阅读顺序**：
1. `MediaEngine/tools/` - 先看工具集
   - 视频分析工具
   - 图像OCR工具
   - 结构化信息提取工具
2. `MediaEngine/agent.py` - 理解如何调用多模态工具
3. `MediaEngine/nodes/` - 看处理节点的差异（与QueryEngine对比）

**重点关注**：
- 多模态工具的实现原理
- 如何处理视频和图像数据
- 如何解析搜索结果卡片的结构化信息
- 为什么选择Gemini 2.5 Pro（多模态理解能力）

**思考问题**：
- 多模态分析相比纯文本分析的难点在哪？
- 为何需要独立的MediaEngine而不是集成在QueryEngine？

### 3. InsightEngine - 数据库挖掘能力

**文件路径**：`InsightEngine/`

**阅读顺序**：
1. `InsightEngine/tools/search.py` - MediaCrawlerDB工具类
   - `search_topic_globally()` - 话题全局搜索
   - `get_comments_by_post_id()` - 评论数据获取
   - `get_topic_statistics()` - 统计分析
   - 其他数据库查询工具
2. `InsightEngine/tools/` - 中间件工具
   - Qwen关键词优化器
   - 多语言情感分析器（重点）
3. `SentimentAnalysisModel/` - 情感分析模型（可选深入）
   - 浏览各模型目录，了解技术选型
4. `InsightEngine/agent.py` - 理解数据库查询的workflow
5. `InsightEngine/nodes/` - 关注数据处理和分析节点

**重点关注**：
- 如何设计数据库查询工具？
- 为什么需要Qwen关键词优化器？
- 多语言情感分析如何实现？
- 为什么选择Kimi K2（长上下文能力）

**思考问题**：
- 数据库挖掘相比互联网搜索的优势是什么？
- 如何将自己的业务数据库接入系统？

### 4. ReportEngine - 报告生成能力

**文件路径**：`ReportEngine/`

**阅读顺序**：
1. `ReportEngine/report_template/` - 浏览报告模板
   - 查看几个.md模板文件
   - 理解模板的结构和变量
2. `ReportEngine/tools/` - 模板选择和HTML生成工具
3. `ReportEngine/agent.py` - 理解报告生成workflow
4. `ReportEngine/nodes/` - 关注模板选择和多轮优化节点

**重点关注**：
- 如何实现模板动态选择？
- 如何支持多轮报告优化？
- HTML生成工具的实现
- 为什么选择Gemini 2.5 Pro（生成能力强）

**思考问题**：
- 报告生成为何需要独立Agent？
- 如何自定义报告模板？

### 阶段验证

能够回答以下问题：
- [ ] 四个Agent分别使用什么工具集？
- [ ] 为何QueryEngine用DeepSeek，MediaEngine用Gemini？
- [ ] InsightEngine的数据从哪里来？
- [ ] ReportEngine如何选择合适的报告模板？
- [ ] 如何添加新的工具到某个Agent？

**对比练习**：
- 制作表格对比四个Agent的差异（工具、LLM、应用场景）

---

## 📖 第四阶段：学习协作机制

**目标**：深入理解ForumEngine的"思维碰撞"实现

**这是系统的创新亮点！**

### 阅读顺序

#### 1. 论坛读取接口
**文件**：`utils/forum_reader.py`

**重点关注**：
- Agent如何读取论坛内容
- 读取接口的设计
- 如何过滤和筛选相关信息

**学习目标**：理解Agent侧的论坛访问机制

#### 2. 监控模块
**文件**：`ForumEngine/monitor.py`

**重点关注**：
- 如何实时监控`logs/forum.log`
- 如何提取关键信息
- 监控的触发条件和频率
- 多线程实现细节

**学习目标**：理解ForumEngine如何监控Agent发言

#### 3. 主持人模块
**文件**：`ForumEngine/llm_host.py`

**重点关注**：
- LLM主持人的提示词设计
- 如何生成总结和引导
- 如何判断是否达成共识
- 如何引导下一轮讨论

**学习目标**：理解主持人如何协调Agent协作

#### 4. 论坛日志
**文件**：`logs/forum.log`（如果有历史记录）

**重点关注**：
- Agent发言的格式
- 主持人总结的格式
- 完整的协作流程示例

**学习目标**：通过实例理解论坛交流模式

#### 5. 系统集成
**文件**：`app.py`中ForumEngine的调用部分

**重点关注**：
- ForumEngine何时启动
- 如何与各Agent协调
- 循环迭代的终止条件
- 异常处理机制

**学习目标**：理解ForumEngine在整体系统中的位置

### 协作流程图

绘制以下流程图帮助理解：

```
用户请求
    ↓
各Agent并行分析
    ↓
Agent写入forum.log
    ↓
ForumEngine监控提取
    ↓
LLM主持人生成总结
    ↓
主持人写入forum.log
    ↓
各Agent读取论坛内容
    ↓
[判断] 是否达成共识？
    ├─ 是：输出最终结果
    └─ 否：进入下一轮迭代（回到"各Agent并行分析"）
```

### 阶段验证

能够回答以下问题：
- [ ] ForumEngine如何实现Agent间的"思维碰撞"？
- [ ] 主持人LLM的作用是什么？
- [ ] 如何判断Agent是否达成共识？
- [ ] 论坛机制相比简单的结果合并有什么优势？
- [ ] 如何防止无限循环迭代？

**实践任务**：
- 绘制ForumEngine的完整协作流程图
- 标注每个环节的数据流向

---

## 📖 第五阶段：学习辅助系统

**目标**：了解数据来源和支撑系统

### 1. 配置系统

**文件**：`config.py`

**重点关注**：
- 数据库配置（DB_HOST、DB_PORT等）
- 各Agent的LLM配置（API_KEY、BASE_URL、MODEL_NAME）
- 网络工具配置（TAVILY_API_KEY、BOCHA_WEB_SEARCH_API_KEY）

**学习目标**：理解系统配置的组织方式

### 2. MindSpider爬虫系统

**阅读顺序**：
1. `MindSpider/main.py` - 爬虫入口
   - 理解命令行参数
   - 理解两阶段爬取流程
2. `MindSpider/schema/mindspider_tables.sql` - 数据库结构
   - 理解表结构设计
   - 理解数据关系
3. `MindSpider/BroadTopicExtraction/` - 话题提取流程（浏览）
4. `MindSpider/DeepSentimentCrawling/` - 深度爬取流程（浏览）

**重点关注**：
- 两阶段爬取的设计思想
- 支持的平台（微博、小红书、抖音等）
- 数据如何存储到数据库

**思考问题**：
- 为何需要两阶段爬取？
- 如何添加新的爬虫平台？

### 3. 情感分析模型

**文件路径**：`SentimentAnalysisModel/`

**浏览各模型目录**（不需要深入代码）：
- `WeiboMultilingualSentiment/` - 多语言模型（推荐）
- `WeiboSentiment_SmallQwen/` - 小参数Qwen3
- `WeiboSentiment_Finetuned/BertChinese-Lora/` - BERT微调
- `WeiboSentiment_Finetuned/GPT2-Lora/` - GPT-2 LoRA
- `WeiboSentiment_MachineLearning/` - 传统ML方法

**重点关注**：
- 各模型的README（如果有）
- 模型的输入输出格式
- 如何选择合适的模型

**学习目标**：了解情感分析的技术选型

### 数据流转图

绘制数据从爬取到分析的完整流程：

```
新闻源/社交平台
    ↓
MindSpider爬虫（两阶段）
    ↓
MySQL数据库（MediaCrawlerDB）
    ↓
情感分析模型（可选）
    ↓
InsightEngine（数据库查询）
    ↓
ForumEngine（协作分析）
    ↓
ReportEngine（报告生成）
    ↓
最终报告
```

### 阶段验证

能够回答以下问题：
- [ ] 数据如何从爬取到分析的完整流程？
- [ ] MindSpider的两阶段爬取分别做什么？
- [ ] 情感分析有哪些技术选项？
- [ ] 如何将自己的数据库接入系统？

---

## ✅ 学习验证与实践建议

### 最终掌握标准

能够回答以下四个核心问题：

#### 1. 为什么不用单一超强LLM？
**参考答案要点**：
- 单一LLM存在思维局限和偏见
- 不同任务需要不同能力（推理/多模态/长上下文/生成）
- 专业分工更高效，成本更优化
- 协作机制产生集体智能，质量更高

#### 2. ForumEngine如何实现"思维碰撞"？
**参考答案要点**：
- Agent将分析结果写入共享论坛日志
- 监控模块实时提取关键信息
- LLM主持人生成总结和引导
- 各Agent读取论坛内容，循环迭代
- 通过辩论和多轮优化达成共识

#### 3. 如何添加新的Agent？
**参考答案要点**：
- 复制现有Agent目录结构
- 实现统一架构（agent.py、state、nodes、tools、prompts）
- 定义专属工具集和提示词模板
- 在app.py注册新Agent
- 添加Streamlit调试界面

#### 4. 数据如何流转（爬取→存储→分析→报告）？
**参考答案要点**：
- MindSpider爬虫爬取多平台数据
- 存储到MySQL数据库（MediaCrawlerDB）
- InsightEngine通过工具查询数据库
- 各Agent协作分析（通过ForumEngine）
- ReportEngine生成最终报告

### 实践任务

#### 任务1：绘制架构图
- 系统整体架构图
- 单个Agent的workflow流程图
- ForumEngine的协作流程图
- 数据流转图

#### 任务2：运行调试
```bash
# 启动完整系统
python app.py

# 单独启动Agent调试
streamlit run SingleEngineApp/query_engine_streamlit_app.py --server.port 8503
```

#### 任务3：代码追踪
- 设置断点，调试QueryEngine的完整workflow
- 观察State在节点间的传递
- 查看LLM的实际请求和响应

#### 任务4：小改动实践
- 修改QueryEngine的提示词模板
- 添加一个简单的自定义工具
- 调整Reflection节点的优化逻辑

### 进阶学习

完成基础学习后，可以尝试：

1. **扩展Agent功能**
   - 为InsightEngine添加新的数据库查询工具
   - 为ReportEngine添加新的报告模板

2. **优化ForumEngine**
   - 调整主持人的提示词策略
   - 优化共识判断逻辑

3. **集成新能力**
   - 接入新的LLM提供商
   - 添加新的爬虫平台支持

4. **性能优化**
   - 实现Agent并行处理
   - 优化数据库查询效率

---

## 📚 核心文档速查

### 必读文档
- `CLAUDE.md` - 项目总览和设计决策
- `README.md`（如果有） - 快速开始指南

### 核心代码文件
- `app.py` - 系统入口
- `config.py` - 全局配置
- `QueryEngine/agent.py` - Agent范例
- `ForumEngine/monitor.py` - 协作机制

### 工具与模型
- `InsightEngine/tools/search.py` - 数据库查询工具
- `SentimentAnalysisModel/` - 情感分析模型
- `MindSpider/main.py` - 爬虫系统入口

---

## 🎓 学习小贴士

1. **不要跳阶段**：按顺序学习很重要，后面的理解依赖前面的基础
2. **多画图**：流程图和架构图能帮助你整理思路
3. **多思考"为什么"**：理解设计理念比记住代码更重要
4. **动手实践**：运行代码、调试、小改动能加深理解
5. **对比学习**：对比各Agent的差异，思考为何这样设计
6. **记录问题**：遇到不理解的地方记下来，后续可能豁然开朗

---

## 🤔 常见疑问解答

### Q1: 为什么有些Agent用异步，有些用同步？
A: 取决于IO密集程度。频繁网络请求的Agent（如QueryEngine）使用异步提高效率。

### Q2: ForumEngine的主持人也是LLM，会不会也有局限性？
A: 会有，但主持人的职责是协调和总结，不做具体分析。且可以配置不同的主持人LLM。

### Q3: 能否用GPT-4替换所有Agent的LLM？
A: 可以，但不推荐。不同任务的最优模型不同，使用专业化LLM更高效且成本更优。

### Q4: 如何处理Agent之间的意见分歧？
A: ForumEngine的主持人会识别分歧点，引导各Agent提供更多证据，通过多轮辩论达成共识。

### Q5: 系统如何保证数据隐私？
A: 私有数据库部署在本地，LLM调用可以使用私有部署的模型，不必将数据发送到公有云。

---

## 📌 结语

BettaFish项目展示了多智能体协作的强大能力。通过专业分工、统一架构和协作机制，系统实现了超越单一LLM的集体智能。

**学习这个项目，你将收获**：
- 多智能体系统的架构设计思想
- 统一架构范式的实践经验
- LLM工程化的最佳实践
- 协作机制的创新思路

**祝你学习愉快！如有疑问，可以参考CLAUDE.md或查阅代码注释。**

---

*最后更新：2025-10-29*
