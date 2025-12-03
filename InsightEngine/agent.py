"""
Deep Search Agent主类
整合所有模块，实现完整的深度搜索流程
"""

import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

from .llms import LLMClient
from .nodes import (
    ReportStructureNode,
    FirstSearchNode, 
    ReflectionNode,
    FirstSummaryNode,
    ReflectionSummaryNode,
    ReportFormattingNode
)
from .state import State
from .tools import TrainingDataDB, DBResponse
from .utils import Config, load_config, format_search_results_for_prompt


class DeepSearchAgent:
    """Deep Search Agent主类"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化Deep Search Agent
        
        Args:
            config: 配置对象，如果不提供则自动加载
        """
        # 加载配置
        self.config = config or load_config()
        
        # 初始化LLM客户端
        self.llm_client = self._initialize_llm()
        
        # 设置数据库环境变量
        os.environ["DB_HOST"] = self.config.db_host or ""
        os.environ["DB_USER"] = self.config.db_user or ""
        os.environ["DB_PASSWORD"] = self.config.db_password or ""
        os.environ["DB_NAME"] = self.config.db_name or ""
        os.environ["DB_PORT"] = str(self.config.db_port)
        os.environ["DB_CHARSET"] = self.config.db_charset
        
        # 初始化搜索工具集
        self.search_agency = TrainingDataDB()

        # 初始化节点
        self._initialize_nodes()

        # 状态
        self.state = State()

        # 确保输出目录存在
        os.makedirs(self.config.output_dir, exist_ok=True)

        print(f"Insight Agent已初始化")
        print(f"使用LLM: {self.llm_client.get_model_info()}")
        print(f"搜索工具集: TrainingDataDB (支持6种训练数据查询工具)")
    
    def _initialize_llm(self) -> LLMClient:
        """初始化LLM客户端"""
        return LLMClient(
            api_key=self.config.llm_api_key,
            model_name=self.config.llm_model_name,
            base_url=self.config.llm_base_url,
        )
    
    def _initialize_nodes(self):
        """初始化处理节点"""
        self.first_search_node = FirstSearchNode(self.llm_client)
        self.reflection_node = ReflectionNode(self.llm_client)
        self.first_summary_node = FirstSummaryNode(self.llm_client)
        self.reflection_summary_node = ReflectionSummaryNode(self.llm_client)
        self.report_formatting_node = ReportFormattingNode(self.llm_client)
    
    def _validate_date_format(self, date_str: str) -> bool:
        """
        验证日期格式是否为YYYY-MM-DD
        
        Args:
            date_str: 日期字符串
            
        Returns:
            是否为有效格式
        """
        if not date_str:
            return False
        
        # 检查格式
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_str):
            return False
        
        # 检查日期是否有效
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def execute_search_tool(self, tool_name: str, query: str, **kwargs) -> DBResponse:
        """
        执行指定的训练数据库查询工具

        Args:
            tool_name: 工具名称，可选值：
                - "search_recent_trainings": 查询最近N天训练记录
                - "search_by_date_range": 按日期范围查询训练记录
                - "get_training_stats": 获取训练统计数据
                - "search_by_distance_range": 按距离范围查询
                - "search_by_heart_rate": 按心率区间查询
                - "get_exercise_type_summary": 按运动类型汇总
            query: 查询描述（用于日志记录）
            **kwargs: 额外参数（如days, start_date, end_date, exercise_type, min_distance_km,
                     max_distance_km, min_avg_hr, max_avg_hr, limit等）

        Returns:
            DBResponse对象
        """
        print(f"  → 执行训练数据查询工具: {tool_name}")
        print(f"  📋 查询描述: '{query}'")

        try:
            if tool_name == "search_recent_trainings":
                days = kwargs.get("days")
                if not days:
                    raise ValueError("search_recent_trainings工具需要days参数")

                exercise_type = kwargs.get("exercise_type")
                limit = kwargs.get("limit", 50)

                response = self.search_agency.search_recent_trainings(
                    days=days,
                    exercise_type=exercise_type,
                    limit=limit
                )

            elif tool_name == "search_by_date_range":
                start_date = kwargs.get("start_date")
                end_date = kwargs.get("end_date")
                if not start_date or not end_date:
                    raise ValueError("search_by_date_range工具需要start_date和end_date参数")

                exercise_type = kwargs.get("exercise_type")
                limit = kwargs.get("limit", 100)

                response = self.search_agency.search_by_date_range(
                    start_date=start_date,
                    end_date=end_date,
                    exercise_type=exercise_type,
                    limit=limit
                )

            elif tool_name == "get_training_stats":
                start_date = kwargs.get("start_date")
                end_date = kwargs.get("end_date")
                exercise_type = kwargs.get("exercise_type")

                response = self.search_agency.get_training_stats(
                    start_date=start_date,
                    end_date=end_date,
                    exercise_type=exercise_type
                )

            elif tool_name == "search_by_distance_range":
                min_distance_km = kwargs.get("min_distance_km")
                if min_distance_km is None:
                    raise ValueError("search_by_distance_range工具需要min_distance_km参数")

                max_distance_km = kwargs.get("max_distance_km")
                exercise_type = kwargs.get("exercise_type")
                limit = kwargs.get("limit", 50)

                response = self.search_agency.search_by_distance_range(
                    min_distance_km=min_distance_km,
                    max_distance_km=max_distance_km,
                    exercise_type=exercise_type,
                    limit=limit
                )

            elif tool_name == "search_by_heart_rate":
                min_avg_hr = kwargs.get("min_avg_hr")
                if min_avg_hr is None:
                    raise ValueError("search_by_heart_rate工具需要min_avg_hr参数")

                max_avg_hr = kwargs.get("max_avg_hr")
                exercise_type = kwargs.get("exercise_type")
                limit = kwargs.get("limit", 50)

                response = self.search_agency.search_by_heart_rate(
                    min_avg_hr=min_avg_hr,
                    max_avg_hr=max_avg_hr,
                    exercise_type=exercise_type,
                    limit=limit
                )

            elif tool_name == "get_exercise_type_summary":
                start_date = kwargs.get("start_date")
                end_date = kwargs.get("end_date")

                response = self.search_agency.get_exercise_type_summary(
                    start_date=start_date,
                    end_date=end_date
                )

            else:
                print(f"    ⚠️ 未知的查询工具: {tool_name}")
                raise ValueError(f"不支持的工具类型: {tool_name}")

            # 输出查询结果统计
            if response.results:
                print(f"  ✅ 找到 {len(response.results)} 条训练记录")
            else:
                print(f"  ℹ️  未找到符合条件的训练记录")

            return response

        except Exception as e:
            print(f"  ❌ 查询执行失败: {str(e)}")
            raise
    
    
    def research(self, query: str, save_report: bool = True) -> str:
        """
        执行深度研究
        
        Args:
            query: 研究查询
            save_report: 是否保存报告到文件
            
        Returns:
            最终报告内容
        """
        print(f"\n{'='*60}")
        print(f"开始深度研究: {query}")
        print(f"{'='*60}")
        
        try:
            # Step 1: 生成报告结构
            self._generate_report_structure(query)
            
            # Step 2: 处理每个段落
            self._process_paragraphs()
            
            # Step 3: 生成最终报告
            final_report = self._generate_final_report()
            
            # Step 4: 保存报告
            if save_report:
                self._save_report(final_report)
            
            print(f"\n{'='*60}")
            print("深度研究完成！")
            print(f"{'='*60}")
            
            return final_report
            
        except Exception as e:
            print(f"研究过程中发生错误: {str(e)}")
            raise e
    
    def _generate_report_structure(self, query: str):
        """生成报告结构"""
        print(f"\n[步骤 1] 生成报告结构...")
        
        # 创建报告结构节点
        report_structure_node = ReportStructureNode(self.llm_client, query)
        
        # 生成结构并更新状态
        self.state = report_structure_node.mutate_state(state=self.state)
        
        print(f"报告结构已生成，共 {len(self.state.paragraphs)} 个段落:")
        for i, paragraph in enumerate(self.state.paragraphs, 1):
            print(f"  {i}. {paragraph.title}")
    
    def _process_paragraphs(self):
        """处理所有段落"""
        total_paragraphs = len(self.state.paragraphs)
        
        for i in range(total_paragraphs):
            print(f"\n[步骤 2.{i+1}] 处理段落: {self.state.paragraphs[i].title}")
            print("-" * 50)
            
            # 初始搜索和总结
            self._initial_search_and_summary(i)
            
            # 反思循环
            self._reflection_loop(i)
            
            # 标记段落完成
            self.state.paragraphs[i].research.mark_completed()
            
            progress = (i + 1) / total_paragraphs * 100
            print(f"段落处理完成 ({progress:.1f}%)")
    
    def _initial_search_and_summary(self, paragraph_index: int):
        """执行初始搜索和总结"""
        paragraph = self.state.paragraphs[paragraph_index]
        
        # 准备搜索输入
        search_input = {
            "title": paragraph.title,
            "content": paragraph.content
        }
        
        # 生成搜索查询和工具选择
        print("  - 生成搜索查询...")
        search_output = self.first_search_node.run(search_input)
        search_query = search_output["search_query"]
        search_tool = search_output.get("search_tool", "search_recent_trainings")  # 默认工具
        reasoning = search_output["reasoning"]
        
        print(f"  - 搜索查询: {search_query}")
        print(f"  - 选择的工具: {search_tool}")
        print(f"  - 推理: {reasoning}")
        
        # 执行搜索
        print("  - 执行数据库查询...")

        # 处理训练数据工具参数
        search_kwargs = {}

        # search_recent_trainings: 需要days参数
        if search_tool == "search_recent_trainings":
            days = search_output.get("days")
            if not days:
                print(f"    ⚠️ search_recent_trainings工具缺少days参数,默认使用30天")
                days = 30
            search_kwargs["days"] = days
            search_kwargs["exercise_type"] = search_output.get("exercise_type")
            search_kwargs["limit"] = search_output.get("limit", 50)
            print(f"  - 查询最近 {days} 天训练记录")

        # search_by_date_range: 需要start_date和end_date
        elif search_tool == "search_by_date_range":
            start_date = search_output.get("start_date")
            end_date = search_output.get("end_date")

            if start_date and end_date:
                if self._validate_date_format(start_date) and self._validate_date_format(end_date):
                    search_kwargs["start_date"] = start_date
                    search_kwargs["end_date"] = end_date
                    search_kwargs["exercise_type"] = search_output.get("exercise_type")
                    search_kwargs["limit"] = search_output.get("limit", 100)
                    print(f"  - 时间范围: {start_date} 到 {end_date}")
                else:
                    print(f"    ⚠️ 日期格式错误,改用search_recent_trainings")
                    search_tool = "search_recent_trainings"
                    search_kwargs = {"days": 30, "limit": 50}
            else:
                print(f"    ⚠️ 缺少日期参数,改用search_recent_trainings")
                search_tool = "search_recent_trainings"
                search_kwargs = {"days": 30, "limit": 50}

        # get_training_stats: 可选start_date和end_date
        elif search_tool == "get_training_stats":
            start_date = search_output.get("start_date")
            end_date = search_output.get("end_date")
            if start_date and self._validate_date_format(start_date):
                search_kwargs["start_date"] = start_date
            if end_date and self._validate_date_format(end_date):
                search_kwargs["end_date"] = end_date
            search_kwargs["exercise_type"] = search_output.get("exercise_type")
            print(f"  - 获取训练统计数据")

        # search_by_distance_range: 需要min_distance_km
        elif search_tool == "search_by_distance_range":
            min_distance_km = search_output.get("min_distance_km")
            if min_distance_km is not None:
                search_kwargs["min_distance_km"] = min_distance_km
                search_kwargs["max_distance_km"] = search_output.get("max_distance_km")
                search_kwargs["exercise_type"] = search_output.get("exercise_type")
                search_kwargs["limit"] = search_output.get("limit", 50)
                print(f"  - 距离范围: {min_distance_km}km+")
            else:
                print(f"    ⚠️ 缺少min_distance_km参数,改用search_recent_trainings")
                search_tool = "search_recent_trainings"
                search_kwargs = {"days": 30, "limit": 50}

        # search_by_heart_rate: 需要min_avg_hr
        elif search_tool == "search_by_heart_rate":
            min_avg_hr = search_output.get("min_avg_hr")
            if min_avg_hr is not None:
                search_kwargs["min_avg_hr"] = min_avg_hr
                search_kwargs["max_avg_hr"] = search_output.get("max_avg_hr")
                search_kwargs["exercise_type"] = search_output.get("exercise_type")
                search_kwargs["limit"] = search_output.get("limit", 50)
                print(f"  - 心率范围: {min_avg_hr}bpm+")
            else:
                print(f"    ⚠️ 缺少min_avg_hr参数,改用search_recent_trainings")
                search_tool = "search_recent_trainings"
                search_kwargs = {"days": 30, "limit": 50}

        # get_exercise_type_summary: 可选start_date和end_date
        elif search_tool == "get_exercise_type_summary":
            start_date = search_output.get("start_date")
            end_date = search_output.get("end_date")
            if start_date and self._validate_date_format(start_date):
                search_kwargs["start_date"] = start_date
            if end_date and self._validate_date_format(end_date):
                search_kwargs["end_date"] = end_date
            print(f"  - 按运动类型汇总")

        else:
            print(f"    ⚠️ 未知工具 {search_tool},使用search_recent_trainings")
            search_tool = "search_recent_trainings"
            search_kwargs = {"days": 30, "limit": 50}

        search_response = self.execute_search_tool(search_tool, search_query, **search_kwargs)
        
        # 转换为兼容格式
        search_results = []
        if search_response and search_response.results:
            # 使用配置文件控制传递给LLM的结果数量，0表示不限制
            if self.config.max_search_results_for_llm > 0:
                max_results = min(len(search_response.results), self.config.max_search_results_for_llm)
            else:
                max_results = len(search_response.results)  # 不限制，传递所有结果
            for result in search_response.results[:max_results]:
                search_results.append({
                    'title': result.title_or_content,
                    'url': result.url or "",
                    'content': result.title_or_content,
                    'score': result.hotness_score,
                    'raw_content': result.title_or_content,
                    'published_date': result.publish_time.isoformat() if result.publish_time else None,
                    'platform': result.platform,
                    'content_type': result.content_type,
                    'author': result.author_nickname,
                    'engagement': result.engagement
                })
        
        if search_results:
            print(f"  - 找到 {len(search_results)} 个搜索结果")
            for j, result in enumerate(search_results, 1):
                date_info = f" (发布于: {result.get('published_date', 'N/A')})" if result.get('published_date') else ""
                print(f"    {j}. {result['title'][:50]}...{date_info}")
        else:
            print("  - 未找到搜索结果")
        
        # 更新状态中的搜索历史
        paragraph.research.add_search_results(search_query, search_results)
        
        # 生成初始总结
        print("  - 生成初始总结...")
        summary_input = {
            "title": paragraph.title,
            "content": paragraph.content,
            "search_query": search_query,
            "search_results": format_search_results_for_prompt(
                search_results, self.config.max_content_length
            )
        }
        
        # 更新状态
        self.state = self.first_summary_node.mutate_state(
            summary_input, self.state, paragraph_index
        )
        
        print("  - 初始总结完成")
    
    def _reflection_loop(self, paragraph_index: int):
        """执行反思循环"""
        paragraph = self.state.paragraphs[paragraph_index]
        
        for reflection_i in range(self.config.max_reflections):
            print(f"  - 反思 {reflection_i + 1}/{self.config.max_reflections}...")
            
            # 准备反思输入
            reflection_input = {
                "title": paragraph.title,
                "content": paragraph.content,
                "paragraph_latest_state": paragraph.research.latest_summary
            }
            
            # 生成反思搜索查询
            reflection_output = self.reflection_node.run(reflection_input)
            search_query = reflection_output["search_query"]
            search_tool = reflection_output.get("search_tool", "search_recent_trainings")  # 默认工具
            reasoning = reflection_output["reasoning"]
            
            print(f"    反思查询: {search_query}")
            print(f"    选择的工具: {search_tool}")
            print(f"    反思推理: {reasoning}")
            
            # 执行反思搜索
            # 处理训练数据工具参数
            search_kwargs = {}

            # search_recent_trainings: 需要days参数
            if search_tool == "search_recent_trainings":
                days = reflection_output.get("days")
                if not days:
                    print(f"      ⚠️ search_recent_trainings工具缺少days参数,默认使用30天")
                    days = 30
                search_kwargs["days"] = days
                search_kwargs["exercise_type"] = reflection_output.get("exercise_type")
                search_kwargs["limit"] = reflection_output.get("limit", 50)
                print(f"    查询最近 {days} 天训练记录")

            # search_by_date_range: 需要start_date和end_date
            elif search_tool == "search_by_date_range":
                start_date = reflection_output.get("start_date")
                end_date = reflection_output.get("end_date")

                if start_date and end_date:
                    if self._validate_date_format(start_date) and self._validate_date_format(end_date):
                        search_kwargs["start_date"] = start_date
                        search_kwargs["end_date"] = end_date
                        search_kwargs["exercise_type"] = reflection_output.get("exercise_type")
                        search_kwargs["limit"] = reflection_output.get("limit", 100)
                        print(f"    时间范围: {start_date} 到 {end_date}")
                    else:
                        print(f"      ⚠️ 日期格式错误,改用search_recent_trainings")
                        search_tool = "search_recent_trainings"
                        search_kwargs = {"days": 30, "limit": 50}
                else:
                    print(f"      ⚠️ 缺少日期参数,改用search_recent_trainings")
                    search_tool = "search_recent_trainings"
                    search_kwargs = {"days": 30, "limit": 50}

            # get_training_stats: 可选start_date和end_date
            elif search_tool == "get_training_stats":
                start_date = reflection_output.get("start_date")
                end_date = reflection_output.get("end_date")
                if start_date and self._validate_date_format(start_date):
                    search_kwargs["start_date"] = start_date
                if end_date and self._validate_date_format(end_date):
                    search_kwargs["end_date"] = end_date
                search_kwargs["exercise_type"] = reflection_output.get("exercise_type")
                print(f"    获取训练统计数据")

            # search_by_distance_range: 需要min_distance_km
            elif search_tool == "search_by_distance_range":
                min_distance_km = reflection_output.get("min_distance_km")
                if min_distance_km is not None:
                    search_kwargs["min_distance_km"] = min_distance_km
                    search_kwargs["max_distance_km"] = reflection_output.get("max_distance_km")
                    search_kwargs["exercise_type"] = reflection_output.get("exercise_type")
                    search_kwargs["limit"] = reflection_output.get("limit", 50)
                    print(f"    距离范围: {min_distance_km}km+")
                else:
                    print(f"      ⚠️ 缺少min_distance_km参数,改用search_recent_trainings")
                    search_tool = "search_recent_trainings"
                    search_kwargs = {"days": 30, "limit": 50}

            # search_by_heart_rate: 需要min_avg_hr
            elif search_tool == "search_by_heart_rate":
                min_avg_hr = reflection_output.get("min_avg_hr")
                if min_avg_hr is not None:
                    search_kwargs["min_avg_hr"] = min_avg_hr
                    search_kwargs["max_avg_hr"] = reflection_output.get("max_avg_hr")
                    search_kwargs["exercise_type"] = reflection_output.get("exercise_type")
                    search_kwargs["limit"] = reflection_output.get("limit", 50)
                    print(f"    心率范围: {min_avg_hr}bpm+")
                else:
                    print(f"      ⚠️ 缺少min_avg_hr参数,改用search_recent_trainings")
                    search_tool = "search_recent_trainings"
                    search_kwargs = {"days": 30, "limit": 50}

            # get_exercise_type_summary: 可选start_date和end_date
            elif search_tool == "get_exercise_type_summary":
                start_date = reflection_output.get("start_date")
                end_date = reflection_output.get("end_date")
                if start_date and self._validate_date_format(start_date):
                    search_kwargs["start_date"] = start_date
                if end_date and self._validate_date_format(end_date):
                    search_kwargs["end_date"] = end_date
                print(f"    按运动类型汇总")

            else:
                print(f"      ⚠️ 未知工具 {search_tool},使用search_recent_trainings")
                search_tool = "search_recent_trainings"
                search_kwargs = {"days": 30, "limit": 50}

            search_response = self.execute_search_tool(search_tool, search_query, **search_kwargs)
            
            # 转换为兼容格式
            search_results = []
            if search_response and search_response.results:
                # 使用配置文件控制传递给LLM的结果数量，0表示不限制
                if self.config.max_search_results_for_llm > 0:
                    max_results = min(len(search_response.results), self.config.max_search_results_for_llm)
                else:
                    max_results = len(search_response.results)  # 不限制，传递所有结果
                for result in search_response.results[:max_results]:
                    search_results.append({
                        'title': result.title_or_content,
                        'url': result.url or "",
                        'content': result.title_or_content,
                        'score': result.hotness_score,
                        'raw_content': result.title_or_content,
                        'published_date': result.publish_time.isoformat() if result.publish_time else None,
                        'platform': result.platform,
                        'content_type': result.content_type,
                        'author': result.author_nickname,
                        'engagement': result.engagement
                    })
            
            if search_results:
                print(f"    找到 {len(search_results)} 个反思搜索结果")
                for j, result in enumerate(search_results, 1):
                    date_info = f" (发布于: {result.get('published_date', 'N/A')})" if result.get('published_date') else ""
                    print(f"      {j}. {result['title'][:50]}...{date_info}")
            else:
                print("    未找到反思搜索结果")
            
            # 更新搜索历史
            paragraph.research.add_search_results(search_query, search_results)
            
            # 生成反思总结
            reflection_summary_input = {
                "title": paragraph.title,
                "content": paragraph.content,
                "search_query": search_query,
                "search_results": format_search_results_for_prompt(
                    search_results, self.config.max_content_length
                ),
                "paragraph_latest_state": paragraph.research.latest_summary
            }
            
            # 更新状态
            self.state = self.reflection_summary_node.mutate_state(
                reflection_summary_input, self.state, paragraph_index
            )
            
            print(f"    反思 {reflection_i + 1} 完成")
    
    def _generate_final_report(self) -> str:
        """生成最终报告"""
        print(f"\n[步骤 3] 生成最终报告...")
        
        # 准备报告数据
        report_data = []
        for paragraph in self.state.paragraphs:
            report_data.append({
                "title": paragraph.title,
                "paragraph_latest_state": paragraph.research.latest_summary
            })
        
        # 格式化报告
        try:
            final_report = self.report_formatting_node.run(report_data)
        except Exception as e:
            print(f"LLM格式化失败，使用备用方法: {str(e)}")
            final_report = self.report_formatting_node.format_report_manually(
                report_data, self.state.report_title
            )
        
        # 更新状态
        self.state.final_report = final_report
        self.state.mark_completed()
        
        print("最终报告生成完成")
        return final_report
    
    def _save_report(self, report_content: str):
        """保存报告到文件"""
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = "".join(c for c in self.state.query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        query_safe = query_safe.replace(' ', '_')[:30]
        
        filename = f"deep_search_report_{query_safe}_{timestamp}.md"
        filepath = os.path.join(self.config.output_dir, filename)
        
        # 保存报告
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"报告已保存到: {filepath}")
        
        # 保存状态（如果配置允许）
        if self.config.save_intermediate_states:
            state_filename = f"state_{query_safe}_{timestamp}.json"
            state_filepath = os.path.join(self.config.output_dir, state_filename)
            self.state.save_to_file(state_filepath)
            print(f"状态已保存到: {state_filepath}")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """获取进度摘要"""
        return self.state.get_progress_summary()
    
    def load_state(self, filepath: str):
        """从文件加载状态"""
        self.state = State.load_from_file(filepath)
        print(f"状态已从 {filepath} 加载")
    
    def save_state(self, filepath: str):
        """保存状态到文件"""
        self.state.save_to_file(filepath)
        print(f"状态已保存到 {filepath}")


def create_agent(config_file: Optional[str] = None) -> DeepSearchAgent:
    """
    创建Deep Search Agent实例的便捷函数
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        DeepSearchAgent实例
    """
    config = load_config(config_file)
    return DeepSearchAgent(config)
