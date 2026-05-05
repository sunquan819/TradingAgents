import streamlit as st
import os
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime
import time
from config_manager import (
    load_config, save_config, clear_config, 
    get_api_key_from_config, save_api_key,
    get_all_saved_api_keys, save_settings,
    get_saved_settings, get_config_file_path
)

LANGUAGES = {
    "English": {
        "title": "TradingAgents - Multi-Agent Trading Analysis",
        "sidebar_header": "Analysis Configuration",
        "ticker_label": "Ticker Symbol",
        "ticker_help": "Enter stock ticker (e.g., NVDA, AAPL, SPY)",
        "date_label": "Analysis Date",
        "llm_header": "LLM Settings",
        "llm_label": "LLM Provider",
        "llm_help": "Select your preferred LLM provider",
        "deep_model_label": "Deep Thinking Model",
        "quick_model_label": "Quick Thinking Model",
        "agent_header": "Agent Settings",
        "analyst_label": "Analyst Team",
        "analyst_help": "Select which analysts to include",
        "debate_label": "Max Debate Rounds",
        "debate_help": "Number of rounds for bull/bear debate",
        "lang_label": "Output Language",
        "api_key_header": "API Key Configuration",
        "api_key_label": "API Key",
        "api_key_help": "Enter your API key",
        "api_key_from_env": "Using from .env file",
        "api_key_saved": "Saved in local config",
        "api_key_placeholder": "Paste your API key here",
        "save_button": "Save Configuration",
        "clear_button": "Clear All Saved Data",
        "config_saved": "Configuration saved!",
        "config_cleared": "All saved data cleared!",
        "config_path": "Config file location",
        "start_button": "Start Analysis",
        "error_select_analyst": "Please select at least one analyst!",
        "error_no_api_key": "Please enter API key for selected provider!",
        "progress_init": "Initializing agents...",
        "progress_market": "Running Market Analyst...",
        "progress_news": "Running News Analyst...",
        "progress_fundamentals": "Running Fundamentals Analyst...",
        "progress_debate": "Bull vs Bear debate...",
        "progress_research": "Research Manager synthesis...",
        "progress_trader": "Trader proposal...",
        "progress_risk": "Risk Management debate...",
        "progress_portfolio": "Portfolio Manager decision...",
        "progress_complete": "Analysis complete!",
        "spinnerText": "Analyzing...",
        "success_complete": "Analysis Complete! Decision:",
        "error_analysis": "Error during analysis:",
        "error_api_keys": "Check your API keys configuration",
        "tab_market": "Market Analysis",
        "tab_news": "News Analysis",
        "tab_fundamentals": "Fundamentals",
        "tab_research": "Research Debate",
        "tab_final": "Final Decision",
        "info_not_selected": "Analyst not selected",
        "bull_header": "Bull Researcher",
        "bear_header": "Bear Researcher",
        "research_manager": "Research Manager Decision",
        "trader_proposal": "Trader Proposal",
        "risk_debate": "Risk Management Debate",
        "portfolio_decision": "Portfolio Manager Final Decision",
        "aggressive": "Aggressive",
        "conservative": "Conservative",
        "neutral": "Neutral",
        "recommendation": "Final Recommendation",
        "metrics_ticker": "Ticker",
        "metrics_date": "Date",
        "metrics_provider": "Provider",
        "sidebar_footer": "Built by Tauric Research",
        "github_button": "GitHub",
        "interface_lang": "Interface Language",
        "lang_toggle": "Switch Language",
        "ollama_note": "Ollama uses local models, no API key needed",
    },
    "Chinese": {
        "title": "TradingAgents - 多智能体交易分析",
        "sidebar_header": "分析配置",
        "ticker_label": "股票代码",
        "ticker_help": "输入股票代码（如：NVDA、AAPL、SPY）",
        "date_label": "分析日期",
        "llm_header": "LLM 设置",
        "llm_label": "LLM 提供商",
        "llm_help": "选择您偏好的 LLM 提供商",
        "deep_model_label": "深度思考模型",
        "quick_model_label": "快速思考模型",
        "agent_header": "智能体设置",
        "analyst_label": "分析师团队",
        "analyst_help": "选择要包含的分析师",
        "debate_label": "最大辩论轮数",
        "debate_help": "多空辩论的轮数",
        "lang_label": "输出语言",
        "api_key_header": "API 密钥配置",
        "api_key_label": "API 密钥",
        "api_key_help": "输入您的 API 密钥",
        "api_key_from_env": "使用 .env 文件中的密钥",
        "api_key_saved": "已保存在本地配置中",
        "api_key_placeholder": "在此粘贴您的 API 密钥",
        "save_button": "保存配置",
        "clear_button": "清除所有保存数据",
        "config_saved": "配置已保存！",
        "config_cleared": "所有保存数据已清除！",
        "config_path": "配置文件位置",
        "start_button": "开始分析",
        "error_select_analyst": "请至少选择一个分析师！",
        "error_no_api_key": "请输入所选提供商的 API 密钥！",
        "progress_init": "初始化智能体...",
        "progress_market": "运行市场分析师...",
        "progress_news": "运行新闻分析师...",
        "progress_fundamentals": "运行基本面分析师...",
        "progress_debate": "多空辩论...",
        "progress_research": "研究经理综合...",
        "progress_trader": "交易员提案...",
        "progress_risk": "风险管理辩论...",
        "progress_portfolio": "投资组合经理决策...",
        "progress_complete": "分析完成！",
        "spinnerText": "正在分析...",
        "success_complete": "分析完成！决策：",
        "error_analysis": "分析过程中出错：",
        "error_api_keys": "请检查 API 密钥配置",
        "tab_market": "市场分析",
        "tab_news": "新闻分析",
        "tab_fundamentals": "基本面",
        "tab_research": "研究辩论",
        "tab_final": "最终决策",
        "info_not_selected": "未选择该分析师",
        "bull_header": "多头研究员",
        "bear_header": "空头研究员",
        "research_manager": "研究经理决策",
        "trader_proposal": "交易员提案",
        "risk_debate": "风险管理辩论",
        "portfolio_decision": "投资组合经理最终决策",
        "aggressive": "激进",
        "conservative": "保守",
        "neutral": "中性",
        "recommendation": "最终建议",
        "metrics_ticker": "股票代码",
        "metrics_date": "日期",
        "metrics_provider": "提供商",
        "sidebar_footer": "由 Tauric Research 构建",
        "github_button": "GitHub",
        "interface_lang": "界面语言",
        "lang_toggle": "切换语言",
        "ollama_note": "Ollama 使用本地模型，无需 API 密钥",
    }
}

API_KEY_ENV_MAP = {
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "xai": "XAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "qwen": "DASHSCOPE_API_KEY",
    "glm": "ZHIPU_API_KEY",
    "nvidia": "NVIDIA_API_KEY",
    "coding_plan": "ALIBABA_CODING_PLAN_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "ollama": None,
}

st.set_page_config(
    page_title="TradingAgents Web",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "interface_lang" not in st.session_state:
    st.session_state.interface_lang = "English"
if "running" not in st.session_state:
    st.session_state.running = False
if "final_state" not in st.session_state:
    st.session_state.final_state = None
if "decision" not in st.session_state:
    st.session_state.decision = None
if "initialized_from_config" not in st.session_state:
    st.session_state.initialized_from_config = False
if "ticker" not in st.session_state:
    st.session_state.ticker = "NVDA"

lang = LANGUAGES[st.session_state.interface_lang]

st.title(lang["title"])
st.markdown("---")

with st.sidebar:
    st.header(lang["sidebar_header"])
    
    interface_lang_choice = st.radio(
        lang["interface_lang"],
        ["English", "Chinese"],
        horizontal=True,
        key="lang_radio"
    )
    if interface_lang_choice != st.session_state.interface_lang:
        st.session_state.interface_lang = interface_lang_choice
        st.rerun()
    
    st.markdown("---")
    
    saved_settings = get_saved_settings()
    saved_api_keys = get_all_saved_api_keys()
    
    # 初始化 ticker（首次运行时从保存的配置加载）
    if not st.session_state.initialized_from_config:
        st.session_state.initialized_from_config = True
        st.session_state.ticker = saved_settings.get("ticker", "NVDA")
    
    # ticker 输入
    ticker = st.text_input(
        lang["ticker_label"],
        value=st.session_state.ticker,
        help=lang["ticker_help"]
    )
    
    # 美化的热门股票选择
    st.markdown("---")
    st.markdown("### 📌 热门股票 / Popular Stocks")
    
    # 美国科技股
    st.markdown("**🇺🇸 美国科技股 / US Tech**")
    us_cols = st.columns(5)
    us_tickers = [("NVDA", "NVIDIA"), ("AAPL", "Apple"), ("MSFT", "Microsoft"), 
                  ("GOOGL", "Google"), ("TSLA", "Tesla")]
    for i, (symbol, name) in enumerate(us_tickers):
        with us_cols[i]:
            if st.button(symbol, key=f"us_{symbol}", help=name, use_container_width=True):
                st.session_state.ticker = symbol
                st.rerun()
    
    # 中国股票
    st.markdown("**🇨🇳 中国股票 / Chinese Stocks**")
    cn_cols = st.columns(5)
    cn_tickers = [("BABA", "阿里巴巴"), ("JD", "京东"), ("PDD", "拼多多"),
                  ("NIO", "蔚来"), ("BILI", "哔哩哔哩")]
    for i, (symbol, name) in enumerate(cn_tickers):
        with cn_cols[i]:
            if st.button(symbol, key=f"cn_{symbol}", help=name, use_container_width=True):
                st.session_state.ticker = symbol
                st.rerun()
    
    # ETF
    st.markdown("**📊 ETF 指数基金**")
    etf_cols = st.columns(4)
    etf_tickers = [("SPY", "S&P 500"), ("QQQ", "纳斯达克100"), 
                   ("VTI", "全市场"), ("IWM", "罗素2000")]
    for i, (symbol, name) in enumerate(etf_tickers):
        with etf_cols[i]:
            if st.button(symbol, key=f"etf_{symbol}", help=name, use_container_width=True):
                st.session_state.ticker = symbol
                st.rerun()
    
    analysis_date = st.date_input(
        lang["date_label"],
        value=datetime.now(),
        max_value=datetime.now()
    )
    
    st.subheader(lang["llm_header"])
    
    llm_provider = st.selectbox(
        lang["llm_label"],
        ["openai", "google", "anthropic", "deepseek", "qwen", "coding_plan", "glm", "nvidia", "xai", "openrouter", "ollama"],
        index=["openai", "google", "anthropic", "deepseek", "qwen", "coding_plan", "glm", "nvidia", "xai", "openrouter", "ollama"].index(
            saved_settings.get("llm_provider", "openai")
        ),
        help=lang["llm_help"]
    )
    
    model_options = {
        "openai": ["gpt-5.4", "gpt-5.4-mini"],
        "google": ["gemini-3.1-pro", "gemini-3.1-flash"],
        "anthropic": ["claude-4.6-sonnet", "claude-4.6-opus"],
        "deepseek": ["deepseek-chat", "deepseek-reasoner"],
        "qwen": ["qwen-max", "qwen-plus"],
        "coding_plan": ["qwen3.6-plus", "kimi-k2.5", "glm-5", "MiniMax-M2.5"],
        "glm": ["glm-5", "glm-4.7"],
        "nvidia": ["deepseek-ai/deepseek-v4-flash", "deepseek-ai/deepseek-v4-pro", "meta/llama-3.3-70b-instruct"],
        "xai": ["grok-4-0709", "grok-4-fast-non-reasoning"],
        "openrouter": ["openai/gpt-5.4", "anthropic/claude-4.6-sonnet"],
        "ollama": ["llama3", "mistral"],
    }
    
    default_deep_idx = 0
    deep_options = model_options.get(llm_provider, ["gpt-5.4"])
    saved_deep = saved_settings.get("deep_model", "")
    if saved_deep in deep_options:
        default_deep_idx = deep_options.index(saved_deep)
    
    deep_model = st.selectbox(
        lang["deep_model_label"],
        deep_options,
        index=default_deep_idx
    )
    
    default_quick_idx = 0
    quick_options = model_options.get(llm_provider, ["gpt-5.4-mini"])
    saved_quick = saved_settings.get("quick_model", "")
    if saved_quick in quick_options:
        default_quick_idx = quick_options.index(saved_quick)
    
    quick_model = st.selectbox(
        lang["quick_model_label"],
        quick_options,
        index=default_quick_idx
    )
    
    st.subheader(lang["agent_header"])
    
    analyst_labels = {
        "market": lang["tab_market"],
        "social": "Sentiment" if st.session_state.interface_lang == "English" else "情绪",
        "news": lang["tab_news"],
        "fundamentals": lang["tab_fundamentals"],
    }
    
    analyst_keys = ["market", "social", "news", "fundamentals"]
    analyst_display = [analyst_labels[k] for k in analyst_keys]
    
    saved_analysts = saved_settings.get("selected_analysts", ["market", "news", "fundamentals"])
    saved_analyst_display = [analyst_labels[k] for k in saved_analysts if k in analyst_labels]
    
    selected_display = st.multiselect(
        lang["analyst_label"],
        analyst_display,
        default=saved_analyst_display,
        help=lang["analyst_help"]
    )
    
    selected_analysts = [analyst_keys[i] for i, d in enumerate(analyst_display) if d in selected_display]
    
    debate_rounds = st.slider(
        lang["debate_label"],
        min_value=1,
        max_value=5,
        value=saved_settings.get("debate_rounds", 1),
        help=lang["debate_help"]
    )
    
    output_language = st.selectbox(
        lang["lang_label"],
        ["English", "Chinese", "Japanese", "Spanish", "French"],
        index=["English", "Chinese", "Japanese", "Spanish", "French"].index(
            saved_settings.get("output_language", "English")
        )
    )
    
    st.markdown("---")
    st.subheader("📊 数据源配置 / Data Source")
    
    data_vendor_options = ["yfinance", "alpha_vantage"]
    saved_data_vendor = saved_settings.get("data_vendor", "yfinance")
    
    data_vendor = st.selectbox(
        "数据源 / Data Vendor",
        data_vendor_options,
        index=data_vendor_options.index(saved_data_vendor),
        help="yfinance: 免费，无需API Key | alpha_vantage: 更稳定，需API Key"
    )
    
    if data_vendor == "alpha_vantage":
        alpha_key_env = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
        alpha_key_saved = saved_api_keys.get("alpha_vantage", "")
        
        if alpha_key_env:
            st.caption("✅ 使用 .env 中的 Alpha Vantage API Key")
        elif alpha_key_saved:
            st.caption("✅ 已保存 Alpha Vantage API Key")
        
        alpha_key_input = st.text_input(
            "Alpha Vantage API Key",
            type="password",
            value=alpha_key_saved if alpha_key_saved and not alpha_key_env else "",
            placeholder="获取免费Key: https://www.alphavantage.co/support/#api-key",
            key="alpha_vantage_key_input"
        )
        
        if alpha_key_input and alpha_key_input != alpha_key_saved:
            save_api_key("alpha_vantage", alpha_key_input)
            saved_api_keys["alpha_vantage"] = alpha_key_input
    else:
        st.caption("✅ yfinance 免费，无需 API Key")
    
    st.markdown("---")
    st.subheader(lang["api_key_header"])
    
    api_key_env_name = API_KEY_ENV_MAP.get(llm_provider)
    
    if llm_provider == "ollama":
        st.info(lang["ollama_note"])
    elif api_key_env_name:
        env_key = os.environ.get(api_key_env_name, "")
        saved_key = saved_api_keys.get(llm_provider, "")
        
        status_msg = ""
        if env_key:
            status_msg = f"✅ {lang['api_key_from_env']}"
        elif saved_key:
            status_msg = f"✅ {lang['api_key_saved']}"
        
        if status_msg:
            st.caption(status_msg)
        
        default_value = saved_key if saved_key and not env_key else ""
        
        api_key_input = st.text_input(
            f"{lang['api_key_label']} ({llm_provider})",
            type="password",
            value=default_value,
            placeholder=lang["api_key_placeholder"],
            help=lang["api_key_help"],
            key=f"api_key_{llm_provider}_input"
        )
        
        if api_key_input and api_key_input != saved_key:
            save_api_key(llm_provider, api_key_input)
            saved_api_keys[llm_provider] = api_key_input
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(lang["save_button"], use_container_width=True):
            settings_to_save = {
                "ticker": ticker,
                "llm_provider": llm_provider,
                "deep_model": deep_model,
                "quick_model": quick_model,
                "selected_analysts": selected_analysts,
                "debate_rounds": debate_rounds,
                "output_language": output_language,
                "data_vendor": data_vendor,
            }
            save_settings(settings_to_save)
            st.success(lang["config_saved"])
    
    with col2:
        if st.button(lang["clear_button"], use_container_width=True):
            clear_config()
            st.session_state.initialized_from_config = False
            st.success(lang["config_cleared"])
            st.rerun()
    
    st.caption(f"{lang['config_path']}: `{get_config_file_path()}`")
    
    st.markdown("---")
    
    if st.button(lang["start_button"], type="primary", use_container_width=True):
        if not selected_analysts:
            st.error(lang["error_select_analyst"])
        elif llm_provider != "ollama" and api_key_env_name:
            final_key = saved_api_keys.get(llm_provider) or os.environ.get(api_key_env_name)
            if not final_key:
                st.error(lang["error_no_api_key"])
            else:
                st.session_state.running = True
                st.session_state.final_state = None
                st.session_state.decision = None
        else:
            st.session_state.running = True
            st.session_state.final_state = None
            st.session_state.decision = None

col1, col2, col3 = st.columns(3)
col1.metric(lang["metrics_ticker"], ticker)
col2.metric(lang["metrics_date"], str(analysis_date))
col3.metric(lang["metrics_provider"], llm_provider)

st.markdown("---")

if st.session_state.running:
    if llm_provider != "ollama" and api_key_env_name:
        final_key = saved_api_keys.get(llm_provider) or os.environ.get(api_key_env_name)
        if final_key:
            os.environ[api_key_env_name] = final_key
    
    if data_vendor == "alpha_vantage" and "alpha_vantage" in saved_api_keys:
        os.environ["ALPHA_VANTAGE_API_KEY"] = saved_api_keys["alpha_vantage"]
    
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = llm_provider
    config["deep_think_llm"] = deep_model
    config["quick_think_llm"] = quick_model
    config["max_debate_rounds"] = debate_rounds
    config["max_risk_discuss_rounds"] = debate_rounds
    config["output_language"] = output_language
    config["data_vendors"] = {
        "core_stock_apis": data_vendor,
        "technical_indicators": data_vendor,
        "fundamental_data": data_vendor,
        "news_data": data_vendor,
    }
    
    progress_bar = st.progress(0, text=lang["progress_init"])
    status_text = st.empty()
    
    status_steps = [
        lang["progress_init"],
        lang["progress_market"],
        lang["progress_news"],
        lang["progress_fundamentals"],
        lang["progress_debate"],
        lang["progress_research"],
        lang["progress_trader"],
        lang["progress_risk"],
        lang["progress_portfolio"],
        lang["progress_complete"],
    ]
    
    try:
        with st.spinner(lang["spinnerText"]):
            ta = TradingAgentsGraph(
                selected_analysts=selected_analysts,
                debug=True,
                config=config
            )
            
            for i, step in enumerate(status_steps):
                progress_bar.progress((i + 1) / len(status_steps), text=step)
                status_text.info(step)
                if i == 0:
                    time.sleep(0.5)
            
            final_state, decision = ta.propagate(ticker, str(analysis_date))
            
            st.session_state.final_state = final_state
            st.session_state.decision = decision
            st.session_state.running = False
            
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"{lang['success_complete']} **{decision}**")
            
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.session_state.running = False
        
        error_msg = str(e)
        
        # 识别错误类型并给出建议
        if "rate limit" in error_msg.lower() or "too many requests" in error_msg.lower():
            st.error(f"{lang['error_analysis']} Rate limit exceeded")
            st.warning("""
**解决方案 / Solutions:**

1. **数据源限制**: 切换到 Alpha Vantage 数据源
   - 获取免费 API Key: https://www.alphavantage.co/support/#api-key
   
2. **LLM API限制**: 
   - 等待 5-10 分钟后重试
   - 使用更稳定的提供商 (如 OpenAI, DeepSeek)
   - Coding Plan 套餐有请求频率限制，每5小时6000次

3. **减少分析师数量**: 选择较少的分析师可减少API调用
            """)
        elif "timeout" in error_msg.lower():
            st.error(f"{lang['error_analysis']} Connection timeout")
            st.warning("""
**解决方案 / Solutions:**

1. 网络连接问题，请检查网络
2. 尝试切换数据源
3. 稍后重试
            """)
        else:
            st.error(f"{lang['error_analysis']} {error_msg}")
            st.info(lang["error_api_keys"])
        
        st.code(error_msg, language="text")

if st.session_state.final_state:
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        lang["tab_market"], lang["tab_news"], lang["tab_fundamentals"],
        lang["tab_research"], lang["tab_final"]
    ])
    
    with tab1:
        if st.session_state.final_state.get("market_report"):
            st.markdown(st.session_state.final_state["market_report"])
        else:
            st.info(lang["info_not_selected"])
    
    with tab2:
        if st.session_state.final_state.get("news_report"):
            st.markdown(st.session_state.final_state["news_report"])
        else:
            st.info(lang["info_not_selected"])
    
    with tab3:
        if st.session_state.final_state.get("fundamentals_report"):
            st.markdown(st.session_state.final_state["fundamentals_report"])
        else:
            st.info(lang["info_not_selected"])
    
    with tab4:
        debate = st.session_state.final_state.get("investment_debate_state", {})
        if debate:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(lang["bull_header"])
                st.markdown(debate.get("bull_history", ""))
            with col2:
                st.subheader(lang["bear_header"])
                st.markdown(debate.get("bear_history", ""))
            
            st.markdown("---")
            st.subheader(lang["research_manager"])
            st.markdown(debate.get("judge_decision", ""))
    
    with tab5:
        st.subheader(lang["trader_proposal"])
        st.markdown(st.session_state.final_state.get("trader_investment_plan", ""))
        
        st.markdown("---")
        
        risk = st.session_state.final_state.get("risk_debate_state", {})
        if risk:
            st.subheader(lang["risk_debate"])
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**{lang['aggressive']}**")
            col1.markdown(risk.get("aggressive_history", ""))
            col2.markdown(f"**{lang['conservative']}**")
            col2.markdown(risk.get("conservative_history", ""))
            col3.markdown(f"**{lang['neutral']}**")
            col3.markdown(risk.get("neutral_history", ""))
        
        st.markdown("---")
        st.subheader(lang["portfolio_decision"])
        final_decision = st.session_state.final_state.get("final_trade_decision", "")
        st.markdown(final_decision)
        
        if "BUY" in str(st.session_state.decision):
            st.success(f"{lang['recommendation']}: {st.session_state.decision}")
        elif "SELL" in str(st.session_state.decision):
            st.error(f"{lang['recommendation']}: {st.session_state.decision}")
        else:
            st.warning(f"{lang['recommendation']}: {st.session_state.decision}")

with st.sidebar:
    st.markdown("---")
    st.caption(lang["sidebar_footer"])
    st.link_button(lang["github_button"], "https://github.com/TauricResearch/TradingAgents")