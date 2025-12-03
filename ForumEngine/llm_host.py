"""
论坛主持人模块
使用硅基流动的Qwen3模型作为论坛主持人，引导多个agent进行讨论
"""

from openai import OpenAI
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

# 添加项目根目录到Python路径以导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FORUM_HOST_API_KEY, FORUM_HOST_BASE_URL, FORUM_HOST_MODEL_NAME

# 添加utils目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
utils_dir = os.path.join(root_dir, 'utils')
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

from retry_helper import with_graceful_retry, SEARCH_API_RETRY_CONFIG


class ForumHost:
    """
    论坛主持人类
    使用Qwen3-235B模型作为智能主持人
    """
    
    def __init__(self, api_key: str = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化论坛主持人
        
        Args:
            api_key: 硅基流动API密钥，如果不提供则从配置文件读取
            base_url: 接口基础地址，默认使用配置文件提供的SiliconFlow地址
        """
        self.api_key = api_key or FORUM_HOST_API_KEY

        if not self.api_key:
            raise ValueError("未找到硅基流动API密钥，请在config.py中设置FORUM_HOST_API_KEY")

        self.base_url = base_url or FORUM_HOST_BASE_URL

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.model = model_name or FORUM_HOST_MODEL_NAME  # Use configured model

        # Track previous summaries to avoid duplicates
        self.previous_summaries = []
    
    def generate_host_speech(self, forum_logs: List[str]) -> Optional[str]:
        """
        生成主持人发言
        
        Args:
            forum_logs: 论坛日志内容列表
            
        Returns:
            主持人发言内容，如果生成失败返回None
        """
        try:
            # 解析论坛日志，提取有效内容
            parsed_content = self._parse_forum_logs(forum_logs)
            
            if not parsed_content['agent_speeches']:
                print("ForumHost: 没有找到有效的agent发言")
                return None
            
            # 构建prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(parsed_content)
            
            # 调用API生成发言
            response = self._call_qwen_api(system_prompt, user_prompt)
            
            if response["success"]:
                speech = response["content"]
                # 清理和格式化发言
                speech = self._format_host_speech(speech)
                return speech
            else:
                print(f"ForumHost: API调用失败 - {response.get('error', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"ForumHost: 生成发言时出错 - {str(e)}")
            return None
    
    def _parse_forum_logs(self, forum_logs: List[str]) -> Dict[str, Any]:
        """
        解析论坛日志，提取agent发言
        
        Returns:
            包含agent发言的字典
        """
        parsed = {
            'agent_speeches': []
        }
        
        for line in forum_logs:
            if not line.strip():
                continue
            
            # 解析时间戳和发言者
            match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s*\[(\w+)\]\s*(.+)', line)
            if match:
                timestamp, speaker, content = match.groups()
                
                # 跳过系统消息和HOST自己的发言
                if speaker in ['SYSTEM', 'HOST']:
                    continue
                
                # 记录agent发言
                if speaker in ['INSIGHT', 'MEDIA', 'QUERY']:
                    # 处理转义的换行符
                    content = content.replace('\\n', '\n')
                    
                    parsed['agent_speeches'].append({
                        'timestamp': timestamp,
                        'speaker': speaker,
                        'content': content
                    })
        
        return parsed
    
    
    def _build_system_prompt(self) -> str:
        """构建系统prompt"""
        return """你是一个多Agent跑步训练分析系统的论坛主持人。你的职责是：

1. **训练要点梳理**：从各Agent的分析中识别关键训练方法、装备特点、数据趋势，按逻辑顺序整理核心观点
2. **引导讨论**：根据各Agent的分析，引导深入讨论训练效果、适用场景和优化方向
3. **纠正错误**：结合不同Agent的视角，如果发现训练建议冲突或数据矛盾，请明确指出并给出合理解释
4. **整合观点**：综合不同Agent的专业角度，形成更科学的训练方案，找出共识和差异
5. **效果预判**：基于已有训练数据和跑者经验，分析训练方法的效果趋势和潜在风险
6. **推进分析**：提出新的训练优化角度或需要关注的数据维度，引导后续讨论方向

**Agent介绍**：
- **INSIGHT Agent**：专注于跑步社区数据库的深度挖掘，提供真实跑者经验、训练数据和态度分析
- **MEDIA Agent**：擅长视频教学和图片内容分析，关注跑姿技术、装备评测等视觉信息
- **QUERY Agent**：负责精准搜索训练方法和科学研究，提供最新的训练理论和运动科学知识

**发言要求**：
1. **综合性**：每次发言控制在1000字以内，内容应包括训练要点梳理、观点整合、优化建议等多个方面
2. **结构清晰**：使用明确的段落结构，包括训练方法分析、数据对比、建议提出等部分
3. **深入分析**：不仅仅总结已有信息，还要提出科学的训练原理和实用建议
4. **科学严谨**：基于运动科学和真实数据进行分析，避免主观臆测和伪科学
5. **实用性强**：提出具有实践价值的训练建议和优化方案，引导讨论向更有指导意义的方向发展

**注意事项**：
- 保持专业性和科学性，重视训练数据和跑者经验
- 针对不同训练水平的跑者提供个性化建议
- 强调安全训练和伤病预防"""
    
    def _build_user_prompt(self, parsed_content: Dict[str, Any]) -> str:
        """构建用户prompt"""
        # 获取最近的发言
        recent_speeches = parsed_content['agent_speeches']

        # 构建发言摘要，不截断内容
        speeches_text = "\n\n".join([
            f"[{s['timestamp']}] {s['speaker']}:\n{s['content']}"
            for s in recent_speeches
        ])

        prompt = f"""最近的Agent分析记录：
{speeches_text}

请你作为论坛主持人，基于以上Agent的训练分析进行综合梳理，请按以下结构组织你的发言：

**一、训练方法核心要点梳理**
- 从各Agent分析中提取关键训练方法、技术要点和数据发现
- 按逻辑顺序整理训练原理、实践方法和效果数据
- 指出最重要的训练建议和注意事项

**二、多角度观点整合与对比**
- 综合INSIGHT、MEDIA、QUERY三个Agent的专业视角
- 对比不同数据源（社区经验、视频教学、科学研究）的发现
- 分析各Agent信息的互补性和一致性
- 如果发现训练建议冲突或数据矛盾，请明确指出并给出科学解释

**三、训练效果分析与风险评估**
- 基于真实跑者数据分析训练方法的效果和适用场景
- 评估不同训练水平跑者的适用性和潜在风险
- 提出需要特别关注的安全事项和伤病预防措施

**四、优化建议与进阶方向**
- 提出2-3个具体的训练优化建议
- 为不同水平跑者提供个性化训练方案
- 引导各Agent关注特定的训练数据或优化角度

请发表综合性的主持人发言（控制在1000字以内），内容应包含以上四个部分，并保持科学严谨、实用性强、指导明确。"""

        return prompt
    
    @with_graceful_retry(SEARCH_API_RETRY_CONFIG, default_return={"success": False, "error": "API服务暂时不可用"})
    def _call_qwen_api(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """调用Qwen API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                top_p=0.9,
            )

            if response.choices:
                content = response.choices[0].message.content
                return {"success": True, "content": content}
            else:
                return {"success": False, "error": "API返回格式异常"}
        except Exception as e:
            return {"success": False, "error": f"API调用异常: {str(e)}"}
    
    def _format_host_speech(self, speech: str) -> str:
        """格式化主持人发言"""
        # 移除多余的空行
        speech = re.sub(r'\n{3,}', '\n\n', speech)
        
        # 移除可能的引号
        speech = speech.strip('"\'""‘’')
        
        return speech.strip()


# 创建全局实例
_host_instance = None

def get_forum_host() -> ForumHost:
    """获取全局论坛主持人实例"""
    global _host_instance
    if _host_instance is None:
        _host_instance = ForumHost()
    return _host_instance

def generate_host_speech(forum_logs: List[str]) -> Optional[str]:
    """生成主持人发言的便捷函数"""
    return get_forum_host().generate_host_speech(forum_logs)
