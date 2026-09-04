# hoval_datapoints

[![Buy Me a Coffee](https://img.shields.io/badge/☕-Buy%20me%20a%20coffee-ffdd00)](https://buymeacoffee.com/bernhardsu9) [![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=HWBBHDSVD3MCC)

**Shared, community-maintained datapoint catalogue for the Hoval® TopTronic® E CAN/Modbus
protocol** — one source of truth for the `(function group, function number, datapoint id)`
triples used by every project reverse-engineering this bus, instead of three or four
projects each maintaining their own incompatible copy.

> **Disclaimer:** independent open-source project, **not affiliated with Hoval AG**.
> Hoval® and TopTronic® are trademarks of Hoval AG. Use at your own risk — you are
> interfacing with your own heating system.

## Why this repo exists

Several independent projects talk to the same Hoval TopTronic E bus and had each
built their own datapoint list:

- [nliaudat/esp_canbus](https://github.com/nliaudat/esp_canbus) — ESP32 CAN shield, reads sensors + writes humidity/modulation in constant mode, has multi-language display names + icons
- [newstedaut/HoxPi](https://github.com/newstedaut/HoxPi) — Raspberry Pi + CAN, emulates Hoval's own Modbus-TCP gateway so the official Loxone templates work 1:1
- [hpoeckl/hoval-exporter](https://github.com/hpoeckl/hoval-exporter) — Prometheus exporter, first to document the FA/compressor level (see below)
- [parren/hoval-ultrasource-agent](https://github.com/parren/hoval-ultrasource-agent), [zittix/Hoval-GW](https://github.com/zittix/Hoval-GW), [chrishrb/hoval-gateway](https://github.com/chrishrb/hoval-gateway)

This repo grew out of a [discussion between two of those projects](https://github.com/nliaudat/esp_canbus/discussions/50)
about writing datapoints beyond what Hoval's own Modbus gateway exposes, and the
realization that merging efforts helps everyone more than three parallel lists.

## Structure (3 layers, deliberately kept separate)

| File / generator | Contents | Committed to git? |
|---|---|---|
| `tools/generate_datapoints.py` → `datapoints.csv` | the raw `(fg, fn, dp, type, scale, min, max, writable, unit)` catalogue | **No** — generate locally (see below) |
| `tools/generate_translations.py` → `translations.csv` | DE/EN names + descriptions keyed by `(fg, fn, dp)` | **No** — generate locally |
| `gui/gui.csv` | mdi-icon + usage/category mapping for dashboards | Yes (once seeded — see `gui/README.md`) |
| `community_additions/<device>/*.csv` | datapoints **not** in Hoval's own list, purely from independent reverse-engineering | **Yes** — this is our own work, freely shareable |

**Why the raw list isn't committed:** the datapoint catalogue is derived from Hoval's
own copyrighted `TTE-GW-Modbus-datapoints.xlsx`. Rather than re-hosting a derivative
of that file, this repo ships only a small generator — point it at your own local copy
of Hoval's public spreadsheet (downloadable from hoval.com, see the script's docstring)
and it produces `datapoints.csv` / `translations.csv` locally. This is the same
approach [HoxPi](https://github.com/newstedaut/HoxPi) already uses in production, and
it means the catalogue is always current with whatever version of the list Hoval
publishes — no stale re-hosted copy to fall out of sync.

```bash
python3 tools/generate_datapoints.py your-copy-of-TTE-GW-Modbus-datapoints.xlsx
python3 tools/generate_translations.py your-copy-of-TTE-GW-Modbus-datapoints.xlsx datapoints.csv
```

## Community additions

The real community value is what's **not** in Hoval's own list — datapoints found by
listening to the bus that answer but were never documented anywhere.

**Layout:** one subfolder per device/subsystem under `community_additions/` (e.g.
`WEZ` = heat generator/compressor level, `HK` = heating circuit, `KWL` = ventilation,
`SG` = smart grid). Keeps the list navigable as more devices and contributors are
added instead of one growing flat folder.

- **`community_additions/WEZ/fa_level_fg60_fn254.csv`** — the compressor/refrigerant-circuit
  "FA" level (`fg=60, fn=254`), readable over the poll arbitration ID `0x06E40801`.
  Verified live on a Hoval UltraSource B comfort C17: lifetime energy counters
  (heating/cooling/DHW in MWh — enables a real seasonal performance factor), live COP,
  refrigerant/source temperatures, water pressure, cooling setpoint. First documented
  by [hpoeckl/hoval-exporter](https://github.com/hpoeckl/hoval-exporter), independently
  confirmed and extended here.

- **`community_additions/WEZ/hydraulics_fg60_fn7.csv`** — the hydraulic level of the
  heat pump (`fg=60, fn=7`): heat-pump flow/return temperature, internal circulation
  pump speed (**0xFFFFFFFF = pump off**) and averaged volume flow. Physics check: flow x
  spread reproduces the controller's own thermal power. **Update 04.09.2026:** the
  refrigerant-circuit datapoints in this group DO answer on an air-source UltraSource B —
  outdoor-unit air inlet, suction gas and hot gas temperature, suction superheat, low- and
  high-side pressure and compressor actual speed (dp 262/263/264/514/518/519/1282, each
  verified against the compressor controller's own database) — but only in one of two
  coupling states: after a mains power cycle they answer while the `fn=254` block dp 20-34
  (error code, return temperature, power, WEZ status) goes silent, and before the power
  cycle it was exactly the other way round. Both CSVs now carry that availability note;
  poll both groups and treat "no answer" as unavailable. The name column of the matching
  Modbus block 31892-31921 is shifted by rows in the public list.
- **`community_additions/WEZ/system_output_setpoints.csv`** — the power setpoint per
  operating mode (`fg=3`, dp 2040/2041/2042) plus the aggregate channel and request flag
  (`fg=4`, dp 1009/2043). Two traps documented: **-127.0 is an invalid marker while
  -100.0 is a valid reading**, and dp 2043 is binary despite being named "0-100% current
  req.". Useful as an early indicator that the compressor is about to start — explicitly
  *not* a start criterion.
- **`community_additions/WEZ/heat_generator_status_codes.csv`** — status codes for the
  heat generator, including **16, 51, 17, 44 and 98, which appear on the bus but in no
  Hoval status list**. Code 16 is proposed as the restart lockout (54 of 54 observed
  blocks sit between a stop and the next start with a demand pending, capped at 15 min).
  Confidence is carried per row, so unverified codes stay visible as unverified.
- **`community_additions/WEZ/corrections_runtime_counters.csv`** — *corrections* to
  Hoval's own list: dp 1034/1035 carry contradictory names in different places (the
  values decide: 1034 = cooling, 1035 = DHW), and 31 of 116 32-bit registers name their
  low word `... low` with a space instead of `..._low`, which silently breaks consumers
  that detect the low word by name suffix.
- **`community_additions/HC/undocumented_fg1.csv`** — heating-circuit datapoints that
  answer a GET but are absent from Hoval's list. Only `1-0-7014` is confirmed; the rest
  are marked UNVERIFIED on purpose.

Contributions of further undocumented datapoints (with the fg/fn/dp, a decode, and how
it was verified) are very welcome — open a PR or an issue. New device/subsystem →
new subfolder.

## Protocol basics (for newcomers)

- Datapoint = triple `(fg, fn, dp)`. `dp` is the control-panel parameter number without
  its dash: `07-044` → `7044`, `03-051` → `3051`.
- `fn` is usually the heating-circuit index: `fn=0` → HC1, `fn=1` → HC2, `fn=2` → HC3.
- SET frame (from the operating module's own arbitration ID, e.g. `0x1FE08801`):
  `[0x01, 0x46, fg, fn, dp_hi, dp_lo] + value_bytes`. `0x40` = GET, `0x42` = ANSWER, `0x46` = SET.
- A GET that never answers usually means write-only or session/page-dependent, not
  "unsupported" — see the write-behaviour notes each project has accumulated.

Full protocol write-up: [esp_canbus discussion #50](https://github.com/nliaudat/esp_canbus/discussions/50).

## Contributing

- Found a new datapoint? Add it to `community_additions/<device>/` (new device → new subfolder) with fg/fn/dp, a name, type,
  scale/unit, and how you verified it (candump capture, panel comparison, ...).
- Found an error in an existing entry? PRs welcome, same rule: say how you verified it.
- Please don't attach Hoval's own spreadsheet or copy its text verbatim into an issue/PR —
  link to the public download instead.

## Credits

Everyone listed under "Why this repo exists" above, and the original protocol
reverse-engineering that made all of these projects possible.

