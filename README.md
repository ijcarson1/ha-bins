# Midlothian Bin Collection — Home Assistant Integration

> **TODO — Migration required:** This plugin is temporarily housed in the
> `gearedapp-ai-os` repository on branch `claude/bin-collection-reminder-yxEn8`
> due to sandbox signing constraints at build time. It should be extracted into
> its own standalone repository (`ha-midlothian-bin-collection`) before being
> shared or submitted to HACS.
>
> **Steps to migrate:**
> 1. Create a new public GitHub repo: `gh repo create ha-midlothian-bin-collection --public`
> 2. `cp -r ha-midlothian-bin-collection/ /path/to/new/repo/`
> 3. `cd /path/to/new/repo && git init && git add . && git commit -m "Initial commit" && git push -u origin main`

A custom Home Assistant integration that fetches your bin collection schedule from **Midlothian Council** and sends a push notification to your phone the evening before collection day.

> **Note:** Midlothian Council is not currently supported by the major generic waste collection integrations. This integration scrapes the [MyMidlothian portal](https://my.midlothian.gov.uk/service/Bin_Collection_Dates) directly. If the council changes their website layout, sensors may stop updating — please [open an issue](https://github.com/ijcarson1/ha-midlothian-bin-collection/issues) if that happens.

---

## What You Get

Four sensors, one per bin type:

| Sensor | Bin | Colour |
|--------|-----|--------|
| `sensor.midlothian_general_waste` | General Waste | Grey |
| `sensor.midlothian_recycling` | Recycling | Blue |
| `sensor.midlothian_garden_waste` | Garden Waste | Brown |
| `sensor.midlothian_glass_food` | Glass & Food | Purple |

Each sensor's **state** is the next collection date (e.g. `2026-03-25`) and it carries these **attributes**:

- `days_until` — integer days until collection (0 = today, 1 = tomorrow)
- `bin_type` — human-readable name
- `bin_colour` — bin colour
- `collection_today` / `collection_tomorrow` — boolean shortcuts

---

## Installation

### Option A — Manual (recommended until HACS listing is available)

1. Download or clone this repository.
2. Copy the `custom_components/midlothian_bins` folder into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

### Option B — HACS (Custom Repository)

1. In HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/ijcarson1/ha-midlothian-bin-collection` as an **Integration**.
3. Search for **Midlothian Bin Collection** and install it.
4. Restart Home Assistant.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Midlothian Bin Collection**.
3. Enter your **postcode** (e.g. `EH22 1BG`).
4. If multiple addresses share your postcode, select yours from the dropdown.
5. Done — sensors will appear within a few seconds.

Sensors refresh every **12 hours**.

---

## Setting Up the Reminder Notification

1. Open `automations/bin_reminder.yaml`.
2. Replace `YOUR_DEVICE_ID` with your actual notify service name.
   - Find it in **Settings → Integrations → Mobile App → your device**.
   - It looks like `notify.mobile_app_my_iphone` or `notify.mobile_app_pixel_8`.
3. Import the automation:
   - **Settings → Automations & Scenes → ⋮ → Import automation** and select the file.
   - Or paste its contents into your `automations.yaml`.

The automation fires every evening at **18:00** and sends a notification only on nights where at least one bin is due the next morning. The message lists which bins to put out.

---

## Dashboard Card Example

```yaml
type: entities
title: Bin Collection
entities:
  - entity: sensor.midlothian_general_waste
    name: General Waste
    secondary_info: attribute
    attribute: days_until
  - entity: sensor.midlothian_recycling
    name: Recycling
    secondary_info: attribute
    attribute: days_until
  - entity: sensor.midlothian_garden_waste
    name: Garden Waste
    secondary_info: attribute
    attribute: days_until
  - entity: sensor.midlothian_glass_food
    name: Glass & Food
    secondary_info: attribute
    attribute: days_until
```

---

## Troubleshooting

**Sensors show `unavailable`**
- Check Home Assistant logs for errors from `custom_components.midlothian_bins`.
- Verify the council website is reachable from your HA host.
- The scraper may need updating if Midlothian Council changed their portal — [open an issue](https://github.com/ijcarson1/ha-midlothian-bin-collection/issues).

**Wrong bin dates**
- The parser matches bin types by keyword. If the council uses unusual terminology, the classification may be off. Open an issue with a screenshot of your collection page.

**Notification not arriving**
- Confirm the `notify.mobile_app_YOUR_DEVICE_ID` service exists in **Developer Tools → Services**.
- Check the companion app is installed and notifications are enabled.

---

## Contributing

PRs welcome. The most valuable contributions right now:
- Confirming / fixing the portal scraping for different addresses
- Adding support for the council's API if a stable endpoint is documented

---

## Licence

MIT
