"""Checks that the severity and limit colours can be told apart with common colour-vision deficiencies

Colours are compared after simulating protanopia, deuteranopia and tritanopia (Machado, Oliveira and Fernandes, 2009,
full severity) as CIE76 colour differences in CIELAB, and each text colour's contrast with the background is checked
against the WCAG 2 AA ratio for normal text.
"""
import itertools
import math

import pytest

pytest.importorskip("textual")

from fprime_console_gds.app import LIMIT_MARKS, LIMIT_STYLES, SEVERITY_STYLES  # noqa: E402
from fprime_console_gds.model import SEVERITY_ORDER  # noqa: E402

VISIONS = {
    "normal": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    "protanopia": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deuteranopia": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritanopia": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}
BACKGROUNDS = ("#121212", "#1e1e1e", "#272727")  # Textual dark theme: background, surface, zebra stripe
MIN_DIFFERENCE = 15.0  # CIE76; about 2.3 is just noticeable
MIN_CONTRAST = 4.5  # WCAG 2 AA, normal text


def linear(colour):
    """Linear RGB of #RRGGBB"""
    channels = [int(colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    return [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]


def seen(colour, vision):
    """Linear RGB of a colour as seen with a kind of colour vision"""
    rgb = linear(colour)
    return [min(1.0, max(0.0, sum(row[index] * rgb[index] for index in range(3)))) for row in VISIONS[vision]]


def lab(rgb):
    """CIELAB (D65) of linear RGB"""
    x = (0.4124564 * rgb[0] + 0.3575761 * rgb[1] + 0.1804375 * rgb[2]) / 0.95047
    y = 0.2126729 * rgb[0] + 0.7151522 * rgb[1] + 0.0721750 * rgb[2]
    z = (0.0193339 * rgb[0] + 0.1191920 * rgb[1] + 0.9503041 * rgb[2]) / 1.08883
    fx, fy, fz = (value ** (1 / 3) if value > 0.008856 else 7.787 * value + 16 / 116 for value in (x, y, z))
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def difference(first, second, vision):
    return math.dist(lab(seen(first, vision)), lab(seen(second, vision)))


def contrast(first, second):
    """WCAG contrast ratio of two colours"""
    luminances = sorted(
        (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2] for rgb in (linear(first), linear(second))), reverse=True
    )
    return (luminances[0] + 0.05) / (luminances[1] + 0.05)


def colours(style):
    """(foreground, background or None) of a style of the form `[bold] #RRGGBB [on #RRGGBB]`"""
    words = [word for word in style.split() if word.startswith("#")]
    return words[0], (words[1] if len(words) > 1 else None)


def test_every_severity_has_a_style_in_explicit_colours():
    assert set(SEVERITY_STYLES) == set(SEVERITY_ORDER)
    for style in list(SEVERITY_STYLES.values()) + list(LIMIT_STYLES.values()):
        assert colours(style)[0].startswith("#"), "named colours depend on the terminal's palette"


@pytest.mark.parametrize("vision", list(VISIONS))
def test_severity_text_colours_are_told_apart(vision):
    text = {name: colours(style)[0] for name, style in SEVERITY_STYLES.items() if colours(style)[1] is None}
    assert len(text) == len(SEVERITY_STYLES) - 1  # All but FATAL, which is a filled row
    for (first, first_colour), (second, second_colour) in itertools.combinations(text.items(), 2):
        assert difference(first_colour, second_colour, vision) >= MIN_DIFFERENCE, (first, second)


@pytest.mark.parametrize("vision", list(VISIONS))
def test_filled_rows_and_cells_stand_out_and_differ(vision):
    fills = {"FATAL": colours(SEVERITY_STYLES["FATAL"])[1]}
    fills.update({f"limit {name}": colours(style)[1] for name, style in LIMIT_STYLES.items() if name != "red"})
    for (first, first_colour), (second, second_colour) in itertools.combinations(fills.items(), 2):
        assert difference(first_colour, second_colour, vision) >= MIN_DIFFERENCE, (first, second)
    for name, fill in fills.items():
        for background in BACKGROUNDS:
            assert difference(fill, background, vision) >= MIN_DIFFERENCE, name


def test_text_is_readable_on_its_background():
    for name, style in list(SEVERITY_STYLES.items()) + list(LIMIT_STYLES.items()):
        foreground, fill = colours(style)
        for background in (fill,) if fill else BACKGROUNDS:
            assert contrast(foreground, background) >= MIN_CONTRAST, (name, background)


def test_colour_is_not_the_only_cue():
    assert "bold" in SEVERITY_STYLES["WARNING_HI"] and "bold" not in SEVERITY_STYLES["WARNING_LO"]
    assert set(LIMIT_MARKS) == set(LIMIT_STYLES) and len(set(LIMIT_MARKS.values())) == len(LIMIT_MARKS)
