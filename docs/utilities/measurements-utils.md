<!-- --8<-- [start:pipe-definition] -->

=== All measurements
```python
nlp = edsnlp.blank("eds")
nlp.add_pipe("eds.sentences")
nlp.add_pipe("eds.tables")
nlp.add_pipe(
    "eds.measurements",
    config=dict(measurements="all", extract_ranges=True),
)
nlp(
    """Poids : 65. Taille : 1.75
On mesure ... à 3mmol/l ; pression : 100mPa-110mPa.
Acte réalisé par ... à 12h13"""
).spans["measurements"]
# Out: [65, 1.75, 3mmol/l, 100mPa-110mPa, 12h13]
```
=== Custom measurements
```python
nlp = edsnlp.blank("eds")
nlp.add_pipe("eds.sentences")
nlp.add_pipe("eds.tables")
nlp.add_pipe(
    "eds.measurements",
    config=dict(
        measurements={
            "concentration": {"unit": "mol_per_l"},
            "pressure": {"unit": "Pa"},
        },
        extract_ranges=True,
    ),
)
nlp(
    """Poids : 65. Taille : 1.75
On mesure ... à 3mmol/l ; pression : 100mPa-110mPa.
Acte réalisé par ... à 12h13"""
).spans["measurements"]
# Out: [3mmol/l, 100mPa-110mPa]
```
=== Predefined measurements
```python
nlp = edsnlp.blank("eds")
nlp.add_pipe("eds.sentences")
nlp.add_pipe("eds.tables")
nlp.add_pipe(
    "eds.measurements",
    config=dict(
        measurements=["weight", "size"],
        extract_ranges=True
    ),
)
nlp("""Poids : 65. Taille : 1.75
On mesure ... à 3mmol/l ; pression : 100mPa-110mPa.
Acte réalisé par ... à 12h13""").spans["measurements"]
# Out: [65, 1.75]

<!-- --8<-- [end:pipe-definition] -->

<!-- --8<-- [start:availability] -->

Availability
--------------------
See `edsnlp.pipes.misc.measurements.patterns` for exhaustive definition.
=== Available measurements
| measurement_name | Example                |
|------------------|------------------------|
| `size`           | `1m50`, `1.50m`...     |
| `weight`         | `12kg`, `1kg300`...    |
| `bmi`            | `BMI: 24`, `24 kg.m-2` |
| `volume`         | `2 cac`, `8ml`...      |
=== Available units
| units                          | Example                |
|--------------------------------|------------------------|
| `mass`                         | `10kgr`, `100mg`...    |
| `mole`                         | `10mmol`, `3mol`...    |
| `length`, `surface`, `volume`  | `12m`, `1cm2`, 0.1l... |
| `time`                         | `1h`,  `2min15`...     |
| `pressure`                     | `1kPa`, `100mmHg`...   |
| `temperature`                  | `5°C`, `100mmHg`...    |
| `count`                        | `2.2x10*2` ...         |

<!-- --8<-- [end:availability] -->
