"""Mizuki 风格色板。

参考站点 https://mizuki.mysqil.com/ 的 theme/variables.css：
亮色与暗色都不是写死一堆十六进制，而是由同一个 hue 通过 OKLCH 计算出来，
再映射到「页面底色 / 卡片 / 主色 / 软按钮 / 文字 / 分割线」这些语义 token 上。

Qt 的样式表和 QColor 都不认识 oklch()，所以这里在 Python 侧做一次
OKLCH -> OKLab -> 线性 sRGB -> gamma 编码的转换，最终输出 #RRGGBB。
"""

import math
from dataclasses import dataclass


def _gamma_encode(channel: float) -> float:
    if channel <= 0.0031308:
        return 12.92 * channel
    return 1.055 * channel ** (1 / 2.4) - 0.055


def _oklab_to_linear_srgb(lightness: float, a: float, b: float):
    """OKLab -> 线性 sRGB（Björn Ottosson 的矩阵）"""
    l_ = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_ = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_ = lightness - 0.0894841775 * a - 1.2914855480 * b

    l = l_**3
    m = m_**3
    s = s_**3

    red = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    green = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    blue = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return red, green, blue


def oklch(lightness: float, chroma: float, hue: float) -> str:
    """oklch(L C H) -> "#RRGGBB"（超出 sRGB 色域的分量会被裁剪）"""
    hue_rad = math.radians(hue)
    a = chroma * math.cos(hue_rad)
    b = chroma * math.sin(hue_rad)

    channels = []
    for linear in _oklab_to_linear_srgb(lightness, a, b):
        channel = _gamma_encode(linear)
        channel = min(1.0, max(0.0, channel))
        channels.append(round(channel * 255))

    return "#{:02x}{:02x}{:02x}".format(*channels)


def _alpha(hex_color: str, alpha: float) -> str:
    """给颜色加透明度，返回 Qt 认识的 #AARRGGBB"""
    value = round(min(1.0, max(0.0, alpha)) * 255)
    return f"#{value:02x}{hex_color.lstrip('#')}"


@dataclass(frozen=True)
class ThemePalette:
    """一套语义化颜色 token（所有界面都只依赖这里的名字）"""

    page_bg: str = ""  # 窗口底色
    surface: str = ""  # 内容卡片 / 歌曲列表的底色
    surface_hover: str = ""  # 列表行悬停
    surface_selected: str = ""  # 列表行选中
    card_bg: str = ""  # 浮动面板（播放列表）
    card_hover: str = ""
    accent: str = ""  # 主色
    accent_hover: str = ""
    accent_active: str = ""
    on_accent: str = ""  # 叠在主色上的文字 / 图标
    text_accent: str = ""  # 主色文字（小字号时用，保证对比度）
    text_accent_soft: str = ""
    text_strong: str = ""  # 标题、正文重点
    text_body: str = ""  # 普通正文
    text_muted: str = ""  # 次要信息
    button_bg: str = ""  # 软按钮
    button_hover: str = ""
    button_pressed: str = ""
    input_bg: str = ""
    border: str = ""  # 输入框 / 细边框
    divider: str = ""  # 区块之间的分割线
    track: str = ""  # 滑块滑槽
    scrollbar: str = ""  # 滚动条滑块
    scrollbar_hover: str = ""
    shadow: str = ""  # 卡片阴影


def build_palette(mode, hue: float) -> ThemePalette:
    """按 Mizuki 的变量表生成一套色板。mode 使用 ThemeMode（True 为暗色）"""
    if not mode:
        # —— 亮色 ——（对应站点 :root，hue=240 时主色 #37a8ec）
        return ThemePalette(
            page_bg=oklch(0.95, 0.01, hue),
            surface="#ffffff",
            surface_hover=oklch(0.95, 0.025, hue),
            surface_selected=oklch(0.90, 0.05, hue),
            card_bg="#ffffff",
            card_hover=oklch(0.98, 0.005, hue),
            accent=oklch(0.70, 0.14, hue),
            accent_hover=oklch(0.64, 0.15, hue),
            accent_active=oklch(0.58, 0.15, hue),
            on_accent="#ffffff",
            text_accent=oklch(0.55, 0.12, hue),
            text_accent_soft=oklch(0.64, 0.10, hue),
            text_strong=oklch(0.25, 0.02, hue),
            text_body=oklch(0.40, 0.03, hue),
            text_muted=oklch(0.58, 0.03, hue),
            button_bg=oklch(0.95, 0.025, hue),
            button_hover=oklch(0.90, 0.05, hue),
            button_pressed=oklch(0.85, 0.08, hue),
            input_bg="#ffffff",
            border=_alpha("#000000", 0.10),
            divider=_alpha("#000000", 0.08),
            track=oklch(0.93, 0.02, hue),
            scrollbar=oklch(0.86, 0.03, hue),
            scrollbar_hover=oklch(0.74, 0.05, hue),
            shadow=_alpha("#000000", 0.10),
        )

    # —— 暗色 ——（对应站点 .dark）
    return ThemePalette(
        page_bg=oklch(0.16, 0.014, hue),
        surface=oklch(0.23, 0.015, hue),
        surface_hover=oklch(0.28, 0.022, hue),
        surface_selected=oklch(0.33, 0.04, hue),
        card_bg=oklch(0.23, 0.015, hue),
        card_hover=oklch(0.28, 0.022, hue),
        accent=oklch(0.75, 0.14, hue),
        accent_hover=oklch(0.80, 0.13, hue),
        accent_active=oklch(0.70, 0.14, hue),
        on_accent=oklch(0.16, 0.02, hue),
        text_accent=oklch(0.75, 0.10, hue),
        text_accent_soft=oklch(0.68, 0.08, hue),
        text_strong=oklch(0.93, 0.01, hue),
        text_body=oklch(0.80, 0.015, hue),
        text_muted=oklch(0.66, 0.02, hue),
        button_bg=oklch(0.33, 0.035, hue),
        button_hover=oklch(0.38, 0.04, hue),
        button_pressed=oklch(0.43, 0.045, hue),
        input_bg=oklch(0.20, 0.015, hue),
        border=_alpha("#ffffff", 0.10),
        divider=_alpha("#ffffff", 0.08),
        track=oklch(0.30, 0.02, hue),
        scrollbar=oklch(0.42, 0.03, hue),
        scrollbar_hover=oklch(0.55, 0.05, hue),
        shadow=_alpha("#000000", 0.35),
    )
