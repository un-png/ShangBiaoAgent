"""商标AI智能助手 - 配置 & 常量"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 优先从项目根目录、其次 data/ 目录加载 .env
_env_paths = [
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent / "data" / ".env",
]
for p in _env_paths:
    if p.exists():
        load_dotenv(p)
        break
else:
    load_dotenv()  # 兜底：从当前目录找

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

DB_PATH = Path(__file__).parent.parent / "trademarks.db"

CATEGORY_NAMES = {
    1: "化学原料", 2: "颜料油漆", 3: "日化用品", 4: "燃料油脂", 5: "医药",
    6: "金属材料", 7: "机械设备", 8: "手工器械", 9: "科学仪器", 10: "医疗器械",
    11: "灯具空调", 12: "运输工具", 13: "军火烟火", 14: "珠宝钟表", 15: "乐器",
    16: "办公用品", 17: "橡胶制品", 18: "皮革皮具", 19: "建筑材料", 20: "家具",
    21: "厨房洁具", 22: "绳网袋篷", 23: "纱线丝", 24: "布料床单", 25: "服装鞋帽",
    26: "花边拉链", 27: "地毯席垫", 28: "玩具健身", 29: "食品", 30: "调味茶糖",
    31: "农林生鲜", 32: "啤酒饮料", 33: "酒", 34: "烟草烟具", 35: "广告销售",
    36: "金融物管", 37: "建筑修理", 38: "通讯服务", 39: "运输贮藏", 40: "材料加工",
    41: "教育娱乐", 42: "科技服务", 43: "餐饮住宿", 44: "医疗园艺", 45: "社会服务",
}
