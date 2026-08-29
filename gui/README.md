# gui.csv

Usage/icon layer, kept separate from `datapoints.csv` and `translations.csv` so it
never collides with the raw (fg, fn, dp) keys or their names.

Proposed schema (matches the `(1)/(2)/(3)` heating-circuit-suffix convention already
used in [nliaudat/esp_canbus](https://github.com/nliaudat/esp_canbus)'s presets):

| column   | meaning                                            |
|----------|-----------------------------------------------------|
| fg       | function group                                       |
| fn       | function number (heating-circuit index: 0/1/2 = HC1/2/3) |
| dp       | datapoint id                                         |
| icon     | Material Design Icons name (`mdi-*`), for dashboard use |
| category | grouping for a UI (e.g. "heating", "dhw", "cooling", "ventilation", "smartgrid") |

Empty for now -- this is the layer [nliaudat/esp_canbus](https://github.com/nliaudat/esp_canbus)
already has richer data for (multi-language display names + icons per datapoint).
First PR here is intended to import that mapping rather than rebuild it from scratch.
