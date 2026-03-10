# finscreener

智能A股选股器 | 基于 Streamlit + Finshare

## 功能特性

- 📊 **财务筛选** - ROE、净利润增长、毛利率、资产负债率
- 💰 **资金筛选** - 主力净流入、大单流入
- 📈 **技术筛选** - 涨跌幅、换手率、量价关系
- 🔥 **市场情绪** - 涨停股、跌停股、资金流向

## 预览

![筛选器](images/screener.png)

## 安装

```bash
git clone https://github.com/finvfamily/finscreener.git
cd finscreener
pip install -r requirements.txt
streamlit run app.py
```

## 使用

```bash
streamlit run app.py
```

然后在浏览器中打开 http://localhost:8501

## 技术栈

- **前端**: Streamlit
- **数据**: [Finshare](https://github.com/finvfamily/finshare)
- **图表**: Plotly

## Star 支持

⭐ Star 支持一下！

[![Star](https://img.shields.io/github/stars/finvfamily/finscreener?style=social)](https://github.com/finvfamily/finscreener)

---

**基于 [Finshare](https://github.com/finvfamily/finshare)** - 免费的A股数据获取库
