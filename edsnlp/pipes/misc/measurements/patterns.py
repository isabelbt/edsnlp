import itertools


def update_config_per(configs: dict) -> dict:
    output_configs = {}
    for key, config in configs.items():
        if "per" in config.keys():
            per_config = {
                "dim": config["dim"],
                "degree": -1 * config["degree"],
                "scale": 1 / config["scale"],
                "terms": config["per"],
                "followed_by": None,
            }
            config.pop("per")
            output_configs.update({f"per_{key}": per_config})
        output_configs.update({key: config})
    return output_configs


def get_scaled_terms(terms, scale_prefix):
    """Generate scaled terms."""
    return [f"{scale}{term}" for term, scale in itertools.product(terms, scale_prefix)]


def create_scaled_config(key, config, scale_prefix, scale_value):
    """Create a scaled configuration dictionary."""
    if key.startswith("per_"):
        scale_value = 1 / scale_value
        scaled_key = f"per_{scale_prefix[0]}{key[4:]}"
    else:
        scaled_key = f"{scale_prefix[0]}{key}"

    return {
        scaled_key: {
            "dim": config["dim"],
            "degree": config["degree"],
            "scale": scale_value,
            "terms": get_scaled_terms(config["terms"], scale_prefix),
            "followed_by": None,
        }
    }


def update_config_scale(configs):
    """Update configurations with scale units and values."""
    scales_prefixes = [
        ("k", "kilo", "kilo-"),
        ("h", "hecto", "hecto-"),
        ("da", "deca", "deca-"),
        ("d", "deci", "deci-"),
        ("c", "centi", "centi-"),
        ("m", "milli", "milli-"),
        ("μ", "u", r"µ", "micro", "micro-"),
        ("n", "nano", "nano-"),
        ("p", "pico", "pico-"),
        ("f", "femto", "femto-"),
    ]
    scales_values = [1e3, 1e2, 1e1, 1e-1, 1e-2, 1e-3, 1e-6, 1e-9, 1e-12, 1e-15]

    output_configs = {}

    for key, config in configs.items():
        for scale_prefix, scale_value in zip(scales_prefixes, scales_values):
            scaled_config = create_scaled_config(key, config, scale_prefix, scale_value)
            output_configs.update(scaled_config)

        output_configs[key] = config

    return output_configs


number_terms = {
    "0.125": ["⅛"],
    "0.16666666": ["⅙"],
    "0.2": ["⅕"],
    "0.25": ["¼"],
    "0.3333333": ["⅓"],
    "0.5": ["½"],
    "2.5": ["21/2"],
    "1": ["un", "une"],
    "2": ["deux"],
    "3": ["trois"],
    "4": ["quatre"],
    "5": ["cinq"],
    "6": ["six"],
    "7": ["sept"],
    "8": ["huit"],
    "9": ["neuf"],
    "10": ["dix"],
    "11": ["onze"],
    "12": ["douze"],
    "13": ["treize"],
    "14": ["quatorze"],
    "15": ["quinze"],
    "16": ["seize"],
    "17": ["dix-sept", "dix sept"],
    "18": ["dix-huit", "dix huit"],
    "19": ["dix-neuf", "dix neuf"],
    "20": ["vingt", "vingts"],
    "30": ["trente"],
    "40": ["quarante"],
    "50": ["cinquante"],
    "60": ["soixante"],
    "70": ["soixante dix", "soixante-dix"],
    "80": ["quatre vingt", "quatre-vingt", "quatre vingts", "quatre-vingts"],
    "90": ["quatre vingt dix", "quatre-vingt-dix"],
    "100": ["cent"],
    "500": ["cinq cent", "cinq-cent"],
    "1000": ["mille", "milles"],
}


number_regex = r"""(?x)
# no digit or floating point number prefix before
(?<![0-9][.,]?)
# integer part like 123 or 1 234
(?:
    0
    |[1-9][0-9]*(?:\ \d{3})*
)
(?:
    # floating point surounded by spaces
    \ +[,.]\ +\d+
    # floating point w/o space
    | [,.]\d+
    # fractions
    | (?:\ /\ |/)[1-9][0-9]*(?:\ \d{3})*
)?"""


common_measurements = {
    "weight": {
        "unit": "kg",
        "unitless_patterns": [
            {
                "terms": ["poids", "poid", "pese", "pesant", "pesait", "pesent"],
                "ranges": [
                    {"min": 0, "max": 200, "unit": "kg"},
                    {"min": 200, "unit": "g"},
                ],
            }
        ],
    },
    "size": {
        "unit": "m",
        "unitless_patterns": [
            {
                "terms": [
                    "mesure",
                    "taille",
                    "mesurant",
                    "mesurent",
                    "mesurait",
                    "mesuree",
                    "hauteur",
                    "largeur",
                    "longueur",
                ],
                "ranges": [
                    {"min": 0, "max": 3, "unit": "m"},
                    {"min": 3, "unit": "cm"},
                ],
            }
        ],
    },
    "bmi": {
        "unit": "kg_per_m2",
        "unitless_patterns": [
            {"terms": ["imc", "bmi"], "ranges": [{"unit": "kg_per_m2"}]}
        ],
    },
    "volume": {"unit": "m3", "unitless_patterns": []},
}

unit_divisors = ["/", "par"]

stopwords = ["par", "sur", "de", "a", ",", "et", "-", "à"]

# Should we only make accented patterns and expect the user to use
# `eds.normalizer` component first ?
range_patterns = [
    ("De", "à"),
    ("De", "a"),
    ("de", "à"),
    ("de", "a"),
    ("Entre", "et"),
    ("entre", "et"),
    (None, "a"),
    (None, "à"),
    (None, "-"),
]


units_config = {
    "g": {
        "dim": "mass",
        "degree": 1,
        "scale": 1,
        "terms": ["gramme", "grammes", "gr", "g"],
        "per": ["g-1", "gr-1", "gr⁻¹", "g⁻¹"],
        "followed_by": None,
    },
    "m": {
        "dim": "length",
        "degree": 1,
        "scale": 1,
        "terms": ["metre", "metres", "m"],
        "per": ["m-1", "m⁻¹"],
        "followed_by": "cm",
    },
    "m2": {
        "dim": "length",
        "degree": 2,
        "scale": 1,
        "terms": ["m2", "m²"],
        "per": ["m-2", "m⁻²"],
        "followed_by": None,
    },
    "m3": {
        "dim": "length",
        "degree": 3,
        "scale": 1,
        "terms": ["m3", "m³"],
        "per": ["m-3", "m⁻³"],
        "followed_by": None,
    },
    "l": {
        "dim": "length",
        "degree": 3,
        "scale": 1e3,
        "terms": ["litre", "litres", "l", "dm3"],
        "per": ["l-1", "l⁻¹"],
        "followed_by": "ml",
    },
    "mol": {
        "dim": "mole",
        "degree": 1,
        "scale": 1,
        "terms": ["mol", "mole", "moles"],
        "followed_by": None,
    },
    "ui": {
        "dim": "ui",
        "degree": 1,
        "scale": 1,
        "terms": ["ui", "u"],
        "per": ["ui-1", "ui⁻¹"],
        "followed_by": None,
    },
    "Pa": {"dim": "Pa", "degree": 1, "scale": 1, "terms": ["Pa"], "followed_by": None},
}

units_config = update_config_per(units_config)
units_config = update_config_scale(units_config)
units_config["kg"]["followed_by"] = "g"
units_config["m"]["followed_by"] = "cm"

units_config.update(
    {
        "%": {"dim": "%", "degree": 1, "scale": 1, "terms": ["%"], "followed_by": None},
        "log": {
            "dim": "log",
            "degree": 1,
            "scale": 1,
            "terms": ["log"],
            "followed_by": None,
        },
        "mmHg": {
            "dim": "mmHg",
            "degree": 1,
            "scale": 1,
            "terms": ["mmHg"],
            "followed_by": None,
        },
        "x10*9": {
            "dim": "count",
            "degree": 1,
            "scale": 1,
            "terms": ["x10*9"],
            "followed_by": None,
        },
        # Durations
        "second": {
            "dim": "time",
            "degree": 1,
            "scale": 1,
            "terms": ["seconde", "secondes", "s"],
            "followed_by": None,
        },
        "minute": {
            "dim": "time",
            "degree": 1,
            "scale": 60,
            "terms": ["mn", "min", "minute", "minutes"],
            "followed_by": "second",
        },
        "hour": {
            "dim": "time",
            "degree": 1,
            "scale": 3600,
            "terms": ["heure", "heures", "h"],
            "followed_by": "minute",
        },
        "day": {
            "dim": "time",
            "degree": 1,
            "scale": 3600 * 24,
            "terms": ["jour", "jours", "j"],
            "followed_by": None,
        },
        "month": {
            "dim": "time",
            "degree": 1,
            "scale": 3600 * 24 * 30.4167,
            "terms": ["mois"],
            "followed_by": None,
        },
        "week": {
            "dim": "time",
            "degree": 1,
            "scale": 3600 * 24 * 7,
            "terms": ["semaine", "semaines", "sem"],
            "followed_by": None,
        },
        "year": {
            "dim": "time",
            "degree": 1,
            "scale": 3600 * 24 * 365.25,
            "terms": ["an", "année", "ans", "années"],
            "followed_by": None,
        },
        # Angle
        "arc-second": {
            "dim": "time",
            "degree": 1,
            "scale": 2 / 60.0,
            "terms": ['"', "''"],
            "followed_by": None,
        },
        "arc-minute": {
            "dim": "time",
            "degree": 1,
            "scale": 2,
            "terms": ["'"],
            "followed_by": "arc-second",
        },
        "degree": {
            "dim": "time",
            "degree": 1,
            "scale": 120,
            "terms": ["degre", "°", "deg"],
            "followed_by": "arc-minute",
        },
        # Temperature
        "celsius": {
            "dim": "temperature",
            "degree": 1,
            "scale": 1,
            "terms": ["°C", "° celsius", "celsius"],
            "followed_by": None,
        },
        "cac": {
            "dim": "length",
            "degree": 3,
            "scale": 5e0,
            "terms": ["cac", "c.a.c", "cuillere à café", "cuillères à café"],
            "followed_by": None,
        },
        "goutte": {
            "dim": "length",
            "degree": 3,
            "scale": 5e-2,
            "terms": ["gt", "goutte", "gouttes"],
            "followed_by": None,
        },
    }
)
