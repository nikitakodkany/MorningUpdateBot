import os
import sys
import schedule
import time
import subprocess
from datetime import datetime
from plyer import notification
from typing import Dict, Any
import yaml

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import Agent
from src.context_manager import ContextManager, ContextType

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def send_notification(title: str, message: str, duration: int = 10):
    """Send a Windows notification using plyer."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_icon=None,  # No custom icon
            timeout=duration,
            toast=False  # Use standard notification
        )
        print(f"Notification sent: {title}")
    except Exception as e:
        print(f"Error sending notification: {e}")
        # Fallback to console output if notification fails
        print(f"\n{title}\n{message}\n")

def run_morning_update():
    """Run the morning update, notify the top update, and save the full update to a file."""
    try:
        # Load configuration
        config = load_config()
        
        # Initialize agent and context manager
        context_manager = ContextManager(config)
        agent = Agent(config, context_manager)
        
        # Run the morning update script and capture its output
        result = subprocess.run(
            [sys.executable, os.path.join("src", "morning_update.py")],
            capture_output=True,
            text=True
        )
        full_update = result.stdout
        
        # Determine the top most important update
        # We'll use the agent's memory of the last decisions for each context
        top_context = None
        top_priority = -1
        top_decision = None
        for context_type in ContextType:
            patterns = agent.memory["learned_patterns"].get(context_type.value, [])
            if patterns:
                last_pattern = patterns[-1]
                importance = last_pattern.get("importance", 0)
                if importance > top_priority:
                    top_priority = importance
                    top_context = context_type
                    top_decision = last_pattern
        
        # Format the notification message
        if top_context and top_decision:
            top_insight = next((insight for insight in top_decision.get('key_insights', []) if insight.strip()), "Update ready")
            notif_msg = f"{top_context.value.title()}: {top_insight}. Check your inbox to know more."
        else:
            notif_msg = "Your Morning Update is ready! Check your inbox to know more."
        # Truncate if too long
        notif_msg = notif_msg[:250]
        
        # Save the full update to a file
        logs_dir = os.path.join("logs")
        os.makedirs(logs_dir, exist_ok=True)
        update_path = os.path.join(logs_dir, "morning_update.txt")
        with open(update_path, "w", encoding="utf-8") as f:
            f.write(full_update)
        
        # Send notification
        send_notification("Morning Update", notif_msg, duration=10)
        
        # Log the update
        log_path = os.path.join("logs", "scheduler.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] Morning update completed successfully\n")
            f.write(f"Top context: {top_context.value if top_context else 'N/A'}\n")
            f.write(f"Notification: {notif_msg}\n")
        
    except Exception as e:
        error_msg = f"Error running morning update: {str(e)}"
        print(error_msg)
        send_notification("Morning Update Error", error_msg)
        # Log the error
        log_path = os.path.join("logs", "scheduler.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] {error_msg}\n")

def main():
    """Main function to run the scheduler."""
    print("Starting scheduler...")
    # For testing: Run the update immediately
    print("Running test update immediately...")
    run_morning_update()
    # Schedule the morning update for future runs
    schedule.every().day.at("07:00").do(run_morning_update)
    print("Scheduled future updates for 7:00 AM daily")
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 