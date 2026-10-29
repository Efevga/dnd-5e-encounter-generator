from itertools import combinations_with_replacement
from .encounter import Encounter

def generate_encounters(monsters,minimum_enemies=1,maximum_enemies=5,max_results = 5000000,progress=None,task=None):
    monster_names = list(monsters.keys())
    encounters = []

    if  progress is not None and task is not None:
        progress.update(task, total=max_results)

    for enemy_count in range(minimum_enemies,maximum_enemies+1):
        combinations = combinations_with_replacement(monster_names,enemy_count)
        for combination in combinations:

            if len(encounters) >= max_results:
                return encounters
            
            monster_counts = {}

            for monster_name in combination:
                if monster_name not in monster_counts:
                    monster_counts[monster_name] = 0

                monster_counts[monster_name] += 1
            encounter = Encounter(monster_counts)
            encounters.append(encounter)

            if progress is not None and task is not None:
                progress.update(task, advance =1)

    return encounters 