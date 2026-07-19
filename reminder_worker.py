"""
商标AI智能助手 - 邮件提醒定时任务
每10分钟扫描一次 my_trademarks 表，对30天内到期且配置了邮箱的商标发送续展提醒。
"""
import time
from datetime import datetime
from services.database import TrademarkDB
from services.mail_service import MailService


def run_once(db: TrademarkDB, mail: MailService):
    """扫描并发送一轮提醒"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*50}")
    print(f"[{now}] 开始扫描到期商标...")

    if not mail.enabled:
        print("[Mail] SMTP未配置，请在.env中设置SMTP_HOST/USER/PASSWORD")
        return

    # 查询待提醒商标：30天内到期、有邮箱、24小时内未提醒过
    pending = db.get_pending_reminders(days=30, cooldown_hours=24)

    if not pending:
        print("没有需要提醒的商标。")
        return

    print(f"找到 {len(pending)} 个待提醒商标。")

    for tm in pending:
        # 计算剩余天数
        exp_date = datetime.strptime(tm["expiry_date"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days

        success = mail.send_reminder(
            to_email=tm["email"],
            name=tm["name"],
            category=tm["category"],
            expiry_date=tm["expiry_date"],
            days_left=days_left,
        )

        if success:
            db.mark_reminded(tm["id"])

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 本轮扫描完成。")


def main():
    print("=" * 50)
    print("商标AI智能助手 - 邮件提醒定时任务")
    print("每10分钟扫描一次，检测30天内到期的商标")
    print("按 Ctrl+C 停止")
    print("=" * 50)

    db = TrademarkDB()
    mail = MailService()

    if not mail.enabled:
        print("\n⚠️  SMTP未配置，请先配置.env文件：")
        print("   SMTP_HOST=smtp.qq.com")
        print("   SMTP_PORT=587")
        print("   SMTP_USER=your_email@qq.com")
        print("   SMTP_PASSWORD=your_smtp_auth_code")
        print("   SMTP_FROM=your_email@qq.com")
        print("\n任务将继续运行但不会发送邮件。")

    while True:
        try:
            run_once(db, mail)
        except Exception as e:
            print(f"[ERROR] {e}")

        # 每10分钟（600秒）
        time.sleep(600)


if __name__ == "__main__":
    main()
