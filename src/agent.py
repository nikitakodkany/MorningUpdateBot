from typing import Dict, Any, List, Optional
import openai
from datetime import datetime
import json
import os
from src.context_manager import ContextManager, ContextType
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class Agent:
    def __init__(self, config: Dict[str, Any], context_manager: ContextManager):
        self.config = config
        self.context_manager = context_manager
        openai.api_key = config['api_keys']['openai']
        self.memory_file = os.path.join("logs", "agent_memory.json")
        self.memory = self._load_memory()
        self.goals = self._initialize_goals()
        self.learning_rate = 0.1
        self.model_name = "facebook/opt-350m"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )

    def _format_prompt(self, context_type: str, data: Dict[str, Any]) -> str:
        context_prompts = {
            "weather": """Given this weather data, analyze and provide:
1. Priority (1-5, where 1 is highest) based on weather severity and impact
2. Key insights about current conditions and any alerts
3. Specific recommended actions for the day

Example response format:
Priority: 4
Insights:
- High temperature of 28°C with heat advisory in effect
- Moderate chance of precipitation (30%)
Actions:
- Stay hydrated and avoid outdoor activities from 12-4 PM
- Keep windows open in the morning for ventilation""",
            
            "stocks": """Given this market data, analyze and provide:
1. Priority (1-5, where 1 is highest) based on market movements
2. Key insights about notable price changes and trends
3. Specific recommended actions for investors

Example response format:
Priority: 2
Insights:
- TSLA up 3.5% on high volume of 120.5M shares
- AAPL down 2.1% with significant market cap of 2.8T
Actions:
- Monitor TSLA for continuation of upward momentum
- Consider AAPL entry points if weakness continues""",
            
            "news": """Given these headlines, analyze and provide:
1. Priority (1-5, where 1 is highest) based on news importance
2. Key insights about major stories and their impact
3. Specific recommended actions to take

Example response format:
Priority: 2
Insights:
- Fed policy shift could impact market conditions
- Major environmental policy changes ahead
Actions:
- Review investment strategy for interest rate changes
- Follow up on climate agreement details""",
            
            "sports": """Given these sports updates, analyze and provide:
1. Priority (1-5, where 1 is highest) based on game importance
2. Key insights about game outcomes and upcoming matches
3. Specific recommended actions for sports followers

Example response format:
Priority: 3
Insights:
- Lakers win close game with strong performance
- Important Celtics vs Bucks game tonight
Actions:
- Watch Celtics-Bucks game for playoff implications
- Track LeBron's performance trend"""
        }
        
        base_prompt = context_prompts.get(context_type, """Analyze this {context_type} data and provide:
1. Priority (1-5, where 1 is highest)
2. Key insights (2-3 points)
3. Recommended actions (1-2 points)""".format(context_type=context_type))
        
        return f"""{base_prompt}

Current data to analyze:
{json.dumps(data, indent=2)}

Provide your analysis following the exact format shown in the example above."""

    def analyze(self, context_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._format_prompt(context_type, data)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                num_return_sequences=1,
                temperature=0.8,
                top_p=0.9,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                do_sample=True
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        try:
            # Extract priority
            priority_line = [line for line in response.split('\n') if line.startswith('Priority:')][0]
            priority = int(priority_line.split(':')[1].strip())
            
            # Extract insights
            insights_start = response.find('Insights:')
            actions_start = response.find('Actions:')
            if insights_start != -1 and actions_start != -1:
                insights_text = response[insights_start:actions_start]
                insights = [line.strip('- ').strip() for line in insights_text.split('\n') if line.strip().startswith('-')]
            else:
                insights = ["Unable to extract insights"]
            
            # Extract actions
            if actions_start != -1:
                actions_text = response[actions_start:]
                actions = [line.strip('- ').strip() for line in actions_text.split('\n') if line.strip().startswith('-')]
            else:
                actions = ["Unable to extract actions"]
            
            # Validate priority
            if priority < 1 or priority > 5:
                priority = 3
            
            return {
                "priority": priority,
                "insights": insights[:2],  # Limit to 2 insights
                "actions": actions[:2]     # Limit to 2 actions
            }
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {response}")
            return {
                "priority": 3,
                "insights": ["Unable to analyze data"],
                "actions": ["Please check the data format"]
            }

    def _load_memory(self) -> Dict[str, Any]:
        """Load agent's memory from file."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading agent memory: {e}")
        return {
            "interactions": [],
            "learned_patterns": {},
            "performance_metrics": {},
            "adaptation_history": []
        }

    def _save_memory(self):
        """Save agent's memory to file."""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving agent memory: {e}")

    def _initialize_goals(self) -> Dict[str, Any]:
        """Initialize agent's goals and objectives."""
        return {
            "primary_goal": "Generate personalized and relevant morning updates",
            "sub_goals": [
                "Maximize information relevance",
                "Optimize content ordering",
                "Adapt to user preferences",
                "Improve decision-making over time"
            ],
            "metrics": {
                "relevance_score": 0.0,
                "user_engagement": 0.0,
                "adaptation_rate": 0.0
            }
        }

    def analyze_context(self, context_type: ContextType, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context data and make autonomous decisions."""
        try:
            # Analyze the context
            analysis = self.analyze(context_type.value, data)
            
            # Update memory with new analysis
            self.memory["interactions"].append({
                "timestamp": datetime.now().isoformat(),
                "context_type": context_type.value,
                "analysis": analysis
            })
            
            # Learn from the analysis
            self._learn_from_analysis(context_type, analysis)
            
            # Save updated memory
            self._save_memory()
            return analysis
        except Exception as e:
            print(f"Error in context analysis: {e}")
            return {}

    def _learn_from_analysis(self, context_type: ContextType, analysis: Dict[str, Any]):
        """Learn from the analysis and update patterns."""
        try:
            # Update learned patterns
            if context_type.value not in self.memory["learned_patterns"]:
                self.memory["learned_patterns"][context_type.value] = []
            
            self.memory["learned_patterns"][context_type.value].append({
                "timestamp": datetime.now().isoformat(),
                "importance": analysis.get("priority", 0),
                "key_insights": analysis.get("insights", [])
            })
            
            # Update performance metrics
            self.goals["metrics"]["relevance_score"] = (
                self.goals["metrics"]["relevance_score"] * (1 - self.learning_rate) +
                analysis.get("priority", 0) * self.learning_rate
            )
            
        except Exception as e:
            print(f"Error in learning process: {e}")

    def get_agent_summary(self) -> str:
        """Get a summary of the agent's state and performance."""
        summary = [
            "🤖 Agent Summary:",
            f"Primary Goal: {self.goals['primary_goal']}",
            "\nSub-Goals:",
            *[f"- {goal}" for goal in self.goals["sub_goals"]],
            "\nPerformance Metrics:",
            f"- Relevance Score: {self.goals['metrics']['relevance_score']:.2f}",
            f"- User Engagement: {self.goals['metrics']['user_engagement']:.2f}",
            f"- Adaptation Rate: {self.goals['metrics']['adaptation_rate']:.2f}",
            "\nLearned Patterns:",
        ]
        
        for context_type, patterns in self.memory["learned_patterns"].items():
            if patterns:
                summary.append(f"\n{context_type.upper()}:")
                latest_pattern = patterns[-1]
                summary.append(f"- Importance: {latest_pattern['importance']}")
                summary.append(f"  Key Insights: {', '.join(latest_pattern['key_insights'][:2])}")
        
        return "\n".join(summary) 