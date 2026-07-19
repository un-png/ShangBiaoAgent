"""商标AI智能助手 - 阿里云商标查询API封装"""
import json
import os
import urllib3
from dotenv import load_dotenv

load_dotenv()

TRADEMARK_HOST = "https://trademark.market.alicloudapi.com"
TRADEMARK_APPCODE = os.getenv("TRADEMARK_APPCODE")


class TrademarkAPI:
    """阿里云商标搜索API——对接国家商标网数据"""

    def __init__(self):
        self.http = urllib3.PoolManager()
        self.enabled = bool(TRADEMARK_APPCODE)

    def search(self, keyword: str, page: int = 1, size: int = 10, ismatch: int = 0) -> dict:
        """
        搜索商标
        :param keyword: 搜索关键词
        :param page: 页码
        :param size: 每页数量
        :param ismatch: 0=模糊匹配, 1=精确匹配
        :return: API返回的JSON数据
        """
        if not self.enabled:
            return {"success": False, "error": "未配置TRADEMARK_APPCODE，请先在.env中设置", "data": []}

        # URL编码关键词
        import urllib.parse
        encoded_keyword = urllib.parse.quote(keyword)

        url = f"{TRADEMARK_HOST}/trademark/search?keyword={encoded_keyword}&pagenum={page}&pagesize={size}&ismatch={ismatch}"

        try:
            resp = self.http.request(
                "GET",
                url,
                headers={"Authorization": f"APPCODE {TRADEMARK_APPCODE}"},
                timeout=10.0,
            )
            data = json.loads(resp.data.decode("utf-8"))
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e), "data": []}

    def search_formatted(self, keyword: str, page: int = 1, size: int = 10, ismatch: int = 0) -> list[dict]:
        """搜索并返回格式化结果"""
        result = self.search(keyword, page, size, ismatch)
        if not result["success"]:
            return []

        data = result["data"]
        # 阿里云API返回格式可能为 {"status":200, "result": {"list": [...]}} 等
        # 做兼容解析
        items = []
        raw = data

        if isinstance(data, dict):
            if "result" in data and isinstance(data["result"], dict):
                raw = data["result"]
            if "list" in raw:
                items = raw["list"]
            elif "data" in raw and isinstance(raw["data"], list):
                items = raw["data"]
            elif "records" in raw:
                items = raw["records"]

        formatted = []
        for item in items:
            formatted.append({
                "name": item.get("name") or item.get("tmName") or "",
                "category": item.get("classid") or item.get("category") or item.get("intCls") or "",
                "applicant": item.get("registrant") or item.get("applicant") or item.get("applicantCn") or "",
                "status": item.get("status") or "",
                "reg_no": item.get("regno") or item.get("regNo") or "",
                "app_date": item.get("appdate") or item.get("appDate") or "",
                "agent": item.get("agent") or "",
                "raw": item,
            })

        return formatted
