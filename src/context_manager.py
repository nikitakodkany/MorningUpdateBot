from typing import Dict, Any, List, Optional
from enum import Enum
import json
import os
from datetime import datetime
from dataclasses import dataclass

class ContextType(Enum):
    WEATHER = "weather"
    STOCKS = "stocks"
    NEWS = "news"
    SPORTS = "sports"

@dataclass
class Context:
    type: ContextType
    data: Dict[str, Any]
    priority: int = 3
    timestamp: Optional[str] = None

class ContextManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.contexts: Dict[ContextType, Context] = {}
        self.context_history: List[Context] = []
        self.active_context: Optional[ContextType] = None
        self.context_file = os.path.join("logs", "context_history.json")
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Load existing context history if available
        self._load_context_history()

    def _load_context_history(self):
        """Load context history from file if it exists."""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r') as f:
                    history_data = json.load(f)
                    self.context_history = [
                        Context(
                            type=ContextType(ctx["type"]),
                            data=ctx["data"],
                            priority=ctx.get("priority", 3),
                            timestamp=ctx.get("timestamp")
                        )
                        for ctx in history_data
                    ]
        except Exception as e:
            print(f"Error loading context history: {e}")

    def _save_context_history(self):
        """Save context history to file."""
        try:
            with open(self.context_file, 'w') as f:
                json.dump([
                    {
                        "type": ctx.type.value,
                        "data": ctx.data,
                        "priority": ctx.priority,
                        "timestamp": ctx.timestamp
                    }
                    for ctx in self.context_history
                ], f, indent=2)
        except Exception as e:
            print(f"Error saving context history: {e}")

    def set_context(self, context_type: ContextType, data: Dict[str, Any], priority: int = 3):
        """Set context data for a specific type."""
        context = Context(
            type=context_type,
            data=data,
            priority=priority,
            timestamp=datetime.now().isoformat()
        )
        self.contexts[context_type] = context
        self.context_history.append(context)
        self._save_context_history()

    def get_context(self, context_type: ContextType) -> Optional[Context]:
        """Get context data for a specific type."""
        return self.contexts.get(context_type)

    def set_context_priority(self, context_type: ContextType, priority: int):
        """Update priority for a specific context type."""
        if context_type in self.contexts:
            self.contexts[context_type].priority = priority

    def get_all_contexts(self) -> Dict[ContextType, Context]:
        """Get all contexts."""
        return self.contexts

    def update_context(self, context_type: ContextType, data: Dict[str, Any]):
        """Update or create a new context."""
        context = Context(context_type, data)
        self.contexts[context_type] = context
        self.context_history.append(context)
        self._save_context_history()

    def switch_context(self, context_type: ContextType) -> bool:
        """Switch to a different context."""
        if context_type in self.contexts:
            self.active_context = context_type
            return True
        return False

    def get_active_context(self) -> Optional[Context]:
        """Get the currently active context."""
        if self.active_context:
            return self.contexts.get(self.active_context)
        return None

    def get_priority_order(self) -> List[ContextType]:
        """Get contexts ordered by priority."""
        return sorted(
            self.contexts.keys(),
            key=lambda x: self.contexts[x].priority
        )

    def clear_inactive_contexts(self):
        """Clear contexts that are no longer active."""
        self.contexts = {
            ctx_type: ctx 
            for ctx_type, ctx in self.contexts.items() 
            if ctx.is_active
        }

    def get_context_summary(self) -> str:
        """Get a summary of all contexts."""
        summary = []
        for ctx_type in self.get_priority_order():
            ctx = self.contexts[ctx_type]
            summary.append(f"{ctx_type.value.upper()}: Priority {ctx.priority}")
            if ctx_type == self.active_context:
                summary[-1] += " (Active)"
        return "\n".join(summary) 