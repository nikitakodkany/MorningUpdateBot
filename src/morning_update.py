import os
import sys
import yaml
from datetime import datetime
from typing import Dict, Any

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fetch_data import DataFetcher
from src.generate_report import ReportGenerator
from src.context_manager import ContextManager, ContextType
from src.agent import Agent
from src.telegram_bot import TelegramBot

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    """Generate and display the morning update."""
    try:
        # Load configuration
        config = load_config()
        
        # Initialize context manager and agent
        context_manager = ContextManager(config)
        agent = Agent(config, context_manager)
        
        # Initialize Telegram bot
        telegram_bot = TelegramBot(
            token=config['telegram']['bot_token'],
            chat_id=config['telegram']['chat_id']
        )
        
        # More realistic test data
        weather_data = {
            "temperature": 28,
            "feels_like": 30,
            "condition": "partly cloudy",
            "precipitation_chance": 30,
            "humidity": 65,
            "wind_speed": 15,
            "alerts": ["Heat advisory in effect until 6 PM"]
        }
        
        stocks_data = {
            "AAPL": {
                "price": 175.25,
                "change": -3.75,
                "change_percent": -2.1,
                "volume": "85.2M",
                "market_cap": "2.8T"
            },
            "TSLA": {
                "price": 242.50,
                "change": +8.30,
                "change_percent": +3.5,
                "volume": "120.5M",
                "market_cap": "768.4B"
            },
            "MSFT": {
                "price": 338.15,
                "change": +2.45,
                "change_percent": +0.7,
                "volume": "22.1M",
                "market_cap": "2.5T"
            }
        }
        
        news_data = {
            "headlines": [
                {
                    "title": "Fed Signals Potential Interest Rate Cut in Coming Months",
                    "category": "Economy",
                    "importance": "high"
                },
                {
                    "title": "Major Tech Company Announces Revolutionary AI Chip",
                    "category": "Technology",
                    "importance": "medium"
                },
                {
                    "title": "Global Climate Summit Reaches Historic Agreement",
                    "category": "Environment",
                    "importance": "high"
                }
            ]
        }
        
        sports_data = {
            "nba": [
                {
                    "game": "Lakers vs Warriors",
                    "score": "120-115",
                    "status": "Final",
                    "highlight": "LeBron's triple-double leads Lakers"
                }
            ],
            "nfl": [
                {
                    "game": "Chiefs vs Bills",
                    "score": "24-17",
                    "status": "Final",
                    "highlight": "Mahomes throws 3 TDs in victory"
                }
            ],
            "upcoming": [
                {
                    "game": "Celtics vs Bucks",
                    "time": "7:30 PM EST",
                    "importance": "Crucial matchup for playoff seeding"
                }
            ]
        }
        
        # Update contexts with realistic data
        context_manager.set_context(ContextType.WEATHER, weather_data)
        context_manager.set_context(ContextType.STOCKS, stocks_data)
        context_manager.set_context(ContextType.NEWS, news_data)
        context_manager.set_context(ContextType.SPORTS, sports_data)
        
        # Analyze each context
        for context_type in ContextType:
            context = context_manager.get_context(context_type)
            if context:
                print(f"\nAnalyzing {context_type.value.upper()}...")
                print("-" * 50)
                analysis = agent.analyze_context(context_type, context.data)
                print(f"Priority: {analysis.get('priority', 'N/A')}")
                print("\nInsights:")
                for insight in analysis.get('insights', []):
                    print(f"- {insight}")
                print("\nActions:")
                for action in analysis.get('actions', []):
                    print(f"- {action}")
                print("-" * 50)
        
        # Get agent summary
        print("\nAGENT SUMMARY")
        print("=" * 50)
        print(agent.get_agent_summary())
        print("=" * 50)
        
        # Generate the report
        report_generator = ReportGenerator(config, context_manager, agent)
        report = report_generator.generate_report(weather_data, stocks_data, news_data, sports_data)
        
        # Send the report via Telegram
        if not telegram_bot.send_morning_update(report):
            print("Error sending morning update via Telegram")
        
        # Print the report to console
        print(report)
        
    except Exception as e:
        error_msg = f"Error generating morning update: {e}"
        print(error_msg)
        # Try to send error notification via Telegram
        try:
            telegram_bot.send_message(f"❌ {error_msg}")
        except:
            pass

if __name__ == "__main__":
    main() 