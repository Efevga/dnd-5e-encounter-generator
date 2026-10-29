from dataclasses import dataclass

@dataclass
class Character:
    name: str
    level: int
    character_class: str
    attack_bonus: int
    ac: int

@dataclass
class Party:
    characters: list[Character]

    @property
    def size(self):
        return len(self.characters)

    @property
    def average_level(self):
        total_level = 0 

        for character in self.characters:
            total_level += character.level
        average = total_level/self.size
        return average


    def get_class_count(self):
        class_counts = {}

        for character in self.characters:
            if character.character_class not in class_counts:
                class_counts[character.character_class] = 0

            class_counts[character.character_class]+=1
        return class_counts