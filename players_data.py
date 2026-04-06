"""
All player data. Stats are out of 99.
Positions: GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST
Rarities: bronze, silver, gold, icon
"""

PLAYERS = [
    # ── ICONS ──────────────────────────────────────────────────────────────
    {"id": 1,  "name": "Ronaldo",       "position": "ST",  "rarity": "icon",   "nationality": "Portugal",  "club": "Al Nassr",    "pace": 89, "shooting": 99, "passing": 82, "defending": 35, "physical": 95, "overall": 91},
    {"id": 2,  "name": "Messi",         "position": "CAM", "rarity": "icon",   "nationality": "Argentina", "club": "Inter Miami", "pace": 81, "shooting": 95, "passing": 99, "defending": 40, "physical": 65, "overall": 94},
    {"id": 3,  "name": "Neymar",        "position": "LW",  "rarity": "icon",   "nationality": "Brazil",    "club": "Al Hilal",    "pace": 90, "shooting": 87, "passing": 87, "defending": 37, "physical": 68, "overall": 89},
    {"id": 4,  "name": "Ronaldinho",    "position": "CAM", "rarity": "icon",   "nationality": "Brazil",    "club": "Retired",     "pace": 85, "shooting": 87, "passing": 90, "defending": 38, "physical": 70, "overall": 92},
    {"id": 5,  "name": "Zidane",        "position": "CM",  "rarity": "icon",   "nationality": "France",    "club": "Retired",     "pace": 78, "shooting": 85, "passing": 96, "defending": 65, "physical": 80, "overall": 93},
    {"id": 6,  "name": "Pele",          "position": "ST",  "rarity": "icon",   "nationality": "Brazil",    "club": "Retired",     "pace": 88, "shooting": 98, "passing": 85, "defending": 44, "physical": 82, "overall": 95},
    {"id": 7,  "name": "Maradona",      "position": "CAM", "rarity": "icon",   "nationality": "Argentina", "club": "Retired",     "pace": 86, "shooting": 90, "passing": 92, "defending": 42, "physical": 75, "overall": 94},

    # ── GOLD ───────────────────────────────────────────────────────────────
    {"id": 10, "name": "Mbappe",        "position": "ST",  "rarity": "gold",   "nationality": "France",    "club": "Real Madrid", "pace": 99, "shooting": 93, "passing": 80, "defending": 40, "physical": 81, "overall": 91},
    {"id": 11, "name": "Haaland",       "position": "ST",  "rarity": "gold",   "nationality": "Norway",    "club": "Man City",    "pace": 89, "shooting": 97, "passing": 65, "defending": 45, "physical": 95, "overall": 91},
    {"id": 12, "name": "Vinicius Jr",   "position": "LW",  "rarity": "gold",   "nationality": "Brazil",    "club": "Real Madrid", "pace": 97, "shooting": 83, "passing": 78, "defending": 30, "physical": 72, "overall": 88},
    {"id": 13, "name": "Bellingham",    "position": "CM",  "rarity": "gold",   "nationality": "England",   "club": "Real Madrid", "pace": 79, "shooting": 87, "passing": 85, "defending": 70, "physical": 88, "overall": 88},
    {"id": 14, "name": "Salah",         "position": "RW",  "rarity": "gold",   "nationality": "Egypt",     "club": "Liverpool",   "pace": 93, "shooting": 90, "passing": 81, "defending": 45, "physical": 76, "overall": 89},
    {"id": 15, "name": "De Bruyne",     "position": "CM",  "rarity": "gold",   "nationality": "Belgium",   "club": "Man City",    "pace": 74, "shooting": 86, "passing": 98, "defending": 64, "physical": 78, "overall": 91},
    {"id": 16, "name": "Benzema",       "position": "ST",  "rarity": "gold",   "nationality": "France",    "club": "Al Ittihad",  "pace": 77, "shooting": 91, "passing": 83, "defending": 39, "physical": 81, "overall": 89},
    {"id": 17, "name": "Alisson",       "position": "GK",  "rarity": "gold",   "nationality": "Brazil",    "club": "Liverpool",   "pace": 60, "shooting": 20, "passing": 75, "defending": 90, "physical": 78, "overall": 90},
    {"id": 18, "name": "Van Dijk",      "position": "CB",  "rarity": "gold",   "nationality": "Netherlands","club": "Liverpool",  "pace": 78, "shooting": 60, "passing": 71, "defending": 93, "physical": 91, "overall": 89},
    {"id": 19, "name": "Rudiger",       "position": "CB",  "rarity": "gold",   "nationality": "Germany",   "club": "Real Madrid", "pace": 80, "shooting": 47, "passing": 60, "defending": 88, "physical": 90, "overall": 85},
    {"id": 20, "name": "Ter Stegen",    "position": "GK",  "rarity": "gold",   "nationality": "Germany",   "club": "Barcelona",   "pace": 58, "shooting": 18, "passing": 78, "defending": 91, "physical": 76, "overall": 89},
    {"id": 21, "name": "Pedri",         "position": "CM",  "rarity": "gold",   "nationality": "Spain",     "club": "Barcelona",   "pace": 78, "shooting": 75, "passing": 90, "defending": 70, "physical": 66, "overall": 87},
    {"id": 22, "name": "Lewandowski",   "position": "ST",  "rarity": "gold",   "nationality": "Poland",    "club": "Barcelona",   "pace": 78, "shooting": 93, "passing": 79, "defending": 42, "physical": 82, "overall": 89},
    {"id": 23, "name": "Kane",          "position": "ST",  "rarity": "gold",   "nationality": "England",   "club": "Bayern",      "pace": 71, "shooting": 93, "passing": 83, "defending": 47, "physical": 83, "overall": 90},
    {"id": 24, "name": "Saka",          "position": "RW",  "rarity": "gold",   "nationality": "England",   "club": "Arsenal",     "pace": 88, "shooting": 82, "passing": 82, "defending": 60, "physical": 68, "overall": 86},
    {"id": 25, "name": "Osimhen",       "position": "ST",  "rarity": "gold",   "nationality": "Nigeria",   "club": "Galatasaray", "pace": 91, "shooting": 87, "passing": 66, "defending": 37, "physical": 89, "overall": 87},
    {"id": 26, "name": "Modric",        "position": "CM",  "rarity": "gold",   "nationality": "Croatia",   "club": "Real Madrid", "pace": 75, "shooting": 76, "passing": 92, "defending": 72, "physical": 66, "overall": 87},
    {"id": 27, "name": "Courtois",      "position": "GK",  "rarity": "gold",   "nationality": "Belgium",   "club": "Real Madrid", "pace": 55, "shooting": 15, "passing": 70, "defending": 92, "physical": 80, "overall": 90},
    {"id": 28, "name": "Dias",          "position": "CB",  "rarity": "gold",   "nationality": "Portugal",  "club": "Man City",    "pace": 76, "shooting": 40, "passing": 65, "defending": 91, "physical": 86, "overall": 88},
    {"id": 29, "name": "Griezmann",     "position": "CAM", "rarity": "gold",   "nationality": "France",    "club": "Atletico",    "pace": 78, "shooting": 85, "passing": 82, "defending": 58, "physical": 73, "overall": 86},
    {"id": 30, "name": "Lamine Yamal",  "position": "RW",  "rarity": "gold",   "nationality": "Spain",     "club": "Barcelona",   "pace": 92, "shooting": 80, "passing": 83, "defending": 35, "physical": 60, "overall": 86},

    # ── SILVER ─────────────────────────────────────────────────────────────
    {"id": 50, "name": "Diaz",          "position": "LW",  "rarity": "silver", "nationality": "Colombia",  "club": "Liverpool",   "pace": 88, "shooting": 77, "passing": 74, "defending": 45, "physical": 70, "overall": 81},
    {"id": 51, "name": "Gundogan",      "position": "CM",  "rarity": "silver", "nationality": "Germany",   "club": "Barcelona",   "pace": 65, "shooting": 77, "passing": 87, "defending": 70, "physical": 68, "overall": 82},
    {"id": 52, "name": "Militao",       "position": "CB",  "rarity": "silver", "nationality": "Brazil",    "club": "Real Madrid", "pace": 82, "shooting": 38, "passing": 60, "defending": 86, "physical": 84, "overall": 83},
    {"id": 53, "name": "Rashford",      "position": "LW",  "rarity": "silver", "nationality": "England",   "club": "Man Utd",     "pace": 92, "shooting": 78, "passing": 72, "defending": 38, "physical": 74, "overall": 82},
    {"id": 54, "name": "Havertz",       "position": "ST",  "rarity": "silver", "nationality": "Germany",   "club": "Arsenal",     "pace": 78, "shooting": 78, "passing": 77, "defending": 58, "physical": 76, "overall": 81},
    {"id": 55, "name": "Valverde",      "position": "CM",  "rarity": "silver", "nationality": "Uruguay",   "club": "Real Madrid", "pace": 85, "shooting": 75, "passing": 79, "defending": 73, "physical": 85, "overall": 83},
    {"id": 56, "name": "Olise",         "position": "RW",  "rarity": "silver", "nationality": "France",    "club": "Bayern",      "pace": 86, "shooting": 79, "passing": 78, "defending": 36, "physical": 62, "overall": 82},
    {"id": 57, "name": "Guiu",          "position": "ST",  "rarity": "silver", "nationality": "Spain",     "club": "Barcelona",   "pace": 75, "shooting": 78, "passing": 68, "defending": 32, "physical": 73, "overall": 79},
    {"id": 58, "name": "Wirtz",         "position": "CAM", "rarity": "silver", "nationality": "Germany",   "club": "Leverkusen",  "pace": 80, "shooting": 78, "passing": 85, "defending": 52, "physical": 66, "overall": 83},
    {"id": 59, "name": "Diogo Jota",    "position": "ST",  "rarity": "silver", "nationality": "Portugal",  "club": "Liverpool",   "pace": 84, "shooting": 82, "passing": 72, "defending": 40, "physical": 73, "overall": 82},
    {"id": 60, "name": "Gavi",          "position": "CM",  "rarity": "silver", "nationality": "Spain",     "club": "Barcelona",   "pace": 75, "shooting": 68, "passing": 85, "defending": 73, "physical": 65, "overall": 82},
    {"id": 61, "name": "Zaha",          "position": "LW",  "rarity": "silver", "nationality": "Ivory Coast","club": "Galatasaray", "pace": 88, "shooting": 74, "passing": 71, "defending": 35, "physical": 70, "overall": 79},
    {"id": 62, "name": "Ederson",       "position": "GK",  "rarity": "silver", "nationality": "Brazil",    "club": "Man City",    "pace": 62, "shooting": 22, "passing": 78, "defending": 87, "physical": 77, "overall": 87},
    {"id": 63, "name": "Trent",         "position": "RB",  "rarity": "silver", "nationality": "England",   "club": "Real Madrid", "pace": 80, "shooting": 76, "passing": 91, "defending": 69, "physical": 66, "overall": 84},
    {"id": 64, "name": "Robertson",     "position": "LB",  "rarity": "silver", "nationality": "Scotland",  "club": "Liverpool",   "pace": 83, "shooting": 62, "passing": 82, "defending": 79, "physical": 75, "overall": 83},

    # ── BRONZE ─────────────────────────────────────────────────────────────
    {"id": 100,"name": "Weghorst",      "position": "ST",  "rarity": "bronze", "nationality": "Netherlands","club": "Hoffenheim",  "pace": 68, "shooting": 72, "passing": 63, "defending": 45, "physical": 82, "overall": 72},
    {"id": 101,"name": "McTominay",     "position": "CM",  "rarity": "bronze", "nationality": "Scotland",  "club": "Napoli",      "pace": 70, "shooting": 68, "passing": 71, "defending": 70, "physical": 80, "overall": 74},
    {"id": 102,"name": "Sels",          "position": "GK",  "rarity": "bronze", "nationality": "Belgium",   "club": "Nottm Forest","pace": 50, "shooting": 15, "passing": 62, "defending": 78, "physical": 72, "overall": 75},
    {"id": 103,"name": "Kilman",        "position": "CB",  "rarity": "bronze", "nationality": "England",   "club": "Wolves",      "pace": 72, "shooting": 35, "passing": 58, "defending": 79, "physical": 80, "overall": 74},
    {"id": 104,"name": "Madueke",       "position": "RW",  "rarity": "bronze", "nationality": "England",   "club": "Chelsea",     "pace": 85, "shooting": 70, "passing": 68, "defending": 30, "physical": 63, "overall": 74},
    {"id": 105,"name": "Iheanacho",     "position": "ST",  "rarity": "bronze", "nationality": "Nigeria",   "club": "Sevilla",     "pace": 72, "shooting": 72, "passing": 65, "defending": 38, "physical": 70, "overall": 73},
    {"id": 106,"name": "Perisic",       "position": "LW",  "rarity": "bronze", "nationality": "Croatia",   "club": "Hajduk Split","pace": 75, "shooting": 70, "passing": 73, "defending": 55, "physical": 72, "overall": 74},
    {"id": 107,"name": "Forsberg",      "position": "CAM", "rarity": "bronze", "nationality": "Sweden",    "club": "Leipzig",     "pace": 73, "shooting": 72, "passing": 78, "defending": 48, "physical": 62, "overall": 75},
    {"id": 108,"name": "Doku",          "position": "LW",  "rarity": "bronze", "nationality": "Belgium",   "club": "Man City",    "pace": 96, "shooting": 68, "passing": 70, "defending": 28, "physical": 60, "overall": 76},
    {"id": 109,"name": "Mykolenko",     "position": "LB",  "rarity": "bronze", "nationality": "Ukraine",   "club": "Everton",     "pace": 80, "shooting": 52, "passing": 68, "defending": 75, "physical": 72, "overall": 73},
    {"id": 110,"name": "Tarkowski",     "position": "CB",  "rarity": "bronze", "nationality": "England",   "club": "Everton",     "pace": 65, "shooting": 40, "passing": 58, "defending": 80, "physical": 83, "overall": 74},
    {"id": 111,"name": "Flekken",       "position": "GK",  "rarity": "bronze", "nationality": "Netherlands","club": "Brentford",   "pace": 48, "shooting": 12, "passing": 60, "defending": 76, "physical": 70, "overall": 73},
    {"id": 112,"name": "Soumare",       "position": "CDM", "rarity": "bronze", "nationality": "France",    "club": "Leicester",   "pace": 78, "shooting": 55, "passing": 70, "defending": 74, "physical": 80, "overall": 73},
    {"id": 113,"name": "Dennis",        "position": "RW",  "rarity": "bronze", "nationality": "Nigeria",   "club": "Nottm Forest","pace": 87, "shooting": 67, "passing": 62, "defending": 28, "physical": 65, "overall": 72},
    {"id": 114,"name": "Traore",        "position": "RW",  "rarity": "bronze", "nationality": "Spain",     "club": "Bournemouth", "pace": 94, "shooting": 62, "passing": 60, "defending": 25, "physical": 68, "overall": 72},
]

RARITY_WEIGHTS = {
    "standard": {"bronze": 60, "silver": 28, "gold": 10, "icon": 2},
    "premium":  {"bronze": 30, "silver": 35, "gold": 28, "icon": 7},
    "elite":    {"bronze": 5,  "silver": 25, "gold": 50, "icon": 20},
}

PACK_COSTS = {
    "standard": 200,
    "premium":  500,
    "elite":    1200,
}

PACK_SIZES = {
    "standard": 5,
    "premium":  5,
    "elite":    5,
}

RARITY_EMOJI = {
    "bronze": "🥉",
    "silver": "🥈",
    "gold":   "🥇",
    "icon":   "👑",
}

POSITION_EMOJI = {
    "GK": "🧤", "CB": "🛡", "LB": "🛡", "RB": "🛡",
    "CDM": "⚙️", "CM": "⚙️", "CAM": "🎯",
    "LW": "⚡", "RW": "⚡", "ST": "🔥",
}
PLAYER_MAP = {p["id"]: p for p in PLAYERS}
