from .calculator import calculate_encounter,calculate_xp_multiplier
from .difficulty import calculate_party_thresholds

def is_within_xp_budget(encounter,monsters,party,party_thresholds,target_difficulty):
    total_xp = 0
    for monster_name,quantity in encounter.monsters.items():
        monster = monsters[monster_name]
        total_xp += monster.xp * quantity

    multiplier = calculate_xp_multiplier(encounter,party)
    adjusted_xp = total_xp * multiplier

    difficulties = ["EASY", "MEDIUM", "HARD", "DEADLY"]
    target_index = difficulties.index(target_difficulty)
    lower_threashold = party_thresholds[target_difficulty]

    if target_difficulty == "DEADLY":
        upper_thershold = lower_threashold*2
    else:
        next_difficulty = difficulties[target_index + 1]
        upper_thershold = party_thresholds[next_difficulty]

    return lower_threashold <= adjusted_xp < upper_thershold

def find_best_encounter(encounters,monsters,party,target_difficulty):
    matching_encounters = []

    party_thresholds = calculate_party_thresholds(party)

    for encounter in encounters:
        if not is_within_xp_budget(encounter,monsters,party,party_thresholds,target_difficulty):
            continue

        analysis = calculate_encounter(encounter,monsters,party)
        if analysis.difficulty == target_difficulty:
            matching_encounters.append((encounter,analysis))

    return matching_encounters

def calculate_xp_score(adjusted_xp,party_thresholds,target_difficulty):
    difficulties = ["EASY","MEDIUM","HARD","DEADLY"]
    target_index = difficulties.index(target_difficulty)

    lower_threshold = party_thresholds[target_difficulty]

    if target_difficulty == "DEADLY":
        upper_threshold = lower_threshold * 2
    else:
        next_difficulty = difficulties[target_index+1]
        upper_threshold = party_thresholds[next_difficulty]

    middle_threshold = (lower_threshold + upper_threshold)/2
    score = abs(adjusted_xp - middle_threshold)
    return score

def calculate_cr_score(encounter,monsters,party):
    party_level = party.average_level 
    total_difference = 0

    for monster_name,quantity in encounter.monsters.items():
        monster = monsters[monster_name]
        difference = abs(monster.cr - party_level)
        total_difference += difference * quantity
    return total_difference

def calculate_action_balance_score(encounter,monsters,party):
    party_actions = party.size
    enemy_actions = 0

    for monster_name,quantity in encounter.monsters.items():
        monster =  monsters[monster_name]
        profile = monster.combat_profile
        enemy_actions += (profile.actions_per_turn * quantity)

        if profile.has_legendary_actions:
            enemy_actions += (profile.legendary_actions * quantity)

    difference = abs(enemy_actions-party_actions)
    return difference

def calculate_cr_warning(encounter,monsters,party):
    party_level = party.average_level
    warnings = []

    for monster_name, quantity in encounter.monsters.items():
        monster = monsters[monster_name]

        if monster.cr > party_level:
            warnings.append(f"{monster_name} (CR {monster.cr})")
    return warnings

def calculate_custom_score(action_balance_score,cr_score,max_action_score,max_cr_score):
    if max_action_score > 0:
        normalized_action = action_balance_score/max_action_score
    else:
        normalized_action = 0

    if max_cr_score > 0:
        normalized_cr = cr_score/max_cr_score
    else:
        normalized_cr = 0

    custom_score = (normalized_action * 0.5 + normalized_cr * 0.5)
    return custom_score

def rank_encounters(matching_encounters,monsters,party,party_thresholds,target_difficulty):
    scored_encounters = []
    action_scores = []
    cr_scores = []

    for encounter,analysis in matching_encounters:
        action_balance_score = calculate_action_balance_score(encounter,monsters,party)
        cr_score = calculate_cr_score(encounter,monsters,party)
        xp_score = calculate_xp_score(analysis.adjusted_xp,party_thresholds,target_difficulty)
        action_scores.append(action_balance_score)
        cr_scores.append(cr_score)
        scored_encounters.append((encounter,analysis,xp_score,cr_score,action_balance_score))

    max_action_score = max(action_scores , default=0)
    max_cr_score = max(cr_scores, default=0)

    ranked_encounters = []

    for encounter,analysis,xp_score,cr_score,action_balance_score in scored_encounters:
        custom_score = calculate_custom_score(action_balance_score,cr_score,max_action_score,max_cr_score)
        ranked_encounters.append((encounter,analysis,xp_score,cr_score,calculate_cr_warning(encounter,monsters,party),action_balance_score,analysis.encounter_threat,custom_score))

    ranked_encounters.sort(key=lambda result: (result[2],result[7]))
    return ranked_encounters