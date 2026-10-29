from dataclasses import dataclass
from .difficulty import calculate_party_thresholds

@dataclass
class EncounterAnalysis:
    enemy_count: int
    total_hp: int
    total_damage: int
    total_xp: int
    xp_multiplier: float
    adjusted_xp: float
    highest_cr: float
    average_cr: float
    offence_threat: float
    defence_threat: float
    encounter_threat: float
    difficulty: str

ACTION_USAGE_RATES = {
    "action": 1.00,
    "bonus_action": 0.90,
    "reaction": 0.15,
    "legendary_action": 0.85
}

def calculate_total_hp(encounter,monsters):
    total_hp = 0

    for monster_name,quantity in encounter.monsters.items():
        monster = monsters[monster_name]
        total_hp += monster.hp * quantity
    return total_hp

def calculate_average_damage(encounter,monsters,party):
    total_damage = 0

    for monster_name,quantity in encounter.monsters.items():
        monster = monsters[monster_name]
        monster_damage = calculate_monster_damage(monster,party)
        total_damage +=(monster_damage * quantity)
    return total_damage

def calculate_highest_cr(encounter,monsters):
    highest_cr = 0

    for monster_name in encounter.monsters:
        monster = monsters[monster_name]

        if monster.cr > highest_cr:
            highest_cr = monster.cr
    return highest_cr

def calculate_average_cr(encounter,monsters):
    total_cr = 0
    enemy_count = 0

    for monster_name,quantity in encounter.monsters.items():
        monster = monsters[monster_name]
        total_cr += monster.cr*quantity
        enemy_count += quantity

    average_cr = total_cr/enemy_count
    return average_cr

def calculate_total_xp(encounter,monsters):
    total_xp = 0
    for monster_name,quantity in encounter.monsters.items():
        monster = monsters[monster_name]
        total_xp += monster.xp * quantity
    return total_xp

def calculate_monster_damage(monster,party):
    if not monster.attacks:
        return 0

    attack = max(monster.attacks, key=lambda attack: (attack.average_damage * attack.attacks_per_action))
    hit_chance = calculate_monster_hit_chance(monster,party)
    damage = attack.average_damage * attack.attacks_per_action * hit_chance

    return damage

def calculate_monster_threat(monster):
    threat = (monster.hp+monster.ac+calculate_monster_damage(monster))
    return threat

def calculate_encounter_threat(offence_threat,defence_threat):
    return offence_threat+defence_threat

def calculate_offence_threat(encounter,monsters,party):
    total_average_damage = calculate_average_damage(encounter,monsters,party)
    return total_average_damage

def calculate_defence_threat(encounter,monsters,party):
    total_defence_threat = 0

    for monster_name,quantity in encounter.monsters.items():
        monster = monsters[monster_name]
        hit_chance = calculate_party_hit_chance(party,monster)
        monster_defence_threat = monster.hp / hit_chance
        total_defence_threat += monster_defence_threat*quantity

    return total_defence_threat

def calculate_hit_chance(attack_bonus,target_ac):
    required_roll = target_ac - attack_bonus
    if required_roll<=1:
        return 0.95

    if required_roll>=20:
        return 0.05

    return (21 - required_roll)/20

def calculate_party_hit_chance(party,monster):
    total_chance = 0

    for character in party.characters:
        chance = calculate_hit_chance(character.attack_bonus,monster.ac)
        total_chance += chance

    average_chance = total_chance/party.size
    return average_chance


def calculate_monster_hit_chance(monster, party):
    total_chance = 0

    for character in party.characters:
        attack = max(monster.attacks,key=lambda attack: (attack.average_damage * attack.attacks_per_action))

        chance = calculate_hit_chance(attack.attack_bonus,character.ac)
        total_chance += chance

    average_chance = total_chance / party.size
    return average_chance

def calculate_total_enemy_actions(encounter,monsters):
    total_actions =0 

    for monster_name,quantity in encounter.monsters.items():
        monster = monsters[monster_name]
        total_actions += monster.combat_profile.actions_per_turn * quantity
    return total_actions

def calculate_enemy_actions(encounter,monsters):
    total_actions = 0 
    
    for monster_name,quantity in encounter.monsters.items():
            monster =  monsters[monster_name]
            profile = monster.combat_profile

            normal_actions = (profile.actions_per_turn * quantity * ACTION_USAGE_RATES["action"])
            bonus_actions = (profile.bonus_actions_per_turn * quantity * ACTION_USAGE_RATES["bonus_action"])
            reactions = (profile.reactions_per_round * quantity * ACTION_USAGE_RATES["reaction"])
            
            legendary_actions = 0
            if profile.has_legendary_actions:
                legendary_actions = (profile.legendary_actions * quantity *  ACTION_USAGE_RATES["legendary_action"])

            total_actions += (normal_actions + bonus_actions + reactions + legendary_actions)
    return total_actions 

def calculate_xp_multiplier(encounter,party):
    enemy_count = encounter.enemy_count

    if enemy_count == 1:
        multiplier=1
    elif enemy_count == 2:
        multiplier=1.5
    elif enemy_count <= 6:
        multiplier=2
    elif enemy_count <= 10:
        multiplier=2.5
    elif enemy_count <= 14:
        multiplier=3
    else:
        multiplier=4

    if party.size < 3:
        if multiplier == 1:
            multiplier=1.5
        elif multiplier == 1.5:
            multiplier=2
        elif multiplier == 2:
            multiplier=2.5
        elif multiplier == 2.5:
            multiplier=3
        elif multiplier == 3:
            multiplier=4
        elif multiplier == 4:
            multiplier=5

    elif party.size >= 6:
        if multiplier == 1:
            multiplier=0.5
        elif multiplier == 1.5:
            multiplier=1
        elif multiplier == 2:
            multiplier=1.5
        elif multiplier == 2.5:
            multiplier=2
        elif multiplier == 3:
            multiplier=2.5
        elif multiplier == 4:
            multiplier=3
    return multiplier

def calculate_adjusted_xp(encounter,monsters,party):
    total_xp = calculate_total_xp(encounter,monsters)
    multiplier = calculate_xp_multiplier(encounter,party)
    adjusted_xp = total_xp*multiplier
    return adjusted_xp

def determine_difficulty(adjusted_xp,party_thresholds):
    if adjusted_xp >= party_thresholds["DEADLY"]:
        return "DEADLY"
    elif adjusted_xp >= party_thresholds["HARD"]:
        return "HARD"
    elif adjusted_xp >= party_thresholds["MEDIUM"]:
        return "MEDIUM"
    elif adjusted_xp >= party_thresholds["EASY"]:
        return "EASY"
    else:
        return "BELOW EASY"

def calculate_encounter(encounter,monsters,party):
    total_hp = calculate_total_hp(encounter,monsters)
    total_damage = calculate_average_damage(encounter,monsters,party)
    total_xp = calculate_total_xp(encounter,monsters)
    highest_cr = calculate_highest_cr(encounter,monsters)
    average_cr = calculate_average_cr(encounter,monsters)
    offence_threat = calculate_offence_threat(encounter,monsters,party)
    defence_threat = calculate_defence_threat(encounter,monsters,party)
    encounter_threat = calculate_encounter_threat(offence_threat,defence_threat)
    xp_multiplier = calculate_xp_multiplier(encounter,party)
    adjusted_xp = total_xp*xp_multiplier
    party_thresholds = calculate_party_thresholds(party)
    difficulty = determine_difficulty(adjusted_xp,party_thresholds)


    calculated = EncounterAnalysis(enemy_count=encounter.enemy_count,
                                   total_hp=total_hp,
                                   total_damage=total_damage,
                                   total_xp=total_xp,
                                   highest_cr=highest_cr,
                                   average_cr=average_cr,
                                   offence_threat=offence_threat,
                                   defence_threat=defence_threat,
                                   encounter_threat=encounter_threat,
                                   xp_multiplier=xp_multiplier,
                                   adjusted_xp=adjusted_xp,
                                   difficulty=difficulty)
    return calculated