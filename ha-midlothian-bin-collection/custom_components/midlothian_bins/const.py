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

BIN_GENERAL = "general_waste"
BIN_RECYCLING = "recycling"
BIN_GARDEN = "garden_waste"
BIN_GLASS_FOOD = "glass_food"

BIN_TYPES = [BIN_GENERAL, BIN_RECYCLING, BIN_GARDEN, BIN_GLASS_FOOD]

BIN_DISPLAY_NAMES = {
    BIN_GENERAL: "General Waste",
    BIN_RECYCLING: "Recycling",
    BIN_GARDEN: "Garden Waste",
    BIN_GLASS_FOOD: "Glass & Food",
}

BIN_COLOURS = {
    BIN_GENERAL: "Grey",
    BIN_RECYCLING: "Blue",
    BIN_GARDEN: "Brown",
    BIN_GLASS_FOOD: "Purple",
}

BIN_ICONS = {
    BIN_GENERAL: "mdi:trash-can",
    BIN_RECYCLING: "mdi:recycle",
    BIN_GARDEN: "mdi:leaf",
    BIN_GLASS_FOOD: "mdi:glass-fragile",
}

CONF_POSTCODE = "postcode"
CONF_UPRN = "uprn"
CONF_ADDRESS = "address"

# Map API service names to our bin type keys
SERVICE_MAP = {
    "residual": BIN_GENERAL,
    "recycling": BIN_RECYCLING,
    "garden": BIN_GARDEN,
    "glass": BIN_GLASS_FOOD,
    "food": BIN_GLASS_FOOD,
    "card": BIN_RECYCLING,
}

# Legacy - kept for config_flow keyword matching
BIN_KEYWORDS = {
    BIN_GENERAL: ["general", "grey", "gray", "refuse", "household", "landfill", "residual"],
    BIN_RECYCLING: ["recycl", "blue", "paper", "card", "plastic", "metal", "can"],
    BIN_GARDEN: ["garden", "brown", "green waste", "grass", "leaf"],
    BIN_GLASS_FOOD: ["glass", "food", "purple", "caddy"],
}
