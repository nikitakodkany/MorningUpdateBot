from typing import Dict, List, Any
import openai
import os

class PriorityDecider:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = os.getenv('OPENAI_API_KEY', config.get('openai_api_key', ''))
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def _create_prompt(self, data: Dict[str, Any]) -> str:
        """Create a prompt for the LLM to analyze the data and decide priorities."""
        return f"""Based on the following data, determine which section should appear first in the morning update.
Consider these rules:
- If weather has rain/snow → put Weather first
- If any stock moves > ±5% → put Finance first
- If the team had a significant game → put Sports first
- Else → start with News

Data:
Weather: {data['weather']}
Stocks: {data['stocks']}
Sports: {data['sports']}
News: {data['news']}

Return only the section name that should appear first (Weather, Finance, Sports, or News)."""

    def decide_priority(self, data: Dict[str, Any]) -> List[str]:
        """Decide the priority order of sections using LLM."""
        try:
            if not self.client:
                return ['News', 'Weather', 'Finance', 'Sports']

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that determines the priority of news sections."},
                    {"role": "user", "content": self._create_prompt(data)}
                ],
                temperature=0.3
            )
            
            first_section = response.choices[0].message.content.strip()
            
            # Define the default order
            sections = ['Weather', 'Finance', 'Sports', 'News']
            
            # Move the chosen section to the front
            if first_section in sections:
                sections.remove(first_section)
                sections.insert(0, first_section)
            
            return sections
            
        except Exception as e:
            print(f"Error in priority decision: {e}")
            # Return default order if there's an error
            return ['News', 'Weather', 'Finance', 'Sports'] 