import os
from typing import Dict, List, Any
from datetime import datetime
from src.context_manager import ContextManager, ContextType
from src.agent import Agent

class ReportGenerator:
    def __init__(self, config: Dict[str, Any], context_manager: ContextManager, agent: Agent):
        self.config = config
        self.openai_api_key = config['api_keys']['openai']
        os.environ['OPENAI_API_KEY'] = self.openai_api_key
        self.context_manager = context_manager
        self.agent = agent

    def _format_weather(self, weather_data: Dict[str, Any]) -> str:
        """Format weather information."""
        if not weather_data:
            return "Weather data unavailable"
        
        return f"""WEATHER Update for {self.config['city']}:
• Temperature: {weather_data['temperature']}°C
• Conditions: {weather_data['condition']}
• Humidity: {weather_data['humidity']}%
• Wind Speed: {weather_data['wind_speed']} m/s
• Precipitation Chance: {weather_data['precipitation_chance']}%
• Alerts: {', '.join(weather_data['alerts'])}"""

    def _format_stocks(self, stocks_data: Dict[str, Dict[str, float]]) -> str:
        """Format stock information."""
        if not stocks_data:
            return "Stock data unavailable"
        
        stocks_text = "STOCKS Market Update:\n"
        for symbol, data in stocks_data.items():
            change_symbol = "↑" if data['change'] > 0 else "↓"
            stocks_text += f"• {symbol}: ${data['price']:.2f} ({change_symbol}{abs(data['change']):.2f}%)\n"
        return stocks_text.strip()

    def _format_news(self, news_data: Dict[str, List[Dict[str, str]]]) -> str:
        """Format news information."""
        if not news_data or 'headlines' not in news_data:
            return "News data unavailable"
        
        news_text = "NEWS Top Headlines:\n"
        for article in news_data['headlines']:
            importance = "⚠️" if article.get('importance') == 'high' else "•"
            news_text += f"{importance} {article['title']}\n"
            if article.get('category'):
                news_text += f"  Category: {article['category']}\n"
        return news_text.strip()

    def _format_sports(self, sports_data: Dict[str, List[Dict[str, str]]]) -> str:
        """Format sports information."""
        if not sports_data:
            return "Sports data unavailable"
        
        sports_text = "SPORTS Update:\n"
        
        # NBA Games
        if 'nba' in sports_data:
            sports_text += "\nNBA:\n"
            for game in sports_data['nba']:
                sports_text += f"• {game['game']} ({game['status']})\n"
                if 'highlight' in game:
                    sports_text += f"  {game['highlight']}\n"
        
        # NFL Games
        if 'nfl' in sports_data:
            sports_text += "\nNFL:\n"
            for game in sports_data['nfl']:
                sports_text += f"• {game['game']} ({game['status']})\n"
                if 'highlight' in game:
                    sports_text += f"  {game['highlight']}\n"
        
        # Upcoming Games
        if 'upcoming' in sports_data:
            sports_text += "\nUpcoming Games:\n"
            for game in sports_data['upcoming']:
                sports_text += f"• {game['game']} at {game['time']}\n"
                if 'importance' in game:
                    sports_text += f"  Note: {game['importance']}\n"
        
        return sports_text.strip()

    def generate_report(self, weather_data: Dict[str, Any], stocks_data: Dict[str, Dict[str, float]], 
                       news_data: List[Dict[str, str]], sports_data: Dict[str, List[Dict[str, str]]]) -> str:
        """Generate the complete morning report."""
        # Generate report header
        report = f"""Morning World Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}
===========================================\n\n"""

        # Get the latest priority analysis for each context
        priorities = {}
        for context_type in ContextType:
            patterns = self.agent.memory["learned_patterns"].get(context_type.value, [])
            if patterns:
                latest_pattern = patterns[-1]
                priorities[context_type] = latest_pattern.get("importance", 3)  # Default to 3 if not found

        # Create sections with their priorities
        sections = {
            ContextType.WEATHER: (self._format_weather, weather_data, priorities.get(ContextType.WEATHER, 3)),
            ContextType.STOCKS: (self._format_stocks, stocks_data, priorities.get(ContextType.STOCKS, 3)),
            ContextType.NEWS: (self._format_news, news_data, priorities.get(ContextType.NEWS, 3)),
            ContextType.SPORTS: (self._format_sports, sports_data, priorities.get(ContextType.SPORTS, 3))
        }
        
        # Sort sections by priority (lower number = higher priority)
        sorted_sections = sorted(sections.items(), key=lambda x: x[1][2])
        
        # Add each section in order of priority
        for context_type, (formatter, data, _) in sorted_sections:
            try:
                section = formatter(data)
                report += section + "\n\n"
            except Exception as e:
                report += f"Error formatting {context_type.value} section: {str(e)}\n\n"

        return report.strip() 