"""商标AI智能助手 - LLM服务（LangChain）"""
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, CATEGORY_NAMES


class LLMService:
    """基于 LangChain 的 LLM 服务"""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
            model="qwen-plus",
            temperature=0.8,
            max_tokens=2000,
        )
        self.llm_low_temp = ChatOpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
            model="qwen-plus",
            temperature=0.3,
            max_tokens=500,
        )

    def _call(self, system_text: str, user_text: str, temperature: str = "creative") -> str:
        """直接构建消息，不走模板解析，避免 JSON 花括号冲突"""
        llm = self.llm if temperature == "creative" else self.llm_low_temp
        try:
            messages = [
                SystemMessage(content=system_text),
                HumanMessage(content=user_text),
            ]
            resp = llm.invoke(messages)
            return resp.content
        except Exception as e:
            return f"[API调用失败] {str(e)}"

    def generate_names(self, industry: str, style: str, keywords: str, count: int = 5) -> list[dict]:
        system = """你是一位资深商标命名专家，精通《商标法》和品牌营销。
请根据用户需求，生成有创意且具备注册可行性的商标名称。

要求：
1. 名称要有显著性，不能是行业通用名称
2. 不能包含县级以上行政区划地名
3. 不能夸大宣传或带有欺骗性
4. 2-4个字为宜，朗朗上口
5. 考虑目标行业的品牌调性

严格返回以下JSON数组格式，不要任何其他文字：
[{"name":"商标名","meaning":"含义解释","reason":"适合该行业的原因","registrability":"注册可行性初步判断"}]"""

        user = f"行业：{industry}\n风格偏好：{style}\n关键词：{keywords}\n请生成{count}个商标名称。"
        text = self._call(system, user)

        try:
            json_match = re.search(r"\[.*\]", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return [{"name": "解析失败", "meaning": text, "reason": "", "registrability": ""}]
        except json.JSONDecodeError:
            return [{"name": "格式错误", "meaning": text, "reason": "", "registrability": ""}]

    def generate_brand_story(self, brand_name: str, brief: str = "") -> str:
        system = """你是一位品牌策划大师，擅长创作打动人心的品牌故事。
请为商标创作一个完整的品牌故事，包含以下部分：

## 品牌起源
## 品牌使命
## 品牌愿景
## 核心价值
## 目标人群
## 品牌调性

用有感染力的语言书写，让消费者产生共鸣。300-500字。
如果简介中信息不完整，请发挥创意补充合理的内容。"""
        user = f"商标名称：{brand_name}\n商标简介：{brief or '请根据商标名称自由发挥创意'}"
        return self._call(system, user)

    def analyze_risk(self, name: str, category: int, similar_list: list[dict]) -> str:
        system = """你是一位经验丰富的商标代理人。根据查询到的近似商标信息，分析目标商标的注册风险。

请输出以下维度的分析：

1. **近似商标分析**：列出主要的近似商标，分析相似程度
2. **类别保护范围**：该类别下哪些小类可能冲突
3. **显著性评估**：商标本身是否具有显著性
4. **综合风险评分**（1-100分，越低风险越大）
5. **注册建议**：是否可以申请，如何提高通过率"""
        similar_text = json.dumps(similar_list, ensure_ascii=False, indent=2)
        cat_name = CATEGORY_NAMES.get(category, "未知")
        user = f"目标商标：{name}\n申请类别：第{category}类（{cat_name}）\n\n已查到的近似商标：\n{similar_text}\n\n请进行风险评估分析。"
        return self._call(system, user)

    def parse_natural_query(self, query: str) -> dict:
        system = """你是一个商标查询助手。从用户自然语言中提取信息，严格返回JSON。

{"name":"商标名称","category":null,"applicant":"","industry":"","intent":"search","target_categories":[],"analysis_needed":""}

规则：
- "我是做XX的"中XX是行业，不是商标名
- 类别是尼斯分类1-45的数字，未明确提及时填null
- intent: search=查询, register=想注册, risk_assess=风险评估, monitor=监控续展
- target_categories: 根据用户行业推断相关尼斯分类编号列表。
  常见映射：
  互联网/软件/科技 → [9,35,38,42]
  餐饮/食品 → [29,30,32,33,35,43]
  服装/鞋帽 → [25,35]
  家具/家居 → [20,21,24,35]
  化妆品/日化 → [3,5,21,35]
  营销/广告/推广 → [35,38,41,42]
  设计类 → [16,35,41,42]
  法律服务 → [45]
  教育培训 → [41]
  医药/健康 → [5,10,35,44]
  酒类 → [33,35]
  如果用户说"全部类目"/"哪些类目"/"什么类别"→ target_categories为全部1-45
  如果用户只说了行业没有说具体类别 → 根据行业推断
- analysis_needed: 用简短一句总结用户真正想了解什么"""

        text = self._call(system, query, temperature="precise")
        try:
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                # 确保target_categories是列表
                if "target_categories" not in result:
                    result["target_categories"] = []
                return result
        except json.JSONDecodeError:
            pass
        return {"name": "", "category": None, "applicant": "", "industry": "", "intent": "search", "target_categories": [], "analysis_needed": ""}

    def analyze_registration_advice(self, name: str, industry: str, target_categories: list[int], existing: list[dict]) -> str:
        """根据用户行业和目标类别，给出注册建议"""
        system = """你是一位资深商标代理顾问。用户想在某行业注册商标，已有查询结果显示了该商标在各类别的注册情况。

请给出全面分析：
1. **用户需求解读**：用户所在行业及应关注的核心类别
2. **已有注册情况**：该商标在用户关心的类别中哪些已被注册/申请
3. **可用类别**：用户关心的类别中哪些尚未被注册（有机会）
4. **风险分析**：
   - 近似风险：是否有同名或近似商标
   - 抢注意味：该商标是否已被他人在核心类别注册
   - 跨类保护：驰名商标的跨类保护风险
5. **综合建议**：
   - 具体建议哪些类别可以尝试注册
   - 哪些类别不建议（风险高）
   - 是否需要调整商标名称或设计
6. **风险评分**（1-100分）：综合注册成功率"""

        existing_text = json.dumps(existing, ensure_ascii=False, indent=2)
        cats_text = ", ".join(str(c) for c in target_categories) if target_categories else "用户未指定"
        user = f"""商标名称：{name}
用户行业：{industry}
用户关心的类别：{cats_text}

已有注册/申请记录：
{existing_text}

请分析该商标在用户行业的注册前景，输出完整报告。"""
        return self._call(system, user)

    def analyze_similarity(self, target_name: str, similar_trademarks: list[dict]) -> str:
        system = """你是一位商标审查员。请对目标商标与近似商标列表进行专业的近似度分析。

对每个近似商标分析：
1. **近似类型**：文字近似/读音近似/含义近似/整体外观近似
2. **近似程度**：高/中/低
3. **冲突风险**：是否构成混淆可能性
4. **结论**：是否建议申请

最后给出综合判断和建议策略。"""
        similar_text = json.dumps(similar_trademarks, ensure_ascii=False, indent=2)
        user = f"目标商标：{target_name}\n\n近似商标列表：\n{similar_text}\n\n请逐一分析近似度。"
        return self._call(system, user)

    def score_trademark(self, name: str, category: int, similar_count: int) -> dict:
        """快速规则评分"""
        score = 100
        details = []

        if len(name) < 2:
            score -= 20
            details.append("名称过短（少于2字），显著性不足")
        elif len(name) > 6:
            score -= 5
            details.append("名称较长，记忆成本高")
        else:
            score += 5
            details.append("名称长度适中")

        if similar_count == 0:
            details.append("未发现相同类别近似商标")
            score += 10
        elif similar_count <= 2:
            score -= similar_count * 10
            details.append(f"发现{similar_count}个近似商标，中度风险")
        elif similar_count <= 5:
            score -= similar_count * 12
            details.append(f"发现{similar_count}个近似商标，较高风险")
        else:
            score -= similar_count * 15
            details.append(f"发现{similar_count}个近似商标，高风险")

        common_words = ["优质", "第一", "最好", "超级", "中国", "中华", "全国"]
        for w in common_words:
            if w in name:
                score -= 15
                details.append(f"包含禁注词汇'{w}'（夸大宣传/地名）")
                break

        score = max(0, min(100, score))

        if score >= 80:
            level, color, suggestion = "高", "🟢", "注册成功率较高，建议尽快申请"
        elif score >= 60:
            level, color, suggestion = "中", "🟡", "存在一定风险，建议调整名称或增加显著性"
        elif score >= 40:
            level, color, suggestion = "较低", "🟠", "风险较高，建议更换名称或增加独特性"
        else:
            level, color, suggestion = "低", "🔴", "不建议申请，存在较高驳回风险"

        return {
            "score": score,
            "level": level,
            "color": color,
            "details": details,
            "suggestion": suggestion,
        }
