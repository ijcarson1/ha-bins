"""Constants for the Midlothian Bin Collection integration."""

from datetime import timedelta

DOMAIN = "midlothian_bins"

COUNCIL_URL = "https://my.midlothian.gov.uk/service/Bin_Collection_Dates"
API_BASE = "https://my.midlothian.gov.uk"
AUTH_URL = f"{API_BASE}/authapi/isauthenticated"
LOOKUP_URL = f"{API_BASE}/apibroker/runLookup"
ADDRESS_LOOKUP_ID = "68f7a2ca3325e"
BIN_LOOKUP_ID = "69a19ba76d3a2"
PORTAL_NAME = "my-midlothian"

SCAN_INTERVAL = timedelta(hours=12)

# --- Bin type keys (one per physical bin / container) ---
BIN_GREY = "grey_bin"          # General waste
BIN_GREEN = "green_bin"        # Paper & card recycling
BIN_BLUE = "blue_bin"          # Plastics, cans & cartons recycling
BIN_GLASS = "glass_box"        # Glass bottles & jars
BIN_FOOD = "food_bin"          # Food waste caddy
BIN_GARDEN = "garden_waste"    # Brown bin (seasonal)

BIN_TYPES = [BIN_GREY, BIN_GREEN, BIN_BLUE, BIN_GLASS, BIN_FOOD, BIN_GARDEN]

BIN_DISPLAY_NAMES = {
    BIN_GREY: "Grey Bin",
    BIN_GREEN: "Green Bin",
    BIN_BLUE: "Blue Bin",
    BIN_GLASS: "Glass Box",
    BIN_FOOD: "Food Bin",
    BIN_GARDEN: "Garden Waste",
}

BIN_COLOURS = {
    BIN_GREY: "Grey",
    BIN_GREEN: "Green",
    BIN_BLUE: "Blue",
    BIN_GLASS: "Red",
    BIN_FOOD: "Dark Grey",
    BIN_GARDEN: "Brown",
}

BIN_ICONS = {
    BIN_GREY: "mdi:trash-can",
    BIN_GREEN: "mdi:newspaper-variant-outline",
    BIN_BLUE: "mdi:recycle",
    BIN_GLASS: "mdi:glass-fragile",
    BIN_FOOD: "mdi:food-apple",
    BIN_GARDEN: "mdi:leaf",
}

CONF_POSTCODE = "postcode"
CONF_UPRN = "uprn"
CONF_ADDRESS = "address"

# Map API service names → bin type.
# Checked in order; first match wins. More specific keywords come first
# to avoid false matches (e.g. "recycling" appearing in multiple services).
SERVICE_RULES: list[tuple[list[str], str]] = [
    # Grey bin – general / residual waste
    (["grey", "residual", "general waste"], BIN_GREY),
    # Green bin – paper & card
    (["green", "paper", "card"], BIN_GREEN),
    # Blue bin – plastics / mixed recycling / generic "recycling"
    (["blue", "plastic", "carton", "recycling"], BIN_BLUE),
    # Glass box
    (["glass"], BIN_GLASS),
    # Food caddy
    (["food", "caddy"], BIN_FOOD),
    # Garden waste (brown bin, seasonal)
    (["garden", "brown"], BIN_GARDEN),
]

# Legacy flat map kept for backwards-compat if anything references it
SERVICE_MAP = {
    "residual": BIN_GREY,
    "grey": BIN_GREY,
    "green": BIN_GREEN,
    "paper": BIN_GREEN,
    "card": BIN_GREEN,
    "blue": BIN_BLUE,
    "plastic": BIN_BLUE,
    "glass": BIN_GLASS,
    "food": BIN_FOOD,
    "garden": BIN_GARDEN,
    "brown": BIN_GARDEN,
}

# Legacy - kept for config_flow keyword matching
BIN_KEYWORDS = {
    BIN_GREY: ["general", "grey", "gray", "refuse", "household", "landfill", "residual"],
    BIN_GREEN: ["green", "paper", "card"],
    BIN_BLUE: ["blue", "plastic", "carton", "can", "mixed recycling"],
    BIN_GLASS: ["glass", "bottle", "jar"],
    BIN_FOOD: ["food", "caddy"],
    BIN_GARDEN: ["garden", "brown", "green waste", "grass", "leaf"],
}
