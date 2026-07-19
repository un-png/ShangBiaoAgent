"""商标AI智能助手 - LangChain工具封装"""
import json
from langchain_core.tools import tool
from .trademark_api import TrademarkAPI

_api = TrademarkAPI()


@tool
def search_trademark(keyword: str, page: int = 1, size: int = 10) -> str:
    """
    搜索国家商标网数据库，查询商标注册情况。
    可用于：查询某商标名是否已被注册、查看某申请人的商标、查询某类别的商标。
    :param keyword: 商标名称关键词
    :param page: 页码，默认第1页
    :param size: 每页返回数量，默认10条
    :return: JSON格式的商标查询结果
    """
    result = _api.search(keyword, page, size)
    if not result["success"]:
        return json.dumps({"error": result.get("error", "查询失败")}, ensure_ascii=False)

    formatted = _api.search_formatted(keyword, page, size)
    summary = []
    for item in formatted:
        summary.append({
            "商标名称": item["name"],
            "类别": item["category"],
            "申请人": item["applicant"],
            "状态": item["status"],
            "注册号": item["reg_no"],
        })

    return json.dumps({
        "total": len(summary),
        "results": summary,
    }, ensure_ascii=False)


TRADEMARK_TOOLS = [search_trademark]
