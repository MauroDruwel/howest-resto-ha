# Howest Resto 🍽️

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![Validate](https://github.com/MauroDruwel/howest-resto-ha/actions/workflows/validate.yml/badge.svg)](https://github.com/MauroDruwel/howest-resto-ha/actions/workflows/validate.yml)
[![Tests](https://github.com/MauroDruwel/howest-resto-ha/actions/workflows/tests.yml/badge.svg)](https://github.com/MauroDruwel/howest-resto-ha/actions/workflows/tests.yml)
[![Quality Gate](https://img.shields.io/badge/Mauro%20Quality%20Gate-Passed-brightgreen)](https://github.com/MauroDruwel/quality-gate)

Home Assistant integration for **Howest University of Applied Sciences** student restaurant menus.

Exposes daily meals, weekly lunch schedules, and native calendar events for all 6 Howest campuses in Kortrijk and Brugge.

---

## ⚡ Features

- **Multi-Campus Support**: Monitor any Howest restaurant (Graaf Karel de Goedelaan, Renaat de Rudderlaan, The Square, Rijselstraat, Sint-Jorisstraat, Spoorwegstraat).
- **Today & Tomorrow Sensors**: Easily check today's and tomorrow's lunch specials in Home Assistant dashboards or send them in morning notification automations.
- **Weekly Menu Overview**: Access complete weekly dishes and daily breakdowns via attributes.
- **Native Calendar Platform**: View menus directly in Home Assistant calendar cards and integrate with calendar automations.
- **Language Preference**: Display dish titles in Dutch, English, or both via Integration Options.
- **Zero Cloud Proxy**: Communicates directly with the Howest restaurant portal using the [`howest-resto`](https://github.com/MauroDruwel/howest-resto) Python library.

---

## 📦 Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Click the top-right three dots menu and choose **Custom repositories**.
3. Add repository URL `https://github.com/MauroDruwel/howest-resto-ha` with category **Integration**.
4. Click **Download**, then restart Home Assistant.

### Manual Installation

1. Download the latest release from the [Releases](https://github.com/MauroDruwel/howest-resto-ha/releases) page.
2. Copy the `custom_components/howest_resto` directory to your Home Assistant's `custom_components/` directory.
3. Restart Home Assistant.

---

## ⚙️ Configuration

1. In Home Assistant, navigate to **Settings → Devices & Services → Add Integration**.
2. Search for **Howest Resto**.
3. Select your campus from the dropdown:
   - `'t Obeetje (Graaf Karel de Goedelaan 5, Kortrijk)`
   - `Plaza (Sint-Martens-Latemlaan 1B, Kortrijk)`
   - `The Square (Luipaardstraat 12A, Kortrijk)`
   - `YUM (Rijselstraat 5, Brugge)`
   - `DAD (Spoorwegstraat 4, Brugge)`
   - `BSI (Nijverheidsstraat 112, Brugge)`
4. Click **Submit**. You can repeat this process to add multiple campuses.

### Options

Click **Configure** on the integration card to adjust:
- **Update interval**: Scan frequency in minutes (default: 60 minutes).
- **Preferred display language**: Choose between Dutch (`dutch`), English (`english`), or bilingual (`both`).

---

## 📊 Entities & Platforms

### Sensors

| Entity | Translation Key | Description |
|---|---|---|
| `sensor.howest_resto_<campus>_today_s_menu` | `today_menu` | Dishes served today (or `Closed` if weekend/no menu) |
| `sensor.howest_resto_<campus>_tomorrow_s_menu` | `tomorrow_menu` | Dishes served tomorrow |
| `sensor.howest_resto_<campus>_weekly_menu` | `weekly_menu` | Number of days with menu available, with full week payload in attributes |

### Calendar

| Entity | Description |
|---|---|
| `calendar.howest_resto_<campus>_menu_calendar` | Displays each day's lunch menu as an all-day calendar event with dish breakdowns |

---

## 💡 Example Automation

Send a notification to your phone every weekday at 11:30 AM with today's lunch menu:

```yaml
alias: "Notify Today's Howest Lunch"
trigger:
  - platform: time
    at: "11:30:00"
condition:
  - condition: time
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri
  - condition: not
    conditions:
      - condition: state
        entity_id: sensor.howest_resto_t_obeetje_today_s_menu
        state: "Closed"
action:
  - service: notify.notify
    data:
      title: "🍽️ Lunch at 't Obeetje"
      message: "{{ states('sensor.howest_resto_t_obeetje_today_s_menu') }}"
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
