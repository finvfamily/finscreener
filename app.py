#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
finscreener: 智能A股选股器
基于 Streamlit + Finshare
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# 页面配置
st.set_page_config(
    page_title="finscreener",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    h1, h2, h3 {
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def get_stock_list():
    """获取股票列表"""
    from finshare import get_stock_list
    try:
        data = get_stock_list()
        if isinstance(data, list):
            return pd.DataFrame(data)
        return data
    except Exception as e:
        st.error(f"获取股票列表失败: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_money_flow_data():
    """获取个股资金流向"""
    from finshare import get_money_flow
    try:
        # 获取市场所有股票的资金流向
        stocks = get_stock_list()
        if stocks.empty:
            return pd.DataFrame()

        results = []
        # 取涨幅前100只股票的资金流向
        top_stocks = stocks.nlargest(100, 'change_pct')['code'].tolist()

        for code in top_stocks[:50]:  # 限制数量避免太慢
            try:
                df = get_money_flow(code)
                if not df.empty:
                    df['code'] = code
                    results.append(df)
            except:
                continue

        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"获取资金流向失败: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_money_flow_industry():
    """获取行业资金流向"""
    from finshare import get_money_flow_industry
    try:
        return get_money_flow_industry()
    except Exception as e:
        st.error(f"获取行业资金流向失败: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_lhb_data():
    """获取龙虎榜数据"""
    from finshare import get_lhb
    try:
        return get_lhb()
    except Exception as e:
        st.error(f"获取龙虎榜失败: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_margin_data():
    """获取融资融券数据"""
    from finshare import get_margin
    try:
        return get_margin()
    except Exception as e:
        st.error(f"获取融资融券失败: {e}")
        return pd.DataFrame()


def format_change_pct(val):
    if pd.isna(val):
        return "0.00%"
    return f"{val:+.2f}%"


def format_money(val):
    if pd.isna(val) or val is None:
        return "0"
    if abs(val) >= 1e8:
        return f"{val/1e8:.2f}亿"
    elif abs(val) >= 1e4:
        return f"{val/1e4:.2f}万"
    return f"{val:.2f}"


def main():
    st.title("🔍 finscreener - 智能A股选股器")

    # 侧边栏 - 筛选条件
    with st.sidebar:
        st.header("筛选条件")

        # 市场选择
        market = st.selectbox(
            "市场",
            ["全部", "上海", "深圳"],
            index=0
        )

        st.markdown("---")

        # 涨跌幅筛选
        st.subheader("📈 涨跌幅筛选")
        change_pct_min = st.slider("涨跌幅下限", -10, 20, -10, step=1)
        change_pct_max = st.slider("涨跌幅上限", -10, 20, 20, step=1)

        st.markdown("---")

        # 成交额筛选
        st.subheader("💰 成交额筛选")
        amount_min = st.number_input("成交额下限(万)", min_value=0, value=0, step=100)

        st.markdown("---")

        # 换手率筛选
        st.subheader("🔄 换手率筛选")
        turnover_min = st.slider("换手率下限", 0, 50, 0, step=1)

        st.markdown("---")

        # 刷新按钮
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # 主页面
    tab1, tab2, tab3, tab4 = st.tabs(["📊 市场筛选", "💰 资金流向", "🐯 龙虎榜", "📈 行业资金"])

    with tab1:
        show_market_filter(change_pct_min, change_pct_max, amount_min, turnover_min, market)

    with tab2:
        show_money_flow_filter()

    with tab3:
        show_lhb_filter()

    with tab4:
        show_industry_flow()


def show_market_filter(change_pct_min, change_pct_max, amount_min, turnover_min, market):
    """市场筛选"""
    st.subheader("📊 市场股票筛选")

    with st.spinner("加载股票数据..."):
        df = get_stock_list()

    if df.empty:
        st.warning("暂无数据")
        return

    # 市场筛选
    if market == "上海":
        df = df[df['code'].str.endswith('.SH')]
    elif market == "深圳":
        df = df[df['code'].str.endswith('.SZ')]

    # 涨跌幅筛选
    df = df[(df['change_pct'] >= change_pct_min) & (df['change_pct'] <= change_pct_max)]

    # 成交额筛选
    if amount_min > 0:
        df = df[df['amount'] >= amount_min * 10000]

    st.success(f"符合条件: {len(df)} 只股票")

    if not df.empty:
        # 显示结果
        df_display = df.copy()
        df_display['change_pct'] = df_display['change_pct'].apply(format_change_pct)
        df_display['amount'] = df_display['amount'].apply(format_money)

        # 选择显示列
        cols = ['code', 'name', 'price', 'change_pct', 'volume', 'amount']
        cols = [c for c in cols if c in df_display.columns]

        st.dataframe(
            df_display[cols],
            column_config={
                "code": "代码",
                "name": "名称",
                "price": "价格",
                "change_pct": "涨跌幅",
                "volume": "成交量",
                "amount": "成交额",
            },
            hide_index=True,
            use_container_width=True,
            height=500
        )

        # 可视化
        st.markdown("---")
        st.subheader("📈 涨跌幅分布")

        fig = px.histogram(
            df,
            x="change_pct",
            nbins=40,
            title="涨跌幅分布",
            labels={"change_pct": "涨跌幅(%)", "count": "股票数量"}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)


def show_money_flow_filter():
    """资金流向筛选"""
    st.subheader("💰 资金流向筛选")

    with st.spinner("加载资金流向数据..."):
        df = get_money_flow_data()

    if df.empty:
        st.warning("暂无资金流向数据")
        return

    # 选择显示列
    cols = ['code', 'trade_date', 'net_inflow_main', 'net_inflow_main_ratio']
    cols = [c for c in cols if c in df.columns]

    if cols:
        df_display = df.copy()
        if 'net_inflow_main' in df_display.columns:
            df_display = df_display.sort_values('net_inflow_main', ascending=False)

        st.dataframe(
            df_display[cols].head(50),
            column_config={
                "code": "代码",
                "trade_date": "日期",
                "net_inflow_main": "主力净流入",
                "net_inflow_main_ratio": "主力净流入占比",
            },
            hide_index=True,
            use_container_width=True,
            height=400
        )


def show_lhb_filter():
    """龙虎榜筛选"""
    st.subheader("🐯 今日龙虎榜")

    with st.spinner("加载龙虎榜数据..."):
        df = get_lhb_data()

    if df.empty:
        st.warning("暂无数据 (可能非交易日)")
        return

    st.success(f"今日上榜: {len(df)} 只股票")

    # 按净买额排序
    df = df.sort_values('net_buy_amount', ascending=False)

    df_display = df.head(30).copy()
    df_display['change_rate'] = df_display['change_rate'].apply(format_change_pct)
    for col in ['net_buy_amount', 'buy_amount', 'sell_amount']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(format_money)

    cols = ['fs_code', 'close_price', 'change_rate', 'net_buy_amount', 'reason']
    cols = [c for c in cols if c in df_display.columns]

    st.dataframe(
        df_display[cols],
        column_config={
            "fs_code": "代码",
            "close_price": "收盘价",
            "change_rate": "涨跌幅",
            "net_buy_amount": "净买额",
            "reason": "上榜原因",
        },
        hide_index=True,
        use_container_width=True,
        height=400
    )


def show_industry_flow():
    """行业资金流向"""
    st.subheader("📈 行业资金流向")

    with st.spinner("加载行业资金流向..."):
        df = get_money_flow_industry()

    if df.empty:
        st.warning("暂无数据")
        return

    # 净流入 TOP10
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔺 净流入 TOP 10")
        top_inflow = df.nlargest(10, 'net_inflow')[['industry', 'net_inflow', 'change_rate']].copy()
        top_inflow['net_inflow'] = top_inflow['net_inflow'].apply(format_money)
        top_inflow['change_rate'] = top_inflow['change_rate'].apply(format_change_pct)
        st.dataframe(top_inflow, hide_index=True, use_container_width=True)

    with col2:
        st.markdown("### 🔻 净流出 TOP 10")
        top_outflow = df.nsmallest(10, 'net_inflow')[['industry', 'net_inflow', 'change_rate']].copy()
        top_outflow['net_inflow'] = top_outflow['net_inflow'].apply(format_money)
        top_outflow['change_rate'] = top_outflow['change_rate'].apply(format_change_pct)
        st.dataframe(top_outflow, hide_index=True, use_container_width=True)

    # 可视化
    st.markdown("---")
    st.subheader("📊 行业资金流向分布")

    df_sorted = df.sort_values('net_inflow', ascending=True).tail(20)
    fig = px.bar(
        df_sorted,
        x='net_inflow',
        y='industry',
        orientation='h',
        color='net_inflow',
        color_continuous_scale=['red', 'gray', 'green'],
        title="行业资金流向 (单位: 元)",
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
