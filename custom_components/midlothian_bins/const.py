"""Constants for the Midlothian Bin Collection integration."""

from datetime import timedelta

DOMAIN = "midlothian_bins"

COUNCIL_URL = "https://my.midlothian.gov.uk/service/Bin_Collection_Dates"

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

BIN_KEYWORDS = {
    BIN_GENERAL: ["general", "grey", "gray", "refuse", "household", "landfill"],
    BIN_RECYCLING: ["recycl", "blue", "paper", "card", "plastic", "metal", "can"],
    BIN_GARDEN: ["garden", "brown", "green waste", "grass", "leaf"],
    BIN_GLASS_FOOD: ["glass", "food", "purple", "caddy"],
}
