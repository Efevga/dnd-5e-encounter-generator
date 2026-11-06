import questionary
from .party import Character, Party
from .monsters import load_monsters
from .generator import generate_encounters
from .optimizer import find_best_encounter, rank_encounters
from .difficulty import calculate_party_thresholds
from .monster_filter import filter_monsters_by_name,filter_monsters_by_cr,filter_monsters_by_type,create_filter,apply_filter
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table

console = Console()

def show_welcome_screen():
    title = Text()
    title.append("D&D ", style="bold white")
    title.append("ENCOUNTER BALANCER", style="bold red")

    messages = "Monster encounter generator"

    console.clear()
    console.print()
    console.print(Panel(Align.center(title + Text(f"\n\n{messages}", style="white"),vertical="middle",),border_style="red",padding=(1, 6),expand=False,),justify="center")
    console.print()

def load_game_monsters():
    console.print("[red]Loading monsters...[/red]")
    monsters = load_monsters()
    return monsters


def create_party():
    characters = []

    number_of_characters = questionary.text("How many characters are in your party?",default="4",validate=lambda value: (value.isdigit() and int(value) > 1 and int(value)<=10)).ask()

    if number_of_characters is None:
        return None

    for i in range(int(number_of_characters)):
        console.print(f"\n[bold red]Character {i + 1}[/bold red]")

        name = questionary.text("Character name:").ask()
        if name is None:
            return None

        character_class = questionary.select("Choose class:",
            choices=["Barbarian", "Bard", "Cleric", "Druid","Fighter", "Monk", "Paladin", "Ranger","Rogue", "Sorcerer", "Warlock", "Wizard"]).ask()

        if character_class is None:
            return None

        level = questionary.select("Choose level:",choices=[str(level) for level in range(1, 21)]).ask()

        if level is None:
            return None

        attack_bonus = questionary.text("Attack bonus:",validate=lambda value: (value.lstrip("+-").isdigit())).ask()

        if attack_bonus is None:
            return None

        ac = questionary.text("Armor Class (AC):",validate=lambda value: (value.isdigit() and int(value) > 0)).ask()

        if ac is None:
            return None

        character = Character(name,int(level),character_class,int(attack_bonus),int(ac))
        characters.append(character)

    return Party(characters)

def choose_encounter_settings():
    difficulty = questionary.select("Choose target difficulty:",choices=["EASY", "MEDIUM", "HARD", "DEADLY"]).ask()
    if difficulty is None:
        return None

    minimum_enemies = questionary.text("Minimum number of monsters:",default="1",validate=lambda value: (value.isdigit() and int(value) >= 1 and int(value) <= 9)).ask()
    if minimum_enemies is None:
        return None

    maximum_enemies = questionary.text("Maximum number of monsters:",default="5",validate=lambda value: (value.isdigit() and int(value) >= int(minimum_enemies) and int(value) <= 10)).ask()
    if maximum_enemies is None:
        return None

    return difficulty, int(minimum_enemies), int(maximum_enemies)

def select_monsters(monsters,filter):
    monster_choices = [questionary.Choice(title=name, value=name, checked=name in filter["selected_names"]) for name in  sorted(monsters.keys())]
    selected_monsters = questionary.checkbox("Select Monsters:", choices=monster_choices).ask()
        
    if selected_monsters is not None:
        filter["selected_names"] = set(selected_monsters)
        
def select_monsters_by_cr(monsters,filter):
    availible_crs = sorted(set(monster.cr for monster in monsters.values()))

    cr_choices = [questionary.Choice(title= f"CR {cr}", value=cr, checked=cr in filter["selected_crs"]) for cr in availible_crs]
    selected_crs = questionary.checkbox("Select Monster CRs:", choices=cr_choices).ask()
    
    if selected_crs is not None:
        filter["selected_crs"] = set(selected_crs)

def select_monster_types(monsters,filter):
    availible_types = sorted(set(monster.monster_type for monster in monsters.values()))
    type_choices = [questionary.Choice(title=monster_type.capitalize(), value=monster_type, checked=monster_type in filter["selected_types"]) for monster_type in availible_types]
    selected_types = questionary.checkbox("Select Monster Types:", choices=type_choices).ask()

    if selected_types is not None:
        filter["selected_types"] = set(selected_types)

def choose_monster_filters(monsters):
    filter = create_filter()

    while True:
        current_monsters = apply_filter(monsters,filter)

        custom_style = questionary.Style([("selected", "fg:#F4320B"),("pointer", "fg:#F4320B"),("highlighted", "fg:#F4320B"),("text", "fg:#F87C63")])

        choice = questionary.select(f"Monster Filtering ({len(current_monsters)} monsters available)",
            choices=["Challenge Rating Filter","Monster Type Filter","Manual Monster Selection","Disable All Filters","Use All Monsters","Generate Encounters"],style=custom_style).ask()

        if choice is None:
            return None
        elif choice == "Challenge Rating Filter":
            select_monsters_by_cr(monsters, filter)
        elif choice == "Monster Type Filter":
            select_monster_types(monsters, filter)
        elif choice == "Manual Monster Selection":
            select_monsters(monsters, filter)
        elif choice == "Disable All Filters":
            filter = create_filter()
        elif choice == "Use All Monsters":
            return monsters
        elif choice == "Generate Encounters":
            if not current_monsters:
                console.print("[orange1]No monsters match your filters![/orange1]")
                continue

            return current_monsters

def generate_and_display_encounters(monsters, party):
    settings = choose_encounter_settings()

    if settings is None:
        console.print("[orange1]Cancelled.[/orange1]")
        return

    difficulty, minimum_enemies, maximum_enemies = settings

    with Progress(SpinnerColumn(style="white"),
    TextColumn("[red]{task.description}"),
    BarColumn(
        style="dim white",
        complete_style="white",
        finished_style="white",
        pulse_style="white"
    ),console=console) as progress:

        task = progress.add_task(f"Generating encounters...",total=5000000)

        encounters = generate_encounters(monsters,minimum_enemies=minimum_enemies,maximum_enemies=maximum_enemies,max_results=5000000,progress=progress,task = task)

    console.print(f"[red]Searching for best encounters...[red]")
    party_thresholds = calculate_party_thresholds(party)

    matching_encounters = find_best_encounter(encounters, monsters, party, difficulty)

    ranked_encounters = rank_encounters(matching_encounters,monsters,party,party_thresholds,difficulty)

    console.print(f"\n[bold red]Encounter Results[/bold red]")
    console.print(f"Target difficulty: {difficulty}")
    console.print(f"Encounters generated: {len(encounters)}")
    console.print(f"Matching encounters: {len(ranked_encounters)}")

    if not ranked_encounters:
        console.print("[orange1]No matching encounters found. Try increasing the maximum monster count or choosing another difficulty.[/orange1]")
        return

    table = Table(title="Top Encounters", title_style="bold white", border_style="red")
    table.add_column("No.", justify="center")
    table.add_column("Monsters", justify="left")
    table.add_column("Adjusted XP", justify="center")
    table.add_column("Difficulty", justify="center")
    table.add_column("Difficulty Difference", justify="center")

    for index, result in enumerate(ranked_encounters[:5], start=1):
        encounter = result[0]
        analysis = result[1]
        xp_score = result[2]

        monster_names = []
        for name,quantity in encounter.monsters.items():
            monster_names.append(f"{name} x{quantity}")
        monster_text = ", ".join(monster_names)

        table.add_row(str(index), monster_text, str(round(analysis.adjusted_xp)), analysis.difficulty, str(round(xp_score, 2)))
    console.print(table)

    best = ranked_encounters[0]
    encounter = best[0]
    analysis = best[1]
    xp_score = best[2]

    table = Table(title="Recommended Encounter",title_style="bold white",border_style="red")

    table.add_column("Details", style="bold white", justify="left")
    table.add_column("Value", justify="center")

    monster_text = []
    for name, quantity in encounter.monsters.items():
        monster_text.append(f"{name} x{quantity}")

    table.add_row("Monsters", ", ".join(monster_text))
    table.add_row("Adjusted XP", f"{analysis.adjusted_xp:.0f}")
    table.add_row("Difficulty", analysis.difficulty)
    table.add_row("Difficulty Difference", f"{xp_score:.2f}")

    console.print(table)



def main():
    show_welcome_screen()
    monsters = load_game_monsters()
    party = create_party()

    if party is not None:
        console.print("\n[bold red]Party created[/bold red]")

        filtered_monsters = choose_monster_filters(monsters)
        if filtered_monsters is None:
            return

        generate_and_display_encounters(filtered_monsters, party)

if __name__ == "__main__":
    main()
