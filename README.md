# AI 全产业链深度分析报告

AI 全产业链六层结构、核心壁垒与估值分析报告(数据截至 2026 年 5 月)。

## 文件说明

- **AI_Industry_Chain_Report.pdf** — 中文深度分析报告(PDF,约 15 页)
- **generate_report.py** — 报告生成脚本(Python,ReportLab + Matplotlib)

## 报告目录

1. 执行摘要
2. AI 产业链六层全景(设备 / 代工 / 元器件 / 云 / 模型 / 应用)
3. 逐层深度分析:不可替代的核心壁垒
   - ASML / TSMC / NVIDIA+HBM / 云厂商 / 模型 / 应用
4. 估值象限:高估 vs 低估
5. 系统性风险与结论(四梯队配置思路)

## 重建 PDF

```bash
python3.12 -m pip install reportlab matplotlib
python3.12 generate_report.py
```

## 数据来源

NVIDIA / TSMC / ASML / Micron / Palantir / Anthropic 官方披露,
Counterpoint、TrendForce、IDC、Gartner、Morgan Stanley、Fortune、CNBC、
The Motley Fool、Tom's Hardware、VanEck、TechCrunch、Forbes、Reuters、
Yahoo Finance、Economic Times 等公开资料。

> 本报告为研究性质,不构成任何投资建议。
