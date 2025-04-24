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
    'Sour Diesel': ['Refreshing'],
    'Meth': [],
    'Cocaine': [],
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

# Base prices for each product
base_prices = {
    'OG Kush': 38,
    'Sour Diesel': 40,
    'Green Crack': 43,
    'Granddaddy Purple': 44,
    'Meth': 70,
    'Cocaine': 80
}

# Ingredient costs
ingredient_costs = {
    'Cuke': 2,
    'Banana': 2,
    'Paracetamol': 3,
    'Donut': 3,
    'Viagra': 4,
    'Mouth Wash': 4,
    'Flu Medicine': 5,
    'Gasoline': 5,
    'Energy Drink': 6,
    'Motor Oil': 6,
    'Mega Bean': 7,
    'Chili': 7,
    'Battery': 8,
    'Iodine': 8,
    'Addy': 9,
    'Horse Semen': 9
}

# Effect price multipliers
effect_multipliers = {
    'Anti-Gravity': 0.54,
    'Athletic': 0.32,
    'Balding': 0.30,
    'Bright-Eyed': 0.40,
    'Calming': 0.10,
    'Calorie-Dense': 0.28,
    'Cyclopean': 0.56,
    'Disorienting': 0.00,
    'Electrifying': 0.50,
    'Energizing': 0.22,
    'Euphoric': 0.18,
    'Explosive': 0.00,
    'Focused': 0.16,
    'Foggy': 0.36,
    'Gingeritis': 0.20,
    'Glowing': 0.48,
    'Jennerising': 0.42,
    'Laxative': 0.00,
    'Long Faced': 0.52,
    'Munchies': 0.12,
    'Paranoia': 0.00,
    'Refreshing': 0.14,
    'Schizophrenia': 0.00,
    'Sedating': 0.26,
    'Seizure-Inducing': 0.00,
    'Shrinking': 0.60,
    'Slippery': 0.34,
    'Smelly': 0.00,
    'Sneaky': 0.24,
    'Spicy': 0.38,
    'Thought-Provoking': 0.44,
    'Toxic': 0.00,
    'Tropic Thunder': 0.46,
    'Zombifying': 0.58
}

# Desired goal checker
def is_goal(state_effects, desired_effects):
    return all(effect in state_effects for effect in desired_effects)

MAX_EFFECTS = 8  # Set this globally

def apply_ingredient(effects, ingredient):
    new_effects = effects.copy()
    rule = effect_rules.get(ingredient, {"replaces": {}, "adds": []})

    # Phase 1: Prepare replacements safely (no collision)
    to_remove = []
    to_add = []
    current_set = set(new_effects)

    for old, new in rule.get("replaces", {}).items():
        if old in current_set and new and new not in current_set:
            to_remove.append(old)
            to_add.append(new)

    # Phase 2: Apply them
    for eff in to_remove:
        new_effects.remove(eff)
    for eff in to_add:
        new_effects.append(eff)

    # Phase 3: Add static effects (if room)
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

            # Phase 1: batch replacements
            to_remove = []
            to_add = []

            current_set = set(new_effects)
            for old, new in rule.get("replaces", {}).items():
                if old in current_set and new and new not in current_set:
                    to_remove.append(old)
                    to_add.append(new)

            for eff in to_remove:
                new_effects.remove(eff)
            for eff in to_add:
                new_effects.append(eff)

            # Phase 2: Add static effects
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
def bfs_solver_multiprocessing(desired_effects, starting_product_choice, max_depth=16):
    total_per_base = sum(len(effect_rules) ** i for i in range(1, max_depth + 1))

    # Filter base products
    if starting_product_choice == 0:
        filtered_products = base_products
    elif starting_product_choice == 1:
        filtered_products = {k: v for k, v in base_products.items() if k in ['OG Kush', 'Granddaddy Purple', 'Green Crack', 'Sour Diesel']}
    elif starting_product_choice == 2:
        filtered_products = {'Meth': []}
    elif starting_product_choice == 3:
        filtered_products = {'Cocaine': []}
    elif starting_product_choice == 4:
        filtered_products = {'OG Kush': base_products.get('OG Kush', [])}
    elif starting_product_choice == 5:
        filtered_products = {'Granddaddy Purple': base_products.get('Granddaddy Purple', [])}
    elif starting_product_choice == 6:
        filtered_products = {'Green Crack': base_products.get('Green Crack', [])}
    else:
        filtered_products = base_products  # fallback

    total = total_per_base * len(filtered_products)

    args_list = [
        (base, effects, desired_effects, max_depth, effect_rules)
        for base, effects in filtered_products.items()
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

def prompt_starting_product():
    print("\n🌱 Which starting product would you like?")
    options = [
        "Anything",
        "Weed only",
        "Meth only",
        "Cocaine only",
        "OG Kush",
        "Granddaddy Purple",
        "Green Crack"
    ]

    for i, name in enumerate(options):
        print(f"{i}: {name}")
    
    while True:
        choice = input("\nPick an option (number): ").strip()
        if choice.isdigit() and 0 <= int(choice) < len(options):
            return int(choice)
        print("❌ Invalid choice. Try again.")

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
            mult = effect_multipliers.get(effect, 0.0)
            print(f"{idx}: {effect} (+{mult:.2f}x)")
        print("\nType a number, name (or part of one), or 'm' to mix.\n")

        print(f"Current effects: {selected}")
        total_multiplier = 1.0 + sum(effect_multipliers.get(e, 0.0) for e in selected)
        print(f"\n🔢 Total effect multiplier: x{total_multiplier:.2f}")
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

        starting_choice = prompt_starting_product()
        desired = prompt_user_for_effects()
        solution = bfs_solver_multiprocessing(desired, starting_choice)

        if solution:
            print("✅ Solution Found!")
            print(f"Start with: {solution['base']}")
            print(f"Ingredients: {' -> '.join(solution['path'])}")
            print(f"Final Effects: {', '.join(solution['effects'])}")
            
            # --- Value/Profit Calculation ---
            base_name = solution['base']
            base_price = base_prices.get(base_name, 0)
            ingredient_cost = sum(ingredient_costs.get(ing, 0) for ing in solution["path"])
            total_multiplier = 1.0 + sum(effect_multipliers.get(eff, 0.0) for eff in solution["effects"])
            final_value = base_price * total_multiplier
            profit = final_value - ingredient_cost

            print("\n💸 Final Financial Summary:")
            print(f"🧪 Base Product: {base_name} (Recommended price: ${base_price})")
            print(f"🧾 Ingredients Used: {', '.join(solution['path'])}")
            print(f"💰 Ingredient Cost: ${ingredient_cost:.2f}")
            print(f"📈 Total Multiplier: x{total_multiplier:.2f}")
            print(f"🏷 Final Product Value: ${final_value:.2f}")
            print(f"📊 Profit: ${profit:.2f}")
            
            print_debug_steps(solution, show_debug=True)
        else:
            print("❌ No valid combination found within depth limit.")
    except KeyboardInterrupt as e:
        print("Goodbye :)")
