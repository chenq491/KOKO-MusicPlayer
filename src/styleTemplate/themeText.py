"""文字语义角色。

以前每加一个标签，都要在父容器的 `update_style` 里补一句
`label.set_color(theme_manager.current.xxx)`，漏掉一个标签在暗色模式下就会变成
黑底黑字。这里把「这段文字是什么角色」单独抽出来，标签自己按角色跟随主题，
父容器只需要关心布局和边框。
"""

from enum import Enum


class TextRole(str, Enum):
    """文字角色 → ThemePalette 字段名"""

    STRONG = "strong"  # 标题、正文强调
    BODY = "body"  # 普通正文
    MUTED = "muted"  # 次要说明：表头、时长、数值
    ACCENT = "accent"  # 主题色强调（当前播放曲目等）
    ACCENT_SOFT = "accent_soft"  # 主题色的弱化版
    ON_ACCENT = "on_accent"  # 铺在主题色底上的文字


_ROLE_ATTRS = {
    TextRole.STRONG: "text_strong",
    TextRole.BODY: "text_body",
    TextRole.MUTED: "text_muted",
    TextRole.ACCENT: "text_accent",
    TextRole.ACCENT_SOFT: "text_accent_soft",
    TextRole.ON_ACCENT: "on_accent",
}


def resolve_text_color(theme, role) -> str:
    """把文字角色翻译成当前主题下的颜色值"""
    return getattr(theme, _ROLE_ATTRS[TextRole(role)])
