import click
from sdk.habit_tracker import HabitTracker
from sdk.ai_coach import AICoach

@click.group()
def cli():
    pass

@cli.command()
@click.argument("habit_name")
@click.option("--status", default="Completed", help="Status of the habit.")
def log(habit_name, status):
    """Log a new habit."""
    tracker = HabitTracker()
    tracker.log_habit(habit_name, status)
    click.echo(f"Habit '{habit_name}' logged with status: {status}")

@cli.command()
def view():
    """View all logged habits."""
    tracker = HabitTracker()
    habits = tracker.view_habits()
    for habit in habits:
        click.echo(f"{habit['date']} - {habit['habit']}: {habit['status']}")

@cli.command()
@click.argument("habit_name")
def motivate(habit_name):
    """Get a motivational tip for a habit."""
    coach = AICoach()
    tip = coach.generate_tip(habit_name)
    click.echo(f"Motivational Tip for '{habit_name}': {tip}")

if __name__ == "__main__":
    cli()
