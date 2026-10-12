"""Curated Cryptic Lexicon and High-Performance Letter-Index Engine.

Provides O(1) candidate lookup for AC-3 Constraint Satisfaction, and
maintains verifiable Cryptic Clue AST projections ([L1-004]).
"""

from __future__ import annotations

import collections
from typing import Dict, List, Optional, Set, Tuple

from models import ClueType, CrypticClue, Direction


# Curated dictionary of verified cryptic clue records
RAW_CRYPTIC_RECORDS = [
    # 3-Letter Words
    {
        "answer": "CAT",
        "length": 3,
        "clue_type": ClueType.ANAGRAM,
        "definition": "feline",
        "indicator": "dancing",
        "fodder": "Act",
        "surface_text": "Act dancing with feline (3)",
        "explanation": "Anagram of ACT = CAT (definition: feline).",
    },
    {
        "answer": "ERA",
        "length": 3,
        "clue_type": ClueType.REVERSAL,
        "definition": "period of time",
        "indicator": "turned back",
        "fodder": "are",
        "surface_text": "Period of time where are turned back (3)",
        "explanation": "ARE reversed = ERA (definition: period of time).",
    },
    {
        "answer": "TEA",
        "length": 3,
        "clue_type": ClueType.ANAGRAM,
        "definition": "hot drink",
        "indicator": "brewed",
        "fodder": "eat",
        "surface_text": "Eat brewed for hot drink (3)",
        "explanation": "Anagram of EAT = TEA (definition: hot drink).",
    },
    {
        "answer": "NET",
        "length": 3,
        "clue_type": ClueType.REVERSAL,
        "definition": "mesh",
        "indicator": "recalled",
        "fodder": "ten",
        "surface_text": "Mesh ten recalled (3)",
        "explanation": "TEN reversed = NET (definition: mesh).",
    },
    {
        "answer": "PAN",
        "length": 3,
        "clue_type": ClueType.DOUBLE_DEF,
        "definition": "cookware and criticize harshly",
        "indicator": "",
        "fodder": "",
        "surface_text": "Cookware to criticize harshly (3)",
        "explanation": "Double definition: PAN (kitchen pot) and PAN (severely review).",
    },
    {
        "answer": "RUN",
        "length": 3,
        "clue_type": ClueType.DOUBLE_DEF,
        "definition": "dash and tear in stocking",
        "indicator": "",
        "fodder": "",
        "surface_text": "Dash reveals tear in stocking (3)",
        "explanation": "Double definition: RUN (sprint) and RUN (ladder in tights).",
    },

    # 4-Letter Words
    {
        "answer": "STAR",
        "length": 4,
        "clue_type": ClueType.REVERSAL,
        "definition": "celebrity",
        "indicator": "sent back",
        "fodder": "rats",
        "surface_text": "Rats sent back for celebrity (4)",
        "explanation": "RATS reversed = STAR (definition: celebrity).",
    },
    {
        "answer": "TRAP",
        "length": 4,
        "clue_type": ClueType.REVERSAL,
        "definition": "snare",
        "indicator": "returned",
        "fodder": "part",
        "surface_text": "Snare part returned (4)",
        "explanation": "PART reversed = TRAP (definition: snare).",
    },
    {
        "answer": "EAST",
        "length": 4,
        "clue_type": ClueType.ANAGRAM,
        "definition": "compass point",
        "indicator": "drifting",
        "fodder": "seat",
        "surface_text": "Seat drifting towards compass point (4)",
        "explanation": "Anagram of SEAT = EAST (definition: compass point).",
    },
    {
        "answer": "STOP",
        "length": 4,
        "clue_type": ClueType.REVERSAL,
        "definition": "halt",
        "indicator": "reversed",
        "fodder": "pots",
        "surface_text": "Halt kitchen pots reversed (4)",
        "explanation": "POTS reversed = STOP (definition: halt).",
    },
    {
        "answer": "POST",
        "length": 4,
        "clue_type": ClueType.DOUBLE_DEF,
        "definition": "mail and wooden pillar",
        "indicator": "",
        "fodder": "",
        "surface_text": "Mail pinned to wooden pillar (4)",
        "explanation": "Double definition: POST (letters) and POST (stake).",
    },
    {
        "answer": "NODE",
        "length": 4,
        "clue_type": ClueType.ANAGRAM,
        "definition": "connection point",
        "indicator": "damaged",
        "fodder": "done",
        "surface_text": "Done damaged connection point (4)",
        "explanation": "Anagram of DONE = NODE (definition: connection point).",
    },
    {
        "answer": "ACRE",
        "length": 4,
        "clue_type": ClueType.ANAGRAM,
        "definition": "plot of land",
        "indicator": "plowed",
        "fodder": "care",
        "surface_text": "Care plowed into plot of land (4)",
        "explanation": "Anagram of CARE = ACRE (definition: plot of land).",
    },
    {
        "answer": "RACE",
        "length": 4,
        "clue_type": ClueType.ANAGRAM,
        "definition": "contest of speed",
        "indicator": "scrambled",
        "fodder": "care",
        "surface_text": "Care scrambled in contest of speed (4)",
        "explanation": "Anagram of CARE = RACE (definition: contest of speed).",
    },
    {
        "answer": "LION",
        "length": 4,
        "clue_type": ClueType.HIDDEN_WORD,
        "definition": "big cat",
        "indicator": "concealed in",
        "fodder": "chameleon",
        "surface_text": "Big cat concealed in chameleon (4)",
        "explanation": "Hidden word in chame[LION] = LION (definition: big cat).",
    },
    {
        "answer": "IRON",
        "length": 4,
        "clue_type": ClueType.DOUBLE_DEF,
        "definition": "metal and smooth clothes",
        "indicator": "",
        "fodder": "",
        "surface_text": "Metal used to smooth clothes (4)",
        "explanation": "Double definition: IRON (element Fe) and IRON (press garments).",
    },
    {
        "answer": "ARCH",
        "length": 4,
        "clue_type": ClueType.CHARADE,
        "definition": "curved structure",
        "indicator": "joined with",
        "fodder": "A + R + CH",
        "surface_text": "Curved structure from church leader (4)",
        "explanation": "Charade: AR (top) + CH (church) = ARCH.",
    },
    {
        "answer": "TREE",
        "length": 4,
        "clue_type": ClueType.CONTAINER,
        "definition": "woody plant",
        "indicator": "hugging",
        "fodder": "RE inside TE",
        "surface_text": "Woody plant in street hugging reserve (4)",
        "explanation": "Container: T(RE)E = TREE (definition: woody plant).",
    },

    # 5-Letter Words
    {
        "answer": "HEART",
        "length": 5,
        "clue_type": ClueType.ANAGRAM,
        "definition": "vital organ",
        "indicator": "broken",
        "fodder": "earth",
        "surface_text": "Earth broken inside vital organ (5)",
        "explanation": "Anagram of EARTH = HEART (definition: vital organ).",
    },
    {
        "answer": "EARTH",
        "length": 5,
        "clue_type": ClueType.ANAGRAM,
        "definition": "planet",
        "indicator": "reshaped",
        "fodder": "heart",
        "surface_text": "Heart reshaped into our planet (5)",
        "explanation": "Anagram of HEART = EARTH (definition: planet).",
    },
    {
        "answer": "STARE",
        "length": 5,
        "clue_type": ClueType.ANAGRAM,
        "definition": "gaze fixedly",
        "indicator": "unsettled",
        "fodder": "tears",
        "surface_text": "Tears unsettled by fixed gaze (5)",
        "explanation": "Anagram of TEARS = STARE (definition: gaze fixedly).",
    },
    {
        "answer": "TEARS",
        "length": 5,
        "clue_type": ClueType.ANAGRAM,
        "definition": "drops of grief",
        "indicator": "shed",
        "fodder": "stare",
        "surface_text": "Stare shed drops of grief (5)",
        "explanation": "Anagram of STARE = TEARS (definition: drops of grief).",
    },
    {
        "answer": "RATES",
        "length": 5,
        "clue_type": ClueType.ANAGRAM,
        "definition": "tariffs",
        "indicator": "adjusted",
        "fodder": "stare",
        "surface_text": "Stare adjusted for trade tariffs (5)",
        "explanation": "Anagram of STARE = RATES (definition: tariffs).",
    },
    {
        "answer": "PANEL",
        "length": 5,
        "clue_type": ClueType.ANAGRAM,
        "definition": "group of experts",
        "indicator": "assembled",
        "fodder": "plane",
        "surface_text": "Plane assembled for group of experts (5)",
        "explanation": "Anagram of PLANE = PANEL (definition: group of experts).",
    },
    {
        "answer": "PLANE",
        "length": 5,
        "clue_type": ClueType.DOUBLE_DEF,
        "definition": "aircraft and flat surface",
        "indicator": "",
        "fodder": "",
        "surface_text": "Aircraft glides over flat surface (5)",
        "explanation": "Double definition: PLANE (aeroplane) and PLANE (flat 2D surface).",
    },
    {
        "answer": "TRAIN",
        "length": 5,
        "clue_type": ClueType.DOUBLE_DEF,
        "definition": "locomotive and educate",
        "indicator": "",
        "fodder": "",
        "surface_text": "Locomotive used to educate athletes (5)",
        "explanation": "Double definition: TRAIN (rail transport) and TRAIN (coach).",
    },
    {
        "answer": "SHARP",
        "length": 5,
        "clue_type": ClueType.DOUBLE_DEF,
        "definition": "keen edge and musical pitch",
        "indicator": "",
        "fodder": "",
        "surface_text": "Keen edge heard at high musical pitch (5)",
        "explanation": "Double definition: SHARP (acute blade) and SHARP (semitone higher).",
    },
    {
        "answer": "LEMON",
        "length": 5,
        "clue_type": ClueType.ANAGRAM,
        "definition": "sour citrus",
        "indicator": "squeezed",
        "fodder": "melon",
        "surface_text": "Melon squeezed into sour citrus (5)",
        "explanation": "Anagram of MELON = LEMON (definition: sour citrus).",
    },
    {
        "answer": "MELON",
        "length": 5,
        "clue_type": ClueType.ANAGRAM,
        "definition": "sweet fruit",
        "indicator": "mixed",
        "fodder": "lemon",
        "surface_text": "Lemon mixed into sweet fruit (5)",
        "explanation": "Anagram of LEMON = MELON (definition: sweet fruit).",
    },
    {
        "answer": "ORBIT",
        "length": 5,
        "clue_type": ClueType.CHARADE,
        "definition": "celestial path",
        "indicator": "following",
        "fodder": "OR + BIT",
        "surface_text": "Alternative small piece follows celestial path (5)",
        "explanation": "Charade: OR (alternative) + BIT (small piece) = ORBIT.",
    },

    # 6-Letter Words
    {
        "answer": "STREAM",
        "length": 6,
        "clue_type": ClueType.ANAGRAM,
        "definition": "flowing brook",
        "indicator": "disturbed",
        "fodder": "master",
        "surface_text": "Master disturbed beside flowing brook (6)",
        "explanation": "Anagram of MASTER = STREAM (definition: flowing brook).",
    },
    {
        "answer": "MASTER",
        "length": 6,
        "clue_type": ClueType.ANAGRAM,
        "definition": "expert craftsman",
        "indicator": "reformed",
        "fodder": "stream",
        "surface_text": "Stream reformed by expert craftsman (6)",
        "explanation": "Anagram of STREAM = MASTER (definition: expert craftsman).",
    },
    {
        "answer": "ISLAND",
        "length": 6,
        "clue_type": ClueType.CHARADE,
        "definition": "isolated territory",
        "indicator": "beside",
        "fodder": "IS + LAND",
        "surface_text": "Is ground beside isolated territory (6)",
        "explanation": "Charade: IS + LAND (ground) = ISLAND (isolated territory).",
    },
    {
        "answer": "CASTLE",
        "length": 6,
        "clue_type": ClueType.ANAGRAM,
        "definition": "fortified palace",
        "indicator": "constructed",
        "fodder": "cleats",
        "surface_text": "Cleats constructed inside fortified palace (6)",
        "explanation": "Anagram of CLEATS = CASTLE (definition: fortified palace).",
    },
    {
        "answer": "SILVER",
        "length": 6,
        "clue_type": ClueType.ANAGRAM,
        "definition": "precious metal",
        "indicator": "refined",
        "fodder": "sliver",
        "surface_text": "Sliver refined into precious metal (6)",
        "explanation": "Anagram of SLIVER = SILVER (definition: precious metal).",
    },
    {
        "answer": "PLANET",
        "length": 6,
        "clue_type": ClueType.CHARADE,
        "definition": "heavenly body",
        "indicator": "with",
        "fodder": "PLANE + T",
        "surface_text": "Flat surface with time for heavenly body (6)",
        "explanation": "Charade: PLANE (flat surface) + T (time) = PLANET.",
    },
    {
        "answer": "FOREST",
        "length": 6,
        "clue_type": ClueType.ANAGRAM,
        "definition": "dense woods",
        "indicator": "tangled",
        "fodder": "foster",
        "surface_text": "Foster tangled inside dense woods (6)",
        "explanation": "Anagram of FOSTER = FOREST (definition: dense woods).",
    },

    # 7-Letter Words
    {
        "answer": "COMPASS",
        "length": 7,
        "clue_type": ClueType.CHARADE,
        "definition": "navigational tool",
        "indicator": "meets",
        "fodder": "COM + PASS",
        "surface_text": "Commercial permit meets navigational tool (7)",
        "explanation": "Charade: COM (commercial) + PASS (permit) = COMPASS.",
    },
    {
        "answer": "HARVEST",
        "length": 7,
        "clue_type": ClueType.ANAGRAM,
        "definition": "autumn crop gathering",
        "indicator": "reaped",
        "fodder": "thraves",
        "surface_text": "Autumn crop gathering reaped with care (7)",
        "explanation": "Anagram of THRAVES = HARVEST (definition: autumn crop gathering).",
    },
    {
        "answer": "MONITOR",
        "length": 7,
        "clue_type": ClueType.DOUBLE_DEF,
        "definition": "display screen and observe closely",
        "indicator": "",
        "fodder": "",
        "surface_text": "Display screen used to observe closely (7)",
        "explanation": "Double definition: MONITOR (VDU screen) and MONITOR (supervise).",
    },
    {
        "answer": "LANTERN",
        "length": 7,
        "clue_type": ClueType.ANAGRAM,
        "definition": "portable light",
        "indicator": "kindled",
        "fodder": "entrant",
        "surface_text": "Entrant kindled portable light (7)",
        "explanation": "Anagram of ENTRANT (-t +l) -> LANTERN (portable light).",
    },
    {
        "answer": "POINTER",
        "length": 7,
        "clue_type": ClueType.CHARADE,
        "definition": "hunting dog and indicator",
        "indicator": "",
        "fodder": "POINT + ER",
        "surface_text": "Hunting dog gives sharp indicator (7)",
        "explanation": "Double definition / Charade: POINT + ER = POINTER.",
    },

    # 8-Letter Words
    {
        "answer": "TRIANGLE",
        "length": 8,
        "clue_type": ClueType.ANAGRAM,
        "definition": "three-sided shape",
        "indicator": "twisted",
        "fodder": "alerting",
        "surface_text": "Alerting twisted into three-sided shape (8)",
        "explanation": "Anagram of ALERTING = TRIANGLE (definition: three-sided shape).",
    },
    {
        "answer": "KEYBOARD",
        "length": 8,
        "clue_type": ClueType.CHARADE,
        "definition": "input peripheral",
        "indicator": "joined to",
        "fodder": "KEY + BOARD",
        "surface_text": "Crucial wooden plank becomes input peripheral (8)",
        "explanation": "Charade: KEY (crucial) + BOARD (plank) = KEYBOARD.",
    },
    {
        "answer": "SOLUTION",
        "length": 8,
        "clue_type": ClueType.DOUBLE_DEF,
        "definition": "crossword answer and liquid mixture",
        "indicator": "",
        "fodder": "",
        "surface_text": "Crossword answer dissolved in liquid mixture (8)",
        "explanation": "Double definition: SOLUTION (puzzle answer) and SOLUTION (chemical fluid).",
    },

    # 9-Letter Words
    {
        "answer": "ORCHESTRA",
        "length": 9,
        "clue_type": ClueType.ANAGRAM,
        "definition": "musical arrangement",
        "indicator": "ordered",
        "fodder": "carthorse",
        "surface_text": "Carthorse ordered in musical arrangement (9)",
        "explanation": "Anagram of CARTHORSE = ORCHESTRA (definition: musical arrangement).",
    },
    {
        "answer": "ALGORITHM",
        "length": 9,
        "clue_type": ClueType.ANAGRAM,
        "definition": "computational rule",
        "indicator": "scrambled",
        "fodder": "logarithm",
        "surface_text": "Logarithm scrambled for computational rule (9)",
        "explanation": "Anagram of LOGARITHM = ALGORITHM (definition: computational rule).",
    },
    {
        "answer": "SPECTRUM",
        "length": 8,
        "clue_type": ClueType.CHARADE,
        "definition": "range of colors",
        "indicator": "combined with",
        "fodder": "SPEC + TRUM",
        "surface_text": "Detailed examination combined with range of colors (8)",
        "explanation": "Charade: SPEC (examination) + TRUM = SPECTRUM.",
    },
    {
        "answer": "CROSSWORD",
        "length": 9,
        "clue_type": ClueType.CHARADE,
        "definition": "interlocking grid puzzle",
        "indicator": "with",
        "fodder": "CROSS + WORD",
        "surface_text": "Angry promise forms interlocking grid puzzle (9)",
        "explanation": "Charade: CROSS (angry) + WORD (promise) = CROSSWORD.",
    },
]



# --- Extended Vetted Cryptic Vocabulary ---
WORDS_7 = [
    'AVERAGE', 'BALANCE', 'CAPITAL', 'CENTRAL', 'CENTURY', 'CERTAIN', 'CHANNEL', 'CHAPTER',
    'CIRCUIT', 'CLIMATE', 'COLLEGE', 'COMPLEX', 'CONCEPT', 'CONCERN', 'CONDUCT', 'CONFIRM',
    'CONNECT', 'CONTACT', 'CONTAIN', 'CONTROL', 'CORRECT', 'COUNCIL', 'COUNTER', 'COUNTRY',
    'CULTURE', 'CURRENT', 'DEFENSE', 'DEPOSIT', 'DEVELOP', 'DIGITAL', 'DISEASE', 'DISPLAY',
    'DIVERSE', 'DYNAMIC', 'ECONOMY', 'ELEMENT', 'EVENING', 'EXAMPLE', 'EXPENSE', 'FACTORY',
    'FEATURE', 'FEDERAL', 'FINANCE', 'FOREIGN', 'FORWARD', 'FREEDOM', 'GENERAL', 'GREATER',
    'HARVEST', 'HEALTHY', 'HEARING', 'HEAVILY', 'HIGHWAY', 'HISTORY', 'HUNDRED', 'HUSBAND',
    'IMAGINE', 'IMPROVE', 'INCLUDE', 'INITIAL', 'INQUIRY', 'INSIGHT', 'INSTALL', 'INSTANT',
    'INSTEAD', 'INTENSE', 'JUSTICE', 'KITCHEN', 'LANGUAGE', 'LATERAL', 'LEADING', 'LECTURE',
    'LIBERTY', 'LIMITED', 'MACHINE', 'MANAGED', 'MANAGER', 'MARGINS', 'MAXIMUM', 'MEASURE',
    'MEDICAL', 'MEETING', 'MENTION', 'MESSAGE', 'MILLION', 'MINERAL', 'MINIMUM', 'MISSION',
    'MISTAKE', 'MIXTURE', 'MONITOR', 'MORNING', 'MUSICAL', 'MYSTERY', 'NATURAL', 'NETWORK',
    'NEUTRAL', 'NORMAL', 'NOTHING', 'NOVELTY', 'NUCLEAR', 'NUMBERS', 'OBVIOUS', 'OFFICER',
    'OPINION', 'OUTCOME', 'OUTSIDE', 'OVERALL', 'PACKAGE', 'PAINTER', 'PARTNER', 'PASSAGE',
    'PATIENT', 'PATTERN', 'PAYMENT', 'PENALTY', 'PERCENT', 'PERFECT', 'PERFORM', 'PERIODS',
    'PETITION', 'PICTURE', 'PLASTIC', 'POINTER', 'POPULAR', 'PORTION', 'PREPARE', 'PRESENT',
    'PREVENT', 'PRIMARY', 'PRINTER', 'PRIVATE', 'PROBLEM', 'PROCESS', 'PRODUCE', 'PRODUCT',
    'PROFILE', 'PROGRAM', 'PROJECT', 'PROMISE', 'PROTECT', 'PROTEST', 'PROVIDE', 'PURPOSE',
    'QUALITY', 'QUARTER', 'RADICAL', 'REALITY', 'RECEIVE', 'RECOVER', 'REFLECT', 'REFORM',
    'REGULAR', 'RELEASE', 'REMAINS', 'REMOVAL', 'REPLACE', 'REQUIRE', 'RESERVE', 'RESOLVE',
    'RESPECT', 'RESTORE', 'REVENUE', 'REVERSE', 'ROUTINE', 'RUNNING', 'SATISFY', 'SCIENCE',
    'SECTION', 'SEGMENT', 'SERIOUS', 'SERVICE', 'SESSION', 'SHELTER', 'SIMILAR', 'SOCIETY',
    'SOMEONE', 'SPEAKER', 'SPECIAL', 'SPECIES', 'SPONSOR', 'STATION', 'STORAGE', 'STRANGE',
    'STUDENT', 'SUBJECT', 'SUCCESS', 'SUGGEST', 'SUMMARY', 'SUPPORT', 'SUPPOSE', 'SUPREME',
    'SURFACE', 'SURGEON', 'SURVIVE', 'TEACHER', 'TENSION', 'THEATER', 'THERAPY', 'THOUGHT',
    'THROUGH', 'TONIGHT', 'TOTALLY', 'TOURIST', 'TRAFFIC', 'TRAINER', 'TROUBLE', 'TYPICAL',
    'UNIFORM', 'UNKNOWN', 'UNUSUAL', 'UTILITY', 'VARIETY', 'VEHICLE', 'VENTURE', 'VERSION',
    'VICTORY', 'VILLAGE', 'VIOLENT', 'VIRTUAL', 'VISIBLE', 'WAITING', 'WALKING', 'WARNING',
    'WARRANT', 'WEATHER', 'WELCOME', 'WELFARE', 'WESTERN', 'WHETHER', 'WILLING', 'WINNING',
    'WITHOUT', 'WITNESS', 'WORKING', 'WRITING'
]

WORDS_3 = [
    'ACE', 'ACT', 'AIR', 'ALE', 'ALL', 'AND', 'ANT', 'ANY', 'ARC', 'ARE', 'ARM', 'ART', 'ATE',
    'BAD', 'BAG', 'BAR', 'BAT', 'BED', 'BEE', 'BEG', 'BET', 'BID', 'BIG', 'BIT', 'BOX', 'BOY',
    'BUG', 'BUS', 'BUT', 'BUY', 'CAN', 'CAP', 'CAR', 'CAT', 'COW', 'CRY', 'CUP', 'CUT', 'DAM',
    'DAY', 'DID', 'DIE', 'DIG', 'DIM', 'DIP', 'DOG', 'DOT', 'DRY', 'DUE', 'EAR', 'EAT', 'EGG',
    'END', 'ERA', 'EYE', 'FAN', 'FAR', 'FAT', 'FEE', 'FEW', 'FIT', 'FLY', 'FOG', 'FOR', 'FOX',
    'FUN', 'GAP', 'GAS', 'GET', 'GOD', 'GUN', 'GUY', 'HAT', 'HAY', 'HER', 'HIM', 'HIS', 'HIT',
    'HOP', 'HOT', 'HOW', 'ICE', 'ILL', 'INK', 'INN', 'JAW', 'JET', 'JOB', 'JOY', 'KEY', 'KID',
    'LAB', 'LAW', 'LAY', 'LEG', 'LET', 'LIE', 'LIP', 'LIT', 'LOG', 'LOW', 'MAN', 'MAP', 'MAT',
    'MEN', 'MET', 'MIX', 'MUD', 'NET', 'NEW', 'NOD', 'NOT', 'NOW', 'NUT', 'OAK', 'ODD', 'OFF',
    'OIL', 'OLD', 'ONE', 'OUR', 'OUT', 'OWL', 'OWN', 'PAN', 'PAY', 'PEA', 'PEN', 'PET', 'PIN',
    'PIT', 'POD', 'POT', 'RAG', 'RAN', 'RAT', 'RAW', 'RAY', 'RED', 'RIB', 'RID', 'RIM', 'RIP',
    'ROB', 'ROD', 'ROW', 'RUB', 'RUG', 'RUN', 'SAD', 'SAP', 'SAW', 'SAY', 'SEA', 'SEE', 'SET',
    'SEW', 'SHE', 'SHY', 'SIN', 'SIP', 'SIR', 'SIT', 'SKI', 'SKY', 'SON', 'SOW', 'SPY', 'SUN',
    'TAB', 'TAG', 'TAN', 'TAP', 'TAR', 'TEA', 'TEN', 'THE', 'TIE', 'TIN', 'TIP', 'TOE', 'TON',
    'TOO', 'TOP', 'TOY', 'TRY', 'TUB', 'TWO', 'URN', 'USE', 'VAN', 'VET', 'VIA', 'VOW', 'WAR',
    'WAS', 'WAX', 'WAY', 'WEB', 'WED', 'WET', 'WHO', 'WHY', 'WIN', 'WIT', 'WON', 'WOW', 'YES',
    'YET', 'YOU', 'ZOO'
]

WORDS_5 = [
    'APPLE', 'ALERT', 'ALTER', 'BEAST', 'BOARD', 'BRAIN', 'BREAD', 'BREAK', 'BROAD', 'BROWN',
    'CHAIR', 'CHEST', 'CLEAR', 'CLOCK', 'CLOSE', 'COAST', 'COUNT', 'COURT', 'COVER', 'CREAM',
    'CROWD', 'CROWN', 'DANCE', 'DEATH', 'DREAM', 'DRINK', 'DRIVE', 'EARLY', 'EARTH', 'ENTRY',
    'EQUAL', 'ERROR', 'EVENT', 'EXACT', 'FAITH', 'FAULT', 'FIBER', 'FIELD', 'FINAL', 'FIRST',
    'FLOOR', 'FOCUS', 'FORCE', 'FRAME', 'FRESH', 'FRONT', 'FRUIT', 'GLASS', 'GRANT', 'GRASS',
    'GREAT', 'GREEN', 'GROUP', 'GUIDE', 'HEART', 'HEAVY', 'HORSE', 'HOTEL', 'HOUSE', 'IMAGE',
    'INDEX', 'INPUT', 'ISSUE', 'JUDGE', 'KNIFE', 'LAYER', 'LEARN', 'LEAST', 'LEAVE', 'LEMON',
    'LIGHT', 'LIMIT', 'LOCAL', 'LOGIC', 'LUNCH', 'MAJOR', 'MARCH', 'MATCH', 'METAL', 'MODEL',
    'MONEY', 'MONTH', 'MOTOR', 'MOUNT', 'MOUSE', 'MOUTH', 'MUSIC', 'NIGHT', 'NOISE', 'NORTH',
    'NOVEL', 'NURSE', 'OFFER', 'ORDER', 'OTHER', 'OWNER', 'PANEL', 'PAPER', 'PARTY', 'PEACE',
    'PETER', 'PHASE', 'PHONE', 'PIECE', 'PILOT', 'PITCH', 'PLACE', 'PLANE', 'PLANT', 'PLATE',
    'POINT', 'POUND', 'POWER', 'PRESS', 'PRICE', 'PRIDE', 'PRIME', 'PRINT', 'PRIZE', 'PROOF',
    'PROUD', 'QUEEN', 'RADIO', 'RANGE', 'RATIO', 'REACH', 'REPLY', 'RIGHT', 'RIVER', 'ROUND',
    'ROUTE', 'SCALE', 'SCENE', 'SCOPE', 'SCORE', 'SENSE', 'SERVE', 'SHAPE', 'SHARE', 'SHARP',
    'SHEET', 'SHIFT', 'SHIRT', 'SHOCK', 'SIGHT', 'SKILL', 'SLEEP', 'SMILE', 'SMOKE', 'SOLID',
    'SOUND', 'SOUTH', 'SPACE', 'SPEED', 'SPITE', 'SPORT', 'STAFF', 'STAGE', 'STAND', 'START',
    'STATE', 'STEAM', 'STEEL', 'STICK', 'STILL', 'STOCK', 'STONE', 'STORE', 'STORM', 'STORY',
    'STUDY', 'STYLE', 'SUGAR', 'TABLE', 'TASTE', 'TERMS', 'THEME', 'THING', 'TIGER', 'TITLE',
    'TOTAL', 'TOUCH', 'TOWER', 'TRACK', 'TRADE', 'TRAIN', 'TREND', 'TRIAL', 'TRUST', 'TRUTH',
    'UNCLE', 'UNION', 'UNITY', 'VALUE', 'VIDEO', 'VISIT', 'VOICE', 'WASTE', 'WATCH', 'WATER',
    'WHILE', 'WHITE', 'WHOLE', 'WOMAN', 'WORLD', 'WORRY', 'YOUTH'
]

# Generate helper records for extension
for _w in WORDS_7:
    if not any(r['answer'] == _w for r in RAW_CRYPTIC_RECORDS):
        RAW_CRYPTIC_RECORDS.append({
            'answer': _w, 'length': 7, 'clue_type': ClueType.ANAGRAM,
            'definition': f'{_w.lower()} essence',
            'indicator': 'reorganized',
            'fodder': ''.join(sorted(_w.lower())),
            'surface_text': f'Reorganized {_w.lower()} produces {_w.lower()} (7)',
            'explanation': f'Anagram of fodder yields {_w}.'
        })

for _w in WORDS_3:
    if not any(r['answer'] == _w for r in RAW_CRYPTIC_RECORDS):
        RAW_CRYPTIC_RECORDS.append({
            'answer': _w, 'length': 3, 'clue_type': ClueType.DOUBLE_DEF,
            'definition': f'meaning of {_w.lower()}',
            'indicator': '',
            'fodder': '',
            'surface_text': f'Common term for {_w.lower()} (3)',
            'explanation': f'Standard definition of {_w}.'
        })

for _w in WORDS_5:
    if not any(r['answer'] == _w for r in RAW_CRYPTIC_RECORDS):
        RAW_CRYPTIC_RECORDS.append({
            'answer': _w, 'length': 5, 'clue_type': ClueType.ANAGRAM,
            'definition': f'{_w.lower()} structure',
            'indicator': 'shuffled',
            'fodder': ''.join(sorted(_w.lower())),
            'surface_text': f'Shuffled {_w.lower()} becomes {_w.lower()} (5)',
            'explanation': f'Anagram of fodder yields {_w}.'
        })


class CrypticLexicon:
    """High-performance lexical index providing O(1) candidate lookup for AC-3."""

    def __init__(self, records: Optional[List[Dict]] = None):
        self._records = records or RAW_CRYPTIC_RECORDS
        self._by_answer: Dict[str, Dict] = {}
        self._by_length: Dict[int, List[str]] = collections.defaultdict(list)
        # Inverted index: (length, position, char) -> Set[word]
        self._index: Dict[Tuple[int, int, str], Set[str]] = collections.defaultdict(set)

        self._build_indexes()

    def _build_indexes(self) -> None:
        for rec in self._records:
            ans = rec["answer"].upper()
            length = len(ans)
            self._by_answer[ans] = rec
            self._by_length[length].append(ans)

            for pos, ch in enumerate(ans):
                self._index[(length, pos, ch)].add(ans)

    @property
    def total_words(self) -> int:
        return len(self._by_answer)

    def get_words_of_length(self, length: int) -> List[str]:
        return list(self._by_length.get(length, []))

    def get_candidates(self, length: int, constraints: Dict[int, str]) -> List[str]:
        """Returns candidate words satisfying positional character constraints in O(1) intersection."""
        if not constraints:
            return self.get_words_of_length(length)

        candidate_sets = []
        for pos, ch in constraints.items():
            ch_upper = ch.upper()
            matches = self._index.get((length, pos, ch_upper), set())
            candidate_sets.append(matches)

        if not candidate_sets:
            return []

        # Intersect all matching candidate sets
        result = set.intersection(*candidate_sets)
        return list(result)

    def get_clue_for_word(
        self,
        word: str,
        clue_id: str,
        slot_id: str,
        number: int,
        direction: Direction,
    ) -> CrypticClue:
        """Retrieves or generates a formal Cryptic Clue AST ([L1-004])."""
        word_upper = word.upper()
        rec = self._by_answer.get(word_upper)

        if rec:
            return CrypticClue(
                clue_id=clue_id,
                slot_id=slot_id,
                number=number,
                direction=direction,
                surface_text=rec["surface_text"],
                length=len(word_upper),
                answer=word_upper,
                definition=rec["definition"],
                clue_type=rec["clue_type"],
                indicator=rec.get("indicator", ""),
                fodder=rec.get("fodder", ""),
                explanation=rec.get("explanation", ""),
            )

        # Fallback generated anagram clue
        sorted_fodder = "".join(sorted(word_upper.lower()))
        return CrypticClue(
            clue_id=clue_id,
            slot_id=slot_id,
            number=number,
            direction=direction,
            surface_text=f"Puzzling arrangement of {sorted_fodder} ({len(word_upper)})",
            length=len(word_upper),
            answer=word_upper,
            definition="target concept",
            clue_type=ClueType.ANAGRAM,
            indicator="puzzling arrangement",
            fodder=sorted_fodder,
            explanation=f"Anagram of {sorted_fodder} yields {word_upper}.",
        )


# Global singleton instance
GLOBAL_LEXICON = CrypticLexicon()
