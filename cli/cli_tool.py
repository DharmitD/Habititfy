import click
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sdk.habit_tracker import HabitTracker
from sdk.ai_coach import AICoach

@click.group()
def cli():
    """Habitify - A powerful habit tracking CLI tool."""
    pass

@cli.command()
def version():
    """Show version information."""
    click.echo("Habitify CLI v1.0.0")
    click.echo("A powerful habit tracking command-line tool")

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

@cli.command()
@click.argument("habit_name")
@click.option("--description", help="Description of the habit")
@click.option("--category", help="Category for the habit (e.g., Health, Productivity)")
def create_habit(habit_name, description, category):
    """Create a new habit with optional description and category."""
    habits_file = "data/habits_metadata.json"
    
    try:
        with open(habits_file, 'r') as f:
            habits_metadata = json.load(f)
    except FileNotFoundError:
        habits_metadata = {}
    
    habits_metadata[habit_name] = {
        'description': description or f"Track your {habit_name.lower()} habit",
        'category': category or 'General',
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'total_entries': 0
    }
    
    with open(habits_file, 'w') as f:
        json.dump(habits_metadata, f, indent=2)
    
    click.echo(f"✅ Created habit '{habit_name}'")
    if description:
        click.echo(f"   Description: {description}")
    if category:
        click.echo(f"   Category: {category}")

@cli.command()
def list_habits():
    """List all created habits with their metadata."""
    habits_file = "data/habits_metadata.json"
    
    try:
        with open(habits_file, 'r') as f:
            habits_metadata = json.load(f)
    except FileNotFoundError:
        click.echo("No habits created yet. Use 'create-habit' to add some!")
        return
    
    if not habits_metadata:
        click.echo("No habits created yet. Use 'create-habit' to add some!")
        return
    
    click.echo("\n📋 CREATED HABITS")
    click.echo("=" * 50)
    
    for habit_name, metadata in habits_metadata.items():
        click.echo(f"\n🎯 {habit_name}")
        click.echo(f"   📝 {metadata['description']}")
        click.echo(f"   📂 Category: {metadata['category']}")
        click.echo(f"   📅 Created: {metadata['created_date']}")
        click.echo(f"   📊 Total entries: {metadata['total_entries']}")

@cli.command()
@click.argument("habit_name")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def remove_habit(habit_name, confirm):
    """Remove a habit and all its metadata."""
    habits_file = "data/habits_metadata.json"
    
    try:
        with open(habits_file, 'r') as f:
            habits_metadata = json.load(f)
    except FileNotFoundError:
        click.echo(f"Habit '{habit_name}' not found.")
        return
    
    if habit_name not in habits_metadata:
        click.echo(f"Habit '{habit_name}' not found.")
        return
    
    if not confirm:
        if not click.confirm(f"Are you sure you want to remove habit '{habit_name}' and all its metadata?"):
            click.echo("Operation cancelled.")
            return
    
    del habits_metadata[habit_name]
    
    with open(habits_file, 'w') as f:
        json.dump(habits_metadata, f, indent=2)
    
    click.echo(f"✅ Removed habit '{habit_name}' and its metadata")

@cli.command()
@click.option("--days", default=30, help="Number of days to show progress for")
def progress(days):
    """Show visual progress charts for all habits."""
    tracker = HabitTracker()
    habits = tracker.view_habits()
    
    if not habits:
        click.echo("No habits found. Start by logging some habits!")
        return
    
    # Filter by date range
    cutoff_date = datetime.now().date() - timedelta(days=days)
    recent_habits = [h for h in habits if datetime.strptime(h['date'], '%Y-%m-%d').date() >= cutoff_date]
    
    # Group by habit
    habit_data = defaultdict(list)
    for h in recent_habits:
        habit_data[h['habit']].append(h)
    
    click.echo(f"\n📊 PROGRESS CHARTS (Last {days} days)")
    click.echo("=" * 60)
    
    for habit_name, entries in habit_data.items():
        click.echo(f"\n🎯 {habit_name}")
        
        # Create a simple ASCII progress bar
        total_days = days
        completed_days = len([e for e in entries if e['status'].lower() in ['completed', 'exceeded']])
        progress_percentage = (completed_days / total_days) * 100
        
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * progress_percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        click.echo(f"   Progress: [{bar}] {progress_percentage:.1f}%")
        click.echo(f"   Completed: {completed_days}/{total_days} days")
        
        # Show recent status
        recent_entries = sorted(entries, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d').date(), reverse=True)[:7]
        click.echo("   Recent: ", nl=False)
        for entry in reversed(recent_entries):
            status_emoji = {
                'completed': '✅',
                'exceeded': '🚀',
                'partial': '⚠️',
                'skipped': '❌'
            }.get(entry['status'].lower(), '📝')
            click.echo(status_emoji, nl=False)
        click.echo()  # New line

@cli.command()
def achievements():
    """Show achievements and badges earned."""
    tracker = HabitTracker()
    habits = tracker.view_habits()
    
    if not habits:
        click.echo("No habits found. Start by logging some habits!")
        return
    
    # Calculate achievements
    achievements = []
    
    # Total entries achievements
    total_entries = len(habits)
    if total_entries >= 1000:
        achievements.append(("🏆", "Data Master", "Logged 1000+ entries"))
    elif total_entries >= 500:
        achievements.append(("🥇", "Data Collector", "Logged 500+ entries"))
    elif total_entries >= 100:
        achievements.append(("🥈", "Data Tracker", "Logged 100+ entries"))
    elif total_entries >= 50:
        achievements.append(("🥉", "Data Starter", "Logged 50+ entries"))
    
    # Streak achievements
    unique_habits = set(h['habit'] for h in habits)
    if len(unique_habits) >= 10:
        achievements.append(("🌟", "Habit Master", "Tracking 10+ different habits"))
    elif len(unique_habits) >= 5:
        achievements.append(("⭐", "Habit Explorer", "Tracking 5+ different habits"))
    
    # Recent completion achievements
    week_ago = datetime.now().date() - timedelta(days=7)
    recent_habits = [h for h in habits if datetime.strptime(h['date'], '%Y-%m-%d').date() >= week_ago]
    completion_count = len([h for h in recent_habits if h['status'].lower() in ['completed', 'exceeded']])
    
    if completion_count >= 20:
        achievements.append(("🔥", "Week Warrior", "Completed 20+ habits this week"))
    elif completion_count >= 10:
        achievements.append(("💪", "Week Champion", "Completed 10+ habits this week"))
    elif completion_count >= 5:
        achievements.append(("👍", "Week Starter", "Completed 5+ habits this week"))
    
    click.echo("\n🏆 ACHIEVEMENTS & BADGES")
    click.echo("=" * 40)
    
    if achievements:
        for emoji, title, description in achievements:
            click.echo(f"{emoji} {title}")
            click.echo(f"   {description}")
            click.echo()
    else:
        click.echo("No achievements yet. Keep tracking your habits to earn badges!")
        click.echo("\n🎯 Tips to earn achievements:")
        click.echo("   • Log 50+ entries to get your first badge")
        click.echo("   • Track 5+ different habits")
        click.echo("   • Complete 5+ habits this week")

@cli.command()
@click.option("--backup-dir", default="backups", help="Directory to store backups")
def backup(backup_dir):
    """Create a backup of all habit data."""
    import shutil
    import os
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"habitify_backup_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Create backup directory
    os.makedirs(backup_path, exist_ok=True)
    
    # Copy data files
    files_to_backup = [
        "data/habits.csv",
        "data/goals.json",
        "data/habits_metadata.json"
    ]
    
    backed_up_files = []
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            backed_up_files.append(file_path)
    
    if backed_up_files:
        click.echo(f"✅ Backup created successfully!")
        click.echo(f"📁 Location: {backup_path}")
        click.echo(f"📄 Files backed up: {len(backed_up_files)}")
        for file_path in backed_up_files:
            click.echo(f"   • {file_path}")
    else:
        click.echo("⚠️ No data files found to backup")

@cli.command()
@click.argument("backup_path")
def restore(backup_path):
    """Restore habit data from a backup."""
    import shutil
    import os
    
    if not os.path.exists(backup_path):
        click.echo(f"❌ Backup path '{backup_path}' does not exist")
        return
    
    if not click.confirm(f"Are you sure you want to restore from '{backup_path}'? This will overwrite current data."):
        click.echo("Operation cancelled.")
        return
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Restore files
    restored_files = []
    for filename in os.listdir(backup_path):
        if filename.endswith(('.csv', '.json')):
            src = os.path.join(backup_path, filename)
            dst = os.path.join("data", filename)
            shutil.copy2(src, dst)
            restored_files.append(filename)
    
    if restored_files:
        click.echo(f"✅ Restore completed successfully!")
        click.echo(f"📄 Files restored: {len(restored_files)}")
        for filename in restored_files:
            click.echo(f"   • {filename}")
    else:
        click.echo("⚠️ No valid backup files found")

if __name__ == "__main__":
    cli()
