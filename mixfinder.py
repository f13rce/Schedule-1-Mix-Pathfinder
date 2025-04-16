from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import pyfiglet
from multiprocessing import Queue
from multiprocessing import Manager
import time

# Base products and their starting effects
base_products = {
    'OG Kush': ['Calming'],
    'Granddaddy Purple': ['Sedating'],
    'Green Crack': ['Energizing'],
    'Sour Diesel': ['Refreshing']
}

# Full list of ingredients and how they transform effects
# Format: ingredient -> list of {adds, replaces}
effect_rules = {
    "Banana": {
        "replaces": {
            "Smelly": "Anti-Gravity",
            "Disorienting": "Focused",
            "Paranoia": "Jennerising",
            "Long-Faced": "Refreshing",
            "Focused": "Seizure-Inducing",
            "Toxic": "Smelly",
            "Calming": "Sneaky",
            "Cyclopean": "Thought-Provoking",
            "Energizing": "Thought-Provoking"
        },
        "adds": ["Gingeritis"]
    },
    "Paracetamol": {
        "replaces": {
            "Munchies": "Anti-Gravity",
            "Electrifying": "Athletic",
            "Paranoia": "Balding",
            "Energizing": "Balding",
            "Spicy": "Bright-Eyed",
            "Foggy": "Calming",
            "Focused": "Gingeritis",
            "Calming": "Slippery",
            "Glowing": "Toxic",
            "Toxic": "Tropic Thunder"
        },
        "adds": ["Sneaky"]
    },
    "Mouth Wash": {
        "replaces": {
            "Calming": "Anti-Gravity",
            "Focused": "Jennerising",
            "Explosive": "Sedating",
            "Calorie-Dense": "Sneaky"
        },
        "adds": ["Balding"]
    },
    "Motor Oil": {
        "replaces": {
            "Paranoia": "Anti-Gravity",
            "Energizing": "Munchies",
            "Munchies": "Schizophrenic",
            "Euphoric": "Sedating",
            "Foggy": "Toxic"
        },
        "adds": ["Slippery"]
    },
    "Donut": {
        "replaces": {
            "Shrinking": "Energizing",
            "Focused": "Euphoric",
            "Calorie-Dense": "Explosive",
            "Jenerising": "Gingeritis",
            "Anti-Gravity": "Slippery",
            "Balding": "Sneaky"
        },
        "adds": ["Calorie-Dense"]
    },
    "Cuke": {
        "replaces": {
            "Munchies": "Athletic",
            "Slippery": "Munchies",
            "Foggy": "Cyclopean",
            "Toxic": "Euphoric",
            "Euphoric": "Laxative",
            "Sneaky": "Paranoia",
            "Gingeritis": "Thought-Provoking"
        },
        "adds": ["Energizing"]
    },
    "Energy Drink": {
        "replaces": {
            "Schizophenic": "Balding",
            "Glowing": "Disorienting",
            "Disorienting": "Electrifying",
            "Euphoric": "Energizing",
            "Spicy": "Euphoric",
            "Foggy": "Laxative",
            "Sedating": "Munchies",
            "Focused": "Shrinking",
            "Tropic Thunder": "Sneaky"
        },
        "adds": ["Athletic"]
    },
    "Iodine": {
        "replaces": {
            "Calorie-Dense": "Gingeritis",
            "Foggy": "Paranoia",
            "Calming": "Balding",
            "Euphoric": "Seizure-Inducing",
            "Toxic": "Sneaky",
            "Refreshing": "Thought-Provoking"
        },
        "adds": ["Jennerising"]
    },
    "Mega Bean": {
        "replaces": {
            "Sneaky": "Calming",
            "Thought-Provoking": "Energizing",
            "Energizing": "Cyclopean",
            "Focused": "Disorienting",
            "Shrinking": "Electrifying",
            "Seizure-Inducing": "Focused",
            "Calming": "Glowing",
            "Athletic": "Laxative",
            "Jennerising": "Paranoia",
            "Slippery": "Toxic"
        },
        "adds": ["Foggy"]
    },
    "Battery": {
        "replaces": {
            "Laxative": "Calorie-Dense",
            "Electrifying": "Euphoric",
            "Cyclopean": "Glowing",
            "Shrinking": "Munchies",
            "Munchies": "Tropic Thunder",
            "Euphoric": "Zombifying"
        },
        "adds": ["Bright-Eyed"]
    },
    "Viagra": {
        "replaces": {
            "Euphoric": "Bright-Eyed",
            "Laxative": "Calming",
            "Athletic": "Sneaky",
            "Disorienting": "Toxic"
        },
        "adds": ["Tropic Thunder"]
    },
    "Gasoline": {
        "replaces": {
            "Paranoia": "Calming",
            "Electrifying": "Disorienting",
            "Energizing": "Spicy",
            "Shrinking": "Focused",
            "Laxative": "Foggy",
            "Disorienting": "Glowing",
            "Munchies": "Sedating",
            "Gingeritis": "Smelly",
            "Jennerising": "Sneaky",
            "Euphoric": "Spicy",
            "Sneaky": "Tropic Thunder"
        },
        "adds": ["Toxic"]
    },
    "Horse Semen": {
        "replaces": {
            "Anti-Gravity": "Calming",
            "Thought-Provoking": "Electrifying",
            "Gingeritis": "Refreshing"
        },
        "adds": ["Long-Faced"]
    },
    "Flu Medicine": {
        "replaces": {
            "Calming": "Bright-Eyed",
            "Focused": "Calming",
            "Laxative": "Euphoric",
            "Cyclopean": "Foggy",
            "Thought-Provoking": "Gingeritis",
            "Athletic": "Munchies",
            "Shrinking": "Paranoia",
            "Electrifying": "Refreshing",
            "Munchies": "Slippery",
            "Euphoric": "Toxic"
        },
        "adds": ["Sedating"]
    },
    "Addy": {
        "replaces": {
            "Long-Faced": "Electrifying",
            "Foggy": "Energizing",
            "Explosive": "Euphoric",
            "Sedating": "Gingeritis",
            "Glowing": "Refreshing"
        },
        "adds": ["Thought-Provoking"]
    },
    "Chili": {
        "replaces": {
            "Sneaky": "Bright-Eyed",
            "Athletic": "Euphoric",
            "Laxative": "Long-Faced",
            "Shrinking": "Refreshing",
            "Munchies": "Toxic",
            "Anti-Gravity": "Tropic Thunder"
        },
        "adds": ["Spicy"]
    }
}

# Desired goal checker
def is_goal(state_effects, desired_effects):
    return all(effect in state_effects for effect in desired_effects)

MAX_EFFECTS = 8  # Set this globally

def apply_ingredient(effects, ingredient):
    new_effects = effects.copy()
    rule = effect_rules.get(ingredient, {"replaces": {}, "adds": []})

    # 1. Apply replacements
    for old, new in rule.get("replaces", {}).items():
        if old in new_effects:
            new_effects.remove(old)
            if new and new not in new_effects:
                new_effects.append(new)

    # 2. Add static effects, if room
    for eff in rule.get("adds", []):
        if eff not in new_effects and len(new_effects) < MAX_EFFECTS:
            new_effects.append(eff)

    return sorted(set(new_effects))

# BFS worker for a single base product (standalone, must be top-level for multiprocessing)
def bfs_worker_process(args, progress_queue):
    base_name, base_effects, desired_effects, max_depth, effect_rules = args

    visited = set()
    queue = deque()
    steps = 0

    initial_state = {
        "base": base_name,
        "effects": base_effects,
        "path": [],
    }
    queue.append(initial_state)
    visited.add(tuple(sorted(base_effects)))

    while queue:
        current = queue.popleft()
        steps += 1

        # ✅ Send periodic progress updates
        if steps % 1000 == 0:
            progress_queue.put(1000)

        if all(effect in current["effects"] for effect in desired_effects):
            progress_queue.put(steps % 1000)  # send remaining step count
            return current

        if len(current["path"]) >= max_depth:
            continue

        for ingredient in effect_rules:
            new_effects = current["effects"].copy()
            rule = effect_rules.get(ingredient, {"replaces": {}, "adds": []})

            for old, new in rule.get("replaces", {}).items():
                if old in new_effects:
                    new_effects.remove(old)
                    if new and new not in new_effects:
                        new_effects.append(new)

            for eff in rule.get("adds", []):
                if eff not in new_effects and len(new_effects) < MAX_EFFECTS:
                    new_effects.append(eff)

            new_effects = sorted(set(new_effects))
            new_path = current["path"] + [ingredient]
            signature = tuple(new_effects)

            if signature not in visited:
                visited.add(signature)
                queue.append({
                    "base": base_name,
                    "effects": new_effects,
                    "path": new_path
                })

    progress_queue.put(steps % 1000)  # Final few steps
    return None

# Multi-process BFS dispatcher
def bfs_solver_multiprocessing(desired_effects, max_depth=16):
    total_per_base = sum(len(effect_rules) ** i for i in range(1, max_depth + 1))
    total = total_per_base * len(base_products)

    args_list = [
        (base, effects, desired_effects, max_depth, effect_rules)
        for base, effects in base_products.items()
    ]

    manager = Manager()
    progress_queue = manager.Queue()

    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(bfs_worker_process, args, progress_queue)
            for args in args_list
        ]

        with tqdm(
            total=total,
            desc="🔬 Finding your mix...",
            bar_format="{l_bar}{bar}| {percentage:3.0f}% | {rate_fmt}",
            ncols=80,
        ) as pbar:
            result = None
            while any(f.done() is False for f in futures):
                try:
                    while not progress_queue.empty():
                        pbar.update(progress_queue.get_nowait())
                except:
                    pass
                time.sleep(0.1)  # Slight delay to reduce CPU usage

            # Final progress update
            while not progress_queue.empty():
                pbar.update(progress_queue.get_nowait())

            for future in futures:
                res = future.result()
                if res:
                    executor.shutdown(wait=False, cancel_futures=True)
                    return res

    return None

def prompt_user_for_effects():
    import os

    def clear_screen():
        os.system('cls' if "nt" in os.name else 'clear')
        
    def print_banner():
        banner = pyfiglet.figlet_format("S1MP", font="doom")
        print(banner)
        print("🔬 Schedule 1 Mix Pathfinder\n")
    
    # Step 1: Build full list of all possible effects
    all_effects = set()
    for rule in effect_rules.values():
        all_effects.update(effect for effect in rule.get("adds", []) if effect)
        all_effects.update(effect for effect in rule.get("replaces", {}).values() if effect)

    all_effects = sorted(all_effects)
    selected = []

    print("\n🧪 Schedule 1 Mix Selector")
    print("Pick effects you want your product to have!\n")

    while True:
        clear_screen()
        print_banner()
        remaining = [e for e in all_effects if e not in selected]

        if not remaining:
            print("🎉 You've selected all known effects! Let's mix!\n")
            break

        print("Available effects:")
        for idx, effect in enumerate(remaining):
            print(f"{idx}: {effect}")
        print("\nType a number, name (or part of one), or 'm' to mix.\n")

        print(f"Current effects: {selected}")
        choice = input("Pick an effect: ").strip().lower()

        if choice in ("m", "mix"):
            break

        # Match by number
        if choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(remaining):
                selected_effect = remaining[idx]
                selected.append(selected_effect)
                print(f"✅ Added: {selected_effect}\n")
                continue
            else:
                print("❌ That number is out of range.\n")
                continue

        # Match by partial text
        matches = [e for e in remaining if choice in e.lower()]
        if len(matches) == 1:
            selected.append(matches[0])
            print(f"✅ Added: {matches[0]}\n")
            if len(selected) >= 8:
                print("Maximum effects reached. Starting to mix...")
                break
        elif len(matches) > 1:
            print("⚠️ Multiple matches found:")
            for e in matches:
                print(f" - {e}")
            print("Please be more specific.\n")
        else:
            print("❌ No match found. Try again.\n")

    return selected

def print_debug_steps(solution, show_debug=True):
    if not show_debug:
        return

    print("\n🔍 Debugging Mix Path...\n")
    print(f"Start with: {solution['base']}")
    effects = base_products[solution['base']].copy()

    for i, ingredient in enumerate(solution["path"], 1):
        rule = effect_rules[ingredient]
        prev_effects = effects.copy()

        replaced = []
        added = []

        # Apply replacements
        for old, new in rule.get("replaces", {}).items():
            if old in effects:
                replaced.append((old, new))
                effects.remove(old)
                if new and new not in effects:
                    effects.append(new)

        # Apply additions
        for eff in rule.get("adds", []):
            if eff not in effects and len(effects) < MAX_EFFECTS:
                added.append(eff)
                effects.append(eff)

        print(f"\nStep {i}/{len(solution['path'])}:")
        print(f"Add: {ingredient}")
        print("Effects replaced:")
        for old, new in replaced:
            print(f" - {old} → {new if new else '❌ removed'}")
        print("Effects gained:")
        for eff in added:
            print(f" + {eff}")
        print("All effects after adding:")
        print(f" → {', '.join(sorted(effects))}")

if __name__ == "__main__":
    try:
        from multiprocessing import freeze_support
        freeze_support()

        desired = prompt_user_for_effects()
        solution = bfs_solver_multiprocessing(desired)

        if solution:
            print("✅ Solution Found!")
            print(f"Start with: {solution['base']}")
            print(f"Ingredients: {' -> '.join(solution['path'])}")
            print(f"Final Effects: {', '.join(solution['effects'])}")
            
            print_debug_steps(solution, show_debug=True)
        else:
            print("❌ No valid combination found within depth limit.")
    except KeyboardInterrupt as e:
        print("Goodbye :)")
