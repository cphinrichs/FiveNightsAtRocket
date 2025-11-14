"""
Five Nights at Rocket - AI Message Generator
Generates dynamic, contextual messages using OpenAI's ChatGPT API
"""

import os
from typing import Optional
import random


class AIMessageGenerator:
    """
    Generates contextual messages using ChatGPT for game events.
    Falls back to predefined messages if API is unavailable.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI message generator.
        
        Args:
            api_key: OpenAI API key (will try environment variable if not provided)
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.client = None
        self.enabled = False
        
        # Try to initialize OpenAI client
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.enabled = True
                print("[AI Messages] ChatGPT message generation enabled")
            except ImportError:
                print("[AI Messages] Warning: 'openai' package not installed. Using fallback messages.")
                print("[AI Messages] Install with: pip install openai")
            except Exception as e:
                print(f"[AI Messages] Warning: Could not initialize OpenAI client: {e}")
        else:
            print("[AI Messages] No API key found. Using fallback messages.")
            print("[AI Messages] Set OPENAI_API_KEY environment variable to enable AI messages.")
    
    def generate_jumpscare_message(self, enemy_name: str, context: dict) -> str:
        """
        Generate a jumpscare death message using ChatGPT.
        
        Args:
            enemy_name: Name of the enemy that killed the player
            context: Dictionary with game context (time, location, etc.)
            
        Returns:
            Generated message string
        """
        if not self.enabled or not self.client:
            return self._get_fallback_message(enemy_name, context)
        
        try:
            # Construct prompt for ChatGPT
            prompt = self._build_jumpscare_prompt(enemy_name, context)
            
            # Special system prompt for Jo-nathan to emphasize bad jokes
            if enemy_name == 'Jo-nathan':
                system_content = "You are a game narrator who loves terrible puns. For Jo-nathan deaths, ALWAYS start with a cringeworthy egg joke/pun, then the death message. Maximum 20 words total. Make the jokes so bad they're funny."
                max_tokens = 60
            else:
                system_content = "You are a witty game narrator for an office horror game. Generate short, darkly humorous death messages (max 15 words). Be creative and match the enemy's personality."
                max_tokens = 50
            
            # Call ChatGPT API with nucleus sampling for more variety
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.8,
                top_p=0.95,  # Nucleus sampling for more diverse outputs
                frequency_penalty=0.3,  # Penalize repetitive phrases
                presence_penalty=0.2,  # Encourage new topics
                n=1
            )
            
            # Extract message
            message = response.choices[0].message.content.strip()
            
            # Remove quotes if present
            if message.startswith('"') and message.endswith('"'):
                message = message[1:-1]
            
            print(f"[AI Messages] Generated: {message}")
            return message
            
        except Exception as e:
            print(f"[AI Messages] Error generating message: {e}")
            return self._get_fallback_message(enemy_name, context)
    
    def _build_jumpscare_prompt(self, enemy_name: str, context: dict) -> str:
        """Build the prompt for ChatGPT based on enemy and context."""
        time_of_day = context.get('time', 'unknown time')
        location = context.get('room', 'unknown room')
        cause = context.get('cause', 'carelessness')
        
        # Special handling for Jo-nathan - always include a bad joke!
        if enemy_name == 'Jo-nathan':
            joke_prompts = [
                f"""Jo-nathan caught the player at {time_of_day} in the {location} (cause: {cause}).

Generate a death message (max 20 words) that includes a terrible egg pun or dad joke. Format:
"[Bad joke/pun]. [Death message]"

Example: "Why did the egg go to school? To get egg-ucated! You didn't. Jo-nathan wins."
Example: "What do you call an egg that never shows up? Egg-stremely dead. Like you."

Your turn:""",
                
                f"""Create Jo-nathan's death message with a cringeworthy egg joke (max 20 words).
Context: Player died at {time_of_day} in {location} - {cause}

Format: Start with a bad egg pun, then the death line.
Example: "Heard about the egg's career? It cracked under pressure. So did you."

Generate:""",
                
                f"""Jo-nathan kills the player and tells them a terrible egg joke first.
Time: {time_of_day} | Location: {location} | Cause: {cause}

Write the worst egg pun you can think of, followed by the death message (max 20 words total).
Example: "Why can't you trust eggs? They crack under pressure! Speaking of which..."

Your joke + death message:""",
                
                f"""Generate a groan-worthy egg joke + death message combo for Jo-nathan (max 20 words).
Player caught at {time_of_day}, {location} - {cause}

Make the joke so bad it hurts. Then deliver the death blow.
Example: "What's an egg's least favorite day? Fry-day! Today's yours."

Go:""",
            ]
            return random.choice(joke_prompts)
        
        # Enemy-specific personality traits with multiple descriptions to vary the prompt
        personality_options = {
            'Jeromathy': [
                'snack-protective and territorial about his desk',
                'violently defensive of his snack supply',
                'becomes enraged when snacks are depleted',
                'guards his snacks with lethal dedication',
            ],
            'Angellica': [
                'productivity-focused, hates YouTube slackers',
                'enforces strict coding discipline, no YouTube allowed',
                'monitors employee productivity obsessively',
                'has zero tolerance for workplace time-wasting',
            ],
            'Runnit': [
                'unpredictable sprinter who blitzes through rooms at high speed',
                'uses hit-and-run tactics, only dangerous while sprinting',
                'fast and chaotic, impossible to predict',
                'lightning-fast runner who strikes without warning',
            ],
            'NextGen Intern': [
                'harmless snack thief (should never kill)',
                'annoying but ultimately harmless',
            ],
        }
        
        # Randomly select a personality description
        personality_list = personality_options.get(enemy_name, ['mysterious office worker'])
        personality = random.choice(personality_list)
        
        # Vary the prompt structure to get more diverse outputs
        prompt_styles = [
            # Style 1: Detailed context
            f"""Create a darkly funny death message for '{enemy_name}' killing the player.

Context: {enemy_name} ({personality}) caught the player at {time_of_day} in the {location}.
Reason: {cause}

Generate a witty, concise message (max 15 words) that captures this moment.""",
            
            # Style 2: Direct instruction
            f"""Write a short death message (max 15 words) for this office horror game scenario:
- Killer: {enemy_name}
- Trait: {personality}
- When: {time_of_day}
- Where: {location}
- Why: {cause}

Make it darkly humorous and reference the killer's personality.""",
            
            # Style 3: Narrative focused
            f"""The player died to {enemy_name} ({personality}) due to {cause}.
Time: {time_of_day} | Place: {location}

Generate a witty game-over message (under 15 words) that roasts the player's mistake.""",
            
            # Style 4: Minimal
            f"""{enemy_name} killed the player. Cause: {cause}. Location: {location}.
Enemy personality: {personality}

Short death message (max 15 words), darkly funny:""",
        ]
        
        # Randomly choose a prompt style
        prompt = random.choice(prompt_styles)
        
        return prompt
    
    def _get_fallback_message(self, enemy_name: str, context: dict) -> str:
        """Get a predefined fallback message when AI is unavailable."""
        fallback_messages = {
            'Jo-nathan': [
                "What did the egg say to the frying pan? 'This is cracking me up!' You didn't laugh either.",
                "Why did Jo-nathan cross the road? To catch YOU. Egg-sactly as planned.",
                "How do you make an egg laugh? Tell it a yolk! How do you die? Forget the egg.",
                "What's an egg's favorite sport? Running! You should've tried it. With an egg.",
                "Why can't eggs tell jokes? They crack up! Unlike you, who just cracked.",
                "What do you call a scared egg? Terri-fried! That's you. Jo-nathan got you.",
            ],
            'Jeromathy': [
                "Jeromathy found his snacks depleted. So is your life expectancy.",
                "Zero snacks, zero mercy. Jeromathy doesn't forgive.",
                "Jeromathy's wrath is as real as his empty snack cabinet.",
                "Should've kept those snacks stocked. Too late now.",
                "Jeromathy takes his snacks seriously. Fatally seriously.",
            ],
            'Angellica': [
                "Angellica saw your YouTube tab. Your final video is over.",
                "YouTube? In THIS office? Angellica says no.",
                "Should've stuck to coding. Angellica doesn't tolerate slackers.",
                "Your productivity score: Zero. Forever.",
                "Angellica enforces the company's no-YouTube policy. Permanently.",
            ],
            'Runnit': [
                "Runnit came out of nowhere. You never saw it coming.",
                "Too fast to dodge, too late to hide. Runnit strikes again.",
                "Blink and you're dead. Runnit doesn't slow down for anyone.",
                "You thought you were safe? Runnit's sprint says otherwise.",
                "Speed kills. Runnit is living (you're not) proof.",
                "Runnit blitzed through. You were just in the way.",
            ],
        }
        
        # Get random message for this enemy
        messages = fallback_messages.get(enemy_name, [
            f"{enemy_name} got you. Try again?",
            f"Caught by {enemy_name}. Better luck next time.",
            f"{enemy_name} wins this round. Restart?",
        ])
        
        return random.choice(messages)
    
    def generate_victory_message(self, context: dict) -> str:
        """
        Generate a victory message using ChatGPT.
        
        Args:
            context: Dictionary with game context (survived time, close calls, etc.)
            
        Returns:
            Generated victory message
        """
        if not self.enabled or not self.client:
            return self._get_fallback_victory_message(context)
        
        try:
            # Vary the prompt structure for more diverse victory messages
            prompt_styles = [
                # Style 1
                f"""Victory! The player survived 9am-5pm in an office where coworkers try to kill you.
Generate a witty, sarcastic victory message (max 20 words) that jokes about surviving a "normal" workday.""",
                
                # Style 2
                f"""Write a short victory message (under 20 words) for beating this office horror game.
The player survived their shift dodging Jo-nathan, Jeromathy, and Angellica.
Tone: Celebratory but darkly humorous about office life.""",
                
                # Style 3
                f"""The player made it from 9am to 5pm without dying to psychotic coworkers.
Create a funny victory message (max 20 words) that highlights the absurdity.""",
                
                # Style 4
                f"""Generate a sarcastic office-themed victory message (under 20 words).
Context: Survived a horror game workday, avoided killer coworkers, made it to clock-out time.""",
            ]
            
            prompt = random.choice(prompt_styles)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a witty game narrator. Generate short victory messages with dry office humor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                temperature=0.8,
                top_p=0.95,
                frequency_penalty=0.3,
                presence_penalty=0.2,
                n=1
            )
            
            message = response.choices[0].message.content.strip()
            if message.startswith('"') and message.endswith('"'):
                message = message[1:-1]
            
            return message
            
        except Exception as e:
            print(f"[AI Messages] Error generating victory message: {e}")
            return self._get_fallback_victory_message(context)
    
    def _get_fallback_victory_message(self, context: dict) -> str:
        """Get a predefined victory message."""
        messages = [
            "You survived until 5pm! That's... just a normal workday, actually.",
            "Congratulations! You've successfully attended work. Tomorrow's another story.",
            "Made it to clock-out time. Your reward? Getting to do it again tomorrow.",
            "Survived the office. The real horror is coming back Monday.",
            "5pm! Time to go home and pretend today was normal.",
        ]
        return random.choice(messages)


# Global instance (initialized when imported)
_ai_generator = None

def get_ai_message_generator() -> AIMessageGenerator:
    """Get the global AI message generator instance."""
    global _ai_generator
    if _ai_generator is None:
        _ai_generator = AIMessageGenerator()
    return _ai_generator
