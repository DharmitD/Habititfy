import click
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
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

@cli.command()
@click.option("--habit", help="Filter statistics for a specific habit")
@click.option("--days", default=30, help="Number of days to analyze (default: 30)")
def stats(habit, days):
    """Show detailed statistics and analytics for habits."""
    tracker = HabitTracker()
    habits = tracker.view_habits()
    
    # Filter by date range
    cutoff_date = datetime.now().date() - timedelta(days=days)
    recent_habits = [h for h in habits if datetime.strptime(h['date'], '%Y-%m-%d').date() >= cutoff_date]
    
    # Filter by specific habit if provided
    if habit:
        recent_habits = [h for h in recent_habits if h['habit'].lower() == habit.lower()]
    
    if not recent_habits:
        click.echo("No habits found for the specified criteria.")
        return
    
    # Calculate statistics
    habit_stats = defaultdict(lambda: {'total': 0, 'completed': 0, 'skipped': 0, 'partial': 0, 'exceeded': 0})
    
    for h in recent_habits:
        habit_name = h['habit']
        status = h['status'].lower()
        habit_stats[habit_name]['total'] += 1
        habit_stats[habit_name][status] += 1
    
    # Display statistics
    click.echo(f"\n📊 Habit Statistics (Last {days} days)")
    click.echo("=" * 50)
    
    for habit_name, stats in habit_stats.items():
        completion_rate = (stats['completed'] + stats['exceeded']) / stats['total'] * 100
        click.echo(f"\n🎯 {habit_name}")
        click.echo(f"   Total entries: {stats['total']}")
        click.echo(f"   Completion rate: {completion_rate:.1f}%")
        click.echo(f"   ✅ Completed: {stats['completed']}")
        click.echo(f"   🚀 Exceeded: {stats['exceeded']}")
        click.echo(f"   ⚠️  Partial: {stats['partial']}")
        click.echo(f"   ❌ Skipped: {stats['skipped']}")

@cli.command()
@click.argument("habit_name")
def streak(habit_name):
    """Calculate current streak for a specific habit."""
    tracker = HabitTracker()
    habits = tracker.view_habits()
    
    # Filter for the specific habit and sort by date
    habit_entries = [h for h in habits if h['habit'].lower() == habit_name.lower()]
    habit_entries.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d').date(), reverse=True)
    
    if not habit_entries:
        click.echo(f"No entries found for habit '{habit_name}'")
        return
    
    # Calculate streak
    current_streak = 0
    today = datetime.now().date()
    
    for entry in habit_entries:
        entry_date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
        if entry_date > today:
            continue
        
        if entry['status'].lower() in ['completed', 'exceeded']:
            if current_streak == 0:
                # First successful entry
                if entry_date == today or entry_date == today - timedelta(days=1):
                    current_streak = 1
                else:
                    break
            else:
                # Check if this entry continues the streak
                expected_date = today - timedelta(days=current_streak)
                if entry_date == expected_date:
                    current_streak += 1
                else:
                    break
        else:
            break
    
    click.echo(f"🔥 Current streak for '{habit_name}': {current_streak} days")

@cli.command()
@click.argument("habit_name")
@click.option("--goal", type=int, help="Set a daily goal for this habit")
def goal(habit_name, goal):
    """Set or view goals for habits."""
    tracker = HabitTracker()
    
    if goal:
        # Set goal (store in a simple JSON file)
        goals_file = "data/goals.json"
        try:
            with open(goals_file, 'r') as f:
                goals = json.load(f)
        except FileNotFoundError:
            goals = {}
        
        goals[habit_name] = goal
        with open(goals_file, 'w') as f:
            json.dump(goals, f, indent=2)
        
        click.echo(f"✅ Goal set for '{habit_name}': {goal} per day")
    else:
        # View current goal
        goals_file = "data/goals.json"
        try:
            with open(goals_file, 'r') as f:
                goals = json.load(f)
            if habit_name in goals:
                click.echo(f"🎯 Current goal for '{habit_name}': {goals[habit_name]} per day")
            else:
                click.echo(f"No goal set for '{habit_name}'")
        except FileNotFoundError:
            click.echo(f"No goal set for '{habit_name}'")

@cli.command()
@click.option("--format", type=click.Choice(['csv', 'json']), default='csv', help="Export format")
@click.option("--output", help="Output file path")
def export(format, output):
    """Export habit data to CSV or JSON format."""
    tracker = HabitTracker()
    habits = tracker.view_habits()
    
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"habit_export_{timestamp}.{format}"
    
    if format == 'csv':
        import csv
        with open(output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Habit', 'Status'])
            for habit in habits:
                writer.writerow([habit['date'], habit['habit'], habit['status']])
    else:  # json
        with open(output, 'w') as f:
            json.dump(habits, f, indent=2)
    
    click.echo(f"✅ Data exported to {output}")

@cli.command()
@click.argument("habit_name")
@click.option("--status", default="Completed", help="Status to log")
@click.option("--count", type=int, default=1, help="Number of entries to log")
def bulk_log(habit_name, status, count):
    """Log multiple entries for a habit at once."""
    tracker = HabitTracker()
    
    for i in range(count):
        tracker.log_habit(habit_name, status)
    
    click.echo(f"✅ Logged {count} entries for '{habit_name}' with status: {status}")

@cli.command()
@click.argument("habit_name")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def delete_habit(habit_name, confirm):
    """Delete all entries for a specific habit."""
    if not confirm:
        if not click.confirm(f"Are you sure you want to delete all entries for '{habit_name}'?"):
            click.echo("Operation cancelled.")
            return
    
    tracker = HabitTracker()
    tracker.delete_habit(habit_name)
    click.echo(f"✅ All entries for '{habit_name}' have been deleted")

@cli.command()
@click.argument("search_term")
@click.option("--status", help="Filter by status")
@click.option("--days", default=30, help="Search within last N days")
def search(search_term, status, days):
    """Search for habits by name or status."""
    tracker = HabitTracker()
    habits = tracker.view_habits()
    
    # Filter by date range
    cutoff_date = datetime.now().date() - timedelta(days=days)
    recent_habits = [h for h in habits if datetime.strptime(h['date'], '%Y-%m-%d').date() >= cutoff_date]
    
    # Filter by search term
    filtered_habits = [h for h in recent_habits if search_term.lower() in h['habit'].lower()]
    
    # Filter by status if provided
    if status:
        filtered_habits = [h for h in filtered_habits if h['status'].lower() == status.lower()]
    
    if not filtered_habits:
        click.echo("No habits found matching your search criteria.")
        return
    
    click.echo(f"\n🔍 Search Results for '{search_term}' (Last {days} days)")
    click.echo("=" * 50)
    
    for habit in filtered_habits:
        status_emoji = {
            'completed': '✅',
            'exceeded': '🚀',
            'partial': '⚠️',
            'skipped': '❌'
        }.get(habit['status'].lower(), '📝')
        
        click.echo(f"{status_emoji} {habit['date']} - {habit['habit']}: {habit['status']}")

@cli.command()
def dashboard():
    """Show a comprehensive dashboard with key metrics."""
    tracker = HabitTracker()
    habits = tracker.view_habits()
    
    if not habits:
        click.echo("No habits found. Start by logging some habits!")
        return
    
    # Calculate metrics
    total_entries = len(habits)
    unique_habits = len(set(h['habit'] for h in habits))
    
    # Last 7 days metrics
    week_ago = datetime.now().date() - timedelta(days=7)
    recent_habits = [h for h in habits if datetime.strptime(h['date'], '%Y-%m-%d').date() >= week_ago]
    
    completion_count = len([h for h in recent_habits if h['status'].lower() in ['completed', 'exceeded']])
    total_recent = len(recent_habits)
    weekly_completion_rate = (completion_count / total_recent * 100) if total_recent > 0 else 0
    
    # Most active habits
    habit_counts = Counter(h['habit'] for h in recent_habits)
    top_habits = habit_counts.most_common(3)
    
    # Display dashboard
    click.echo("\n📈 HABITIFY DASHBOARD")
    click.echo("=" * 40)
    click.echo(f"📊 Total entries: {total_entries}")
    click.echo(f"🎯 Unique habits: {unique_habits}")
    click.echo(f"📅 This week's completion rate: {weekly_completion_rate:.1f}%")
    click.echo(f"🔥 Most active habits this week:")
    
    for i, (habit, count) in enumerate(top_habits, 1):
        click.echo(f"   {i}. {habit}: {count} entries")
    
    # Recent activity
    click.echo(f"\n📝 Recent Activity (Last 5 entries):")
    recent_entries = sorted(habits, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d').date(), reverse=True)[:5]
    
    for entry in recent_entries:
        status_emoji = {
            'completed': '✅',
            'exceeded': '🚀',
            'partial': '⚠️',
            'skipped': '❌'
        }.get(entry['status'].lower(), '📝')
        
        click.echo(f"   {status_emoji} {entry['date']} - {entry['habit']}")

if __name__ == "__main__":
    cli()
