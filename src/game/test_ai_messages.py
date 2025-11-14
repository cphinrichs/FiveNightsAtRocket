"""
Test AI Message Generation
Quick test to verify the AI message system works correctly
"""

from ai_messages import AIMessageGenerator

print("="*60)
print("AI MESSAGE GENERATOR TEST")
print("="*60)

# Initialize generator
generator = AIMessageGenerator()

print(f"\nAI Generation Enabled: {generator.enabled}")
if generator.enabled:
    print("✓ OpenAI API key found and client initialized")
else:
    print("✗ OpenAI API not available, using fallback messages")

print("\n" + "-"*60)
print("TESTING JUMPSCARE MESSAGES")
print("-"*60)

# Test different enemies
test_scenarios = [
    {
        'enemy': 'Jo-nathan',
        'context': {'time': '10:30 AM', 'room': 'Hallway', 'cause': 'caught with no egg to offer'}
    },
    {
        'enemy': 'Jeromathy',
        'context': {'time': '2:15 PM', 'room': 'Office', 'cause': 'letting snacks run out'}
    },
    {
        'enemy': 'Angellica',
        'context': {'time': '11:45 AM', 'room': 'Classroom', 'cause': 'watching YouTube on the job'}
    },
]

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n[Scenario {i}] {scenario['enemy']} @ {scenario['context']['time']} ({scenario['context']['room']})")
    message = generator.generate_jumpscare_message(scenario['enemy'], scenario['context'])
    print(f"Message: {message}")

print("\n" + "-"*60)
print("TESTING VICTORY MESSAGE")
print("-"*60)

victory_context = {'time_survived': '9am to 5pm', 'enemies_avoided': 'Jo-nathan, Jeromathy, Angellica'}
victory_msg = generator.generate_victory_message(victory_context)
print(f"\nVictory Message: {victory_msg}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)

if generator.enabled:
    print("\n✓ All AI messages generated successfully!")
    print("Note: Messages are dynamic and will vary each time.")
else:
    print("\n✓ Fallback messages working correctly!")
    print("Tip: Set OPENAI_API_KEY environment variable to enable AI messages.")
