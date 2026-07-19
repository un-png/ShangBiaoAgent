"""商标AI智能助手 - Qwen文生图Logo服务"""
import urllib.request
from tempfile import NamedTemporaryFile
import dashscope
from dashscope import ImageSynthesis
from .config import DASHSCOPE_API_KEY


class LogoService:
    """Qwen 文生图 Logo 生成"""

    def generate(self, brand_name: str, style_desc: str, color: str = "", brief: str = "") -> str | None:
        """
        使用Qwen文生图模型生成Logo，返回临时文件路径。
        优先尝试 qwen-image-max，失败降级到 wanx-v1。
        """
        parts = [f"minimalist logo design for brand '{brand_name}'"]
        if brief:
            parts.append(f"brand concept: {brief}")
        if style_desc:
            parts.append(style_desc)
        if color:
            parts.append(f"{color} color scheme")
        parts.append("simple clean vector style, white background, high quality, professional, no text clutter")
        prompt = ", ".join(parts)
        dashscope.api_key = DASHSCOPE_API_KEY

        for model in ["qwen-image-max", "wanx-v1"]:
            try:
                resp = ImageSynthesis.call(
                    model=model,
                    prompt=prompt,
                    n=1,
                    size="1024*1024",
                )
                if resp.status_code == 200 and resp.output.results:
                    url = resp.output.results[0].url
                    tmp = NamedTemporaryFile(delete=False, suffix=".png")
                    urllib.request.urlretrieve(url, tmp.name)
                    return tmp.name
            except Exception as e:
                print(f"[{model}] Logo生成异常: {e}")
                continue

        return None
