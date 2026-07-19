"""商标AI智能助手 - SQLite数据库 & 到期提醒"""
import sqlite3
from datetime import datetime, timedelta
from .config import DB_PATH


class TrademarkDB:
    """SQLite 商标数据库 + 到期提醒"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self._seed_if_empty()

    # ---- 建表 ----
    def _init_db(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS trademarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category INTEGER NOT NULL,
                applicant TEXT DEFAULT '',
                status TEXT DEFAULT 'registered',
                registration_date TEXT DEFAULT '',
                expiry_date TEXT DEFAULT '',
                description TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS my_trademarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category INTEGER NOT NULL,
                registration_no TEXT DEFAULT '',
                applicant TEXT DEFAULT '',
                registration_date TEXT DEFAULT '',
                expiry_date TEXT NOT NULL,
                notes TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                remind_before_days INTEGER DEFAULT 30,
                last_reminded_at TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now','localtime'))
            );
        """)
        # 兼容旧表：如果缺少字段则补充
        try:
            self.conn.execute("ALTER TABLE my_trademarks ADD COLUMN last_reminded_at TEXT DEFAULT ''")
        except Exception:
            pass
        self.conn.commit()

    # ---- 种子数据 ----
    def _seed_if_empty(self):
        cnt = self.conn.execute("SELECT COUNT(*) FROM trademarks").fetchone()[0]
        if cnt > 0:
            return

        seed_data = [
            ("华为", 9, "华为技术有限公司", "registered", "2020-03-15", "2030-03-14", "智能手机、平板电脑、可穿戴设备"),
            ("小米", 9, "小米科技有限责任公司", "registered", "2019-08-20", "2029-08-19", "手机、智能家居设备"),
            ("红米", 9, "小米科技有限责任公司", "registered", "2021-01-10", "2031-01-09", "智能手机"),
            ("OPPO", 9, "OPPO广东移动通信有限公司", "registered", "2020-06-01", "2030-05-31", "手机、充电器、耳机"),
            ("VIVO", 9, "维沃移动通信有限公司", "registered", "2020-07-15", "2030-07-14", "智能手机、手机配件"),
            ("传音", 9, "深圳传音控股股份有限公司", "registered", "2021-03-20", "2031-03-19", "手机"),
            ("华伟", 9, "深圳华伟电子有限公司", "rejected", "2023-01-01", "", "手机壳、数据线"),
            ("康师傅", 30, "顶益(开曼岛)控股有限公司", "registered", "2019-05-10", "2029-05-09", "方便面、调味品"),
            ("康帅博", 30, "某食品有限公司", "rejected", "2023-02-01", "", "方便面（因近似'康师傅'被驳回）"),
            ("统一", 30, "统一企业股份有限公司", "registered", "2020-11-15", "2030-11-14", "方便面、饮料"),
            ("三只松鼠", 29, "三只松鼠股份有限公司", "registered", "2019-12-01", "2029-11-30", "坚果、零食"),
            ("良品铺子", 29, "良品铺子股份有限公司", "registered", "2020-02-20", "2030-02-19", "休闲食品"),
            ("百草味", 29, "杭州郝姆斯食品有限公司", "registered", "2021-05-10", "2031-05-09", "坚果、果干"),
            ("李子柒", 30, "四川子柒文化传播有限公司", "registered", "2020-08-15", "2030-08-14", "食品、调味料"),
            ("海底捞", 43, "四川海底捞餐饮股份有限公司", "registered", "2019-07-20", "2029-07-19", "餐厅、餐饮服务"),
            ("西贝", 43, "北京西贝餐饮管理有限公司", "registered", "2020-03-10", "2030-03-09", "餐厅、外卖服务"),
            ("外婆家", 43, "浙江外婆家餐饮有限公司", "registered", "2021-01-20", "2031-01-19", "餐饮服务"),
            ("绿茶", 43, "杭州绿茶餐饮管理有限公司", "registered", "2020-09-01", "2030-08-31", "餐厅"),
            ("奈雪的茶", 43, "深圳市品道餐饮管理有限公司", "registered", "2020-04-10", "2030-04-09", "茶饮、餐饮"),
            ("喜茶", 43, "深圳美西西餐饮管理有限公司", "registered", "2020-05-15", "2030-05-14", "茶饮、甜品"),
            ("张三", 45, "张三法律咨询有限公司", "registered", "2021-06-01", "2031-05-31", "法律服务"),
            ("张三", 41, "张三教育科技有限公司", "registered", "2020-12-10", "2030-12-09", "教育培训"),
            ("张三疯", 43, "厦门张三疯餐饮管理有限公司", "registered", "2020-07-20", "2030-07-19", "奶茶店"),
            ("李宁", 25, "李宁(中国)体育用品有限公司", "registered", "2019-06-15", "2029-06-14", "运动服装、运动鞋"),
            ("安踏", 25, "安踏(中国)有限公司", "registered", "2019-08-01", "2029-07-31", "运动鞋服"),
            ("特步", 25, "特步(中国)有限公司", "registered", "2020-02-15", "2030-02-14", "运动鞋、运动服"),
            ("海澜之家", 25, "海澜之家品牌管理有限公司", "registered", "2020-10-20", "2030-10-19", "男装"),
            ("安塔", 25, "某体育用品有限公司", "pending", "2024-01-10", "", "运动鞋（安踏提异议中）"),
            ("茅台", 33, "中国贵州茅台酒厂(集团)有限责任公司", "registered", "2019-05-01", "2029-04-30", "白酒"),
            ("五粮液", 33, "宜宾五粮液股份有限公司", "registered", "2019-07-10", "2029-07-09", "白酒"),
            ("江小白", 33, "重庆江小白酒业有限公司", "registered", "2021-03-15", "2031-03-14", "白酒、果酒"),
            ("同仁堂", 5, "中国北京同仁堂(集团)有限责任公司", "registered", "2019-11-01", "2029-10-31", "中药、中成药"),
            ("云南白药", 5, "云南白药集团股份有限公司", "registered", "2020-01-15", "2030-01-14", "中药制剂、创可贴"),
            ("百雀羚", 3, "上海百雀羚日用化学有限公司", "registered", "2020-06-20", "2030-06-19", "化妆品、护肤品"),
            ("自然堂", 3, "伽蓝(集团)股份有限公司", "registered", "2020-04-15", "2030-04-14", "护肤品、化妆品"),
            ("珀莱雅", 3, "珀莱雅化妆品股份有限公司", "registered", "2021-02-10", "2031-02-09", "化妆品"),
            ("比亚迪", 12, "比亚迪股份有限公司", "registered", "2020-09-20", "2030-09-19", "汽车、电动车"),
            ("蔚来", 12, "上海蔚来汽车有限公司", "registered", "2021-04-15", "2031-04-14", "电动汽车"),
            ("全友", 20, "全友家私有限公司", "registered", "2020-03-20", "2030-03-19", "家具"),
            ("顾家家居", 20, "顾家家居股份有限公司", "registered", "2019-08-10", "2029-08-09", "家具、沙发"),
            ("曲美", 20, "曲美家居集团股份有限公司", "registered", "2020-11-20", "2030-11-19", "家具"),
            ("友全", 20, "成都友全家具有限公司", "rejected", "2023-05-10", "", "家具（因近似'全友'被驳回）"),
            ("阿里巴巴", 35, "阿里巴巴集团控股有限公司", "registered", "2019-09-10", "2029-09-09", "广告、商业管理"),
            ("京东", 35, "北京京东世纪贸易有限公司", "registered", "2020-06-01", "2030-05-31", "广告、市场营销"),
            ("拼多多", 35, "上海寻梦信息技术有限公司", "registered", "2021-01-15", "2031-01-14", "广告、在线推广"),
            ("格力", 11, "珠海格力电器股份有限公司", "registered", "2019-10-20", "2029-10-19", "空调、家电"),
            ("美的", 11, "美的集团股份有限公司", "registered", "2020-05-10", "2030-05-09", "空调、厨房电器"),
            ("海尔", 11, "海尔集团公司", "registered", "2019-12-01", "2029-11-30", "冰箱、洗衣机、家电"),
            ("抖音", 42, "北京抖音信息服务有限公司", "registered", "2020-08-20", "2030-08-19", "软件、平台即服务"),
            ("微信", 42, "腾讯科技(深圳)有限公司", "registered", "2020-01-10", "2030-01-09", "即时通讯软件"),
            ("大疆", 9, "深圳市大疆创新科技有限公司", "registered", "2021-05-20", "2031-05-19", "无人机、航拍设备"),
        ]

        self.conn.executemany(
            "INSERT INTO trademarks (name, category, applicant, status, registration_date, expiry_date, description) VALUES (?,?,?,?,?,?,?)",
            seed_data,
        )
        self.conn.commit()

    # ---- 查询 ----
    def search(self, name: str = "", category: int = None, applicant: str = "") -> list[dict]:
        sql = "SELECT * FROM trademarks WHERE 1=1"
        params = []
        if name:
            sql += " AND name LIKE ?"
            params.append(f"%{name}%")
        if category:
            sql += " AND category = ?"
            params.append(category)
        if applicant:
            sql += " AND applicant LIKE ?"
            params.append(f"%{applicant}%")
        sql += " ORDER BY category, name"
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def search_similar(self, name: str, category: int = None) -> list[dict]:
        results = []
        if category:
            rows = self.conn.execute(
                "SELECT * FROM trademarks WHERE category=? AND name LIKE ? AND name != ?",
                (category, f"%{name}%", name),
            ).fetchall()
            results.extend(dict(r) for r in rows)

        if not results and category:
            for ch in name:
                rows = self.conn.execute(
                    "SELECT * FROM trademarks WHERE category=? AND name LIKE ? AND name != ?",
                    (category, f"%{ch}%", name),
                ).fetchall()
                for r in rows:
                    d = dict(r)
                    if d not in results:
                        results.append(d)

        rows = self.conn.execute("SELECT * FROM trademarks WHERE name = ?", (name,)).fetchall()
        for r in rows:
            d = dict(r)
            if d not in results:
                results.append(d)

        return results

    def check_name_exists(self, name: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM trademarks WHERE name LIKE ?", (f"%{name}%",)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        total = self.conn.execute("SELECT COUNT(*) FROM trademarks").fetchone()[0]
        by_status = {}
        for row in self.conn.execute("SELECT status, COUNT(*) as cnt FROM trademarks GROUP BY status").fetchall():
            by_status[row["status"]] = row["cnt"]
        by_category = {}
        for row in self.conn.execute(
            "SELECT category, COUNT(*) as cnt FROM trademarks GROUP BY category ORDER BY cnt DESC LIMIT 10"
        ).fetchall():
            by_category[row["category"]] = row["cnt"]
        return {"total": total, "by_status": by_status, "by_category": by_category}

    # ---- 我的商标（到期提醒） ----
    def bind_trademark(self, data: dict):
        self.conn.execute(
            """INSERT INTO my_trademarks (name, category, registration_no, applicant,
               registration_date, expiry_date, notes, phone, email, remind_before_days)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                data["name"], data["category"], data.get("registration_no", ""),
                data.get("applicant", ""), data.get("registration_date", ""),
                data["expiry_date"], data.get("notes", ""),
                data.get("phone", ""), data.get("email", ""),
                data.get("remind_before_days", 30),
            ),
        )
        self.conn.commit()

    def get_my_trademarks(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM my_trademarks ORDER BY expiry_date ASC").fetchall()
        return [dict(r) for r in rows]

    def get_expiring_soon(self, days: int = 30) -> list[dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        deadline = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        rows = self.conn.execute(
            "SELECT * FROM my_trademarks WHERE expiry_date BETWEEN ? AND ? ORDER BY expiry_date ASC",
            (today, deadline),
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_my_trademark(self, tm_id: int):
        self.conn.execute("DELETE FROM my_trademarks WHERE id=?", (tm_id,))
        self.conn.commit()

    # ---- 邮件提醒（定时任务用） ----
    def get_pending_reminders(self, days: int = 30, cooldown_hours: int = 24) -> list[dict]:
        """
        查询需要发送提醒的商标：
        - 到期日在 days 天以内
        - 配置了邮箱
        - 距离上次提醒超过 cooldown_hours 小时（避免重复发送）
        """
        today = datetime.now().strftime("%Y-%m-%d")
        deadline = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        cooldown_time = (datetime.now() - timedelta(hours=cooldown_hours)).strftime("%Y-%m-%d %H:%M:%S")

        rows = self.conn.execute(
            """SELECT * FROM my_trademarks
               WHERE expiry_date BETWEEN ? AND ?
                 AND email != ''
                 AND (last_reminded_at == '' OR last_reminded_at < ?)
               ORDER BY expiry_date ASC""",
            (today, deadline, cooldown_time),
        ).fetchall()
        return [dict(r) for r in rows]

    def mark_reminded(self, tm_id: int):
        """标记已发送提醒"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "UPDATE my_trademarks SET last_reminded_at=? WHERE id=?",
            (now, tm_id),
        )
        self.conn.commit()
