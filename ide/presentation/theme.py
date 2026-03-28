"""
N4-IDE Theme and Styling System.

Centralized color palette and styling constants following Figma design system.
All components reference these constants for consistency.

Color Palette:
- Primary: #005FB8 (Blue)
- Secondary: Grays and neutrals
- Success: #7EDF8C (Green)
- Error: #DA3633 (Red)
- Warning: #F9AB00 (Amber)

Typography:
- Font Family: "Open Sans" (main), "Roboto Mono" (code)
- Sizes: 12px (small), 14px (body), 16px (label), 28px (title)

Spacing (multiples of 4px):
- 4px: xs
- 8px: sm
- 12px: md
- 16px: lg
- 20px: xl
- 32px: 2xl
"""


# Color constants (direct strings to avoid Enum.value property conflicts)
class Color:
    """Color constants from N4-IDE design system."""

    PRIMARY = "#005FB8"
    PRIMARY_DARK = "#003A70"
    PRIMARY_LIGHT = "#2D7AC2"

    SURFACE = "white"
    SURFACE_ALT = "rgba(255, 255, 255, 0.70)"
    BACKGROUND = "#F3F3F3"
    BACKGROUND_HOVER = "rgba(0, 0, 0, 0.04)"
    BACKGROUND_ACTIVE = "rgba(0, 0, 0, 0.08)"

    TEXT_PRIMARY = "rgba(0, 0, 0, 0.90)"
    TEXT_SECONDARY = "rgba(0, 0, 0, 0.61)"
    TEXT_TERTIARY = "rgba(0, 0, 0, 0.40)"
    TEXT_DISABLED = "#CCCCCC"

    BORDER_DEFAULT = "rgba(0, 0, 0, 0.06)"
    BORDER_HOVER = "rgba(0, 0, 0, 0.12)"
    BORDER_FOCUS = "#005FB8"

    SUCCESS = "#7EDF8C"
    ERROR = "#DA3633"
    ERROR_DARK = "#B71C1C"
    WARNING = "#F9AB00"

    CODE_KEYWORD = "#439C37"
    CODE_STRING = "#3C6382"
    CODE_NUMBER = "#D33905"


class FontFamily:
    """Font families from design system."""

    PRIMARY = '"Open Sans"'
    MONO = '"Roboto Mono"'


class FontSize:
    """Font sizes from design system (in pixels)."""

    TINY = "12px"
    SMALL = "14px"
    BASE = "14px"
    BODY = "14px"
    LABEL = "16px"
    TITLE = "28px"
    HEADING = "32px"


class FontWeight:
    """Font weights from design system."""

    THIN = "300"
    LIGHT = "400"
    NORMAL = "400"
    MEDIUM = "500"
    SEMI_BOLD = "600"
    BOLD = "700"


class Spacing:
    """Spacing constants (multiples of 4px grid)."""

    XS = "4px"
    SM = "8px"
    MD = "12px"
    LG = "16px"
    XL = "20px"
    XXL = "32px"


class BorderRadius:
    """Border radius values."""

    SMALL = "3px"
    MEDIUM = "4px"
    LARGE = "7px"
    FULL = "999px"


class Shadow:
    """Box shadow presets."""

    NONE = "none"
    SMALL = "0px 2px 4px rgba(0, 0, 0, 0.04)"
    MEDIUM = "0px 2px 21px rgba(0, 0, 0, 0.15), 0px 32px 64px rgba(0, 0, 0, 0.19)"
    LARGE = "0px 8px 16px rgba(0, 0, 0, 0.15)"


def get_stylesheet_string(name: str) -> str:
    """
    Get CSS stylesheet string for a named component style.

    Args:
        name: Component name (e.g., 'button', 'combobox', 'section')

    Returns:
        CSS stylesheet string for Qt
    """
    styles = {
        "button_accent": f"""
            QPushButton {{
                padding: {Spacing.SM} {Spacing.MD} 7px {Spacing.MD};
                background-color: {Color.PRIMARY};
                color: white;
                border: 1px solid {Color.PRIMARY_LIGHT};
                border-radius: {BorderRadius.MEDIUM};
                font-family: {FontFamily.PRIMARY};
                font-size: {FontSize.SMALL};
                font-weight: {FontWeight.NORMAL};
            }}
            QPushButton:hover {{
                background-color: {Color.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: #002D52;
            }}
            QPushButton:disabled {{
                background-color: {Color.TEXT_DISABLED};
                color: #666666;
                border: 1px solid #EEEEEE;
            }}
        """,
        "button_secondary": f"""
            QPushButton {{
                padding: {Spacing.SM} {Spacing.MD} 7px {Spacing.MD};
                background-color: {Color.SURFACE_ALT};
                color: {Color.TEXT_PRIMARY};
                border: 1px solid black;
                border-radius: {BorderRadius.MEDIUM};
                font-family: {FontFamily.PRIMARY};
                font-size: {FontSize.SMALL};
                font-weight: {FontWeight.NORMAL};
            }}
            QPushButton:hover {{
                background-color: {Color.SURFACE};
                border: 1px solid {Color.PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 95, 184, 0.1);
            }}
            QPushButton:disabled {{
                background-color: #F5F5F5;
                color: {Color.TEXT_DISABLED};
                border: 1px solid #EEEEEE;
            }}
        """,
        "combobox": f"""
            QComboBox {{
                padding: {Spacing.SM} {Spacing.SM};
                background-color: {Color.SURFACE_ALT};
                border: 1px {Color.BORDER_DEFAULT} solid;
                border-radius: {BorderRadius.SMALL};
                color: {Color.TEXT_PRIMARY};
                font-family: {FontFamily.PRIMARY};
                font-size: {FontSize.SMALL};
            }}
            QComboBox:hover {{
                background-color: {Color.SURFACE};
                border: 1px solid {Color.PRIMARY};
            }}
            QComboBox:focus {{
                border: 2px solid {Color.PRIMARY};
                padding: 3px 7px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 12px;
                margin-right: {Spacing.SM};
            }}
            QAbstractItemView {{
                background-color: {Color.SURFACE};
                border: 1px solid {Color.BORDER_DEFAULT};
                border-radius: {BorderRadius.SMALL};
                selection-background-color: {Color.PRIMARY};
                color: {Color.TEXT_PRIMARY};
            }}
        """,
        "textbox": f"""
            QLineEdit {{
                padding: {Spacing.SM} {Spacing.SM};
                background-color: {Color.SURFACE};
                border: 1px solid {Color.BORDER_DEFAULT};
                border-radius: {BorderRadius.SMALL};
                color: {Color.TEXT_PRIMARY};
                font-family: {FontFamily.PRIMARY};
                font-size: {FontSize.SMALL};
            }}
            QLineEdit:hover {{
                border: 1px solid {Color.BORDER_HOVER};
            }}
            QLineEdit:focus {{
                border: 2px solid {Color.PRIMARY};
                padding: 3px 7px;
            }}
            QLineEdit::placeholder {{
                color: {Color.TEXT_TERTIARY};
            }}
        """,
        "section": f"""
            Section {{
                background-color: {Color.SURFACE_ALT};
                border: 1px solid {Color.BORDER_DEFAULT};
                border-radius: {BorderRadius.LARGE};
            }}
        """,
    }
    return styles.get(name, "")


def create_button_stylesheet(
    bg_color: str = Color.PRIMARY,
    text_color: str = "white",
    hover_bg: str = Color.PRIMARY_DARK,
) -> str:
    """
    Create custom button stylesheet.

    Args:
        bg_color: Background color
        text_color: Text color
        hover_bg: Hover background color

    Returns:
        CSS stylesheet string
    """
    return f"""
        QPushButton {{
            padding: {Spacing.SM} {Spacing.MD} 7px {Spacing.MD};
            background-color: {bg_color};
            color: {text_color};
            border: 1px solid {hover_bg};
            border-radius: {BorderRadius.MEDIUM};
            font-family: {FontFamily.PRIMARY};
            font-size: {FontSize.SMALL};
            font-weight: {FontWeight.NORMAL};
        }}
        QPushButton:hover {{
            background-color: {hover_bg};
        }}
        QPushButton:pressed {{
            opacity: 0.8;
        }}
    """


def create_titled_section_stylesheet(title_color: str = Color.TEXT_PRIMARY) -> str:
    """
    Create stylesheet for section with title.

    Args:
        title_color: Title text color

    Returns:
        CSS stylesheet string
    """
    return f"""
        QLabel {{
            color: {title_color};
            font-family: {FontFamily.PRIMARY};
            font-size: {FontSize.TITLE};
            font-weight: {FontWeight.SEMI_BOLD};
            margin-bottom: {Spacing.MD};
        }}
    """
