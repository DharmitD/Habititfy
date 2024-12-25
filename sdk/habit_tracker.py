import csv
from datetime import datetime
from typing import List, Dict

class HabitTracker:
    def __init__(self, data_file="data/habits.csv"):
        self.data_file = data_file

    def log_habit(self, habit_name: str, status: str):
        """Log a new habit entry."""
        with open(self.data_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().date(), habit_name, status])

    def view_habits(self) -> List[Dict]:
        """View all logged habits."""
        habits = []
        with open(self.data_file, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                habits.append({"date": row[0], "habit": row[1], "status": row[2]})
        return habits

    def delete_habit(self, habit_name: str):
        """Delete all entries of a specific habit."""
        with open(self.data_file, mode="r") as file:
            rows = list(csv.reader(file))
        with open(self.data_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows([row for row in rows if row[1] != habit_name])
