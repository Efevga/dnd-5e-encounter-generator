XP_THRESHOLDS = {
    1:  {"EASY": 25,   "MEDIUM": 50,   "HARD": 75,   "DEADLY": 100},
    2:  {"EASY": 50,   "MEDIUM": 100,  "HARD": 150,  "DEADLY": 200},
    3:  {"EASY": 75,   "MEDIUM": 150,  "HARD": 225,  "DEADLY": 400},
    4:  {"EASY": 125,  "MEDIUM": 250,  "HARD": 375,  "DEADLY": 500},
    5:  {"EASY": 250,  "MEDIUM": 500,  "HARD": 750,  "DEADLY": 1100},
    6:  {"EASY": 300,  "MEDIUM": 600,  "HARD": 900,  "DEADLY": 1400},
    7:  {"EASY": 350,  "MEDIUM": 750,  "HARD": 1100, "DEADLY": 1700},
    8:  {"EASY": 450,  "MEDIUM": 900,  "HARD": 1400, "DEADLY": 2100},
    9:  {"EASY": 550,  "MEDIUM": 1100, "HARD": 1600, "DEADLY": 2400},
    10: {"EASY": 600,  "MEDIUM": 1200, "HARD": 1900, "DEADLY": 2800},
    11: {"EASY": 800,  "MEDIUM": 1600, "HARD": 2400, "DEADLY": 3600},
    12: {"EASY": 1000, "MEDIUM": 2000, "HARD": 3000, "DEADLY": 4500},
    13: {"EASY": 1100, "MEDIUM": 2200, "HARD": 3400, "DEADLY": 5100},
    14: {"EASY": 1250, "MEDIUM": 2500, "HARD": 3800, "DEADLY": 5700},
    15: {"EASY": 1400, "MEDIUM": 2800, "HARD": 4300, "DEADLY": 6400},
    16: {"EASY": 1600, "MEDIUM": 3200, "HARD": 4800, "DEADLY": 7200},
    17: {"EASY": 2000, "MEDIUM": 3900, "HARD": 5900, "DEADLY": 8800},
    18: {"EASY": 2100, "MEDIUM": 4200, "HARD": 6300, "DEADLY": 9500},
    19: {"EASY": 2400, "MEDIUM": 4900, "HARD": 7300, "DEADLY": 10900},
    20: {"EASY": 2800, "MEDIUM": 5700, "HARD": 8500, "DEADLY": 12700},
}

def calculate_party_thresholds(party):
    thresholds = {"EASY":0,"MEDIUM":0,"HARD":0,"DEADLY":0}

    for character in party.characters:
        character_thresholds = XP_THRESHOLDS[character.level]
        thresholds["EASY"] += character_thresholds["EASY"]
        thresholds["MEDIUM"] += character_thresholds["MEDIUM"]
        thresholds["HARD"] += character_thresholds["HARD"]
        thresholds["DEADLY"] += character_thresholds["DEADLY"]
    return thresholds    