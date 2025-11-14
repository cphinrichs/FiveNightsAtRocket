"""
Test script to check AI message variety
Generates multiple messages for the same scenario to verify randomness
"""

import os
from ai_messages import AIMessageGenerator

# Set API key if available
api_key = os.environ.get('OPENAI_API_KEY')

print("=" * 60)
print("AI MESSAGE VARIETY TEST")
print("=" * 60)

generator = AIMessageGenerator(api_key)
print(f"AI Enabled: {generator.enabled}")
print()

if not generator.enabled:
    print("⚠ API key not set. Testing fallback messages only.")
    print()

# Test Angellica death scenario 5 times
print("=" * 60)
print("Testing Angellica Death Message (5 generations)")
print("=" * 60)

context = {
    'time': '2:30 PM',
    'room': 'Classroom',
    'cause': 'watching YouTube on the job',
}

for i in range(1, 6):
    message = generator.generate_jumpscare_message('Angellica', context)
    print(f"\n[Generation {i}]")
    print(f"  {message}")

print()
print("=" * 60)
print("Testing Jo-nathan Death Message (5 generations)")
print("=" * 60)

context = {
    'time': '11:00 AM',
    'room': 'Hallway',
    'cause': 'caught with no egg to offer',
}

for i in range(1, 6):
    message = generator.generate_jumpscare_message('Jo-nathan', context)
    print(f"\n[Generation {i}]")
    print(f"  {message}")

print()
print("=" * 60)
print("Testing Victory Message (5 generations)")
print("=" * 60)

victory_context = {
    'time_survived': '9am to 5pm',
    'enemies_avoided': 'Jo-nathan, Jeromathy, Angellica',
}

for i in range(1, 6):
    message = generator.generate_victory_message(victory_context)
    print(f"\n[Generation {i}]")
    print(f"  {message}")

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
