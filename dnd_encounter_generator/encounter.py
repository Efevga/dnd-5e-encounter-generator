from dataclasses import dataclass

@dataclass
class Encounter:
    monsters: dict[str,int]

    @property
    def enemy_count(self):
        return sum(self.monsters.values())

    def add_monster(self,monster_name: str, quantity: int=1):
        self.monsters[monster_name] = (self.monsters.get(monster_name,0) + quantity)