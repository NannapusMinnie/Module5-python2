import math

# =================
# Input Validation
# =================
def input_validation(value:str , name: str = "Value") -> float:
    """
    Convert input string to float, remove commas/spaces, and ensure it is positive.
    
    Args:
        value (str): The input string to validate.
        name (str): Name of the value for error messages. Defaults to "Value".
    
    Returns:
        float: The validated positive number.
    
    Raises:
        ValueError: If the input is not a number or is not positive.
    """

    value = value.replace(",", "").replace(" ", "")
    try:
        number = float(value)
    except ValueError:
        raise ValueError(f"{name} must be a number. 😠")
    if number <= 0:
        raise ValueError(f"{name} must be positive. 😠")
    return number

# ===========
# Plan Class
# ===========
class Plan:
    def __init__(self, name: str, allowance: float, expenses: float, goal: float, periods: int, unit: str = "day", multiplier: int = 1):
        """
        Initialize a Plan object.

        Args:
            name (str): Name of the plan.
            allowance (float): Income per period.
            expenses (float): Expenses per period.
            goal (float): Target savings.
            periods (int): Number of periods in the plan.
            unit (str, optional): Time unit ("day", "week", "month", "year"). Defaults to "day".
            multiplier (int, optional): Conversion factor to days. Defaults to 1
        """
        self.name = name
        self.allowance = allowance
        self.expenses = expenses
        self.goal = goal
        self.periods = periods
        self.unit = unit
        self.multiplier = multiplier # for unit convertion
        self.saved_so_far = 0.0 # use for tracker
        self.days_passed = 0 # use for tracker

    def net(self) -> float:
        """Return net savings per period (allowance - expenses)."""
        return self.allowance - self.expenses

    def add_saved(self, amount: float) -> None:
        """Add saved amount and increment days passed.
        
        Args:
            amount (float): Amount saved today.
        
        Raises:
            ValueError: If amount is not positive.
        """
        if amount <= 0:
            raise ValueError("Saved amount must be positive!")
        self.saved_so_far += amount
        self.days_passed += 1

    def update_allowance(self, new_allowance: float) -> None:
        """Update allowance for the plan.
        
        Args:
            new_allowance (float): New allowance value.
        
        Raises:
            ValueError: If allowance is not positive.
        """
        if new_allowance <= 0:
            raise ValueError("Allowance must be positive!")
        self.allowance = new_allowance

    def update_expenses(self, new_expenses: float) -> None:
        """Update expenses for the plan.
        
        Args:
            new_expenses (float): New expenses value.
        
        Raises:
            ValueError: If expenses are not positive.
        """
        if new_expenses <= 0:
            raise ValueError("Expenses must be positive!")
        self.expenses = new_expenses

    def reset(self) -> None:
        """Reset saved_so_far and days_passed to zero."""
        self.saved_so_far = 0.0
        self.days_passed = 0

    def total_days(self) -> int:
        """Return total days in the plan considering multiplier."""
        return int(self.periods * self.multiplier)

    # for tracker only: daily needed from now on
    def daily_needed(self) -> float:
        """Calculate daily saving needed from now to reach the goal.
        
        Returns:
            float: Daily amount required to meet goal.
        """
        remaining = self.goal - self.saved_so_far
        total_days = self.total_days()
        remaining_days = total_days - self.days_passed
        if remaining_days <= 0:
            return 0
        if remaining < 0:  # already exceeded goal
            return -(self.saved_so_far - self.goal) / remaining_days
        return remaining / remaining_days

    def progress_report(self) -> dict:
        """Return a dictionary summarizing the plan's progress.
        
        Returns:
            dict: Progress details including goal, saved, remaining, daily needed, etc.
        """
        total_days = self.total_days()
        remaining = max(self.goal - self.saved_so_far, 0.0)
        days_left = max(total_days - self.days_passed, 0)

        if self.days_passed > 0:
            average_saved = self.saved_so_far / self.days_passed
        else:
            average_saved = 0.0

        expected_total = average_saved * total_days

        return {
            "goal": self.goal,
            "saved_so_far": self.saved_so_far,
            "remaining": remaining,
            "days_passed": self.days_passed, 
            "days_left": days_left,
            "daily_needed": self.daily_needed(),
            "average_saved": average_saved,
            "expected_total": expected_total,
            "total_days": total_days
        }

# ==============
# Plans Manager
# ==============
class PlansManager:
    def __init__(self) -> None:
        """Initialise the plans dictionary"""
        self.plans = {}  # key: plan.name -> value: Plan instance

    def save_plan(self, plan: Plan) -> None:
        """Save plan in memory and append to file.
        
        Args:
            plan (Plan): Plan instance to save.
        """
        # save to memory and write all plans to file (keeps file consistent)
        self.plans[plan.name] = plan
        self.write_plan_to_file(plan)
        print(f"🎉 Plan '{plan.name}' saved!")

    def write_plan_to_file(self, plan: Plan) -> None:
        """Append a single plan to file.
        
        Args:
            plan (Plan): Plan instance to write.
        """
         # append one plan
        with open("the-plan.txt", "a") as f:
            f.write(f"{plan.name}|{plan.allowance}|{plan.expenses}|{plan.goal}|{plan.periods}|{plan.unit}|{plan.multiplier}|{plan.saved_so_far}|{plan.days_passed}\n")

    def write_all_plans_to_file(self) -> None:
        """Overwrite file with all current plans."""
        # rewrite the whole file with all current plans when update or delete
        with open("the-plan.txt", "w") as f:
            for p in self.plans.values():
                f.write(f"{p.name}|{p.allowance}|{p.expenses}|{p.goal}|{p.periods}|{p.unit}|{p.multiplier}|{p.saved_so_far}|{p.days_passed}\n")
 
    def load_plans_from_file(self) -> None:
        """Load plans from file into memory."""
        try:
            with open("the-plan.txt", "r") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 9:
                        name, allowance, expenses, goal, periods, unit, multiplier, saved_so_far, days_passed = parts
                        the_plan = Plan(
                            name,
                            float(allowance),
                            float(expenses),
                            float(goal),
                            int(periods),
                            unit,
                            int(multiplier)
                        )
                        the_plan.saved_so_far = float(saved_so_far)
                        the_plan.days_passed = int(days_passed)
                        self.plans[the_plan.name] = the_plan # dictionary containing keys and values
        except FileNotFoundError:
            print("File is not found")

# ========================
# Decorator for Time Unit
# ========================
def with_time_unit(menu_func):
    """
    Decorator to add a time unit selection before calling the menu function.

    Args:
        menu_func (function): A function that takes three arguments:
            - plans_manager
            - multiplier (int): Conversion factor to days based on chosen unit.
            - unit (str): Time unit chosen by the user ("day", "week", "month", "year").

    Returns:
        function: A wrapper function that asks the user for a time unit
                  and then calls `menu_func` with the selected multiplier and unit.
    """
    def wrapper(plans_manager: PlansManager) -> None:
        """
        Wrapper function that asks the user to select a time unit, 
        calculates the corresponding multiplier, and then calls the original menu function.

        Args:
            plans_manager (object): The manager that handles plans (e.g., PlansManager instance).

        Returns:
            object: The result returned by the wrapped menu function.
        """
        while True:
            print("Choose time unit:")
            print("type 1 for Day")
            print("type 2 for Week")
            print("type 3 for Month")
            print("type 4 for Year")
            choice = input("Enter choice (1-4): ")
            if choice == "1":
                unit = "day"
                multiplier = 1
                break
            elif choice == "2":
                unit = "week"
                multiplier = 7
                break
            elif choice == "3":
                unit = "month"
                multiplier = 30
                break
            elif choice == "4":
                unit = "year"
                multiplier = 365
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
        return menu_func(plans_manager, multiplier, unit)
    return wrapper

# ===============================
# Menu 1: Check Goal Feasibility
# ===============================
@with_time_unit
def menu_check_feasibility(plans_manager: PlansManager, multiplier: int, unit_name: str) -> None:
    """
    Check if the savings goal is feasible given allowance, expenses, and duration.

    Args:
        plans_manager (PlansManager): Instance of PlansManager to save plans.
        multiplier (int): Number of days per chosen time unit.
        unit_name (str): Name of the time unit (day/week/month/year).
    """

    print(f"\n=== CHECK IF GOAL IS POSSIBLE ({unit_name}) ===\n")
    try:
        allowance = input_validation(input(f"Enter allowance per {unit_name}: "), "Allowance")
        expenses = input_validation(input(f"Enter expenses per {unit_name}: "), "Expenses")
        duration = input_validation(input(f"Enter number of {unit_name}s you plan to save for: "), "Duration")
        goal = input_validation(input("Enter your savings goal: "), "Goal")
    except ValueError as e:
        print("Input error:", e)
        return

    # Normalize per day
    daily_allowance = allowance / multiplier
    daily_expenses = expenses / multiplier
    daily_saving = daily_allowance - daily_expenses
    total_days = int(duration) * multiplier
    total_saving_possible = daily_saving * total_days
    required_daily = math.ceil(goal / total_days)

    print("\n--- RESULT ---")
        
    if total_saving_possible >= goal:
        extra = total_saving_possible - goal
        print(f"($◡$)🤑 Goal is possible!")
        print(f"You need to save at least {required_daily/multiplier} per {unit_name} to reach your goal.")
        print(f"If you save the max allowance({daily_saving}) daily, you could have extra {math.floor(extra)} THB at the end.")
        save_choice = input("Do you want to save this plan? (y/n): ").lower()
        if save_choice == "y":
            plan_name = input("Enter a name for your plan: ")
            plan = Plan(plan_name, allowance, expenses, goal, int(duration), unit_name, multiplier)
            plans_manager.save_plan(plan)
    else:
        max_possible = daily_allowance * total_days
        needed_cut = math.ceil((goal / total_days) + daily_expenses - daily_allowance)

        if max_possible < goal:
            print("Even if you cut all your expenses, your goal is NOT possible.")
            print(f"Maximum you could save is {math.floor(max_possible)} THB.")
            print(f"Maximum daily saving would be {math.floor(daily_allowance)} THB/day.")
            return

        print("⚠️ Goal is NOT possible with current expenses.")
        print(f"You must cut your expenses by at least {math.ceil(needed_cut/multiplier)} per {unit_name}.")

        adjust = input("Do you want to adjust expenses and save this plan? (y/n): ").lower()
        if adjust == "y":
            new_expenses = expenses - (needed_cut / multiplier)  # convert back to unit amount
            plan_name = input("Enter a name for your plan: ")
            plan = Plan(plan_name, allowance, new_expenses, goal, int(duration), unit_name, multiplier)
            plans_manager.save_plan(plan)

# ====================
# Menu 2: Time Needed
# ====================
@with_time_unit
def menu_time_needed(plans_manager: PlansManager, multiplier: int, unit_name: str) -> None:
    """
    Calculate the time required to reach a savings goal with optional compound interest.

    Args:
        plans_manager (PlansManager): Instance of PlansManager to save plans.
        multiplier (int): Number of days per chosen time unit.
        unit_name (str): Name of the time unit (day/week/month/year).
    """

    print(f"\n=== CALCULATE TIME TO REACH GOAL ({unit_name}) ===\n")
    try:
        allowance = input_validation(input(f"Allowance per {unit_name}: "), "Allowance")
        expenses = input_validation(input(f"Expenses per {unit_name}: "), "Expenses")
        goal = input_validation(input("Savings goal: "), "Goal")
    except ValueError as e:
        print("Invalid input:", e)
        return

    net = allowance - expenses
    if net <= 0:
        print("\nYou cannot save any money with current spending.")
        print(f"You must cut {(expenses - allowance) + 1} per {unit_name} to start saving")
        return

    use_interest = input("Add compound interest? (y/n): ").lower()
    if use_interest == "n":
        periods_needed = math.ceil(goal / net) # number of chosen units
        print("\n--- RESULT WITHOUT INTEREST ---")
        print(f"Time needed: {periods_needed} {unit_name}(s)")
        days = periods_needed * multiplier
        print(f"≈ {days} days")
        print(f"≈ {days/7:.2f} weeks")
        print(f"≈ {days/30:.2f} months")
        print(f"≈ {days/365:.2f} years")
    else:
        try:
            interest_rate = input_validation(input("Enter annual interest rate (%): "), "Interest rate") / 100
            total_saved = 0.0
            total_days = 0
            while total_saved < goal:
                total_saved += (net/multiplier)
                total_saved *= (1 + interest_rate/365)
                total_days += 1
            periods_needed = math.ceil(total_days / multiplier)
            print("\n--- RESULT WITH INTEREST ---")
            print(f"Time needed: {periods_needed} {unit_name}(s)")
            print(f"≈ {total_days} days")
            print(f"≈ {total_days/7:.2f} weeks")
            print(f"≈ {total_days/30:.2f} months")
            print(f"≈ {total_days/365:.2f} years")
        except ValueError as e:
            print("Invalid input:", e)
            return

    save_choice = input("Do you want to save this plan? (y/n): ").lower()
    if save_choice == "y":
        plan_name = input("Enter a name for your plan: ")
        plan = Plan(plan_name, allowance, expenses, goal, periods_needed, unit_name, multiplier)
        plans_manager.save_plan(plan)
    else:
        print("Plan is not saved")        

# ==================
# Tracker Functions
# ==================
def add_saved_amount(plan: Plan, plans_manager: PlansManager) -> None:
    """
    Add an amount saved for a plan today and update the plan in memory/file.

    Args:
        plan (Plan): The plan object being tracked.
        plans_manager (PlansManager): Instance managing all plans.
    """
    
    try:
        amount = input_validation(input("Enter amount saved today: "), "Saved amount")
        plan.add_saved(amount)

        plans_manager.write_all_plans_to_file()
        print(f" Added {amount}. Total saved: {plan.saved_so_far} THB.")
        
        if plan.saved_so_far >= plan.goal:
            extra_saved = plan.saved_so_far - plan.goal
            if extra_saved > 0:
                print(f"You have saved {extra_saved} THB more than your goal! 🎉💰")
            elif extra_saved == 0:
                print("You reached your goal exactly! 💵🎯")

    except ValueError as e:
        print("Invalid input:", e)

def show_progress_report(plan: Plan) -> None:
    """
    Display a progress report for a given plan, including goal, saved amount,
    remaining amount, daily target, and status.

    Args:
        plan (Plan): The plan object being tracked
    """
    report = plan.progress_report() # get dictionary that contain plan details
    print("\n--- PROGRESS REPORT ---")
    print(f"Goal: {report['goal']} THB")
    print(f"Saved so far: {report['saved_so_far']} THB")
    print(f"Remaining: {report['remaining']} THB")
    print(f"Days passed: {report['days_passed']}")
    print(f"Days left: {report['days_left']}")
    print(f"Daily saving needed to reach goal: {report['daily_needed']} THB/day")
    print(f"Average saved per day: {report['average_saved']:.2f} THB")
    print(f"If you continue saving this average, you will have: {report['expected_total']} THB")
    
    expected_by_now = plan.daily_needed() * plan.days_passed
    status = "Right on track"
    if plan.saved_so_far > expected_by_now:
        status = "Ahead of schedule"
    elif plan.saved_so_far < expected_by_now:
        status = "Behind schedule"
    else:
        status = "Right on track"

    print(f"Status: {status}")


def adjust_plan(plan: Plan, plans_manager: PlansManager) -> None:
    """
    Adjust allowance and expenses for a plan and update the plan data.

    Args:
        plan (Plan): The plan object to adjust.
        plans_manager (PlansManager): Instance managing all plans.
    """
    try:
        new_allowance = input_validation(input(f"Current allowance: {plan.allowance}. New allowance: "), "Allowance")
        new_expenses = input_validation(input(f"Current expenses: {plan.expenses}. New expenses: "), "Expenses")
        plan.update_allowance(new_allowance)
        plan.update_expenses(new_expenses)

        plans_manager.write_all_plans_to_file()
        required_per_period = plan.daily_needed() * plan.multiplier
        print(f"Plan updated. New net saving per {plan.unit}: {required_per_period} THB")
    except ValueError as e:
        print("Invalid input:", e)

def recalc_daily_needed(plan: Plan) -> None:
    """
    Recalculate the daily saving needed for a plan to reach its goal.

    Args:
        plan (Plan): The plan object to recalculate.
    """

    new_daily_needed = plan.daily_needed()
    if new_daily_needed == 0 and plan.saved_so_far >= plan.goal:
        print("🎉 Goal already reached!")
    elif new_daily_needed == 0:
        print("⚠️ No time left.")
    else:
        print(f"New daily saving needed to reach goal: {math.ceil(new_daily_needed)} THB/day")

def reset_plan(plan: Plan, plans_manager: PlansManager) -> None:
    """
    Reset saved_so_far and days_passed for a plan.

    Args:
        plan (Plan): The plan object to reset.
        plans_manager (PlansManager): Instance managing all plans.
    """
    confirm = input("Are you sure you want to reset this plan? (y/n): ").lower()
    if confirm == 'y':
        plan.reset()
        plans_manager.write_all_plans_to_file()
        print("Plan data has been reset.")
    else:
        print("Reset canceled.")

def track_plan(plan: Plan, plans_manager: PlansManager) -> None:
    """
    Interactive tracker menu for a single plan, allowing:
        - Adding saved amounts
        - Viewing progress report
        - Adjusting allowance/expenses
        - Recalculating daily target
        - Resetting plan

    Args:
        plan (Plan): The plan object to track.
        plans_manager (PlansManager): Instance managing all plans.
    """

    while True:
        print(f"\n=== TRACKER: {plan.name} ===")
        print("type 1 to Add saved amount today")
        print("type 2 to View progress report")
        print("type 3 to Adjust allowance / expenses")
        print("type 4 to Recalculate daily saving target")
        print("type 5 to Reset plan data")
        print("type 6 to Exit tracker")

        choice = input("Enter the number of your choice: ")
        if choice == "1":
            add_saved_amount(plan, plans_manager)
        elif choice == "2":
            show_progress_report(plan)
        elif choice == "3":
            adjust_plan(plan, plans_manager)
        elif choice == "4":
            recalc_daily_needed(plan)
        elif choice == "5":
            reset_plan(plan, plans_manager)
        elif choice == "6":
            break
        else:
            print("Invalid option.")

# ====================================
# Menu 3: View / Track / Delete Plans
# ====================================
def menu_view_plans(plans_manager: PlansManager) -> None:
    """
    View all saved plans, select a plan to track, view details, or delete it.

    Args:
        plans_manager (PlansManager): Instance managing all plans.
    """

    if not plans_manager.plans:
        print("No saved plans found.")
        return

    while True:
        print("\n=== SAVED PLANS ===")
        plan_names = list(plans_manager.plans.keys()) # get plans' names can convert them to a list

        for index, name in enumerate(plan_names, 1): # start at 1      
            plan = plans_manager.plans[name]
            print(f"{index}. {name} (goal: {plan.goal} THB)")
        print("0. Exit saved plans menu")  # Added option to exit

        try:
            choice = int(input("Choose a plan by number: "))
            if choice == 0:
                break  # exit outer loop
            if choice < 0 or choice > len(plan_names):
                print("Invalid plan number. Try again.")
                continue
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        selected_name = plan_names[choice - 1]
        selected_plan = plans_manager.plans[selected_name]

        while True:
            print(f"\n=== PLAN: {selected_name} ===")
            print("type 1 to Start tracker")
            print("type 2 to View plan details")
            print("type 3 to Delete this plan")
            print("type 4 to Return to saved plans list")

            action = input("Enter 1, 2, 3, or 4: ")
            if action == "1":
                track_plan(selected_plan, plans_manager)
            elif action == "2":
                print(f"\nPlan '{selected_name}':")
                print(f"Allowance: {selected_plan.allowance}")
                print(f"Expenses: {selected_plan.expenses}")
                print(f"Net saving per {selected_plan.unit}: {selected_plan.net()}")
                print(f"Goal: {selected_plan.goal}")
                print(f"Saved so far: {selected_plan.saved_so_far}")
                print(f"Periods: {selected_plan.periods} {selected_plan.unit}(s)")
                print(f"Total days in plan: {selected_plan.total_days()}")
            elif action == "3":
                confirm = input(f"Are you sure you want to delete '{selected_name}'? (y/n): ").lower()
                if confirm == "y":
                    plans_manager.plans.pop(selected_name, None)
                    plans_manager.write_all_plans_to_file()
                    print(f"Plan '{selected_name}' is deleted.")
                    break  # return to saved plans list
            elif action == "4":
                break  # return to saved plans list
            else:
                print("Invalid option. Please choose 1-4.")

# =============
# Main Program
# =============
def main() -> None:
    """
    Main entry point for the Saving Planner program.
    Loads saved plans, presents main menu, and handles user interactions.
    """

    print(" Welcome to Saving Planner 2.0! :)")
    plans_manager = PlansManager()
    plans_manager.load_plans_from_file()

    while True:
        print("\n=== MAIN MENU ===")
        print("type 1 to Check if goal is possible")
        print("type 2 to Calculate time needed to reach goal")
        print("type 3 to View saved plans / Tracker")
        print("type 4 to Exit")

        choice = input("Enter your choice (1-4): ")
        if choice == "1":
            menu_check_feasibility(plans_manager)
        elif choice == "2":
            menu_time_needed(plans_manager)
        elif choice == "3":
            menu_view_plans(plans_manager)
        elif choice == "4":
            print("Thank you for using Saving Planner 2.0 Bye!")
            break
        else:
            print("Invalid choice. Try again.")

main()