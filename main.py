"""
商标AI智能助手 - Demo
覆盖全部功能：一站式起名/商标查询/风险评估/自然语言问答/到期提醒
"""
import streamlit as st
from services import LLMService, LogoService, TrademarkDB, TrademarkAPI, CATEGORY_NAMES
from datetime import datetime, timedelta

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="商标AI智能助手",
    page_icon="🏷",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #666; margin-bottom: 1.5rem; }
    .name-card {
        border: 1px solid #e0e0e0; border-radius: 12px; padding: 1.2rem;
        margin-bottom: 0.8rem; background: #fafafa; transition: all 0.2s;
    }
    .name-card:hover { border-color: #ff4b4b; box-shadow: 0 2px 8px rgba(255,75,75,0.1); }
    .name-card.selected { border-color: #e03030; background: #fff5f5; }
    .name-title { font-size: 1.3rem; font-weight: 700; color: #e03030; }
    .score-big { font-size: 3rem; font-weight: 800; text-align: center; }
    .stat-box { text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; }
    .stat-num { font-size: 2rem; font-weight: 700; color: #e03030; }
    .stat-label { font-size: 0.85rem; color: #888; }
    .expiry-warn { background: #fff3cd; border-left: 4px solid #ffc107; padding: 0.8rem; border-radius: 4px; margin: 0.3rem 0; }
    .expiry-danger { background: #ffe0e0; border-left: 4px solid #dc3545; padding: 0.8rem; border-radius: 4px; margin: 0.3rem 0; }
    .footer { text-align: center; color: #aaa; margin-top: 3rem; font-size: 0.8rem; }
    .api-badge { display:inline-block; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700; }
    .api-badge.real { background:#d4edda; color:#155724; }
    .api-badge.mock { background:#e2e3e5; color:#383d41; }
    @keyframes dot-pulse { 0%, 20% { opacity:0; } 50% { opacity:1; } 100% { opacity:0; } }
    .loading-dots span { animation: dot-pulse 1.4s infinite; display:inline-block; font-size:1.5rem; }
    .loading-dots span:nth-child(2) { animation-delay:0.2s; }
    .loading-dots span:nth-child(3) { animation-delay:0.4s; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 初始化
# ============================================================
@st.cache_resource
def init_services():
    return LLMService(), LogoService(), TrademarkDB(), TrademarkAPI()

llm, logo_service, db, tm_api = init_services()

# 导航状态
if "page" not in st.session_state:
    st.session_state.page = "首页"
if "generated_names" not in st.session_state:
    st.session_state.generated_names = []
if "selected_name" not in st.session_state:
    st.session_state.selected_name = ""
if "selected_index" not in st.session_state:
    st.session_state.selected_index = -1

# ============================================================
# 侧边栏导航
# ============================================================
with st.sidebar:
    st.markdown("### 🏷 商标AI助手")

    # API状态
    if tm_api.enabled:
        st.markdown('<span class="api-badge real">● 已接通国家商标网API</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="api-badge mock">○ 模拟数据模式</span>', unsafe_allow_html=True)

    st.markdown("---")
    pages = {
        "🏠 首页": "首页",
        "🚀 一站式起名": "一站式",
        "🔍 商标查询": "查询",
        "📊 风险评估": "风险",
        "💬 智能问答": "问答",
        "📋 我的商标": "我的商标",
    }
    for label, key in pages.items():
        if st.sidebar.button(label, use_container_width=True,
                             type="primary" if st.session_state.page == key else "secondary"):
            st.session_state.page = key
            st.rerun()

    st.markdown("---")
    st.caption("Demo v1.1 | 支持国家商标网API")

# ============================================================
# 首页
# ============================================================
if st.session_state.page == "首页":
    st.markdown('<p class="main-header">🏷 商标AI智能助手</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI驱动的一站式商标服务：起名 → 设计 → 查询 → 风险评估 → 到期监控</p>',
                unsafe_allow_html=True)

    stats = db.get_stats()
    api_status = "✅ 已接通" if tm_api.enabled else "○ 未配置"
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["total"]}</div><div class="stat-label">本地模拟数据</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["by_status"].get("registered", 0)}</div><div class="stat-label">已注册案例</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["by_status"].get("rejected", 0)}</div><div class="stat-label">驳回案例</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(db.get_my_trademarks())}</div><div class="stat-label">我绑定的商标</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{api_status}</div><div class="stat-label">官方API</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("⚡ 快速入口")
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        if st.button("🚀 一站式起名（起名→Logo→故事）", use_container_width=True):
            st.session_state.page = "一站式"; st.rerun()
    with qc2:
        if st.button("📊 评估注册风险", use_container_width=True):
            st.session_state.page = "风险"; st.rerun()
    with qc3:
        if st.button("💬 自然语言查询", use_container_width=True):
            st.session_state.page = "问答"; st.rerun()
    with qc4:
        if st.button("📋 绑定商标/到期提醒", use_container_width=True):
            st.session_state.page = "我的商标"; st.rerun()

    st.markdown("---")
    st.subheader("📌 功能一览")
    features = [
        ("🚀 一站式起名", "大白话描述需求 → AI生成商标名 → Logo设计 → 品牌故事，一气呵成"),
        ("🔍 商标查询", "对接国家商标网API + 本地数据库，查询商标注册情况"),
        ("📊 风险评估", "AI自检商标通过率，近似商标分析 + 风险评分"),
        ("💬 智能问答", "说人话就能查：45类张三有无、我是做家具的帮我评估风险"),
        ("📋 到期提醒", "绑定商标后到期高亮提醒（支持短信/邮件/站内待办配置）"),
    ]
    for icon_title, desc in features:
        st.markdown(f"**{icon_title}**：{desc}")

    st.markdown("---")
    if not tm_api.enabled:
        st.info("💡 **提示**：在 `.env` 文件中设置 `TRADEMARK_APPCODE` 即可接通国家商标网实时数据查询。")

# ============================================================
# 一站式起名（合并需求1-3：起名 → Logo → 品牌故事）
# ============================================================
elif st.session_state.page == "一站式":
    st.markdown('<p class="main-header">🚀 一站式商标起名</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">用大白话描述你的业务，AI一次性完成：起名 → Logo设计 → 品牌故事</p>', unsafe_allow_html=True)

    # --- Step 1: 生成名称 ---
    st.subheader("Step 1️⃣ 描述你的需求")
    c1, c2, c3 = st.columns(3)
    with c1:
        industry = st.text_input("行业/业务", placeholder="例如：家具、餐饮、服装...")
    with c2:
        style = st.selectbox("品牌风格", ["", "简约现代", "国潮复古", "年轻潮流", "高端奢华", "亲民温馨", "科技感", "自然环保"])
    with c3:
        count = st.slider("生成数量", 3, 10, 5)
    keywords = st.text_input("关键词（可选）", placeholder="例如：健康、快乐、品质...")

    if st.button("🚀 生成商标名称", type="primary", use_container_width=True, disabled=not industry):
        with st.status("✨ AI正在为你创作商标名称...", expanded=True) as status:
            st.markdown('<div class="loading-dots">创意构思中<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
            st.session_state.generated_names = llm.generate_names(industry, style, keywords, count)
            st.session_state.selected_index = -1
            st.session_state.selected_name = ""
            st.session_state.pop("brand_story", None)
            st.session_state.pop("logo_path", None)
            status.update(label=f"✅ 已生成 {len(st.session_state.generated_names)} 个商标名称", state="complete")

    # --- Step 2: 选择名称 ---
    names = st.session_state.generated_names
    if names:
        st.markdown("---")
        st.subheader("Step 2️⃣ 选择你喜欢的商标名")
        cols = st.columns(min(len(names), 3))
        for i, item in enumerate(names):
            nm = item.get("name", "N/A")
            with cols[i % 3]:
                selected = st.session_state.selected_index == i
                card_class = "name-card selected" if selected else "name-card"
                st.markdown(f"""
                <div class="{card_class}">
                    <span class="name-title">{i+1}. {nm}</span>
                    <p><b>含义：</b>{item.get('meaning', '')}</p>
                    <p><b>适合原因：</b>{item.get('reason', '')}</p>
                    <p>📋 {item.get('registrability', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"✅ 选这个", key=f"pick_{i}", use_container_width=True):
                    st.session_state.selected_index = i
                    st.session_state.selected_name = nm
                    st.rerun()

    # --- Step 3: 自动生成Logo + 品牌故事 ---
    if st.session_state.selected_name:
        sel_name = st.session_state.selected_name
        st.markdown("---")
        st.subheader(f"Step 3️⃣「{sel_name}」Logo + 品牌故事")
        tab1, tab2 = st.tabs(["🎨 Logo设计", "📖 品牌故事"])

        # 共享的商标简介
        brief = st.text_area(
            "📝 商标简介",
            placeholder="描述你的商标理念、目标客户、产品特点等，Logo和品牌故事将基于此创作。\n例如：一个面向年轻人的新式茶饮品牌，主打健康水果茶，风格清新自然...",
            key="trademark_brief",
            height=100,
        )

        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                logo_style = st.text_input("Logo风格描述", placeholder="极简风格、线条感、圆形构图...", key="logo_style_input")
            with c2:
                logo_color = st.selectbox(
                    "色彩方案（可选）",
                    ["不指定", "red/gold", "blue/white", "green/nature", "black/gold", "purple/silver", "orange/warm"],
                    key="logo_color_input",
                )

            if st.button("🎨 生成Logo", type="primary", key="gen_logo_btn"):
                with st.status("🎨 AI正在设计Logo...", expanded=True) as logo_status:
                    st.markdown('<div class="loading-dots">渲染中<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
                    color_param = "" if logo_color == "不指定" else logo_color
                    path = logo_service.generate(sel_name, logo_style, color_param, brief)
                    if path:
                        st.session_state.logo_path = path
                        logo_status.update(label="✅ Logo生成完成", state="complete")
                    else:
                        logo_status.update(label="⚠️ Logo生成失败，请重试", state="error")

            if st.session_state.get("logo_path"):
                st.image(st.session_state.logo_path, caption=f"「{sel_name}」商标Logo", width=400)
                with open(st.session_state.logo_path, "rb") as f:
                    st.download_button("📥 下载Logo", f.read(), f"logo_{sel_name}.png", mime="image/png")

        with tab2:
            st.caption("品牌故事将基于上方「商标简介」+ 商标名称自动创作")

            if st.button("✍️ 生成品牌故事", type="primary", key="gen_story_btn"):
                with st.status("✍️ AI正在创作品牌故事...", expanded=True) as story_status:
                    st.markdown('<div class="loading-dots">撰写中<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
                    story_prompt = brief if brief else sel_name
                    st.session_state.brand_story = llm.generate_brand_story(sel_name, story_prompt)
                    story_status.update(label="✅ 品牌故事创作完成", state="complete")

            if st.session_state.get("brand_story"):
                st.markdown(st.session_state.brand_story)

        # 快捷跳转到风险评估
        st.markdown("---")
        if st.button("📊 评估「{}」注册风险 →".format(sel_name), use_container_width=True):
            st.session_state.page = "风险"
            st.rerun()

# ============================================================
# 商标查询（本地DB + 国家商标网API）
# ============================================================
elif st.session_state.page == "查询":
    st.markdown('<p class="main-header">🔍 商标查询</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">支持本地数据库 + 国家商标网API实时查询</p>', unsafe_allow_html=True)

    src = st.radio("数据源", ["📦 本地模拟数据", "🌐 国家商标网API（实时）"],
                    index=1 if tm_api.enabled else 0, horizontal=True)
    use_api = "API" in src and tm_api.enabled

    c1, c2, c3 = st.columns(3)
    with c1:
        search_name = st.text_input("商标名称", placeholder="例如：华为、张三...")
    with c2:
        search_cat = st.selectbox("类别（可选）", ["全部"] + [f"第{i}类 - {CATEGORY_NAMES.get(i, '')}" for i in range(1, 46)], index=0)
    with c3:
        if use_api:
            search_match = st.selectbox("匹配方式", ["模糊匹配", "精确匹配"])
        else:
            search_applicant = st.text_input("申请人（可选）", placeholder="例如：华为技术...")

    category_id = None
    if search_cat != "全部":
        category_id = int(search_cat.split("类")[0].replace("第", ""))

    if st.button("🔍 查询", type="primary", use_container_width=True):
        if use_api and search_name:
            ismatch = 1 if search_match == "精确匹配" else 0
            with st.status("🌐 正在查询国家商标网...", expanded=True) as status:
                st.markdown('<div class="loading-dots">查询中<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
                api_results = tm_api.search_formatted(search_name, size=20, ismatch=ismatch)
                st.session_state.search_results_api = api_results
                st.session_state.search_results = []
                status.update(label=f"✅ 查询完成，共找到 {len(api_results)} 条结果", state="complete")
        else:
            with st.status("🔍 正在查询本地数据库...", expanded=True) as status:
                st.markdown('<div class="loading-dots">查询中<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
                results = db.search(name=search_name, category=category_id, applicant=search_applicant if not use_api else "")
                st.session_state.search_results = results
                st.session_state.search_results_api = []
                status.update(label=f"✅ 查询完成，共找到 {len(results)} 条结果", state="complete")

    # 显示API结果
    if st.session_state.get("search_results_api"):
        results = st.session_state.search_results_api
        st.markdown(f"---\n### 🌐 国家商标网查询结果（共 {len(results)} 条）")
        if not results:
            st.info("未找到匹配的商标记录。该名称可能具备较好的注册前景。")
        else:
            for r in results:
                st.markdown(f"""
                **{r['name']}** · 第{r['category']}类 · {r['status']}
                > 申请人：{r['applicant']} | 注册号：{r['reg_no']} | 申请日：{r.get('app_date', 'N/A')}
                > 代理机构：{r.get('agent', 'N/A')}
                """)

    # 显示本地DB结果
    if st.session_state.get("search_results"):
        results = st.session_state.search_results
        st.markdown(f"---\n### 📦 本地查询结果（共 {len(results)} 条）")
        if not results:
            st.info("未找到匹配的商标记录。")
        else:
            for r in results:
                status_map = {"registered": "✅ 已注册", "pending": "⏳ 审查中", "rejected": "❌ 已驳回"}
                status_text = status_map.get(r["status"], r["status"])
                cat_name = CATEGORY_NAMES.get(r["category"], "")
                st.markdown(f"""
                **{r['name']}** · 第{r['category']}类({cat_name}) · {status_text}
                > 申请人：{r['applicant']} | 注册日期：{r['registration_date']} | 到期：{r['expiry_date']}
                > {r['description']}
                """)

# ============================================================
# 风险评估
# ============================================================
elif st.session_state.page == "风险":
    st.markdown('<p class="main-header">📊 商标注册风险评估</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI自检商标注册通过率，结合国家商标网实时数据 + AI深度分析</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        risk_name = st.text_input("商标名称",
                                  value=st.session_state.selected_name,
                                  placeholder="输入要评估的商标名称")
    with c2:
        risk_cat = st.selectbox("申请类别",
                                [i for i in range(1, 46)],
                                index=19,
                                format_func=lambda x: f"第{x}类 - {CATEGORY_NAMES.get(x, '')}")

    if st.button("📊 开始评估", type="primary", use_container_width=True, disabled=not risk_name):
        with st.status("📊 正在全面评估商标风险...", expanded=True) as status:
            st.markdown('<div class="loading-dots">查询近似商标中<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
            similar_local = db.search_similar(risk_name, risk_cat)

            similar_api = []
            if tm_api.enabled:
                similar_api = tm_api.search_formatted(risk_name, size=10)

            all_similar = similar_local + similar_api
            st.markdown(f"已找到 **{len(similar_local)}** 个本地近似商标 + **{len(similar_api)}** 个API近似商标")

            st.markdown('<div class="loading-dots">AI深度分析中<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
            quick_score = llm.score_trademark(risk_name, risk_cat, len(all_similar))
            llm_analysis = llm.analyze_risk(risk_name, risk_cat, all_similar[:10])

            st.session_state.risk_result = {
                "name": risk_name,
                "category": risk_cat,
                "similar_local": similar_local,
                "similar_api": similar_api,
                "all_similar": all_similar,
                "quick_score": quick_score,
                "llm_analysis": llm_analysis,
            }
            status.update(label=f"✅ 风险评估完成 — 综合评分 {quick_score['score']}/100", state="complete")

    if "risk_result" in st.session_state:
        result = st.session_state.risk_result
        st.markdown("---")

        # 评分卡片
        score_data = result["quick_score"]
        col1, col2 = st.columns([1, 2])
        with col1:
            color_map = {"🟢": "#28a745", "🟡": "#ffc107", "🟠": "#fd7e14", "🔴": "#dc3545"}
            sc = score_data["color"]
            for emoji, hx in color_map.items():
                if emoji in sc:
                    hex_color = hx
                    break
            else:
                hex_color = "#28a745"
            st.markdown(f"""
            <div style="text-align:center; padding:2rem; background:#fafafa; border-radius:12px;">
                <div style="font-size:0.9rem; color:#888; margin-bottom:0.5rem;">综合风险评分</div>
                <div class="score-big" style="color:{hex_color};">{score_data['score']}</div>
                <div style="font-size:1.2rem; margin:0.5rem 0;">{sc} {score_data['level']}风险</div>
                <div style="color:#666; font-size:0.9rem;">{score_data['suggestion']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.subheader("📋 快速诊断")
            for detail in score_data["details"]:
                st.markdown(f"- {detail}")

        # 近似商标
        st.markdown("---")
        st.subheader(f"📑 近似商标分析")

        if result["similar_api"]:
            st.caption("🌐 国家商标网API数据")
            for s in result["similar_api"][:5]:
                st.markdown(f"- **{s['name']}** · 第{s['category']}类 · {s['status']} · {s['applicant']}")

        if result["similar_local"]:
            st.caption("📦 本地数据库")
            for s in result["similar_local"]:
                cat_name = CATEGORY_NAMES.get(s["category"], "")
                st.markdown(f"- **{s['name']}** · 第{s['category']}类({cat_name}) · {s['status']} · {s['applicant']}")

        if not result["all_similar"]:
            st.success("未发现近似商标，该名称在该类别具备较好的注册前景。")

        # LLM深度分析
        st.markdown("---")
        st.subheader("🤖 AI深度分析报告")
        st.markdown(result["llm_analysis"])

# ============================================================
# 智能问答
# ============================================================
elif st.session_state.page == "问答":
    st.markdown('<p class="main-header">💬 智能问答</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">用自然语言查商标，说人话就能搜</p>', unsafe_allow_html=True)

    st.info("""
    **试试这样问：**
    - "45类，张三，有没有注册？"
    - "我是做家具的，想注册'木语'，帮我查查能注册吗"
    - "华为在哪些类别注册了商标？"
    - "我是做餐饮的，帮我分析'蜀味香'的注册风险"
    - "帮我查全友家具有没有近似商标，第20类"
    """)

    nl_query = st.text_area("输入你的问题", placeholder="用大白话描述你的需求...", height=80)

    if st.button("💬 智能分析", type="primary", use_container_width=True, disabled=not nl_query):
        with st.status("💬 AI正在理解你的需求...", expanded=True) as status:
            st.markdown('<div class="loading-dots">解析自然语言中<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
            parsed = llm.parse_natural_query(nl_query)
            name = parsed.get("name", "")
            category = parsed.get("category")
            applicant = parsed.get("applicant", "")
            intent = parsed.get("intent", "search")
            industry = parsed.get("industry", "")

            results = []
            similar = []
            if name or category or applicant:
                results = db.search(name=name, category=category, applicant=applicant)
                similar = db.search_similar(name, category) if name else []

            api_results = []
            if tm_api.enabled and name:
                st.markdown('<div class="loading-dots">查询国家商标网中<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
                api_results = tm_api.search_formatted(name, size=10)

            st.session_state.nl_result = {
                "parsed": parsed,
                "results": results,
                "api_results": api_results,
                "similar": similar,
                "intent": intent,
                "industry": industry,
                "name": name,
                "target_categories": parsed.get("target_categories", []),
                "analysis_needed": parsed.get("analysis_needed", ""),
            }
            total = len(results) + len(api_results)
            status.update(label=f"✅ 分析完成 — 共找到 {total} 条相关结果", state="complete")

    if "nl_result" in st.session_state:
        nl = st.session_state.nl_result
        parsed = nl["parsed"]
        target_cats = parsed.get("target_categories", [])
        all_api = nl.get("api_results", [])
        st.markdown("---")

        st.subheader("🧠 AI理解结果")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("商标名称", parsed.get("name") or "未识别")
        with c2:
            st.metric("用户行业", parsed.get("industry") or "未识别")
        with c3:
            cat_labels = [f"第{c}类({CATEGORY_NAMES.get(c, '')})" for c in target_cats]
            st.metric("推断目标类别", ", ".join(cat_labels) if cat_labels else "未推断")
        if parsed.get("analysis_needed"):
            st.info(f"📝 {parsed['analysis_needed']}")

        st.markdown("---")

        if all_api:
            # 分组：目标类别中的注册 vs 其他类别
            blocked = {}
            free_cats = set(target_cats)
            other = []

            for r in all_api:
                cat = r.get("category")
                cat_int = int(cat) if cat and str(cat).isdigit() else 0
                if target_cats and cat_int in target_cats:
                    blocked.setdefault(cat_int, []).append(r)
                    free_cats.discard(cat_int)
                else:
                    other.append(r)

            st.subheader("📊 注册可行性分析")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("##### 🚫 已注册（障碍类别）")
                if blocked:
                    for cat_int, items in blocked.items():
                        cat_name = CATEGORY_NAMES.get(cat_int, "")
                        for r in items:
                            st.markdown(f"- **第{cat_int}类({cat_name})** · {r['status']} · {r['applicant']}")
                else:
                    st.success("目标类别中未发现注册记录")
            with col_b:
                st.markdown("##### ✅ 可尝试注册（机会类别）")
                if free_cats:
                    for c in sorted(free_cats):
                        st.markdown(f"- 第{c}类({CATEGORY_NAMES.get(c, '')}) · 暂未发现注册")
                else:
                    st.warning("目标类别已全部被注册")

            # 风险评分
            blocked_count = sum(len(v) for v in blocked.values())
            target_total = len(target_cats) if target_cats else 1
            ratio = blocked_count / max(target_total, 1)
            if ratio >= 0.8:
                risk_score, risk_color, risk_level = 20, "#dc3545", "🔴 高危"
            elif ratio >= 0.5:
                risk_score, risk_color, risk_level = 50, "#fd7e14", "🟠 中危"
            elif ratio > 0:
                risk_score, risk_color, risk_level = 75, "#ffc107", "🟡 注意"
            else:
                risk_score, risk_color, risk_level = 90, "#28a745", "🟢 乐观"

            st.markdown(f"""
            <div style="text-align:center; padding:1.5rem; background:#fafafa; border-radius:12px; margin:1rem 0;">
                <div style="font-size:0.9rem; color:#888;">综合注册可行性评分</div>
                <div class="score-big" style="color:{risk_color};">{risk_score}</div>
                <div style="font-size:1.1rem;">{risk_level}</div>
                <div style="color:#666; font-size:0.85rem;">
                    目标{target_total}个类别，{len(blocked)}个已被注册，{len(free_cats)}个可尝试
                </div>
            </div>
            """, unsafe_allow_html=True)

            if other:
                with st.expander(f"📋 其他类别注册情况（{len(other)}条）"):
                    for r in other:
                        cat_name = CATEGORY_NAMES.get(int(r['category']) if str(r['category']).isdigit() else 0, "")
                        st.markdown(f"- **{r['name']}** · 第{r['category']}类({cat_name}) · {r['status']} · {r['applicant']}")

            # AI综合建议
            if nl.get("name") and nl.get("industry"):
                st.markdown("---")
                st.subheader("🤖 AI综合注册建议")
                with st.status("🤖 AI正在生成注册策略...", expanded=True) as advice_status:
                    advice = llm.analyze_registration_advice(
                        nl["name"], nl["industry"], target_cats, all_api[:15]
                    )
                    st.markdown(advice)
                    advice_status.update(label="✅ 分析完成", state="complete")

        if not all_api:
            if nl.get("name"):
                st.success(f"未找到与「{nl['name']}」匹配的商标记录。该名称可能具备较好的注册前景。")

        # 本地DB结果
        if nl.get("results"):
            with st.expander(f"📦 本地数据库补充（{len(nl['results'])}条）"):
                for r in nl["results"]:
                    cat_name = CATEGORY_NAMES.get(r["category"], "")
                    st.markdown(f"- **{r['name']}** · 第{r['category']}类({cat_name}) · {r['status']} · {r['applicant']}")

# ============================================================
# 我的商标
# ============================================================
elif st.session_state.page == "我的商标":
    st.markdown('<p class="main-header">📋 我的商标</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">绑定商标，到期前自动提醒（待办高亮 + 短信 + 邮件）</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 商标列表", "➕ 绑定新商标"])

    with tab1:
        my_list = db.get_my_trademarks()
        expiring = db.get_expiring_soon(30)

        if expiring:
            st.warning(f"⚠️ 有 {len(expiring)} 个商标即将到期（30天内），请及时续展！")

        if not my_list:
            st.info("还没有绑定任何商标，去「绑定新商标」添加吧。")
        else:
            for tm in my_list:
                exp_date = datetime.strptime(tm["expiry_date"], "%Y-%m-%d")
                days_left = (exp_date - datetime.now()).days

                if days_left < 0:
                    cls, tag = "expiry-danger", "🔴 已过期"
                elif days_left <= 30:
                    cls, tag = "expiry-danger", f"⚠️ 仅剩{days_left}天"
                elif days_left <= 90:
                    cls, tag = "expiry-warn", f"🟡 剩余{days_left}天"
                else:
                    cls, tag = "", f"🟢 剩余{days_left}天"

                cat_name = CATEGORY_NAMES.get(tm["category"], "")
                st.markdown(f"""
                <div class="{cls}">
                    <b>{tm['name']}</b> · 第{tm['category']}类({cat_name}) · {tag}<br>
                    <small>注册号：{tm['registration_no'] or 'N/A'} | 到期日：{tm['expiry_date']} |
                    提醒方式：{'📱短信' if tm['phone'] else ''} {'📧邮件' if tm['email'] else ''} {'📋待办'}</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑 删除", key=f"del_{tm['id']}"):
                    db.delete_my_trademark(tm["id"])
                    st.rerun()

    with tab2:
        with st.form("bind_form"):
            c1, c2 = st.columns(2)
            with c1:
                b_name = st.text_input("商标名称*")
                b_cat = st.selectbox("类别*", [i for i in range(1, 46)],
                                     format_func=lambda x: f"第{x}类 - {CATEGORY_NAMES.get(x, '')}")
                b_reg_no = st.text_input("注册号")
                b_applicant = st.text_input("申请人")
            with c2:
                b_reg_date = st.date_input("注册日期")
                b_exp_date = st.date_input("到期日期*", min_value=datetime.now().date())
                b_remind = st.number_input("提前提醒天数", min_value=7, max_value=180, value=30)
                b_phone = st.text_input("手机号（短信提醒）")
                b_email = st.text_input("邮箱（邮件提醒）")
            b_notes = st.text_area("备注")

            if st.form_submit_button("✅ 绑定商标", type="primary", use_container_width=True):
                if b_name and b_exp_date:
                    db.bind_trademark({
                        "name": b_name,
                        "category": b_cat,
                        "registration_no": b_reg_no,
                        "applicant": b_applicant,
                        "registration_date": b_reg_date.strftime("%Y-%m-%d") if b_reg_date else "",
                        "expiry_date": b_exp_date.strftime("%Y-%m-%d"),
                        "notes": b_notes,
                        "phone": b_phone,
                        "email": b_email,
                        "remind_before_days": b_remind,
                    })
                    st.success(f"商标「{b_name}」绑定成功！到期前{b_remind}天会提醒你。")
                    st.rerun()
                else:
                    st.error("请至少填写商标名称和到期日期。")

# ============================================================
st.markdown("---")
st.markdown('<p class="footer">商标AI智能助手 Demo v1.1 · Powered by DashScope + 阿里云商标API</p>',
            unsafe_allow_html=True)
