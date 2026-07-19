"""
商标AI智能助手 - 邮件提醒定时任务
每10分钟扫描 my_trademarks 表，对30天内到期且配置了邮箱的商标发送续展提醒。
每个商标每24小时最多收到1封邮件（防止重复骚扰）。
"""
import sys
import time
from datetime import datetime
from services.database import TrademarkDB
from services.mail_service import MailService

_flush = lambda s: print(s, flush=True)


def run_once(db: TrademarkDB, mail: MailService):
    """扫描并发送一轮提醒"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _flush(f"\n{'='*50}")
    _flush(f"[Worker] {now} 开始扫描...")

    if not mail.enabled:
        _flush("[Worker] SMTP未配置，请在.env中设置SMTP_HOST/USER/PASSWORD，跳过扫描")
        return

    # 30天到期的商标，24小时内未提醒过的
    pending = db.get_pending_reminders(days=30, cooldown_hours=24)

    if not pending:
        _flush("[Worker] 没有需要提醒的商标")
        return

    _flush(f"[Worker] 发现 {len(pending)} 个待提醒商标")

    for tm in pending:
        exp_date = datetime.strptime(tm["expiry_date"], "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days

        _flush(f"  -> 发送: {tm['name']}(第{tm['category']}类) -> {tm['email']} (剩余{days_left}天)")

        success = mail.send_reminder(
            to_email=tm["email"],
            name=tm["name"],
            category=tm["category"],
            expiry_date=tm["expiry_date"],
            days_left=days_left,
        )

        if success:
            db.mark_reminded(tm["id"])
            _flush(f"     ✅ 已发送，下次提醒需24小时后")
        else:
            _flush(f"     ❌ 发送失败，检查SMTP配置或邮箱地址")

    _flush(f"[Worker] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 本轮完成")


def main():
    _flush("=" * 50)
    _flush("商标AI智能助手 - 邮件提醒Worker")
    _flush("扫描间隔: 10分钟 | 到期范围: 30天内 | 发送频率: 每商标24小时1次")
    _flush("=" * 50)

    db = TrademarkDB()
    mail = MailService()

    _flush(f"[Worker] SMTP状态: {'已配置' if mail.enabled else '未配置'}")
    _flush(f"[Worker] 已绑定商标数量: {len(db.get_my_trademarks())}")

    if not mail.enabled:
        _flush("\n⚠️  请配置 .env 中的 SMTP_* 参数来启用邮件发送")

    # 启动后立即执行一次
    run_once(db, mail)

    while True:
        try:
            time.sleep(600)  # 10分钟
            run_once(db, mail)
        except Exception as e:
            _flush(f"[Worker] ERROR: {e}")


if __name__ == "__main__":
    main()
