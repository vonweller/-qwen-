"""
简化的主窗口样式设置
"""

def setup_simple_style(main_window):
    """设置简化样式"""
    from src.ui.main_window_styles import MAIN_WINDOW_STYLE
    main_window.setStyleSheet(MAIN_WINDOW_STYLE)