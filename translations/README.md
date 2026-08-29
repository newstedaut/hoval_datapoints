# translations.csv

Names + descriptions per `(fg, fn, dp)` key, generated from Hoval's own DE/EN text
columns via `tools/generate_translations.py`. Not committed here (would mean
re-hosting Hoval's copyrighted text) -- generate your own from the current xlsx:

```bash
python3 tools/generate_datapoints.py your-copy.xlsx        # -> datapoints.csv
python3 tools/generate_translations.py your-copy.xlsx datapoints.csv
```

Columns: `fg, fn, dp, name_de, desc_de, name_en, desc_en`.

Hoval maintains the English column patchily -- where `desc_en`/`name_en` is empty,
fall back to the German column.
