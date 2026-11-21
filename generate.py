#!/usr/bin/env python3
"""Draw the news-image-20261120 v2 front page: 35 stories from Friday
20 November 2026, rendered as one dense 1024x1024 newspaper page.

Deterministic by construction: no network, no clock, no randomness.
Running this script twice produces byte-identical PNG output.

Usage: python3 generate.py [output-path]   (default: entry.png next
to this file)
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
W, H = 1024, 1024
MARGIN = 22
LEFT = MARGIN
RIGHT = W - MARGIN
CW = RIGHT - LEFT  # 980 content width

# Vertical budget (sums to 1024):
#   masthead 123 | strip 41 | stats 61 | tabs 31 | leads 246 |
#   cards 225 | map+digest 236 | date check 30 | footer 31
Y_MASTHEAD = 0
Y_STRIP = 123
Y_STATS = 164
Y_TABS = 225
Y_LEADS = 256
Y_CARDS = 502
Y_MAP = 727
Y_DATECHECK = 963
Y_FOOTER = 993

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (20, 18, 16)
GRAY = (74, 70, 64)
FAINT = (120, 114, 102)
RULE = (30, 28, 25)
LIGHT_RULE = (201, 194, 180)
VERMILION = (179, 64, 42)
TAB_BG = (239, 231, 211)
CHECK_BG = (233, 225, 207)
SKY = (220, 231, 236)
SEA = (127, 168, 188)
SEA_DEEP = (90, 130, 150)
SLATE = (74, 107, 124)
SLATE_DARK = (46, 58, 66)
LAND = (217, 207, 180)
LAND_DARK = (198, 186, 155)
TAN = (216, 205, 178)
WHITE = (255, 255, 255)
MAP_WATER = (185, 207, 217)
MAP_LAND = (222, 211, 184)
MAP_LINE = (155, 178, 190)

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype/liberation"
_FONT_CACHE = {}


def F(size, bold=False, serif=False, italic=False):
    """Cached Liberation font loader (serif for headlines, sans for body)."""
    key = (size, bold, serif, italic)
    if key not in _FONT_CACHE:
        if serif:
            if bold:
                name = "LiberationSerif-Bold.ttf"
            elif italic:
                name = "LiberationSerif-Italic.ttf"
            else:
                name = "LiberationSerif-Regular.ttf"
        else:
            if bold:
                name = "LiberationSans-Bold.ttf"
            elif italic:
                name = "LiberationSans-Italic.ttf"
            else:
                name = "LiberationSans-Regular.ttf"
        _FONT_CACHE[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _FONT_CACHE[key]


# ---------------------------------------------------------------- text helpers
def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, max_w):
    """Greedy word wrap; overlong words are split by character."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if tw(d, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            while tw(d, cur, font) > max_w and len(cur) > 1:
                cut = len(cur) - 1
                while cut > 1 and tw(d, cur[:cut], font) > max_w:
                    cut -= 1
                lines.append(cur[:cut])
                cur = cur[cut:]
    if cur:
        lines.append(cur)
    return lines


def draw_centered(d, cx, y, text, font, fill):
    d.text((cx - tw(d, text, font) / 2, y), text, font=font, fill=fill)


def draw_tracked(d, cx, y, text, font, fill, tracking=3):
    """Centered text with fixed extra space between letters."""
    widths = [tw(d, ch, font) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def rich_wrap(d, segments, max_w):
    """Wrap mixed-font segments. segments: [(text, font, fill), ...].
    Returns lines; each line is a list of (word, font, fill)."""
    words = []
    for text, font, fill in segments:
        for w in text.split(" "):
            if w:
                words.append((w, font, fill))
    lines, cur, cur_w = [], [], 0.0
    for w, font, fill in words:
        ww = tw(d, w, font)
        sw = tw(d, " ", font) if cur else 0.0
        if cur and cur_w + sw + ww > max_w:
            lines.append(cur)
            cur, cur_w = [], 0.0
            sw = 0.0
        cur.append((w, font, fill))
        cur_w += sw + ww
    if cur:
        lines.append(cur)
    return lines


def draw_rich_line(d, x, y, line):
    for w, font, fill in line:
        d.text((x, y), w, font=font, fill=fill)
        x += tw(d, w, font) + tw(d, " ", font)


def hline(d, x0, x1, y, width=1, fill=RULE):
    d.rectangle([x0, y, x1, y + width - 1], fill=fill)


def vline(d, x, y0, y1, width=1, fill=LIGHT_RULE):
    d.rectangle([x, y0, x + width - 1, y1], fill=fill)


# ---------------------------------------------------------------- the 35 stories
LEADS = [
    {
        "num": "01", "region": "EUROPE",
        "headline": "Russia strikes Kyiv\u2019s bridges",
        "body": ("Russia attacked Ukraine overnight with more than 400 drones "
                 "and over 110 missiles, including 27 ballistic missiles. "
                 "Three bridges across Kyiv\u2019s Dnipro River were hit; "
                 "President Zelensky said at least nine people were killed "
                 "across Ukraine."),
        "source": "Zelensky; Kyiv mayor",
        "illo": "kyiv",
    },
    {
        "num": "02", "region": "ASIA",
        "headline": "Akvan crosses India\u2019s coast",
        "body": ("Cyclone Akvan crossed near Gopalpur on Friday morning with "
                 "sustained winds of 70\u201380 km/h, gusting to 90. Chief "
                 "Secretary Anu Garg said about 370,000 people had been "
                 "evacuated in Odisha. No major damage or loss of life was "
                 "reported."),
        "source": "IMD; Odisha government",
        "illo": "akvan",
    },
    {
        "num": "03", "region": "ASIA",
        "headline": "AI rout sweeps Asian markets",
        "body": ("AI-linked selling battered Asian stock markets on Friday. "
                 "Taiwan\u2019s Taiex fell 6.2% at Friday\u2019s close; "
                 "regional shares headed for their worst week since 2020."),
        "source": "Reuters",
        "illo": "markets",
    },
]

CARDS = [
    ("04", "COP31: NO DEAL YET",
     "Antalya\u2019s final-day draft drops fossil-fuel phase-out language; "
     "adaptation finance remains unresolved.",
     "UN News; Reuters", "cop31"),
    ("05", "UK\u2013EU RESET AGREED",
     "The deal sets timelines for youth mobility, food trade and "
     "carbon-market cooperation.",
     "Reuters", "ukeu"),
    ("06", "SEOUL PARTY BACKS IMPEACHMENT",
     "The ruling Democratic Party adopts seeking Chief Justice Cho Hee-dae\u2019s "
     "impeachment as official policy.",
     "Yonhap", "court"),
    ("07", "ESTONIA TO CLOSE ROAD BORDER",
     "Estonia plans a Russia road-border closure lasting at least six months "
     "after a foiled sabotage plot.",
     "Euronews; Kyiv Independent", "border"),
    ("08", "RUSSIAN WEAPONS FALL IN POLAND",
     "Two Russian missiles and a suspected jet-powered drone came down in "
     "Poland during Russia\u2019s attack on Ukraine, Polish officials said. "
     "No injuries were reported.",
     "AP \u00b7 Polish defence ministry", "poland"),
    ("09", "SENEGAL BOAT DISASTER",
     "Four people die and dozens remain missing after a migrant boat "
     "capsizes off Yenne.",
     "Al Jazeera", "boat"),
    ("10", "TONGA DECLARES DROUGHT EMERGENCY",
     "The Pacific kingdom declares an emergency as El Ni\u00f1o brings drought.",
     "RNZ", "drought"),
    ("11", "RIO TINTO\u2019S PANGUNA PLEDGE",
     "Rio Tinto pledges $370 million to address the Bougainville mine\u2019s legacy.",
     "Reuters", "mine"),
    ("12", "FLORIDA RIVER SETS RECORD",
     "The St. Johns River reaches a record 18.3 feet; schools close.",
     "AP", "river"),
    ("13", "IRAQI FORCES ENTER JURF AL-SAKHAR",
     "Forces enter under an agreement with Kataib Hezbollah.",
     "Al Jazeera", "checkpoint"),
]

DIGEST = [
    ("14", "JAPAN", "October CPI up 2.3%; December BoJ hike eyed.",
     "Reuters"),
    ("15", "CHINA", "Lending rates hold an 18th month: 1-year 3.0%, "
     "5-year 3.5%.", "PBOC; Reuters"),
    ("16", "UKRAINE", "UNICEF: at least 1,144 children killed or injured "
     "Jan\u2013Oct.", "UNICEF"),
    ("17", "ITALY", "CGIL 24-hour budget strike; rallies in 100 squares.",
     "CGIL; AFP"),
    ("18", "RUSSIA", "Ukrainian drones hit Druzhba pumping station in "
     "Tatarstan.", "Kyiv Independent"),
    ("19", "LONDON", "Britain, Norway pledge \u00a3100m+ for two Ukrainian "
     "naval vessels.", "Reuters"),
    ("20", "DENMARK", "Parliament approves Greenland defence bill.", "AFP"),
    ("21", "CANBERRA", "AUKUS sales could shrink US fleet, budget office "
     "warns.", "Reuters"),
    ("22", "IOWA", "US Army to detonate 68 unstable explosive barrels at "
     "noon.", "AP"),
    ("23", "WASHINGTON", "Pentagon puts US war on Iran cost at $48.3bn.",
     "AP"),
    ("24", "BRAZIL", "Lula visits ailing Indigenous chief Raoni.",
     "Al Jazeera"),
    ("25", "HONG KONG", "Fines to triple after deadly Tai Po blaze.",
     "SCMP"),
    ("26", "SPACE", "BepiColombo reaches Mercury; orbit insertion "
     "Saturday.", "ESA"),
    ("27", "BRAZIL", "Isolated Aw\u00e1 people contact government team.",
     "Euronews"),
    ("28", "NIGERIA", "Moves to end jail terms for attempted suicide.",
     "BBC"),
    ("29", "GHANA", "$50m presidential jet purchase sparks controversy.",
     "France 24"),
    ("30", "WASHINGTON", "Senate passes bill to speed energy, data-centre "
     "permits.", "AP"),
    ("31", "MALAWI", "Fuel crisis: motorists queue through night for "
     "petrol.", "Al Jazeera"),
    ("32", "NEW DELHI", "Pakistani minister joins SCO meeting in India, "
     "first since 2025.", "The Hindu"),
    ("33", "INDONESIA", "Parliament approves asset-forfeiture legislation.",
     "Reuters"),
    ("34", "WELLINGTON", "Phillips hits 118 vs India; first Kiwi with "
     "centuries in all 3 formats in a year.", "ICC; AP"),
    ("35", "SOUTH AFRICA", "Police: hundreds of women killed in three "
     "months.", "BBC"),
]

STRIP = ["KYIV: BRIDGES HIT", "AKVAN MAKES LANDFALL",
         "AI SELL-OFF HITS ASIA", "COP31: DEAL UNRESOLVED"]

STATS = [
    ("3", "KYIV BRIDGES HIT \u00b7 01", ""),
    ("370,000", "EVACUATED IN ODISHA \u00b7 02", "Odisha government"),
    ("1,144", "CHILDREN KILLED OR INJURED IN UKRAINE \u00b7 16",
     "Jan\u2013Oct 2026 \u00b7 UNICEF"),
    ("$370m", "PANGUNA LEGACY PLEDGE \u00b7 11", ""),
    ("18.3 ft", "ST. JOHNS RIVER RECORD \u00b7 12", ""),
    ("\u22126.2%", "TAIWAN TAIEX, FRIDAY\u2019S CLOSE \u00b7 03", "Reuters"),
]

TABS = [("EUROPE", 9), ("ASIA", 8), ("MIDDLE EAST", 2), ("AFRICA", 5),
        ("NORTH AMERICA", 4), ("LATIN AMERICA", 2), ("OCEANIA", 4),
        ("GLOBAL", 1)]

DATECHECK_LABEL = "DATE CHECK \u2014"
DATECHECK_TEXT = (
    "Excluded as November 19 news: Shenzhen Trump\u2013Xi\u2013Putin summit; "
    "Anthropic $83 IPO pricing and Nasdaq debut; ICJ Rohingya verdict; "
    "GTA VI launch; Voyager 1 one-light-day confirmation; Han Duck-soo "
    "acquittal. Also distinguished \u2014 cancer-pill trial: findings released "
    "Thursday 19 November; Bukele: registration occurred Thursday night, "
    "19 November.")

FOOTER_L1 = ("Every story here happened, or was first reported, on Friday "
             "20 November 2026.")
FOOTER_L2 = ("Sources: Reuters, AP, AFP, BBC, Al Jazeera, Guardian, IMD, "
             "UN News, ICC, EU Council, ESA, PBOC, Yonhap, RNZ, SCMP, "
             "Euronews. Original drawings.")


# ---------------------------------------------------------------- illustrations
# Flat vector-style drawings, one per illustrated story (leads 01-03 and
# cards 04-13). Each draws inside the given box only.

def illo_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # apartment blocks on both banks
    for bx, bw, bh in ((0.02, 0.16, 0.42), (0.20, 0.12, 0.55),
                       (0.66, 0.14, 0.48), (0.82, 0.16, 0.38)):
        d.rectangle([x + w * bx, y + h * (0.52 - bh), x + w * (bx + bw),
                     y + h * 0.52], fill=SLATE_DARK)
        for wy in range(3):
            for wx in range(max(1, int(bw * w / 14))):
                d.rectangle([x + w * bx + 4 + wx * 11, y + h * (0.52 - bh) + 5 + wy * 9,
                             x + w * bx + 8 + wx * 11, y + h * (0.52 - bh) + 9 + wy * 9],
                            fill=(214, 200, 160))
    # river
    d.rectangle([x, y + h * 0.52, x + w, y + h], fill=SEA)
    for i in range(6):
        d.line([x + w * (0.05 + i * 0.16), y + h * 0.72,
                x + w * (0.11 + i * 0.16), y + h * 0.72], fill=WHITE, width=2)
    # three bridges spanning the river
    for bx in (0.10, 0.42, 0.72):
        bx0, bx1 = x + w * bx, x + w * (bx + 0.22)
        d.rectangle([bx0, y + h * 0.46, bx1, y + h * 0.52], fill=INK)
        d.arc([bx0, y + h * 0.46, bx1, y + h * 0.78], 180, 360, fill=INK, width=3)
        d.line([bx0 + 4, y + h * 0.46, bx0 + 4, y + h * 0.36], fill=INK, width=3)
        d.line([bx1 - 4, y + h * 0.46, bx1 - 4, y + h * 0.36], fill=INK, width=3)
        d.line([bx0 + 4, y + h * 0.36, bx1 - 4, y + h * 0.36], fill=INK, width=2)
    # one restrained smoke plume
    for i, (sx, sy, r) in enumerate(((0.30, 0.30, 7), (0.315, 0.22, 9),
                                     (0.33, 0.14, 11))):
        d.ellipse([x + w * sx - r, y + h * sy - r,
                   x + w * sx + r, y + h * sy + r], fill=(150, 148, 142))


def illo_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # sea (left) and coast (right)
    d.polygon([(x, y + h * 0.55), (x + w * 0.55, y + h * 0.35),
               (x + w * 0.62, y + h), (x, y + h)], fill=SEA)
    d.polygon([(x + w * 0.55, y + h * 0.35), (x + w, y + h * 0.30),
               (x + w, y + h), (x + w * 0.62, y + h)], fill=LAND)
    # cyclone spiral: concentric arcs over the sea
    cx, cy = x + w * 0.26, y + h * 0.42
    for i, r in enumerate((34, 26, 18, 10)):
        d.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8],
              200 + i * 40, 200 + i * 40 + 250, fill=WHITE, width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=WHITE)
    # shelter roof + evacuation arrow on land
    sx = x + w * 0.74
    d.polygon([(sx, y + h * 0.52), (sx + 26, y + h * 0.52),
               (sx + 13, y + h * 0.38)], fill=VERMILION)
    d.rectangle([sx + 3, y + h * 0.52, sx + 23, y + h * 0.66], fill=SLATE_DARK)
    d.line([sx - 8, y + h * 0.80, sx + 34, y + h * 0.80], fill=INK, width=3)
    d.polygon([(sx + 34, y + h * 0.80), (sx + 26, y + h * 0.74),
               (sx + 26, y + h * 0.86)], fill=INK)


def illo_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SLATE_DARK)
    # three market screens
    for i, sx in enumerate((0.06, 0.38, 0.70)):
        sx0 = x + w * sx
        d.rectangle([sx0, y + h * 0.18, sx0 + w * 0.24, y + h * 0.62],
                    fill=(232, 226, 208))
        d.rectangle([sx0, y + h * 0.18, sx0 + w * 0.24, y + h * 0.30],
                    fill=SLATE)
        for j in range(3):
            d.line([sx0 + 5, y + h * (0.38 + j * 0.08),
                    sx0 + w * 0.24 - 5 - j * 8, y + h * (0.38 + j * 0.08)],
                   fill=GRAY, width=2)
    # chip silhouettes along the bottom
    for cx in (0.14, 0.46, 0.78):
        cx0, cy0 = x + w * cx, y + h * 0.72
        d.rectangle([cx0, cy0, cx0 + 26, cy0 + 16], fill=INK)
        for p in range(3):
            d.line([cx0 + 5 + p * 8, cy0, cx0 + 5 + p * 8, cy0 - 5],
                   fill=INK, width=2)
            d.line([cx0 + 5 + p * 8, cy0 + 16, cx0 + 5 + p * 8, cy0 + 21],
                   fill=INK, width=2)
    # descending vermilion line across everything
    d.line([(x + w * 0.04, y + h * 0.12), (x + w * 0.38, y + h * 0.38),
            (x + w * 0.62, y + h * 0.30), (x + w * 0.96, y + h * 0.72)],
           fill=VERMILION, width=4)
    d.polygon([(x + w * 0.96, y + h * 0.72), (x + w * 0.90, y + h * 0.62),
               (x + w * 0.88, y + h * 0.74)], fill=VERMILION)


def illo_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # globe
    d.ellipse([x + 6, y + 3, x + 26, y + 23], fill=SEA, outline=SLATE_DARK)
    d.arc([x + 11, y + 3, x + 21, y + 23], 90, 270, fill=SLATE_DARK)
    d.line([x + 6, y + 13, x + 26, y + 13], fill=SLATE_DARK)
    # lectern
    d.polygon([(x + w * 0.42, y + h * 0.30), (x + w * 0.58, y + h * 0.30),
               (x + w * 0.54, y + h - 3), (x + w * 0.46, y + h - 3)],
              fill=SLATE_DARK)
    d.rectangle([x + w * 0.40, y + h * 0.22, x + w * 0.60, y + h * 0.30],
                fill=INK)
    # document with an unfinished final line
    dx = x + w * 0.68
    d.rectangle([dx, y + 3, dx + w * 0.26, y + h - 3], fill=WHITE,
                outline=SLATE_DARK)
    for i in range(3):
        d.line([dx + 4, y + 8 + i * 5, dx + w * 0.26 - 4, y + 8 + i * 5],
               fill=GRAY, width=1)
    for i in range(3):  # dashed unfinished line
        d.line([dx + 4 + i * 8, y + 23, dx + 8 + i * 8, y + 23],
               fill=VERMILION, width=2)


def illo_ukeu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # two flag panels joined by a narrow bridge
    d.rectangle([x + 4, y + 5, x + w * 0.38, y + h - 6], fill=(40, 70, 130))
    for i in range(5):
        d.ellipse([x + 8 + i * 7, y + 9, x + 11 + i * 7, y + 12], fill=(250, 210, 60))
    d.rectangle([x + w * 0.62, y + 5, x + w - 4, y + h - 6],
                fill=(200, 200, 205))
    d.rectangle([x + w * 0.62, y + h * 0.42, x + w - 4, y + h * 0.58],
                fill=VERMILION)
    d.rectangle([x + w * 0.76, y + 5, x + w * 0.84, y + h - 6], fill=VERMILION)
    d.rectangle([x + w * 0.38, y + h * 0.44, x + w * 0.62, y + h * 0.56],
                fill=INK)
    d.arc([x + w * 0.38, y + h * 0.44, x + w * 0.62, y + h * 0.86],
          180, 360, fill=INK, width=2)


def illo_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    cx = x + w / 2
    d.polygon([(cx - w * 0.36, y + h * 0.34), (cx + w * 0.36, y + h * 0.34),
               (cx, y + h * 0.10)], fill=SLATE_DARK)
    d.rectangle([cx - w * 0.36, y + h * 0.34, cx + w * 0.36, y + h * 0.42],
                fill=INK)
    for i in range(4):
        px = cx - w * 0.28 + i * w * 0.19
        d.rectangle([px, y + h * 0.42, px + 5, y + h * 0.78], fill=SLATE_DARK)
    d.rectangle([cx - w * 0.40, y + h * 0.78, cx + w * 0.40, y + h * 0.86],
                fill=INK)
    d.rectangle([cx - w * 0.44, y + h * 0.86, cx + w * 0.44, y + h - 2],
                fill=SLATE_DARK)


def illo_border(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=LAND)
    # road band
    d.rectangle([x, y + h * 0.55, x + w, y + h * 0.85], fill=(140, 138, 130))
    for i in range(6):
        d.line([x + 6 + i * 30, y + h * 0.70, x + 18 + i * 30, y + h * 0.70],
               fill=WHITE, width=2)
    # closed barrier: striped bar
    d.rectangle([x + w * 0.30, y + h * 0.18, x + w * 0.72, y + h * 0.32],
                fill=WHITE, outline=INK)
    for i in range(4):
        bx = x + w * 0.30 + i * (w * 0.42 / 4)
        d.polygon([(bx, y + h * 0.32), (bx + 8, y + h * 0.18),
                   (bx + 16, y + h * 0.18), (bx + 8, y + h * 0.32)],
                  fill=VERMILION)
    d.line([x + w * 0.32, y + h * 0.32, x + w * 0.32, y + h * 0.62],
           fill=INK, width=3)
    d.line([x + w * 0.70, y + h * 0.32, x + w * 0.70, y + h * 0.62],
           fill=INK, width=3)
    # signpost
    d.line([x + w * 0.84, y + h * 0.20, x + w * 0.84, y + h * 0.60],
           fill=INK, width=2)
    d.ellipse([x + w * 0.84 - 6, y + h * 0.10, x + w * 0.84 + 6,
               y + h * 0.10 + 12], fill=WHITE, outline=VERMILION, width=2)
    d.line([x + w * 0.84 - 4, y + h * 0.10 + 6, x + w * 0.84 + 4,
            y + h * 0.10 + 6], fill=VERMILION, width=2)


def illo_parliament(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # domed building
    d.rectangle([x + w * 0.08, y + h * 0.42, x + w * 0.55, y + h - 3],
                fill=SLATE_DARK)
    d.pieslice([x + w * 0.20, y + h * 0.10, x + w * 0.43, y + h * 0.55],
               180, 360, fill=SLATE_DARK)
    d.line([x + w * 0.315, y + h * 0.02, x + w * 0.315, y + h * 0.12],
           fill=INK, width=2)
    for i in range(3):
        d.rectangle([x + w * 0.13 + i * w * 0.13, y + h * 0.55,
                     x + w * 0.19 + i * w * 0.13, y + h * 0.78],
                    fill=(214, 200, 160))
    # legal document with seal
    dx = x + w * 0.64
    d.rectangle([dx, y + 4, dx + w * 0.28, y + h - 4], fill=WHITE,
                outline=SLATE_DARK)
    for i in range(3):
        d.line([dx + 4, y + 8 + i * 5, dx + w * 0.28 - 4, y + 8 + i * 5],
               fill=GRAY, width=1)
    d.ellipse([dx + w * 0.28 - 13, y + h - 13, dx + w * 0.28 - 3, y + h - 3],
              fill=VERMILION)


def illo_poland(d, x, y, w, h):
    # Fully proportional: this card's long copy can shrink the box to
    # 12 px tall, so every element scales with h.
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # ploughed field: furrows as converging diagonal lines
    d.rectangle([x, y + h * 0.45, x + w, y + h], fill=(190, 170, 120))
    for i in range(7):
        fx = x + w * (0.04 + i * 0.15)
        d.line([fx, y + h, fx + w * 0.08, y + h * 0.45],
               fill=(150, 128, 80), width=2)
    d.line([x, y + h * 0.45, x + w, y + h * 0.45], fill=(150, 128, 80),
           width=1)
    # small grounded missile silhouette lying in the field
    bh = max(3, int(h * 0.20))       # body height
    fh = max(2, int(h * 0.15))       # fin height
    mx, my = x + w * 0.16, y + h * 0.66
    d.rectangle([mx, my, mx + w * 0.34, my + bh], fill=SLATE_DARK)
    d.polygon([(mx + w * 0.34, my), (mx + w * 0.34 + 9, my + bh / 2),
               (mx + w * 0.34, my + bh)], fill=SLATE_DARK)
    d.polygon([(mx, my), (mx - 5, my - fh), (mx + 6, my)], fill=SLATE_DARK)
    d.polygon([(mx, my + bh), (mx - 5, my + bh + fh), (mx + 6, my + bh)],
              fill=SLATE_DARK)
    # boundary marker post with a striped cap
    px = x + w * 0.80
    cap0 = y + max(2, int(h * 0.22))
    cap1 = y + max(4, int(h * 0.30))
    d.rectangle([px, cap1, px + 5, y + h * 0.82], fill=INK)
    d.rectangle([px - 2, cap0, px + 7, cap1], fill=WHITE, outline=INK)
    d.rectangle([px - 2, cap0, px + 7, cap0 + max(1, (cap1 - cap0) // 2)],
                fill=VERMILION)


def illo_boat(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # distant coast
    d.polygon([(x + w * 0.62, y + h * 0.30), (x + w, y + h * 0.22),
               (x + w, y + h * 0.45), (x + w * 0.62, y + h * 0.45)],
              fill=LAND_DARK)
    # waves
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=SEA)
    for i in range(5):
        d.arc([x + i * 36, y + h * 0.62, x + 28 + i * 36, y + h * 0.82],
              180, 360, fill=WHITE, width=2)
    # small tilted boat
    d.polygon([(x + w * 0.14, y + h * 0.42), (x + w * 0.46, y + h * 0.30),
               (x + w * 0.42, y + h * 0.52), (x + w * 0.18, y + h * 0.62)],
              fill=(122, 74, 42))
    d.line([x + w * 0.30, y + h * 0.30, x + w * 0.34, y + h * 0.10],
           fill=INK, width=2)
    d.polygon([(x + w * 0.34, y + h * 0.10), (x + w * 0.34, y + h * 0.26),
               (x + w * 0.50, y + h * 0.26)], fill=WHITE)


def illo_drought(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 214, 170))
    # cracked dry ground
    d.rectangle([x, y + h * 0.45, x + w, y + h], fill=(206, 178, 130))
    for (x0, y0, x1, y1) in ((0.10, 0.50, 0.22, 0.75), (0.22, 0.75, 0.34, 0.62),
                             (0.45, 0.48, 0.55, 0.80), (0.55, 0.80, 0.70, 0.66),
                             (0.72, 0.52, 0.86, 0.85), (0.30, 0.85, 0.50, 0.95)):
        d.line([x + w * x0, y + h * y0, x + w * x1, y + h * y1],
               fill=(140, 110, 70), width=2)
    # sun + one water drop, scaled so the drop tip stays inside the box
    d.ellipse([x + w * 0.06, y + h * 0.08, x + w * 0.06 + 16,
               y + h * 0.08 + 16], fill=(230, 170, 60))
    ds = max(4, int(h * 0.28))
    dx, dy = x + w * 0.80, y + h * 0.32
    d.polygon([(dx, dy - ds), (dx + ds * 0.8, dy + ds * 0.2),
               (dx - ds * 0.8, dy + ds * 0.2)], fill=SEA_DEEP)
    d.ellipse([dx - ds * 0.8, dy - ds * 0.2, dx + ds * 0.8,
               dy + ds * 1.2], fill=SEA_DEEP)


def illo_mine(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # terraced open pit
    for i, (inset, top) in enumerate(((0.06, 0.30), (0.16, 0.45),
                                      (0.26, 0.60), (0.36, 0.75))):
        shade = (176 - i * 14, 150 - i * 12, 110 - i * 10)
        d.polygon([(x + w * inset, y + h * top),
                   (x + w * (1 - inset), y + h * top),
                   (x + w * (1 - inset - 0.08), y + h * (top + 0.16)),
                   (x + w * (inset + 0.08), y + h * (top + 0.16))],
                  fill=shade)
    d.rectangle([x + w * 0.40, y + h * 0.88, x + w * 0.60, y + h * 0.97],
                fill=SLATE_DARK)
    # small truck on the rim
    d.rectangle([x + w * 0.10, y + h * 0.18, x + w * 0.24, y + h * 0.28],
                fill=VERMILION)
    d.rectangle([x + w * 0.24, y + h * 0.22, x + w * 0.29, y + h * 0.28],
                fill=INK)
    d.ellipse([x + w * 0.12, y + h * 0.27, x + w * 0.12 + 6,
               y + h * 0.27 + 6], fill=INK)
    d.ellipse([x + w * 0.22, y + h * 0.27, x + w * 0.22 + 6,
               y + h * 0.27 + 6], fill=INK)


def illo_river(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # flooded houses: rooftops above water
    for hx, hw in ((0.08, 0.26), (0.42, 0.24)):
        d.polygon([(x + w * hx, y + h * 0.55), (x + w * (hx + hw), y + h * 0.55),
                   (x + w * (hx + hw / 2), y + h * 0.32)], fill=SLATE_DARK)
        d.rectangle([x + w * hx + 3, y + h * 0.55, x + w * (hx + hw) - 3,
                     y + h * 0.66], fill=(214, 200, 160))
    # water
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=SEA)
    for i in range(5):
        d.line([x + 6 + i * 34, y + h * 0.78, x + 22 + i * 34, y + h * 0.78],
               fill=WHITE, width=2)
    # gauge post with high-water mark
    gx = x + w * 0.80
    d.rectangle([gx, y + h * 0.14, gx + 6, y + h - 3], fill=WHITE,
                outline=INK)
    for i in range(4):
        d.line([gx, y + h * (0.22 + i * 0.18), gx + 6,
                y + h * (0.22 + i * 0.18)], fill=INK, width=1)
    d.line([gx - 8, y + h * 0.22, gx + 14, y + h * 0.22], fill=VERMILION,
           width=3)


def illo_checkpoint(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=LAND)
    # buildings behind
    d.rectangle([x + w * 0.06, y + h * 0.30, x + w * 0.30, y + h * 0.62],
                fill=SLATE_DARK)
    d.rectangle([x + w * 0.68, y + h * 0.22, x + w * 0.94, y + h * 0.62],
                fill=SLATE_DARK)
    d.rectangle([x + w * 0.72, y + h * 0.30, x + w * 0.78, y + h * 0.40],
                fill=(214, 200, 160))
    d.rectangle([x + w * 0.84, y + h * 0.30, x + w * 0.90, y + h * 0.40],
                fill=(214, 200, 160))
    # road + checkpoint barrier
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(140, 138, 130))
    d.rectangle([x + w * 0.34, y + h * 0.44, x + w * 0.66, y + h * 0.54],
                fill=WHITE, outline=INK)
    for i in range(3):
        bx = x + w * 0.34 + i * (w * 0.32 / 3)
        d.polygon([(bx, y + h * 0.54), (bx + 6, y + h * 0.44),
                   (bx + 12, y + h * 0.44), (bx + 6, y + h * 0.54)],
                  fill=VERMILION)
    d.line([x + w * 0.36, y + h * 0.54, x + w * 0.36, y + h * 0.80],
           fill=INK, width=3)
    d.line([x + w * 0.64, y + h * 0.54, x + w * 0.64, y + h * 0.80],
           fill=INK, width=3)
    # location marker pin, scaled to the box so it never pokes above it
    # (the old fixed 16 px radius crossed the row divider at small heights)
    px, py = x + w * 0.50, y + h * 0.40
    pr = max(4, int(h * 0.20))
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=VERMILION)
    d.polygon([(px - pr, py + pr * 0.4), (px + pr, py + pr * 0.4),
               (px, py + pr * 1.6)], fill=VERMILION)
    cr = max(2, int(pr * 0.4))
    d.ellipse([px - cr, py - cr, px + cr, py + cr], fill=WHITE)


ILLOS = {
    "kyiv": illo_kyiv, "akvan": illo_akvan, "markets": illo_markets,
    "cop31": illo_cop31, "ukeu": illo_ukeu, "court": illo_court,
    "border": illo_border, "parliament": illo_parliament, "boat": illo_boat,
    "poland": illo_poland,
    "drought": illo_drought, "mine": illo_mine, "river": illo_river,
    "checkpoint": illo_checkpoint,
}


# ---------------------------------------------------------------- world map
# Simplified continent silhouettes as (lon, lat) polygons.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 72), (-85, 70),
     (-80, 73), (-65, 62), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-81, 25), (-84, 30), (-90, 29), (-97, 26), (-105, 22),
     (-110, 24), (-114, 29), (-120, 34), (-124, 40), (-124, 48), (-130, 55),
     (-140, 60), (-155, 58), (-165, 60)],
    # Greenland
    [(-45, 60), (-40, 65), (-30, 68), (-22, 70), (-30, 76), (-45, 76),
     (-58, 74), (-55, 70), (-50, 64)],
    # South America
    [(-78, 8), (-72, 12), (-62, 10), (-52, 5), (-44, -3), (-35, -8),
     (-38, -15), (-40, -22), (-48, -28), (-52, -33), (-58, -38), (-62, -41),
     (-65, -45), (-68, -50), (-70, -54), (-72, -50), (-73, -40), (-72, -30),
     (-70, -20), (-75, -15), (-78, -8), (-80, -3)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 31), (-5, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 2), (41, -2), (40, -10), (35, -18),
     (32, -26), (28, -33), (20, -35), (17, -29), (14, -22), (12, -6), (9, 4),
     (4, 6), (-8, 5), (-13, 8)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 68), (40, 68),
     (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 77), (110, 74),
     (120, 73), (130, 72), (140, 72), (150, 70), (160, 69), (170, 67),
     (178, 65), (178, 62), (170, 60), (162, 56), (158, 52), (155, 45),
     (150, 42), (142, 40), (140, 35), (135, 34), (130, 33), (127, 35),
     (122, 38), (120, 32), (122, 28), (118, 25), (110, 20), (108, 12),
     (105, 9), (103, 2), (100, 6), (98, 10), (95, 16), (92, 21), (88, 22),
     (86, 20), (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25),
     (60, 25), (57, 27), (52, 26), (50, 29), (48, 30), (44, 29), (40, 28),
     (36, 36), (33, 36), (30, 36), (27, 37), (23, 36), (19, 40), (16, 42),
     (12, 44), (8, 44), (3, 43), (-2, 37), (-6, 36), (-9, 37)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (1, 52), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 36), (141, 39),
     (142, 43), (144, 44), (141, 42), (139, 38), (136, 35), (133, 34)],
    # Sumatra, Borneo, New Guinea
    [(95, 5), (100, 0), (104, -5), (106, -6), (102, -4), (98, 2)],
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (112, -3)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -10), (147, -9),
     (142, -8), (137, -7), (132, -4)],
    # Australia
    [(114, -22), (114, -30), (118, -35), (124, -33), (129, -32), (132, -32),
     (135, -35), (138, -35), (140, -38), (145, -38), (147, -42), (150, -37),
     (153, -32), (153, -27), (151, -24), (146, -19), (142, -15), (142, -11),
     (137, -12), (132, -12), (126, -14), (122, -17), (118, -20)],
    # New Zealand
    [(167, -45), (170, -42), (173, -39), (175, -38), (178, -38), (175, -41),
     (172, -43), (168, -46)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -25), (45, -25),
     (44, -20)],
]

# (number, lon, lat) for the 13 illustrated stories.
PINS = [
    ("01", 31, 50), ("02", 85, 19), ("03", 122, 32), ("04", 31, 37),
    ("05", 0, 51.5), ("06", 127, 37.5), ("07", 27, 59), ("08", 22, 50),
    ("09", -17, 15), ("10", -175, -21), ("11", 155, -6), ("12", -81, 30),
    ("13", 44, 32.5),
]

# Candidate label offsets (dx, dy from the pin dot), tried in order.
LABEL_OFFSETS = [(9, -7), (9, 3), (-23, -7), (-23, 3), (9, -18), (-23, -18),
                 (9, 12), (-23, 12), (-7, -19), (-7, 10), (14, -12),
                 (-28, -12)]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=MAP_WATER, outline=SLATE_DARK)

    def proj(lon, lat):
        px = x + (lon + 180) / 360.0 * w
        py = y + (78 - lat) / 136.0 * h
        return px, py

    # graticule
    for lon in range(-150, 181, 30):
        gx = x + (lon + 180) / 360.0 * w
        d.line([gx, y, gx, y + h], fill=MAP_LINE, width=1)
    for lat in range(-60, 79, 30):
        gy = y + (78 - lat) / 136.0 * h
        d.line([x, gy, x + w, gy], fill=MAP_LINE, width=1)
    # land
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly],
                  fill=MAP_LAND, outline=(150, 138, 108))
    # pin dots + numbered labels with leader lines
    placed = []  # label rects already used
    pin03_label = None
    num_font = F(8, bold=True)
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=INK,
                  outline=WHITE)
        chosen = None
        for dx, dy in LABEL_OFFSETS:
            lx, ly = px + dx, py + dy
            rect = (lx, ly, lx + 14, ly + 14)
            if rect[0] < x + 1 or rect[1] < y + 1:
                continue
            if rect[2] > x + w - 1 or rect[3] > y + h - 1:
                continue
            if any(not (rect[2] < r[0] or rect[0] > r[2] or
                        rect[3] < r[1] or rect[1] > r[3]) for r in placed):
                continue
            chosen = (lx, ly)
            placed.append(rect)
            break
        if chosen is None:  # last resort: on top of the dot
            chosen = (px - 7, py - 19)
            placed.append((chosen[0], chosen[1], chosen[0] + 14,
                           chosen[1] + 14))
        lx, ly = chosen
        cx, cy = lx + 7, ly + 7
        d.line([px, py, cx, cy], fill=INK, width=1)
        d.ellipse([lx, ly, lx + 14, ly + 14], fill=INK, outline=WHITE)
        tw_num = tw(d, num, num_font)
        d.text((cx - tw_num / 2, cy - 5), num, font=num_font, fill=WHITE)
        if num == "03":
            pin03_label = (lx, ly)
    # Regional callout for pin 03 so one anchor does not imply one city:
    # top-right corner of the map. (At the old 220 px width it sat
    # directly above the pin-03 label, but at 180 px that strip is
    # occupied by the pin-06 label, so the callout moves to the clear
    # strip above all labels instead.)
    if pin03_label is not None:
        call = F(8, bold=True)
        text = "ASIA MARKETS"
        tx = x + w - 2 - tw(d, text, call)
        d.text((tx, y + 3), text, font=call, fill=INK)


# ---------------------------------------------------------------- sections
def draw_masthead(d):
    cx = LEFT + CW / 2
    draw_tracked(d, cx, 12, "THE WORLD IN ONE DAY", F(15, bold=True),
                 INK, tracking=4)
    date_font = F(48, bold=True, serif=True)
    date = "Friday 20 November 2026"
    while tw(d, date, date_font) > CW - 20 and date_font.size > 30:
        date_font = F(date_font.size - 2, bold=True, serif=True)
    draw_centered(d, cx, 34, date, date_font, INK)
    draw_tracked(d, cx, 94, "35 STORIES \u00b7 8 REGIONS", F(13, bold=True),
                 GRAY, tracking=3)
    hline(d, LEFT, RIGHT, 120, width=3)


def draw_strip(d):
    col_w = CW / 4
    font = F(15, bold=True)
    for i, text in enumerate(STRIP):
        cx = LEFT + col_w * (i + 0.5)
        draw_centered(d, cx, Y_STRIP + 13, text, font, INK)
        if i:
            vline(d, int(LEFT + col_w * i), Y_STRIP + 6, Y_STRIP + 35)
    hline(d, LEFT, RIGHT, Y_STRIP + 40)


def draw_stats(d):
    # Number, label and attribution all sit on fixed baselines shared by
    # all six boxes: the label block is bottom-anchored so one-line and
    # two-line labels end on the same line, and the attribution (where
    # present) sits on one line below it.
    col_w = CW / 6
    num_f = F(25, bold=True, serif=True)
    label_f = F(9, bold=True)
    sub_f = F(8)
    label_last_y = Y_STATS + 39
    sub_y = Y_STATS + 49
    for i, (num, label, sub) in enumerate(STATS):
        x0 = LEFT + col_w * i
        cx = x0 + col_w / 2
        d.text((cx - tw(d, num, num_f) / 2, Y_STATS + 4), num,
               font=num_f, fill=VERMILION)
        lines = wrap(d, label, label_f, col_w - 12)
        ly = label_last_y - (len(lines[:2]) - 1) * 11
        for line in lines[:2]:
            draw_centered(d, cx, ly, line, label_f, INK)
            ly += 11
        if sub:
            draw_centered(d, cx, sub_y, sub, sub_f, GRAY)
        if i:
            vline(d, int(x0), Y_STATS + 6, Y_STATS + 55)
    hline(d, LEFT, RIGHT, Y_STATS + 60)


def draw_tabs(d):
    d.rectangle([LEFT, Y_TABS, RIGHT, Y_TABS + 30], fill=TAB_BG)
    col_w = CW / len(TABS)
    for i, (region, count) in enumerate(TABS):
        x0 = LEFT + col_w * i
        cx = x0 + col_w / 2
        rf, cf = F(12, bold=True), F(12, bold=True)
        total = tw(d, region, rf) + 5 + tw(d, str(count), cf)
        rx = cx - total / 2
        d.text((rx, Y_TABS + 9), region, font=rf, fill=INK)
        d.text((rx + tw(d, region, rf) + 5, Y_TABS + 9), str(count),
               font=cf, fill=VERMILION)
        if i:
            vline(d, int(x0), Y_TABS + 5, Y_TABS + 26, fill=(210, 200, 175))
    hline(d, LEFT, RIGHT, Y_TABS + 30)


def draw_lead(d, x, y, w, h, lead):
    """One illustrated lead. The illustration height flexes so the text
    block always fits inside the fixed-height lead row."""
    tag_f = F(11, bold=True)
    src_f = F(10)
    for head_size, body_size in ((27, 13), (26, 13), (25, 12), (24, 12)):
        head_f = F(head_size, bold=True, serif=True)
        body_f = F(body_size)
        head_lines = wrap(d, lead["headline"], head_f, w - 4)
        body_lines = wrap(d, lead["body"], body_f, w - 4)
        head_h = len(head_lines) * (head_size + 3)
        body_h = len(body_lines) * (body_size + 4)
        text_h = 14 + head_h + 4 + body_h + 14
        illo_h = h - text_h - 8
        if illo_h >= 64 or (head_size, body_size) == (24, 12):
            break
    illo_h = max(56, min(92, illo_h))
    ILLOS[lead["illo"]](d, x, y, w, illo_h)
    d.rectangle([x, y, x + w, y + illo_h], outline=SLATE_DARK)
    ty = y + illo_h + 6
    d.text((x, ty), lead["num"], font=tag_f, fill=VERMILION)
    d.text((x + tw(d, lead["num"] + "  ", tag_f), ty),
           "\u00b7 " + lead["region"], font=tag_f, fill=GRAY)
    hy = ty + 15
    for line in head_lines:
        d.text((x, hy), line, font=head_f, fill=INK)
        hy += head_size + 3
    by = hy + 3
    for line in body_lines:
        d.text((x, by), line, font=body_f, fill=INK)
        by += body_size + 4
    d.text((x, by + 1), "(" + lead["source"] + ")", font=src_f, fill=GRAY)


def draw_leads(d):
    # Kyiv takes 36% of the row; Akvan and markets split the rest.
    w1 = int(CW * 0.36)
    w2 = (CW - w1 - 20) // 2
    w3 = CW - w1 - w2 - 20
    xs = [LEFT, LEFT + w1 + 10, LEFT + w1 + 10 + w2 + 10]
    ws = [w1, w2, w3]
    for (x, w, lead) in zip(xs, ws, LEADS):
        draw_lead(d, x, Y_LEADS + 4, w, Y_CARDS - Y_LEADS - 8, lead)
    vline(d, LEFT + w1 + 5, Y_LEADS + 4, Y_CARDS - 4)
    vline(d, LEFT + w1 + 10 + w2 + 5, Y_LEADS + 4, Y_CARDS - 4)
    hline(d, LEFT, RIGHT, Y_CARDS - 1)


def draw_card(d, x, y, w, h, card):
    num, headline, body, source, illo_key = card
    pad = 5
    text_w = w - pad * 2
    src_f = F(9)
    # Try headline/body sizes and illustration heights until it fits.
    # The small end (head 13, body 9, illo 12) exists for the long
    # Poland card; other cards still pick their larger sizes first.
    chosen = None
    for head_size in (15, 14, 13):
        for body_size in (11, 10, 9):
            for illo_h in (36, 32, 28, 24, 20, 16, 12):
                head_f = F(head_size, bold=True, serif=True)
                body_f = F(body_size)
                head_lines = wrap(d, num + "  " + headline, head_f, text_w)
                body_lines = wrap(d, body, body_f, text_w)
                need = (illo_h + 4 + len(head_lines) * (head_size + 2) + 2
                        + len(body_lines) * (body_size + 2) + 2 + 11)
                if need <= h - 4:
                    chosen = (head_size, body_size, illo_h, head_lines,
                              body_lines)
                    break
            if chosen:
                break
        if chosen:
            break
    if chosen is None:  # smallest fallback; never clip the copy
        head_size, body_size, illo_h = 13, 9, 12
        head_f = F(head_size, bold=True, serif=True)
        body_f = F(body_size)
        head_lines = wrap(d, num + "  " + headline, head_f, text_w)
        body_lines = wrap(d, body, body_f, text_w)
    else:
        head_size, body_size, illo_h, head_lines, body_lines = chosen
        head_f = F(head_size, bold=True, serif=True)
        body_f = F(body_size)
    ILLOS[illo_key](d, x + pad, y + 3, text_w, illo_h)
    d.rectangle([x + pad, y + 3, x + pad + text_w, y + 3 + illo_h],
                outline=SLATE_DARK)
    hy = y + 3 + illo_h + 5
    for i, line in enumerate(head_lines):
        if i == 0:
            # vermilion number, then the headline in ink. wrap() collapses
            # the double space after the number to one, so split on the
            # first whitespace instead of slicing a fixed width.
            parts = line.split(None, 1)
            rest = parts[1] if len(parts) > 1 else ""
            num_w = tw(d, num + " ", head_f)
            d.text((x + pad, hy), num, font=head_f, fill=VERMILION)
            d.text((x + pad + num_w, hy), rest, font=head_f, fill=INK)
        else:
            d.text((x + pad, hy), line, font=head_f, fill=INK)
        hy += head_size + 2
    by = hy + 2
    for line in body_lines:
        d.text((x + pad, by), line, font=body_f, fill=INK)
        by += body_size + 2
    d.text((x + pad, by + 1), "(" + source + ")", font=src_f, fill=GRAY)


def draw_cards(d):
    col_w = CW / 5
    row_h = (Y_MAP - Y_CARDS) // 2
    for i, card in enumerate(CARDS):
        col, row = i % 5, i // 5
        x = LEFT + int(col_w * col)
        y = Y_CARDS + row * row_h
        draw_card(d, x, y, int(col_w), row_h, card)
    for k in range(1, 5):
        vline(d, int(LEFT + col_w * k), Y_CARDS + 4, Y_MAP - 4)
    hline(d, LEFT, RIGHT, Y_CARDS + row_h)
    hline(d, LEFT, RIGHT, Y_MAP - 1)


def draw_digest_column(d, x, y, w, items, size, gap=0):
    """Render one digest column; returns the height used."""
    # Tight leading (size+1) and zero inter-item gap: at 12 px type the
    # 8-item middle column is 16 lines x 13 px = 208 px, which only fits
    # the fixed 211 px slot with gap 0. The bold "NN PLACE:" lead-in
    # keeps items visually separated instead.
    leading = size + 1
    num_f = F(size, bold=True)
    subj_f = F(size, bold=True)
    body_f = F(size)
    src_f = F(size)
    cy = y
    for num, subj, body, source in items:
        segments = [(num + " ", num_f, VERMILION),
                    (subj + ": ", subj_f, INK),
                    (body + " ", body_f, INK),
                    ("\u2014 " + source, src_f, GRAY)]
        lines = rich_wrap(d, segments, w)
        for line in lines:
            draw_rich_line(d, x, cy, line)
            cy += leading
        cy += gap
    return cy - y


def draw_map_digest(d):
    map_w = 180
    map_x0 = LEFT
    # map title + subtitle
    d.text((map_x0, Y_MAP + 3), "WHERE IT HAPPENED", font=F(12, bold=True),
           fill=INK)
    d.text((map_x0, Y_MAP + 18), "Numbers match illustrated reports.",
           font=F(9), fill=GRAY)
    draw_map(d, map_x0, Y_MAP + 33, map_w, Y_DATECHECK - Y_MAP - 37)
    vline(d, map_x0 + map_w + 6, Y_MAP + 4, Y_DATECHECK - 4)
    # digest heading
    dx = map_x0 + map_w + 14
    d.text((dx, Y_MAP + 3), "ALSO IN THE FRIDAY FILE \u2014 22 MORE STORIES",
           font=F(13, bold=True), fill=INK)
    col_gap = 10
    col_w = (RIGHT - dx - 2 * col_gap) // 3
    items_y = Y_MAP + 23
    max_h = Y_DATECHECK - items_y - 2
    # Three columns, 7/8/7: the middle column takes the extra item
    # because the first and last columns hold the longest items.
    cols = [DIGEST[:7], DIGEST[7:15], DIGEST[15:]]
    # Largest font size whose tallest column still fits. Measured with
    # zero inter-item gap: at 12 px the 8-item middle column is
    # 16 lines x 13 px leading = 208 px against the 211 px slot, so any
    # gap at all overflows it; the bold lead-ins carry the separation.
    heights = None
    for size in (12, 11, 10, 9, 8):
        leading = size + 1
        heights = []
        for col in cols:
            total = 0
            for num, subj, body, source in col:
                segments = [(num + " ", F(size, bold=True), VERMILION),
                            (subj + ": ", F(size, bold=True), INK),
                            (body + " ", F(size), INK),
                            ("\u2014 " + source, F(size), GRAY)]
                total += len(rich_wrap(d, segments, col_w)) * leading
            heights.append(total)
        if max(heights) <= max_h:
            break
    # Spread any leftover vertical room as extra space between items.
    slack = max_h - max(heights)
    gap = min(4, max(0, slack // 12))
    for i, col in enumerate(cols):
        draw_digest_column(d, dx + i * (col_w + col_gap), items_y, col_w,
                           col, size, gap)


def draw_datecheck(d):
    # One compact paragraph in a ~30 px box; the freed space belongs to
    # the digest. Largest size whose wrap fits the box height.
    d.rectangle([LEFT, Y_DATECHECK + 1, RIGHT, Y_FOOTER - 1], fill=CHECK_BG)
    x0 = LEFT + 8
    w = CW - 16
    avail = Y_FOOTER - Y_DATECHECK - 7
    lines = None
    for size in (9, 8, 7):
        label_f = F(size, bold=True)
        body_f = F(size)
        lines = rich_wrap(d, [(DATECHECK_LABEL + "  ", label_f, VERMILION),
                              (DATECHECK_TEXT, body_f, INK)], w)
        if len(lines) * (size + 2) <= avail:
            break
    ly = Y_DATECHECK + 5
    for line in lines:
        draw_rich_line(d, x0, ly, line)
        ly += size + 2


def draw_footer(d):
    cx = LEFT + CW / 2
    hline(d, LEFT, RIGHT, Y_FOOTER)
    draw_centered(d, cx, Y_FOOTER + 4, FOOTER_L1, F(10), GRAY)
    draw_centered(d, cx, Y_FOOTER + 17, FOOTER_L2, F(10), GRAY)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_strip(d)
    draw_stats(d)
    draw_tabs(d)
    draw_leads(d)
    draw_cards(d)
    draw_map_digest(d)
    draw_datecheck(d)
    draw_footer(d)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, "PNG")
    print("wrote %s (%d bytes)" % (out, os.path.getsize(out)))


if __name__ == "__main__":
    main()
