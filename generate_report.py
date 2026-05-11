# -*- coding: utf-8 -*-
"""
AI 全产业链深度分析报告 PDF 生成脚本 (v2 · 表格换行修复 + 图表美化)
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Image,
)

# ========== 字体注册 ==========
CJK_REG = "/projects/sandbox/aizhilv/fonts/NotoSansSC-Regular.ttf"
CJK_BOLD = CJK_REG

pdfmetrics.registerFont(TTFont("CJK", CJK_REG))
pdfmetrics.registerFont(TTFont("CJK-Bold", CJK_BOLD))
registerFontFamily("CJK", normal="CJK", bold="CJK-Bold",
                   italic="CJK", boldItalic="CJK-Bold")

# ========== 配色 ==========
C_NAVY    = colors.HexColor("#0B2447")
C_BLUE    = colors.HexColor("#19376D")
C_INDIGO  = colors.HexColor("#576CBC")
C_ACCENT  = colors.HexColor("#A5D7E8")
C_LIGHT   = colors.HexColor("#F4F6FB")
C_TEXT    = colors.HexColor("#222222")
C_MUTED   = colors.HexColor("#666666")
C_BORDER  = colors.HexColor("#D0D5E0")
C_GOOD    = colors.HexColor("#2E7D32")
C_WARN    = colors.HexColor("#EF6C00")
C_BAD     = colors.HexColor("#C62828")

# ========== 样式 ==========
styles = getSampleStyleSheet()

COVER_TITLE = ParagraphStyle(
    "CoverTitle", parent=styles["Title"], fontName="CJK-Bold",
    fontSize=28, leading=40, alignment=TA_CENTER, textColor=C_NAVY,
    spaceAfter=12, wordWrap="CJK",
)
COVER_SUB = ParagraphStyle(
    "CoverSub", parent=styles["Normal"], fontName="CJK",
    fontSize=14, leading=22, alignment=TA_CENTER, textColor=C_BLUE,
    spaceAfter=6, wordWrap="CJK",
)
COVER_META = ParagraphStyle(
    "CoverMeta", parent=styles["Normal"], fontName="CJK",
    fontSize=11, leading=18, alignment=TA_CENTER, textColor=C_MUTED,
    wordWrap="CJK",
)

H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="CJK-Bold",
    fontSize=18, leading=26, textColor=C_NAVY,
    spaceBefore=10, spaceAfter=8, wordWrap="CJK",
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName="CJK-Bold",
    fontSize=14, leading=22, textColor=C_BLUE,
    spaceBefore=10, spaceAfter=4, wordWrap="CJK",
)
H3 = ParagraphStyle(
    "H3", parent=styles["Heading3"], fontName="CJK-Bold",
    fontSize=12, leading=18, textColor=C_INDIGO,
    spaceBefore=6, spaceAfter=2, wordWrap="CJK",
)
BODY = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="CJK",
    fontSize=10.5, leading=18, alignment=TA_JUSTIFY,
    textColor=C_TEXT, spaceAfter=4, wordWrap="CJK",
)
BULLET = ParagraphStyle(
    "Bullet", parent=BODY, leftIndent=14, bulletIndent=2,
)
NOTE = ParagraphStyle(
    "Note", parent=BODY, fontSize=9, leading=14, textColor=C_MUTED,
)

# 单元格专用样式(强制中文断行)
CELL_HEADER = ParagraphStyle(
    "CellHeader", fontName="CJK-Bold", fontSize=10, leading=13,
    textColor=colors.white, alignment=TA_CENTER, wordWrap="CJK",
)
CELL_BODY = ParagraphStyle(
    "CellBody", fontName="CJK", fontSize=9.2, leading=13,
    textColor=C_TEXT, alignment=TA_LEFT, wordWrap="CJK",
)
CELL_BODY_CENTER = ParagraphStyle(
    "CellBodyCenter", parent=CELL_BODY, alignment=TA_CENTER,
)

# ========== 工具函数 ==========
def P(text, style=BODY):
    return Paragraph(text, style)

def cellH(text):
    """表头单元格"""
    return Paragraph(text, CELL_HEADER)

def cellL(text):
    """左对齐单元格(带中文断行)"""
    return Paragraph(text, CELL_BODY)

def cellC(text):
    """居中单元格(带中文断行)"""
    return Paragraph(text, CELL_BODY_CENTER)

def wrap_table_data(data, align_first_left=True):
    """把二维表格数据全部包成 Paragraph,确保中文自动换行"""
    wrapped = []
    for i, row in enumerate(data):
        wrapped_row = []
        for j, cell in enumerate(row):
            if i == 0:
                wrapped_row.append(cellH(str(cell)))
            elif align_first_left and j == 0:
                wrapped_row.append(cellL(str(cell)))
            else:
                wrapped_row.append(cellC(str(cell)))
        wrapped.append(wrapped_row)
    return wrapped

def styled_table(data, col_widths, row_heights=None, align_first_left=True):
    """创建支持中文自动换行的表格"""
    wrapped = wrap_table_data(data, align_first_left)
    t = Table(wrapped, colWidths=col_widths, rowHeights=row_heights,
              repeatRows=1, splitByRow=1)
    cmds = [
        ("VALIGN",  (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, C_NAVY),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, C_NAVY),
        ("LINEBEFORE", (0, 0), (0, -1), 0.3, C_BORDER),
        ("LINEAFTER", (-1, 0), (-1, -1), 0.3, C_BORDER),
        ("INNERGRID", (0, 1), (-1, -1), 0.25, C_BORDER),
        # 表头
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]
    # 斑马条纹
    for i in range(1, len(data)):
        bg = C_LIGHT if i % 2 == 1 else colors.white
        cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(cmds))
    return t

def hr(width=17*cm, color=C_BLUE):
    t = Table([[""]], colWidths=[width], rowHeights=[0.1])
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.8, color)]))
    return t

# ========== 图表生成 ==========
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch

fm.fontManager.addfont(CJK_REG)
plt.rcParams["font.family"] = "Noto Sans SC"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.edgecolor"] = "#CCCCCC"
plt.rcParams["axes.labelcolor"] = "#333333"
plt.rcParams["xtick.color"] = "#666666"
plt.rcParams["ytick.color"] = "#666666"

CHART_DIR = "/projects/sandbox/aizhilv/charts"
os.makedirs(CHART_DIR, exist_ok=True)

def _style_ax(ax, title=None, ylabel=None, xlabel=None):
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", color="#0B2447", pad=14)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10.5, color="#333")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10.5, color="#333")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.grid(axis="y", linestyle="--", alpha=0.35, color="#999")
    ax.set_axisbelow(True)

# --- 1. 超大规模厂商资本开支 ---
def chart_hyperscaler_capex():
    names = ["Amazon\n(AWS)", "Microsoft", "Alphabet", "Meta", "Oracle", "CoreWeave"]
    capex = [200, 190, 185, 135, 40, 25]
    colors_bar = ["#FF9900", "#00A4EF", "#4285F4", "#1877F2", "#F80000", "#00E0A4"]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor("white")
    bars = ax.bar(names, capex, color=colors_bar, width=0.65,
                  edgecolor="white", linewidth=1.5)
    for b, v in zip(bars, capex):
        ax.text(b.get_x() + b.get_width()/2, v + 6, f"${v}B",
                ha="center", fontsize=11, fontweight="bold", color="#222")
    ax.set_ylim(0, 235)
    _style_ax(ax, title="2026 年全球主要超大规模厂商 AI 资本开支指引",
              ylabel="资本开支(十亿美元)")
    ax.text(0.5, -0.22, "合计约 7,750 亿美元,其中 ~44% 流向 NVIDIA",
            transform=ax.transAxes, ha="center", fontsize=10,
            color="#666", style="italic")
    plt.tight_layout()
    path = os.path.join(CHART_DIR, "hyperscaler_capex.png")
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return path

# --- 2. AI 芯片市场份额 (甜甜圈图) ---
def chart_ai_chip_share():
    labels = ["NVIDIA", "云厂商自研 ASIC", "AMD", "其他"]
    sizes = [81, 10, 6, 3]
    colors_pie = ["#76B900", "#4285F4", "#ED1C24", "#BBBBBB"]
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    fig.patch.set_facecolor("white")
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors_pie, autopct="%1.0f%%",
        startangle=90, pctdistance=0.78,
        textprops={"fontsize": 11, "fontweight": "bold"},
        wedgeprops={"edgecolor": "white", "linewidth": 2.5, "width": 0.42},
    )
    for a in autotexts:
        a.set_color("white")
        a.set_fontsize(11)
    # 中心文字
    ax.text(0, 0.08, "81%", ha="center", va="center",
            fontsize=26, fontweight="bold", color="#76B900")
    ax.text(0, -0.14, "NVIDIA 主导", ha="center", va="center",
            fontsize=11, color="#666")
    ax.set_title("2026 年 AI 数据中心加速器市场份额", fontsize=13,
                 fontweight="bold", color="#0B2447", pad=12)
    ax.text(0.5, -0.05, "数据来源:IDC 估算",
            transform=ax.transAxes, ha="center", fontsize=9,
            color="#888", style="italic")
    plt.tight_layout()
    path = os.path.join(CHART_DIR, "ai_chip_share.png")
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return path

# --- 3. HBM 市场份额 ---
def chart_hbm_share():
    labels = ["SK Hynix", "Samsung", "Micron"]
    sizes = [57, 22, 21]
    colors_pie = ["#CC0000", "#1428A0", "#0066B2"]
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    fig.patch.set_facecolor("white")
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors_pie, autopct="%1.0f%%",
        startangle=120, pctdistance=0.78,
        textprops={"fontsize": 12, "fontweight": "bold"},
        wedgeprops={"edgecolor": "white", "linewidth": 2.5, "width": 0.42},
    )
    for a in autotexts:
        a.set_color("white")
        a.set_fontsize(12)
    ax.text(0, 0.08, "57%", ha="center", va="center",
            fontsize=26, fontweight="bold", color="#CC0000")
    ax.text(0, -0.14, "SK Hynix 领跑", ha="center", va="center",
            fontsize=11, color="#666")
    ax.set_title("2025 Q3 HBM 全球市场份额", fontsize=13,
                 fontweight="bold", color="#0B2447", pad=12)
    ax.text(0.5, -0.05, "数据来源:Counterpoint Research",
            transform=ax.transAxes, ha="center", fontsize=9,
            color="#888", style="italic")
    plt.tight_layout()
    path = os.path.join(CHART_DIR, "hbm_share.png")
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return path

# --- 4. Anthropic ARR 增长 ---
def chart_anthropic_arr():
    months = ["2024-12", "2025-06", "2025-12", "2026-02", "2026-04"]
    arr = [1, 4, 9, 19, 30]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor("white")
    # 填充区域
    ax.fill_between(months, arr, alpha=0.15, color="#D97757")
    ax.plot(months, arr, marker="o", linewidth=3, color="#D97757",
            markersize=11, markerfacecolor="white",
            markeredgecolor="#D97757", markeredgewidth=2.5)
    for x, y in zip(months, arr):
        ax.annotate(f"${y}B", (x, y), textcoords="offset points",
                    xytext=(0, 14), ha="center", fontsize=11,
                    fontweight="bold", color="#8B3A1F")
    _style_ax(ax, title="Anthropic 年化收入(ARR)爆发式增长",
              ylabel="ARR(十亿美元)")
    ax.set_ylim(0, 38)
    ax.text(0.5, -0.22, "18 个月 30 倍增长 · Claude Code 驱动",
            transform=ax.transAxes, ha="center", fontsize=10,
            color="#666", style="italic")
    plt.tight_layout()
    path = os.path.join(CHART_DIR, "anthropic_arr.png")
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return path

# --- 5. 估值象限 ---
def chart_valuation_quadrant():
    companies = [
        ("NVIDIA",    35, 60, 4500, "#76B900"),
        ("TSMC",      28, 35, 1400, "#C00000"),
        ("ASML",      40, 20, 450,  "#FF6600"),
        ("Broadcom",  42, 30, 1400, "#CC0000"),
        ("Microsoft", 34, 18, 4200, "#00A4EF"),
        ("Alphabet",  26, 15, 2700, "#4285F4"),
        ("Meta",      25, 14, 1700, "#1877F2"),
        ("Amazon",    38, 13, 2300, "#FF9900"),
        ("Palantir",  230, 71, 400, "#000000"),
        ("Micron",    18, 50, 700,  "#0066B2"),
        ("SK Hynix",  10, 45, 260,  "#CC0000"),
        ("AMD",       45, 40, 450,  "#ED1C24"),
    ]
    fig, ax = plt.subplots(figsize=(10, 6.5))
    fig.patch.set_facecolor("white")

    # 象限背景色(分四区)
    ax.axvspan(0, 30, 25, 80, alpha=0.08, color="#2E7D32")   # 左上:最优
    ax.axvspan(30, 260, 0, 25, alpha=0.06, color="#FF6F00")  # 右下:溢价
    ax.axvspan(30, 260, 25, 80, alpha=0.08, color="#C62828") # 右上:透支
    ax.axvspan(0, 30, 0, 25, alpha=0.06, color="#455A64")    # 左下:稳健

    for name, pe, g, mc, c in companies:
        ax.scatter(pe, g, s=max(mc*0.09, 80), color=c, alpha=0.78,
                   edgecolors="white", linewidth=2, zorder=3)
        ax.annotate(name, (pe, g), xytext=(8, 8),
                    textcoords="offset points", fontsize=10,
                    fontweight="bold", color="#222", zorder=4)

    # 象限分隔线
    ax.axvline(30, color="#555", linestyle="--", linewidth=1, alpha=0.6)
    ax.axhline(25, color="#555", linestyle="--", linewidth=1, alpha=0.6)

    # 象限标签
    ax.text(5, 77, "左上 · 高性价比",  fontsize=10, color="#2E7D32", fontweight="bold", alpha=0.9)
    ax.text(200, 77, "右上 · 高估值高增长", fontsize=10, color="#C62828", fontweight="bold", alpha=0.9)
    ax.text(200, 2, "右下 · 护城河溢价", fontsize=10, color="#FF6F00", fontweight="bold", alpha=0.9)
    ax.text(5, 2, "左下 · 稳健",       fontsize=10, color="#455A64", fontweight="bold", alpha=0.9)

    ax.set_xlabel("前瞻市盈率 PE(倍)", fontsize=11, color="#333")
    ax.set_ylabel("2026 年营收增速(% YoY)", fontsize=11, color="#333")
    ax.set_title("AI 产业链核心公司估值 vs 增速(气泡面积 = 市值规模)",
                 fontsize=13, fontweight="bold", color="#0B2447", pad=14)
    ax.grid(linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 80)

    plt.tight_layout()
    path = os.path.join(CHART_DIR, "valuation_quadrant.png")
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return path

# --- 6. 产业链利润分配示意图 ---
def chart_profit_flow():
    layers = ["设备\n(ASML)", "代工\n(TSMC)", "GPU\n(NVIDIA)",
              "HBM\n(SK Hynix等)", "云\n(MSFT/AWS)", "模型\n(OpenAI等)", "应用\n(Palantir等)"]
    gm = [53, 66, 75, 75, 35, -20, 70]  # 毛利率%
    col_map = []
    for v in gm:
        if v >= 60: col_map.append("#2E7D32")
        elif v >= 30: col_map.append("#FFA726")
        else: col_map.append("#C62828")

    fig, ax = plt.subplots(figsize=(9.5, 4.5))
    fig.patch.set_facecolor("white")
    bars = ax.barh(layers, gm, color=col_map, edgecolor="white",
                   linewidth=1.5, height=0.65)
    for b, v in zip(bars, gm):
        x = v + 2 if v >= 0 else v - 2
        ha = "left" if v >= 0 else "right"
        ax.text(x, b.get_y() + b.get_height()/2, f"{v}%",
                va="center", ha=ha, fontsize=11, fontweight="bold", color="#222")
    ax.set_xlim(-35, 95)
    ax.axvline(0, color="#999", linewidth=0.8)
    ax.set_xlabel("毛利率(%)", fontsize=10.5, color="#333")
    ax.set_title("AI 产业链各层毛利率对比:利润高度集中在上游",
                 fontsize=13, fontweight="bold", color="#0B2447", pad=14)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCC")
    ax.spines["bottom"].set_color("#CCC")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    plt.tight_layout()
    path = os.path.join(CHART_DIR, "profit_flow.png")
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return path

# 生成全部图表
img_capex     = chart_hyperscaler_capex()
img_chip      = chart_ai_chip_share()
img_hbm       = chart_hbm_share()
img_anthropic = chart_anthropic_arr()
img_valuation = chart_valuation_quadrant()
img_profit    = chart_profit_flow()

# ========== 页眉页脚 ==========
def on_page(canvas, doc):
    canvas.saveState()
    # 页眉
    canvas.setFont("CJK-Bold", 9)
    canvas.setFillColor(C_BLUE)
    canvas.drawString(2*cm, A4[1] - 1.2*cm, "AI 全产业链深度分析报告")
    canvas.setFont("CJK", 8.5)
    canvas.setFillColor(C_MUTED)
    canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.2*cm, "2026 年 5 月")
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, A4[1] - 1.4*cm, A4[0] - 2*cm, A4[1] - 1.4*cm)

    # 页脚
    canvas.setFont("CJK", 8)
    canvas.setFillColor(C_MUTED)
    canvas.drawString(2*cm, 1*cm, "Kiro AI Research · 研究报告(非投资建议)")
    canvas.drawRightString(A4[0] - 2*cm, 1*cm, f"— {doc.page} —")
    canvas.restoreState()

# ========== 构建文档 ==========
OUT_PDF = "/projects/sandbox/aizhilv/AI_Industry_Chain_Report.pdf"
doc = SimpleDocTemplate(
    OUT_PDF, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=1.6*cm,
    title="AI 全产业链深度分析报告",
    author="Kiro AI Research",
)

story = []

# ---------- 封面 ----------
story.append(Spacer(1, 4*cm))
story.append(P("AI 全产业链", COVER_TITLE))
story.append(P("深度分析报告", COVER_TITLE))
story.append(Spacer(1, 0.8*cm))
story.append(hr(width=6*cm, color=C_INDIGO))
story.append(Spacer(1, 0.6*cm))
story.append(P("从硅到应用:六层产业链、核心壁垒与估值象限", COVER_SUB))
story.append(Spacer(1, 3.5*cm))
story.append(P("—— 数据截至 2026 年 5 月 ——", COVER_META))
story.append(Spacer(1, 0.3*cm))
story.append(P("Kiro AI Research", COVER_META))
story.append(P("基于公开披露财报、IDC / Gartner / Counterpoint / TrendForce 数据整理", COVER_META))
story.append(Spacer(1, 3*cm))
disclaimer = ("<b>免责声明:</b> 本报告为研究性质,不构成任何投资建议。"
              "所有数据来自公开渠道,读者据此操作,风险自担。"
              "市场有风险,决策需谨慎。")
story.append(P(disclaimer, NOTE))
story.append(PageBreak())

# ---------- 一、执行摘要 ----------
story.append(P("一、执行摘要", H1))
story.append(hr())
story.append(Spacer(1, 8))

story.append(P("核心判断", H2))
summary_points = [
    "<b>AI 是本世纪最大的资本开支周期</b>:2026 年北美前六大云厂商 AI 资本开支合计约 7,750 亿美元,"
    "同比 2025 年的 4,100 亿增长约 70%。TrendForce 预计全球前九大 CSP 2026 年合计 8,300 亿美元。",
    "<b>利润分布极不均衡</b>:绝大部分利润集中在<b>上游三强</b>——NVIDIA(GPU)、TSMC(代工)、"
    "ASML(光刻),加上 HBM 三强(SK Hynix / Samsung / Micron),构成 AI 时代不可替代的『卖铲人』。",
    "<b>模型层呈三极格局</b>:Anthropic ARR 从 2024 年末的 10 亿美元飙升至 2026 年 4 月的 300 亿美元,"
    "18 个月 30 倍增长,估值从 615 亿跃至 9,000 亿美元量级。",
    "<b>AI 原生应用出现新巨头</b>:Palantir 市值突破 4,000 亿美元,季度营收增速 85% 创历史新高,"
    "Rule of 40 达 145%,但 PE 超过 200 倍,『卓越基本面 + 极端估值』。",
    "<b>整体估值偏高但非纯粹泡沫</b>:席勒 CAPE 约 38-40 倍(155 年来第二高,仅次 2000 年);"
    "AI 股占 S&amp;P 500 市值约 45%,集中度创新高;但核心公司盈利远超 2000 年互联网泡沫。",
]
for s in summary_points:
    story.append(P("• " + s, BULLET))

story.append(Spacer(1, 10))
story.append(P("一句话结论", H2))
story.append(P(
    "<b>上游硬件『卖铲人』处于结构性低估或合理偏高,模型层与头部 AI 原生应用估值明显透支,"
    "中游云厂商最平衡,下游传统 SaaS 中有估值重估机会。</b>", BODY))

story.append(PageBreak())

# ---------- 二、产业链全景 ----------
story.append(P("二、AI 产业链六层全景", H1))
story.append(hr())
story.append(Spacer(1, 6))
story.append(P(
    "AI 产业链可清晰划分为六个层级,每层都有其核心玩家和壁垒特征。"
    "<b>越往上游(接近硅),壁垒越硬、利润率越高但资本密集</b>;"
    "越往下游(接近用户),边际成本越低但同质化竞争风险越大。", BODY))
story.append(Spacer(1, 8))

# 产业链六层表(列宽适当加大 + 内容精简)
layer_data = [
    ["层级", "代表企业", "核心产品 / 服务", "毛利率", "壁垒类型"],
    ["① 半导体设备", "ASML、应用材料、东京电子、Lam Research", "EUV / High-NA 光刻机、刻蚀设备", "50%+", "技术专利 + 20 年研发积累"],
    ["② 晶圆代工", "TSMC、Samsung Foundry、Intel", "3nm / 2nm 先进制程代工", "66%", "工艺良率 + 产能 + 客户绑定"],
    ["③ 核心元器件", "NVIDIA、AMD、Broadcom、SK Hynix、Samsung、Micron", "GPU、ASIC、HBM、交换机芯片", "70-75%", "架构 + CUDA 生态 + 先进封装"],
    ["④ 云基础设施", "Microsoft Azure、AWS、Google Cloud、Oracle、CoreWeave", "算力租赁、训练 / 推理平台", "30-40%", "规模效应 + 客户粘性 + 能源协议"],
    ["⑤ 大模型", "OpenAI、Anthropic、Google DeepMind、xAI、DeepSeek", "Claude / GPT / Gemini / Grok 等", "-30% ~ 40%(亏损中)", "人才 + 算力 + 数据闭环"],
    ["⑥ AI 应用", "Palantir、ServiceNow、Salesforce、Cursor、Perplexity、Adobe", "垂直 AI 平台、Copilot、智能代理", "60-85%", "场景理解 + 数据网络效应"],
]
# 列宽:总计 17cm
story.append(styled_table(
    layer_data,
    col_widths=[2.2*cm, 3.8*cm, 4.0*cm, 2.3*cm, 4.7*cm],
))
story.append(Spacer(1, 14))

# 毛利率图
story.append(P("利润在产业链上的分布", H2))
story.append(P(
    "毛利率是衡量壁垒强度最直接的指标。越接近硅,毛利率越高,"
    "反过来说明这几层的<b>议价权</b>也最强。", BODY))
story.append(Image(img_profit, width=16*cm, height=7.6*cm))
story.append(Spacer(1, 8))

# 资本开支图
story.append(P("需求侧:超大规模厂商资本开支", H2))
story.append(P(
    "2026 年六大云厂商 AI 资本开支合计约 <b>7,750 亿美元</b>,"
    "其中 <b>约 44%(~3,400 亿)</b> 最终流向 NVIDIA,"
    "另有 15-20% 流向 HBM 厂商、ASML 与 TSMC。", BODY))
story.append(Image(img_capex, width=16*cm, height=8*cm))
story.append(P("数据来源:各公司 2026Q1 财报与指引,Fortune、TrendForce、DCKnowledge 整理", NOTE))

story.append(PageBreak())

# ---------- 三、逐层分析 ----------
story.append(P("三、逐层深度分析:不可替代的核心壁垒", H1))
story.append(hr())

# 3.1 ASML
story.append(P("3.1  第一层 · 半导体设备:ASML 的绝对垄断", H2))
story.append(P("<b>核心玩家:</b> ASML(荷兰)、应用材料(AMAT)、Lam Research、KLA、东京电子(TEL)", BODY))
story.append(P(
    "ASML 是<b>全球唯一能制造 EUV 光刻机的公司</b>,市场份额 100%,"
    "没有竞争对手、没有可替代方案——这是当今科技产业链中最硬的单点垄断。", BODY))
story.append(Spacer(1, 6))

asml_data = [
    ["关键指标", "2026 数据"],
    ["EUV 市场份额", "100%(全球唯一)"],
    ["2026 年营收指引", "€360-400 亿"],
    ["Q1 2026 营收", "€88 亿(同比 +13%)"],
    ["Q1 毛利率", "53%"],
    ["全球 EUV 装机量", "约 200+ 台(截至 2026-04)"],
    ["2026 EUV 出货目标", "60 台;2027 年计划 80 台"],
    ["SK Hynix 单笔订单", "79 亿美元(约 30 台 EUV,交付至 2027)"],
    ["单台 EUV 价格", "约 1.8-2.1 亿美元(High-NA 约 3.8 亿)"],
]
story.append(styled_table(asml_data, col_widths=[5.5*cm, 11.5*cm]))
story.append(Spacer(1, 10))

story.append(P("壁垒分析", H3))
moat_asml = [
    "<b>供应链耦合度极高</b>:单台 EUV 由 10 万+零部件构成,光源来自德国 TRUMPF,光学系统来自蔡司,整个供应链需 20+ 年才能复制。",
    "<b>专利墙</b>:ASML 掌握 EUV 关键专利超 14,000 项,与蔡司形成排他合作。",
    "<b>客户深度绑定</b>:TSMC、Samsung、SK Hynix、Intel 下一代产线规划必须与 ASML 产能对齐。",
    "<b>出口管制反而强化护城河</b>:美国对华 EUV 禁令固化了 ASML 在非中国市场的地位。",
]
for m in moat_asml:
    story.append(P("• " + m, BULLET))
story.append(Spacer(1, 4))
story.append(P(
    "<b>估值判断:合理偏高。</b>前瞻 PE 约 40 倍,1 年涨幅 135%。"
    "长期逻辑坚实(2030 年 €600 亿营收可见度),但短期对 High-NA 量产节奏与中国业务依赖偏高,回调风险存在。", BODY))

story.append(PageBreak())

# 3.2 TSMC
story.append(P("3.2  第二层 · 晶圆代工:TSMC 的制程护城河", H2))
story.append(P("<b>核心玩家:</b> TSMC、Samsung Foundry、Intel Foundry(后两者距第一名仍有 1-2 代差距)", BODY))
story.append(P(
    "先进制程的竞争已经演化为<b>单寡头格局</b>。TSMC 生产了全球 <b>90%+ 的 5nm 以下 AI 芯片</b>,"
    "包括 NVIDIA Blackwell / Vera Rubin、AMD MI355X、Google TPU v7、"
    "AWS Trainium 3、Meta MTIA v3、Apple M5 / A20。", BODY))
story.append(Spacer(1, 6))

tsmc_data = [
    ["关键指标", "2026 数据"],
    ["Q1 2026 营收", "$359 亿(同比 +40.6%)"],
    ["Q1 毛利率", "66.2%(创新高,上调长期目标)"],
    ["HPC 营收占比", "61%(2024Q1 仅 46%)"],
    ["3nm 占晶圆营收", "25%"],
    ["≤7nm 先进工艺占比", "74%"],
    ["2nm 产能", "2026 全年订单全部售罄"],
    ["2026 资本开支", "$420-460 亿"],
    ["Q2 营收指引", "$390-402 亿(远超分析师 $381 亿共识)"],
]
story.append(styled_table(tsmc_data, col_widths=[5.5*cm, 11.5*cm]))
story.append(Spacer(1, 10))

story.append(P("壁垒分析", H3))
moat_tsmc = [
    "<b>工艺良率优势</b>:2nm 首批量产良率据报道已达 60%+,Samsung 2nm 约 30-40%,Intel 18A 仍在 ramp。",
    "<b>产能调度能力</b>:Apple 提前 2-3 年绑定最先进节点首批产能,形成『最好的客户养最好的工艺』正反馈。",
    "<b>先进封装 CoWoS 瓶颈</b>:NVIDIA B200 必须用 TSMC 的 CoWoS-L,是 NVIDIA 出货节奏的实际决定因素。",
    "<b>地缘风险反而强化定价权</b>:面对台海地缘,客户越担心越提前锁产能,推动长期供货协议。",
]
for m in moat_tsmc:
    story.append(P("• " + m, BULLET))
story.append(Spacer(1, 4))
story.append(P(
    "<b>估值判断:低估。</b>PE 仅约 28 倍,营收增速 35%+,是少数 FCF 快速增长的重资本公司。"
    "对比 NVIDIA 享受的估值溢价,TSMC 作为『NVIDIA 的供应商之母』估值显著落后。", BODY))

story.append(PageBreak())

# 3.3 NVIDIA + HBM
story.append(P("3.3  第三层 · 核心元器件:NVIDIA + HBM 三强", H2))

story.append(P("(A)NVIDIA:CUDA 生态的不可替代性", H3))
nv_data = [
    ["关键指标", "2026 数据"],
    ["FY2026 全年营收", "约 $1,940 亿(同比 +73.2%)"],
    ["FY26 Q4 数据中心营收", "$62.3 亿(同比 +75%)"],
    ["数据中心占总营收", "91.5%"],
    ["AI 加速器市场份额(IDC)", "约 81%"],
    ["Blackwell + Vera Rubin 2026-2027 预期销售", "约 $10,000 亿"],
    ["市值(2026-05)", "约 $4.5 万亿"],
    ["前瞻 PE", "约 35 倍"],
]
story.append(styled_table(nv_data, col_widths=[6.5*cm, 10.5*cm]))
story.append(Spacer(1, 10))

story.append(Image(img_chip, width=13*cm, height=9*cm))
story.append(Spacer(1, 8))

story.append(P("NVIDIA 护城河三要素", H3))
moat_nv = [
    "<b>CUDA 软件栈</b>:20 年积累,500 万开发者,1,000+ 专业库(cuDNN、TensorRT、NCCL)。即便 AMD ROCm、Intel oneAPI 追赶,迁移成本依然巨大。",
    "<b>NVLink / NVSwitch 高速互联</b>:GB200 NVL72 整机柜 72 颗 GPU 共享 30 TB 显存,竞争对手短期难以复刻的系统级优势。",
    "<b>快速迭代节奏</b>:H100 → B200 → GB300 → Vera Rubin → Rubin Ultra 每年一代,将对手永远甩在上一代。",
]
for m in moat_nv:
    story.append(P("• " + m, BULLET))
story.append(Spacer(1, 4))
story.append(P(
    "<b>潜在威胁:</b>超大规模自研 ASIC(Google TPU v7、AWS Trainium 3、Meta MTIA v3、Microsoft Maia)"
    "正在蚕食约 10% 市场,2027-2028 年可能压缩至 70-75%。", BODY))
story.append(P(
    "<b>估值判断:合理。</b>前瞻 PE 35 倍对应 60%+ 营收增速、70%+ 毛利率,"
    "PEG 约 0.6-0.7,远低于 2000 年思科泡沫时的 100+ PE。", BODY))

story.append(PageBreak())

story.append(P("(B)HBM 三强:SK Hynix、Samsung、Micron", H3))
story.append(P(
    "HBM(High Bandwidth Memory)是 AI 训练芯片最稀缺的部件——一颗 B200 需要 8 颗 HBM3E,"
    "单颗芯片 HBM 成本约 $3,500,占 BOM 近 50%。", BODY))
story.append(Spacer(1, 6))
story.append(Image(img_hbm, width=13*cm, height=9*cm))
story.append(Spacer(1, 10))

hbm_data = [
    ["公司", "2026 数据点", "核心优势"],
    ["SK Hynix", "HBM 份额 57%;2025 全年经营利润 47.2 万亿韩元,首次超越 Samsung", "HBM3E 先发 + NVIDIA 独家绑定"],
    ["Samsung", "HBM 份额 22%;HBM4 已获客户正面评价", "规模 + 垂直整合(自有代工)"],
    ["Micron", "HBM 份额 21%;市值突破 $7,000 亿(YTD +124%);FY Q3 指引营收 $335 亿、毛利率 81%", "HBM3E 良率反超 Samsung"],
]
story.append(styled_table(hbm_data, col_widths=[2.5*cm, 9.0*cm, 5.5*cm]))
story.append(Spacer(1, 10))
story.append(P(
    "<b>估值判断:Micron 和 SK Hynix 结构性低估正在被快速修正。</b>"
    "Micron 前瞻 PE 仅 18 倍,但毛利率从 2023 年的 -30% 跃至 75%,典型内存周期反转。"
    "SK Hynix PE 约 10 倍,估值比 Micron 更便宜,但受韩国股市整体折价影响。", BODY))

story.append(PageBreak())

# 3.4 云基础设施
story.append(P("3.4  第四层 · 云基础设施:三超多强", H2))
story.append(Spacer(1, 6))

cloud_data = [
    ["公司", "2026 资本开支", "核心 AI 资产", "估值"],
    ["Microsoft", "$1,900 亿\n(+130% YoY)", "Azure + OpenAI 独家算力合作",
     "PE 34x\n市值 $4.2T"],
    ["Alphabet", "$1,800-1,900 亿", "TPU v7 + Gemini + Google Cloud(积压 $4,600 亿)",
     "PE 26x\n市值 $2.7T"],
    ["Amazon", "$2,000 亿", "AWS + Trainium 3(自研芯片 ARR $200 亿)",
     "PE 38x\n市值 $2.3T"],
    ["Meta", "$1,250-1,450 亿", "MTIA 自研芯片 + 开源 Llama 4/5",
     "PE 25x\n市值 $1.7T"],
    ["Oracle", "$400 亿", "OCI(加速增长,押注 AI 企业级)",
     "PE 32x\n市值 $900B"],
    ["CoreWeave", "$250 亿", "纯 AI 算力租赁(OpenAI / Microsoft 大客户)",
     "PS 8x\n市值 $85B"],
]
story.append(styled_table(cloud_data, col_widths=[2.5*cm, 3.3*cm, 7.5*cm, 3.7*cm]))
story.append(Spacer(1, 10))

story.append(P("壁垒分析:规模、网络、能源", H3))
moat_cloud = [
    "<b>电力 &amp; 土地前置协议</b>:2026 年数据中心缺的已经不是 GPU 而是<b>电</b>。Microsoft 重启三哩岛核电、Amazon 签 Talen 核电 PPA,都是规模优势的体现。",
    "<b>客户绑定与迁移成本</b>:企业 AI 工作负载上云后数据和管道与平台深度耦合,迁移成本极高。",
    "<b>自研芯片降低对 NVIDIA 的依赖</b>:Google TPU v7 已到第 7 代,AWS Trainium 3 据报道 TCO 比 H100 低 40%。",
    "<b>模型公司独家合作</b>:MSFT × OpenAI、Amazon/Google × Anthropic、Google × DeepMind 内循环。",
]
for m in moat_cloud:
    story.append(P("• " + m, BULLET))
story.append(Spacer(1, 4))
story.append(P(
    "<b>估值判断:Alphabet 低估、Meta 合理、Microsoft/Amazon 合理偏高、Oracle/CoreWeave 高估。</b>"
    "Alphabet 同时具备 TPU、Gemini、Waymo、YouTube 四张牌,但 PE 只有 26 倍,是头部大厂中最具性价比的一家。", BODY))

story.append(PageBreak())

# 3.5 大模型
story.append(P("3.5  第五层 · 大模型:三极格局", H2))
story.append(Image(img_anthropic, width=16*cm, height=8*cm))
story.append(Spacer(1, 10))

model_data = [
    ["公司", "旗舰模型", "最新估值", "ARR\n(2026-04)", "营收来源"],
    ["OpenAI", "GPT-5.5", "约 $8,800 亿\n(二级市场)", "约 $250 亿", "ChatGPT 订阅 + API + 企业"],
    ["Anthropic", "Claude Opus 4.7", "在谈 $9,000 亿融资", "$300 亿", "Claude Code + 企业 API"],
    ["Google DeepMind", "Gemini 3.1 Pro", "内嵌 Alphabet", "$100-150 亿(估)", "Google Cloud + 消费产品"],
    ["xAI", "Grok 4.20", "约 $2,000 亿", "约 $30 亿", "X 平台 + API"],
    ["DeepSeek", "DeepSeek V4", "未披露(民营)", "—", "开源 + API"],
]
story.append(styled_table(model_data, col_widths=[3.0*cm, 3.0*cm, 3.2*cm, 2.3*cm, 5.5*cm]))
story.append(Spacer(1, 10))

story.append(P("壁垒:算力 × 人才 × 数据反馈闭环", H3))
moat_model = [
    "<b>算力规模门槛</b>:训练前沿模型需要 10 万+ GPU 集群 + 100 TWh 级电力,全球只有 5-7 家能做到。",
    "<b>顶尖人才密度</b>:全球能训练 1T 参数以上模型的研究员不超过 2,000 人,主要聚集在 5 家公司。",
    "<b>RLHF 数据闭环</b>:Claude Code 每天处理数十亿行代码反馈、ChatGPT 数十亿对话,后入者无法短期获得的飞轮。",
    "<b>安全与合规壁垒</b>:企业采购 LLM 需要 SOC2、ISO 42001、HIPAA 等认证,新玩家进入周期长达 2 年+。",
]
for m in moat_model:
    story.append(P("• " + m, BULLET))
story.append(Spacer(1, 4))
story.append(P(
    "<b>估值判断:极端高估但逻辑可自洽。</b>"
    "Anthropic 估值/ARR 约 30 倍,OpenAI 约 35 倍,与 SaaS 同行对比高 3-5 倍,"
    "但考虑到 ARR 增速 3x/年 + 模型能力仍在快速跃迁,是『按 2028 年估值看现在合理』的典型定价。"
    "<b>一旦增速收敛到 50% 以下将面临大幅修正。</b>", BODY))

story.append(PageBreak())

# 3.6 应用层
story.append(P("3.6  第六层 · AI 应用:正在分化的下游", H2))
story.append(Spacer(1, 6))

app_data = [
    ["公司", "核心产品", "2026 数据", "估值"],
    ["Palantir", "AIP + Foundry\n(企业 / 政府)", "Q1 营收 $16.3 亿(+85% YoY);Rule of 40 = 145%",
     "市值 $400B\nPS 70x,PE 230x"],
    ["ServiceNow", "Now Assist\n(企业工作流 AI)", "2026 ARR $150 亿(+22%)",
     "PE 50x\n市值 $300B"],
    ["Salesforce", "Agentforce / Einstein", "AI ARR 约 $20 亿,增速快但基数大",
     "PE 28x\n市值 $330B"],
    ["Adobe", "Firefly + GenAI 套件", "Creative Cloud AI 收入渗透率 40%",
     "PE 23x\n市值 $240B"],
    ["Cursor\n(Anysphere)", "AI 编辑器\n(Claude + GPT)", "ARR 超 $5 亿,用户增长爆炸",
     "最新估值 $100 亿"],
    ["Perplexity", "AI 搜索", "ARR 约 $3 亿",
     "估值 $180 亿"],
    ["Duolingo", "AI 语言学习", "Max 订阅渗透率 15%",
     "PE 85x\n市值 $180B"],
]
story.append(styled_table(app_data, col_widths=[2.8*cm, 3.8*cm, 6.7*cm, 3.7*cm]))
story.append(Spacer(1, 10))

story.append(P("壁垒:场景 × 数据 × 工作流绑定", H3))
moat_app = [
    "<b>垂直数据</b>:Palantir 的政府/国防数据、ServiceNow 的 IT 工单数据、Salesforce 的 CRM 数据,都是大模型无法替代的『原材料』。",
    "<b>工作流嵌入</b>:AI 功能越嵌入既有工作流(报表、合规、客服),替换成本越高。",
    "<b>分发渠道</b>:消费类应用(Perplexity、Duolingo、Cursor),用户心智与默认选择权是核心。",
]
for m in moat_app:
    story.append(P("• " + m, BULLET))
story.append(Spacer(1, 4))
story.append(P(
    "<b>估值判断:严重两极。</b>"
    "Palantir / Duolingo / Cursor 等『AI 纯正标的』被机构抢筹,估值已透支 2-3 年增长;"
    "Adobe、Salesforce 这类『被低估的 AI 受益者』PE 仅 20-28 倍,反而是更稳健的 AI 应用曝险方式。", BODY))

story.append(PageBreak())

# ---------- 四、估值象限 ----------
story.append(P("四、估值象限:一张图看清高估与低估", H1))
story.append(hr())
story.append(Spacer(1, 6))
story.append(P(
    "横轴为前瞻 PE,纵轴为 2026 年营收增速,气泡面积代表市值规模。"
    "<b>右上</b>(高增长 + 高估值)多为模型层与 AI 原生应用;"
    "<b>左下</b>(低估值 + 中等增长)反而是被忽视的大型云厂商。", BODY))
story.append(Spacer(1, 8))

story.append(Image(img_valuation, width=16.5*cm, height=10.7*cm))
story.append(Spacer(1, 10))

quadrant_data = [
    ["象限", "特征", "代表公司", "投资含义"],
    ["① 右上:高增长高 PE", "增速 &gt; 25%\nPE &gt; 30", "Palantir、AMD、Broadcom、Micron、Anthropic*",
     "赔率巨大,但对增长放缓零容忍"],
    ["② 左上:高增长低 PE", "增速 &gt; 25%\nPE &lt; 30", "TSMC、SK Hynix*、NVIDIA(边缘)",
     "<b>最优性价比区域</b>"],
    ["③ 右下:低增长高 PE", "增速 &lt; 25%\nPE &gt; 30", "Microsoft、Amazon、ASML",
     "定价对『护城河 + 确定性』支付溢价"],
    ["④ 左下:低增长低 PE", "增速 &lt; 25%\nPE &lt; 30", "Alphabet、Meta、Adobe",
     "<b>被市场忽视的稳健 AI 曝险</b>"],
]
story.append(styled_table(quadrant_data, col_widths=[3.3*cm, 2.5*cm, 5.8*cm, 5.4*cm]))
story.append(Spacer(1, 6))
story.append(P("* 标记为未上市或非公开市场估值估算。", NOTE))

story.append(PageBreak())

# ---------- 五、风险与结论 ----------
story.append(P("五、系统性风险与结论", H1))
story.append(hr())

story.append(P("5.1  需要密切监控的五个风险", H2))
risks = [
    "<b>① 估值风险:席勒 CAPE 约 38-40 倍</b>,仅次于 2000 年(44);S&amp;P 500 顶部 10 只股票占比超过 2000 年峰值 50%;AI 股占 S&amp;P 500 市值约 45%,与 AI 相关的信用债规模约 1.4 万亿美元。",
    "<b>② 资本开支见顶风险</b>:云厂商 2026 年合计 7,000-7,750 亿美元,2027 年指引预期继续上行至约 9,000 亿。若任何一家头部云厂商明确放缓指引,NVIDIA / TSMC / ASML 短期都将承压。",
    "<b>③ 模型商品化</b>:DeepSeek、Qwen、Llama 的开源路线已将推理成本压低 90%+;若基础模型最终『水电化』,OpenAI / Anthropic 当前估值逻辑会被重估。",
    "<b>④ 能源瓶颈</b>:2027 年北美数据中心用电预计达 550 TWh,相当于英国全年用电 2 倍;电力和核电供给不足可能成为整个资本开支链条的硬约束。",
    "<b>⑤ 地缘冲击</b>:台海、中东、AI 芯片管制、欧盟 AI Act 合规任何一项大规模升级,都将冲击全链条。",
]
for r in risks:
    story.append(P("• " + r, BULLET))
story.append(Spacer(1, 10))

story.append(P("5.2  最终结论:四梯队配置思路", H2))
concl_data = [
    ["梯队", "代表公司", "建议仓位角色", "估值状态"],
    ["<b>压舱石</b>\n硬件瓶颈", "TSMC、ASML、SK Hynix", "核心长期底仓", "低估至合理"],
    ["<b>进攻手</b>\nAI 算力龙头", "NVIDIA、Broadcom、Micron", "Beta 仓位", "合理偏高"],
    ["<b>现金流锚</b>\n大云厂商", "Alphabet、Microsoft、Meta", "平衡仓位", "Alphabet 低估,其余合理"],
    ["<b>赔率博弈</b>\n模型 + 应用", "Anthropic*、OpenAI*、Palantir", "小仓位 + 严格止损", "高估但存在拐点"],
]
story.append(styled_table(concl_data, col_widths=[3.2*cm, 4.8*cm, 4.0*cm, 5.0*cm]))
story.append(Spacer(1, 12))

story.append(P("一句话总结", H2))
story.append(P(
    "<b>AI 是真的,泡沫也是真的。</b>"
    "真正不可替代的环节少于市场以为的数量——"
    "<b>ASML、TSMC、NVIDIA、SK Hynix 四家公司定义了整个 AI 时代的物理上限</b>。"
    "往下走,云厂商有强护城河但差异化不足,模型公司商业模式仍在证明中,"
    "应用层会有大赢家但现在出手的胜率不高。", BODY))
story.append(Spacer(1, 6))
story.append(P(
    "<b>一句话配置建议:</b>"
    "在硬件瓶颈公司买确定性,在被低估的云厂商(Alphabet)买安全边际,"
    "在模型层用小仓位买期权,在应用层等待『基本面兑现 + 估值回落』的双击时点。", BODY))

story.append(Spacer(1, 16))
story.append(hr())
story.append(Spacer(1, 6))
story.append(P(
    "<b>数据来源:</b> NVIDIA / TSMC / ASML / Micron / Palantir / Anthropic 官方披露;"
    "Counterpoint、TrendForce、IDC、Gartner、Morgan Stanley、Fortune、CNBC、The Motley Fool、"
    "Tom's Hardware、VanEck、TechCrunch、Forbes、Reuters、Yahoo Finance、Economic Times 等公开资料。"
    "数据截至 2026-05-11。", NOTE))
story.append(P(
    "<b>版权合规:</b> 本报告引用的所有外部数据均为事实性引用,并已做必要改写以符合合理使用原则。", NOTE))
story.append(P(
    "<b>免责声明:</b> 本报告为研究性质,不构成任何投资建议。市场有风险,决策需谨慎。", NOTE))

# ========== 生成 ==========
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT_PDF}")
print(f"Size: {os.path.getsize(OUT_PDF)/1024:.1f} KB")
