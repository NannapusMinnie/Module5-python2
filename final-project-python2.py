import math

# =======================
# Helper Functions
# =======================

def validate_positive(value, name="Value"):
    if value <= 0:
        raise ValueError(f"{name} must be a positive number.")

def choose_time_unit():
    """Ask the user to select a time unit and return multiplier and name."""
    print("\nSelect time unit:")
    print("1. Day")
    print("2. Week")
    print("3. Month")
    print("4. Year")
    unit_choice = input("Enter choice: ")

    if unit_choice == '1':
        return 1, "day"
    elif unit_choice == '2':
        return 7, "week"
    elif unit_choice == '3':
        return 30, "month"
    elif unit_choice == '4':
        return 365, "year"
    else:
        print("Invalid choice.")
        return None, None

# =======================
# Decorator for Time Unit
# =======================

def with_time_unit(func):
    """Decorator to ask user for time unit and pass multiplier and unit_name."""
    def wrapper(*args, **kwargs):
        multiplier, unit_name = choose_time_unit()
        if multiplier is None:
            return
        return func(*args, multiplier=multiplier, unit_name=unit_name, **kwargs)
    return wrapper

# =======================
# Save Plan Function
# =======================

def save_plan(plans, allowance, expenses, duration, goal, unit="day", multiplier=1):
    """Save a plan into plans dictionary."""
    name = input("Enter a name for your plan: ")
    plans[name] = {
        "allowance": allowance,
        "expenses": expenses,
        "net": allowance - expenses,
        "goal": goal,
        "unit": unit,
        "multiplier": multiplier,
        "saved_so_far": 0,
        "days_passed": 0,
        "periods": duration
    }
    print("🎉 Plan saved successfully!")

# =======================
# Menu 1: Check Goal Feasibility
# =======================

@with_time_unit
def menu_check_feasibility(plans, multiplier, unit_name):
    """Menu 1: Checks if the user's savings goal is possible."""
    print(f"\n=== CHECK IF GOAL IS POSSIBLE ({unit_name}) ===\n")
    try:
        allowance = float(input(f"Enter allowance per {unit_name}: "))
        expenses = float(input(f"Enter expenses per {unit_name}: "))
        duration = int(input(f"Enter number of {unit_name}s you plan to save for: "))
        goal = float(input("Enter your savings goal: "))

        validate_positive(allowance, "Allowance")
        validate_positive(duration, "Duration")
        validate_positive(goal, "Goal")
    except ValueError as e:
        print("Input error:", e)
        return

    money_saved = allowance - expenses
    total_saved = money_saved * duration
    max_possible = allowance * duration

    print("\n--- RESULT ---")

    # CASE 1: Goal possible
    if total_saved >= goal:
        print("✅ Goal is possible with your current plan!")
        extra = total_saved - goal
        print(f"You will have {extra:.2f} extra money at the end.")

        save_choice = input("Do you want to save this plan? (y/n): ").lower()
        if save_choice == 'y':
            save_plan(plans, allowance, expenses, duration, goal, unit=unit_name, multiplier=multiplier)
        return

    # CASE 2: Goal impossible even if cutting all expenses
    if max_possible < goal:
        print("❌ Goal is NOT possible even if you cut ALL expenses.")
        missing = goal - max_possible
        print(f"You would still be short by {missing:.2f}.")
        return

    # CASE 3: Possible if cutting some expenses
    print("⚠️ Goal is NOT possible with your current spending.")
    print("However, it IS possible if you reduce your expenses.")

    required_per_period = goal / duration
    needed_cut = required_per_period - money_saved

    print(f"You must cut your expenses by at least {needed_cut:.2f} per {unit_name}.")

    adjust = input("Do you want to adjust expenses and save this plan? (y/n): ").lower()
    if adjust == 'y':
        new_expenses = expenses - needed_cut
        save_plan(plans, allowance, new_expenses, duration, goal, unit=unit_name, multiplier=multiplier)

# =======================
# Menu 2: Time Needed
# =======================

@with_time_unit
def menu_time_needed(plans, multiplier, unit_name):
    """Menu 2: Calculates time to reach a goal."""
    print(f"\n=== CALCULATE TIME TO REACH GOAL ({unit_name}) ===\n")
    try:
        allowance = float(input(f"Allowance per {unit_name}: "))
        expenses = float(input(f"Expenses per {unit_name}: "))
        goal = float(input("Savings goal: "))

        validate_positive(allowance, "Allowance")
        validate_positive(goal, "Goal")
    except ValueError as e:
        print("Invalid input:", e)
        return

    net = allowance - expenses
    if net <= 0:
        print("❌ You cannot save any money with your current spending.")
        return

    use_interest = input("Add interest? (y/n): ").lower()

    if use_interest == 'n':
        periods_needed = goal / net
        days = periods_needed * multiplier
        print("\n--- RESULT WITHOUT INTEREST ---")
        print(f"Time needed: {periods_needed:.2f} {unit_name}s")
        print(f"≈ {days:.0f} days")
        print(f"≈ {days/7:.2f} weeks")
        print(f"≈ {days/30:.2f} months")
        print(f"≈ {days/365:.2f} years")
    else:
        try:
            interest_rate = float(input("Enter annual interest rate (%, e.g., 3 for 3%): ")) / 100
            total_saved = 0
            total_days = 0
            while total_saved < goal:
                total_saved += net  # daily saving
                total_saved *= (1 + interest_rate / 365)  # apply daily interest
                total_days += 1
            periods_needed = total_days / multiplier
            print("\n--- RESULT WITH INTEREST ---")
            print(f"Time needed: {periods_needed:.2f} {unit_name}s")
            print(f"≈ {total_days:.0f} days")
            print(f"≈ {total_days/7:.2f} weeks")
            print(f"≈ {total_days/30:.2f} months")
            print(f"≈ {total_days/365:.2f} years")
        except ValueError:
            print("Invalid interest rate.")
            return

    save_choice = input("\nSave this plan? (y/n): ").lower()
    if save_choice == 'y':
        save_plan(plans, allowance, expenses, periods_needed, goal, unit=unit_name, multiplier=multiplier)

# =======================
# Tracker Functions
# =======================

def add_saved_amount(plan):
    try:
        amount = float(input("Enter amount saved today: "))
        validate_positive(amount, "Saved amount")
    except ValueError as e:
        print("Invalid input:", e)
        return

    plan["saved_so_far"] += amount
    plan["days_passed"] += 1
    print(f"✅ Added {amount:.2f}. Total saved: {plan['saved_so_far']:.2f} THB.")

    if plan["saved_so_far"] >= plan["goal"]:
        print("🎉 Congratulations! You have reached your goal!")

def show_progress_report(plan):
    saved = plan["saved_so_far"]
    goal = plan["goal"]
    days_passed = plan["days_passed"]
    total_periods = plan["periods"]

    remaining = max(goal - saved, 0)
    days_left = max(total_periods - days_passed, 0)
    daily_needed = remaining / days_left if days_left > 0 else 0

    average_saved = saved / days_passed if days_passed > 0 else 0
    expected_total = average_saved * total_periods

    print("\n--- PROGRESS REPORT ---")
    print(f"Goal: {goal:.2f} THB")
    print(f"Saved so far: {saved:.2f} THB")
    print(f"Remaining: {remaining:.2f} THB")
    print(f"Days passed: {days_passed}")
    print(f"Days left: {days_left}")
    print(f"Daily saving needed to reach goal: {daily_needed:.2f} THB/day")
    print(f"Average saved per day: {average_saved:.2f} THB")
    print(f"If you continue saving this average, you will have: {expected_total:.2f} THB")

    if saved >= daily_needed * days_passed:
        print("✅ You are ahead of schedule!")
    else:
        print("⚠️ You are behind schedule.")

def adjust_plan(plan):
    try:
        new_allowance = float(input(f"Current allowance: {plan['allowance']}. New allowance: "))
        new_expenses = float(input(f"Current expenses: {plan['expenses']}. New expenses: "))
        validate_positive(new_allowance, "Allowance")
        validate_positive(new_expenses, "Expenses")
    except ValueError as e:
        print("Invalid input:", e)
        return

    plan["allowance"] = new_allowance
    plan["expenses"] = new_expenses
    plan["net"] = new_allowance - new_expenses
    print(f"✅ Plan updated. New net saving per period: {plan['net']:.2f} THB")

def recalc_daily_needed(plan):
    remaining = plan["goal"] - plan["saved_so_far"]
    remaining_periods = plan["periods"] - plan["days_passed"]

    if remaining <= 0:
        print("🎉 Goal already reached!")
        return
    if remaining_periods <= 0:
        print("⚠️ No periods left. Consider extending your plan.")
        return

    new_daily_needed = remaining / remaining_periods
    print(f" New daily saving needed to reach goal: {new_daily_needed:.2f} THB/day")

def reset_plan(plan):
    confirm = input("Are you sure you want to reset this plan? (y/n): ").lower()
    if confirm == 'y':
        plan["saved_so_far"] = 0
        plan["days_passed"] = 0
        print("✅ Plan data has been reset.")
    else:
        print("Reset canceled.")

def track_plan(plans, name):
    plan = plans[name]
    while True:
        print(f"\n=== TRACKER: {name} ===")
        print("1. Add saved amount today")
        print("2. View progress report")
        print("3. Adjust allowance / expenses")
        print("4. Recalculate daily saving target")
        print("5. Reset plan data")
        print("6. Exit tracker")

        choice = input("Choose: ")

        if choice == "1":
            add_saved_amount(plan)
        elif choice == "2":
            show_progress_report(plan)
        elif choice == "3":
            adjust_plan(plan)
        elif choice == "4":
            recalc_daily_needed(plan)
        elif choice == "5":
            reset_plan(plan)
        elif choice == "6":
            break
        else:
            print("Invalid option.")

# =======================
# Menu 3: View / Track / Delete Plans
# =======================

def menu_view_plans(plans):
    if not plans:
        print("No saved plans found.")
        return

    print("\nSaved plans:")
    plan_names = list(plans.keys())
    for i, name in enumerate(plan_names, 1):
        goal = plans[name]['goal']
        print(f"{i}. {name} (goal: {goal} THB)")

    try:
        choice = int(input("\nChoose a plan by number: "))
        if choice < 1 or choice > len(plan_names):
            print("Invalid plan number.")
            return
    except ValueError:
        print("Invalid input.")
        return

    selected = plan_names[choice - 1]
    plan = plans[selected]

    print(f"\n=== PLAN: {selected} ===")
    print("1. Start tracker")
    print("2. Delete this plan")
    print("3. Return")
    action = input("Choose: ")

    if action == '1':
        track_plan(plans, selected)
    elif action == '2':
        confirm = input("Are you sure? (y/n): ").lower()
        if confirm == 'y':
            del plans[selected]
            print("Plan deleted.")
    else:
        print("Returning...")

# =======================
# Main Program Loop
# =======================

def main():
    print(" Welcome to Saving Planner 2.0! :) \n")
    plans = {}  # All plans exist in memory

    while True:
        print("\n=== MAIN MENU ===")
        print("1. Check if goal is possible")
        print("2. Calculate time needed to reach goal")
        print("3. View saved plans / Tracker")
        print("4. Exit")

        choice = input("Enter choice (1-4): ")

        if choice == "1":
            menu_check_feasibility(plans)
        elif choice == "2":
            menu_time_needed(plans)
        elif choice == "3":
            menu_view_plans(plans)
        elif choice == "4":
            print("\nThank you for using Saving Planner 2.0! Byee :)")
            break
        else:
            print("Invalid choice. Please select 1-4.")

# =======================
# Run the program
# =======================

if __name__ == "__main__":
    main()