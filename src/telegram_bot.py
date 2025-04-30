import os
import requests
from typing import Optional

class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, text: str, parse_mode: Optional[str] = None) -> bool:
        """Send a message to the specified chat."""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=data)
            
            if response.status_code != 200:
                print(f"Error sending message. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
            return True
        except Exception as e:
            print(f"Exception while sending Telegram message: {str(e)}")
            return False

    def send_morning_update(self, update_text: str) -> bool:
        """Send the morning update with proper formatting."""
        try:
            # Split the update into chunks if it's too long (Telegram has a 4096 character limit)
            max_length = 4000  # Leave some room for formatting
            chunks = [update_text[i:i+max_length] for i in range(0, len(update_text), max_length)]
            
            success = True
            for i, chunk in enumerate(chunks):
                # Add header for first chunk, continuation for others
                if i == 0:
                    formatted_text = f"🌅 <b>Morning Update</b>\n\n{chunk}"
                else:
                    formatted_text = f"<b>Continued...</b>\n\n{chunk}"
                
                if not self.send_message(formatted_text, parse_mode="HTML"):
                    success = False
                    print(f"Failed to send chunk {i+1} of {len(chunks)}")
            
            return success
        except Exception as e:
            print(f"Exception in send_morning_update: {str(e)}")
            return False 