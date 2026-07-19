"""商标AI智能助手 - 邮件发送服务"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class MailService:
    """SMTP邮件发送"""

    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "smtp.qq.com")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.from_addr = os.getenv("SMTP_FROM", self.user)
        self.enabled = bool(self.user and self.password)

    def send_reminder(self, to_email: str, name: str, category: int, expiry_date: str, days_left: int) -> bool:
        """发送商标到期提醒邮件"""
        if not self.enabled:
            print(f"[Mail] SMTP未配置，跳过发送: {name} -> {to_email}")
            return False

        subject = f"【商标续展提醒】您的商标「{name}」将于{days_left}天后到期"

        html_body = f"""
        <div style="max-width:600px;margin:0 auto;font-family:'Microsoft YaHei',Arial,sans-serif;">
            <div style="background:#e03030;color:#fff;padding:20px;border-radius:8px 8px 0 0;">
                <h2 style="margin:0;">商标续展提醒</h2>
            </div>
            <div style="border:1px solid #e0e0e0;border-top:none;padding:24px;border-radius:0 0 8px 8px;">
                <p>尊敬的客户：</p>
                <p>您的商标注册信息如下，即将到期，请及时办理续展手续：</p>
                <table style="width:100%;border-collapse:collapse;margin:16px 0;">
                    <tr><td style="padding:8px;border:1px solid #eee;background:#f8f8f8;"><b>商标名称</b></td><td style="padding:8px;border:1px solid #eee;">{name}</td></tr>
                    <tr><td style="padding:8px;border:1px solid #eee;background:#f8f8f8;"><b>类别</b></td><td style="padding:8px;border:1px solid #eee;">第{category}类</td></tr>
                    <tr><td style="padding:8px;border:1px solid #eee;background:#f8f8f8;"><b>到期日期</b></td><td style="padding:8px;border:1px solid #eee;color:#e03030;font-weight:700;">{expiry_date}</td></tr>
                    <tr><td style="padding:8px;border:1px solid #eee;background:#f8f8f8;"><b>剩余天数</b></td><td style="padding:8px;border:1px solid #eee;color:#e03030;font-weight:700;">{days_left} 天</td></tr>
                </table>
                <p>商标有效期为10年，到期后需在12个月内办理续展，否则商标将被注销。</p>
                <p>如有疑问，请联系您的商标顾问。</p>
                <br>
                <p style="color:#999;font-size:12px;">此邮件由商标AI智能助手自动发送，请勿回复。</p>
            </div>
        </div>
        """

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_addr
            msg["To"] = to_email
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            server = smtplib.SMTP(self.host, self.port, timeout=15)
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.from_addr, to_email, msg.as_string())
            server.quit()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[Mail] {now} 已发送: {name} -> {to_email} (剩余{days_left}天)")
            return True
        except Exception as e:
            print(f"[Mail] 发送失败: {name} -> {to_email}, 错误: {e}")
            return False
