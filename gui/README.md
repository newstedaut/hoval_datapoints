# gui.csv

Usage/icon/category layer, kept separate from `datapoints.csv` and `translations.csv`
so it never collides with the raw (fg, fn, dp) keys or their names.

## Two-tier approach (proposed 30.08.2026, following discussion #50)

Most datapoints don't need a hand-picked icon — the **unit already implies a sensible
Home Assistant `device_class` + `icon`** (°C → temperature, kWh → energy, % → power_factor
or humidity depending on the name, m³/h → volume_flow_rate, bar/Pa → pressure, ...).
[nliaudat](https://github.com/nliaudat/esp_canbus) pointed out his own per-datapoint
icon mapping is really just this rule applied by hand.

So instead of hand-filling `gui.csv` for every single datapoint:

1. **Default tier (code, not CSV):** a small `unit -> {device_class, icon,
   unit_of_measurement}` lookup function (see `esp_canbus`'s implementation) covers the
   large majority of datapoints automatically. Belongs in each consumer project
   (HA integration, exporter, ...), not duplicated as data here, since it's pure
   derivation logic with no Hoval-specific content.
2. **`gui.csv` (this file, committed) is only for the exceptions the default tier
   can't get right:** ambiguous units (e.g. plain `%` that's a valve/modulation
   position, not humidity or power factor), and the `category` grouping for a
   dashboard (heating/dhw/cooling/ventilation/smartgrid), which can't be derived
   from the unit alone.

Schema (matches the `(1)/(2)/(3)` heating-circuit-suffix convention already used in
[nliaudat/esp_canbus](https://github.com/nliaudat/esp_canbus)'s presets):

| column   | meaning                                            |
|----------|-----------------------------------------------------|
| fg       | function group                                       |
| fn       | function number (heating-circuit index: 0/1/2 = HC1/2/3) |
| dp       | datapoint id                                         |
| icon     | Material Design Icons name (`mdi-*`) — only set when it should override the unit-based default |
| category | grouping for a UI (e.g. "heating", "dhw", "cooling", "ventilation", "smartgrid") |

Empty for now. Still open: should the unit→icon default function itself live in this
repo too (e.g. `tools/gui_defaults.py`), shared across consumer projects, so everyone
gets the same default mapping instead of reimplementing it? Up for discussion in #50.
