import gspread
from flask import Flask
from flask_caching import Cache

app = Flask(__name__)
app.config.from_mapping({"CACHE_TYPE": "SimpleCache"})
cache = Cache(app)

SPREADSHEET_ID = "175dbUBlzB3PJY0SV-5j0CcLiXIPxxx_R80OLq4nFC2c"
MODES = {
    "sword": "🗡️ Sword",
    "vanilla": " 🌄 Vanilla",
    "pot": "🧪 Pot",
    "nethpot": "♟️ Netherite Pot",
    "uhc": "💓 UHC",
    "axe": "🪓 Axe",
    "smp": "🛡️ SMP"
}


def get_color(color: dict) -> int:
    return (int(color["red"] * 255) << 16) + (int(color["green"] * 255) << 8) + int(color["blue"] * 255)


@app.route("/tiers/<mode>")
@cache.cached(timeout=300)
def get_tiers(mode: str):
    if mode not in MODES:
        return {"error": f"mode must be one of {list(MODES.keys())}"}, 400
    mode = MODES[mode]

    gc = gspread.service_account()
    sheet = gc.open_by_key(SPREADSHEET_ID)
    tiers = dict()

    for index, col in enumerate("B D F H J".split()):
        metadata = sheet.fetch_sheet_metadata({"includeGridData": True, "ranges": f"{mode}!{col}2:{col}"})
        cells = metadata["sheets"][0]["data"][0]["rowData"]
        filled_cells = [c for c in cells if "values" in c]  # remove all empty cells
        for cell in filled_cells:
            values = cell["values"][0]
            if "effectiveValue" in values:
                name = values["effectiveValue"]
                name = name["stringValue"] if "stringValue" in name else str(name["numberValue"])
                name = name.strip()

                if len(name) <= 0:
                    continue

                color = values["effectiveFormat"]["backgroundColor"]
                match get_color(color):
                    case 0x3c78d8:  # High tier
                        tiers[name] = f"HT{index + 1}"
                    case 0xa4c1f4:  # Low tier
                        tiers[name] = f"LT{index + 1}"

    return tiers
