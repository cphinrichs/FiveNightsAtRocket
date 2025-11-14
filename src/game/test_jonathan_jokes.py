"""
Test Jo-nathan's bad jokes specifically
"""

import os
from ai_messages import AIMessageGenerator

# Set API key
api_key = os.environ.get('OPENAI_API_KEY')

print("=" * 70)
print("JO-NATHAN'S BAD JOKE TEST")
print("=" * 70)

generator = AIMessageGenerator(api_key)
print(f"AI Enabled: {generator.enabled}")
print()

if not generator.enabled:
    print("⚠ API key not set. Testing fallback jokes only.")
    print()

# Test Jo-nathan's bad jokes 10 times!
print("=" * 70)
print("Testing Jo-nathan's Terrible Egg Jokes (10 generations)")
print("=" * 70)

context = {
    'time': '11:30 AM',
    'room': 'Hallway',
    'cause': 'caught with no egg to offer',
}

for i in range(1, 11):
    message = generator.generate_jumpscare_message('Jo-nathan', context)
    print(f"\n[Death #{i}]")
    print(f"  {message}")

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nDid Jo-nathan tell terrible jokes? Let's hope so! 🥚")
