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
            "Energizing": "Euphoric",
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
    'Cocaine': 150,
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
    'Horse Semen': 9,
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
    rule = effect_rules.get(ingredient, {"replaces": {}, "adds": []})
    replaces = rule.get("replaces", {})
    adds = rule.get("adds", [])

    original_effects = list(effects)
    replacements = {}
    removed_effects = set()

    # Step 1: Plan all replacements based on original state
    for old in original_effects:
        if old in replaces:
            new = replaces[old]
            replacements[old] = new
            removed_effects.add(old)

    # Step 2: Apply replacements
    updated_effects = []
    for eff in original_effects:
        if eff in replacements:
            new_eff = replacements[eff]
            updated_effects.append(new_eff)
        else:
            updated_effects.append(eff)

    # Step 3: Apply static additions, even if it was replaced out
    for eff in adds:
        if eff not in updated_effects or eff in removed_effects:
            if len(updated_effects) < MAX_EFFECTS:
                updated_effects.append(eff)

    # Step 4: De-dupe and return
    return sorted(set(updated_effects))

def filter_base_products(starting_product_choice):
    if starting_product_choice == 0:
        return base_products
    elif starting_product_choice == 1:
        return {k: v for k, v in base_products.items() if k in ['OG Kush', 'Granddaddy Purple', 'Green Crack', 'Sour Diesel']}
    elif starting_product_choice == 2:
        return {'Meth': []}
    elif starting_product_choice == 3:
        return {'Cocaine': []}
    elif starting_product_choice == 4:
        return {'OG Kush': base_products.get('OG Kush', [])}
    elif starting_product_choice == 5:
        return {'Granddaddy Purple': base_products.get('Granddaddy Purple', [])}
    elif starting_product_choice == 6:
        return {'Green Crack': base_products.get('Green Crack', [])}
    else:
        return base_products

def bfs_worker_profit(args, progress_queue):
    base_name, base_effects, max_depth, effect_rules = args
    best_result = None
    best_profit = float('-inf')

    visited = {}
    queue = deque()
    steps = 0

    initial_state = {
        "effects": base_effects.copy(),
        "path": []
    }
    queue.append(initial_state)
    visited[tuple(sorted(base_effects))] = 0

    while queue:
        current = queue.popleft()
        steps += 1

        if steps % 1000 == 0:
            progress_queue.put(1000)

        # Calculate profit
        unique_effects = sorted(set(current["effects"]))
        if len(current["path"]) <= max_depth:
            base_price = base_prices.get(base_name, 0)
            ingredient_cost = sum(ingredient_costs.get(ing, 0) for ing in current["path"])
            total_multiplier = 1.0 + sum(effect_multipliers.get(eff, 0.0) for eff in unique_effects)
            final_value = base_price * total_multiplier
            profit = final_value - ingredient_cost

            if profit > best_profit:
                best_result = {
                    "base": base_name,
                    "effects": unique_effects,
                    "path": current["path"]
                }
                best_profit = profit

        if len(current["path"]) >= max_depth:
            continue

        for ingredient in effect_rules:
            new_effects = apply_ingredient(current["effects"], ingredient)
            new_path = current["path"] + [ingredient]
            signature = tuple(sorted(new_effects))

            if visited.get(signature, float('inf')) > len(new_path):
                visited[signature] = len(new_path)
                queue.append({
                    "effects": new_effects,
                    "path": new_path
                })

    progress_queue.put(steps % 1000)
    return best_result

def bfs_solver_multiprocessing_profit(starting_product_choice, max_depth=8):
    filtered_products = filter_base_products(starting_product_choice)

    total = sum(len(effect_rules) ** i for i in range(1, max_depth + 1)) * len(filtered_products)

    args_list = [
        (base, effects, max_depth, effect_rules)
        for base, effects in filtered_products.items()
    ]

    manager = Manager()
    progress_queue = manager.Queue()

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(bfs_worker_profit, args, progress_queue) for args in args_list]

        with tqdm(total=total, desc="💸 Calculating Profit...", ncols=80) as pbar:
            result = None
            while any(f.done() is False for f in futures):
                try:
                    while not progress_queue.empty():
                        pbar.update(progress_queue.get_nowait())
                except:
                    pass
                time.sleep(0.1)

            while not progress_queue.empty():
                pbar.update(progress_queue.get_nowait())

            best = None
            best_profit = float('-inf')
            for future in futures:
                res = future.result()
                if res:
                    base_name = res['base']
                    base_price = base_prices.get(base_name, 0)
                    cost = sum(ingredient_costs.get(i, 0) for i in res["path"])
                    multiplier = 1.0 + sum(effect_multipliers.get(e, 0.0) for e in res["effects"])
                    value = base_price * multiplier
                    profit = value - cost

                    if profit > best_profit:
                        best_profit = profit
                        best = res
            return best

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

def print_banner():
    banner = pyfiglet.figlet_format("S1MP", font="doom")
    print(banner)
    print("🔬 Schedule 1 Mix Pathfinder\n")

def prompt_user_for_effects():
    import os

    def clear_screen():
        os.system('cls' if "nt" in os.name else 'clear')
    
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
        rule = effect_rules.get(ingredient, {"replaces": {}, "adds": []})
        replaces = rule.get("replaces", {})
        adds = rule.get("adds", [])

        original_effects = list(effects)
        replacements = {}
        removed_effects = set()

        for old in original_effects:
            if old in replaces:
                replacements[old] = replaces[old]
                removed_effects.add(old)

        updated_effects = []
        replaced_log = []
        for eff in original_effects:
            if eff in replacements:
                new_eff = replacements[eff]
                updated_effects.append(new_eff)
                replaced_log.append((eff, new_eff))
            else:
                updated_effects.append(eff)

        added_log = []
        for eff in adds:
            if eff not in updated_effects or eff in removed_effects:
                if len(updated_effects) < MAX_EFFECTS:
                    updated_effects.append(eff)
                    added_log.append(eff)

        print(f"\nStep {i}/{len(solution['path'])}:")
        print(f"Add: {ingredient}")
        print("Effects replaced:")
        if replaced_log:
            for old, new in replaced_log:
                print(f" - {old} → {new}")
        else:
            print(" (none)")
        print("Effects gained:")
        if added_log:
            for eff in added_log:
                print(f" + {eff}")
        else:
            print(" (none)")
        print("All effects after adding:")
        print(f" → {', '.join(sorted(set(updated_effects)))}")

        effects = sorted(set(updated_effects))

if __name__ == "__main__":
    try:
        from multiprocessing import freeze_support
        freeze_support()

        print_banner()
        print("1. Find a mix with desired effects")
        print("2. Find the most profitable mix\n")

        while True:
            mode = input("Choose mode (1 or 2): ").strip()
            if mode in ("1", "2"):
                break
            print("❌ Invalid choice. Please type 1 or 2.")

        starting_choice = prompt_starting_product()

        if mode == "1":
            desired = prompt_user_for_effects()
            solution = bfs_solver_multiprocessing(desired, starting_choice)

            if solution:
                print("✅ Solution Found!")
                print(f"Start with: {solution['base']}")
                print(f"Ingredients: {' -> '.join(solution['path'])}")
                print(f"Final Effects: {', '.join(solution['effects'])}")
                
                # Value/Profit Calculation
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
                print(f"📊 Profit: ${profit:.2f} per baggie")

                print_debug_steps(solution, show_debug=True)
            else:
                print("❌ No valid combination found within depth limit.")
        
        elif mode == "2":
            max_ingredients = 8
            base_names = list(base_products.keys())
            base_name = base_names[starting_choice] if starting_choice < len(base_names) else "OG Kush"
            solution = bfs_solver_multiprocessing_profit(base_name, max_depth=max_ingredients)

            if solution:
                print("💸 Best Profit Mix Found!")
                print(f"Start with: {solution['base']}")
                print(f"Ingredients: {' -> '.join(solution['path'])}")
                print(f"Final Effects: {', '.join(solution['effects'])}")

                base_price = base_prices.get(solution['base'], 0)
                ingredient_cost = sum(ingredient_costs.get(ing, 0) for ing in solution["path"])
                total_multiplier = 1.0 + sum(effect_multipliers.get(eff, 0.0) for eff in solution["effects"])
                final_value = base_price * total_multiplier
                profit = final_value - ingredient_cost

                print("\n💸 Final Financial Summary:")
                print(f"🧪 Base Product: {solution['base']} (Recommended price: ${base_price})")
                print(f"🧾 Ingredients Used: {', '.join(solution['path'])}")
                print(f"💰 Ingredient Cost: ${ingredient_cost:.2f}")
                print(f"📈 Total Multiplier: x{total_multiplier:.2f}")
                print(f"🏷 Final Product Value: ${final_value:.2f}")
                print(f"📊 Profit: ${profit:.2f}")

                print_debug_steps(solution, show_debug=True)
            else:
                print("❌ No profitable mix found.")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
