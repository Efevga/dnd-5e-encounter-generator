import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Attack:
    name: str
    average_damage: int
    damage_type: str
    range: int
    attacks_per_action: int
    attack_bonus: int

@dataclass
class CombatProfile:
    actions_per_turn: int
    bonus_actions_per_turn: int
    reactions_per_round: int
    has_legendary_actions: bool
    legendary_actions: int
    has_lair_actions: bool
    has_spellcasting: bool
    has_area_attacks: bool
    has_control_effects: bool

@dataclass
class Monster:
    name: str
    cr: float
    hp: int
    ac: int 
    xp: int 
    monster_type: str 
    attacks: list[Attack]
    combat_profile: CombatProfile
    
def load_monsters(file=None):
    if file is None:
        file = Path(__file__).parent /"data"/"monsters.json"

    with open(file, "r", encoding="utf-8") as file:
        data = json.load(file)

    monsters = {}

    for name,stats in data.items():
        attacks = []
        for attack in stats["attacks"]:
            attacks.append(Attack(name=attack["name"],
                    average_damage=attack["average_damage"],
                    damage_type=attack["damage_type"],
                    range=attack["range"],
                    attacks_per_action=attack["attacks_per_action"],
                    attack_bonus=attack["attack_bonus"]))

        combat_profile = CombatProfile(
            actions_per_turn=stats["actions_per_turn"],
            bonus_actions_per_turn=stats["bonus_actions_per_turn"],
            reactions_per_round=stats["reactions_per_round"],

            has_legendary_actions=stats["has_legendary_actions"],
            legendary_actions=stats["legendary_actions"],

            has_lair_actions=stats["has_lair_actions"],
            has_spellcasting=stats["has_spellcasting"],
            has_area_attacks=stats["has_area_attacks"],
            has_control_effects=stats["has_control_effects"]
        )

        monsters[name] = Monster(
            name=name,
            cr=stats["cr"],
            hp=stats["hp"],
            ac=stats["ac"],
            xp=stats["xp"],
            monster_type=stats["type"],
            attacks=attacks,
            combat_profile=combat_profile
        )

    return monsters