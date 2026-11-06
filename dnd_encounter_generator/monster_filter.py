def filter_monsters_by_name(monsters, selected_names):
    filtered_monsters = {}
    for name in selected_names:
        if name in monsters:
            filtered_monsters[name] = monsters[name]

    return filtered_monsters

def filter_monsters_by_cr(monsters, slected_crs):
    filtered_monsters = {}

    for name,monster in monsters.items():
        if monster.cr in slected_crs:
            filtered_monsters[name] = monster
    return filtered_monsters

def filter_monsters_by_type(monsters, selected_types):
    filtered_monsters = {}

    for name,monster in monsters.items():
        if monster.monster_type in selected_types:
            filtered_monsters[name] = monster
    return filtered_monsters

def create_filter():
    return {"selected_crs": set(),"selected_types": set(),"selected_names": set()}

def apply_filter(monsters,filter):
    filtered_monsters = monsters.copy()
    if filter["selected_crs"]:
        filtered_monsters = filter_monsters_by_cr(filtered_monsters,filter["selected_crs"])

    if filter["selected_types"]:
        filtered_monsters = filter_monsters_by_type(filtered_monsters,filter["selected_types"])

    if filter["selected_names"]:
        manual_monsters = filter_monsters_by_name(monsters,filter["selected_names"])
        filtered_monsters.update(manual_monsters)

    return filtered_monsters