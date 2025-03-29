from .schema import DocumentColors, RenderingMode, Appearance


def get_document_colors(
    rendering_mode: RenderingMode,
    appearance: Appearance,
) -> DocumentColors:
    match appearance:
        case Appearance.LIGHT:
            return light_colors(rendering_mode)
        case Appearance.DARK:
            return dark_colors(rendering_mode)
        case _:
            raise ValueError(f"Invalid appearance: {appearance}")


def light_colors(rendering_mode: RenderingMode) -> DocumentColors:
    return DocumentColors(
        background="255, 255, 255",
        text="0, 0, 0",
        header_background="51, 51, 51",
        header_text="255, 255, 255",
        hero_background="240, 240, 240",
        hero_text="0, 0, 0",
        link="51, 102, 255" if rendering_mode == RenderingMode.DIGITAL else "0, 0, 0",
        aside_background="245, 245, 245",
        aside_text="0, 0, 0",
        aside_border="102, 102, 102",
        table_border="240, 240, 240",
        code_border="204, 204, 204",
        code_background="247, 247, 247",
    )


def dark_colors(rendering_mode: RenderingMode) -> DocumentColors:
    return DocumentColors(
        background="0, 0, 0",
        text="255, 255, 255",
        header_background="51, 51, 51",
        header_text="255, 255, 255",
        hero_background="30, 30, 30",
        hero_text="255, 255, 255",
    )
