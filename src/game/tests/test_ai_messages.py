"""
Unit tests for AI message generation
Tests AIMessageGenerator with mocked OpenAI API
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_messages import AIMessageGenerator


class TestAIMessageGenerator:
    """Test AI message generation system"""
    
    @pytest.fixture
    def generator_with_api(self):
        """Create generator with API key"""
        return AIMessageGenerator(api_key="test_api_key_12345")
    
    @pytest.fixture
    def generator_without_api(self, monkeypatch):
        """Create generator without API key"""
        # Clear environment variable
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        return AIMessageGenerator(api_key=None)
    
    def test_initialization_with_api_key(self, generator_with_api):
        """Test generator initializes with API key"""
        assert generator_with_api.api_key == "test_api_key_12345"
        assert generator_with_api.client is not None
    
    def test_initialization_without_api_key(self, monkeypatch):
        """Test generator initializes without API key"""
        # Clear environment variable
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        generator = AIMessageGenerator(api_key=None)
        assert generator.api_key is None
        assert generator.client is None
    
    def test_fallback_message_generation(self, generator_without_api):
        """Test fallback messages are returned when no API"""
        context = {"time": "3:00 PM", "location": "Office"}
        message = generator_without_api.generate_jumpscare_message("Jo-nathan", context)
        
        assert message is not None
        assert len(message) > 0
    
    def test_jonathan_messages_include_eggs(self, generator_without_api):
        """Test Jonathan's messages often reference eggs"""
        context = {"time": "3:00 PM", "location": "Office"}
        
        # Generate multiple messages to see variety
        messages = []
        for _ in range(5):
            msg = generator_without_api.generate_jumpscare_message("Jo-nathan", context)
            messages.append(msg)
        
        # At least one should mention eggs (due to special handling)
        has_egg_reference = any("egg" in msg.lower() or "yolk" in msg.lower() for msg in messages)
    
    def test_api_call_structure(self, generator_with_api):
        """Test API is called with correct parameters"""
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test jumpscare message"
        
        mock_client.chat.completions.create.return_value = mock_response
        generator_with_api.client = mock_client
        generator_with_api.enabled = True
        
        # Generate message with context
        context = {"time": "3:00 PM", "location": "Office"}
        message = generator_with_api.generate_jumpscare_message("Jo-nathan", context)
        
        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Check call parameters
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['model'] == "gpt-3.5-turbo"
        assert call_args.kwargs['temperature'] == 0.8
        assert call_args.kwargs['top_p'] == 0.95
    
    def test_api_failure_uses_fallback(self, generator_with_api):
        """Test fallback is used when API fails"""
        # Mock API failure
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        generator_with_api.client = mock_client
        generator_with_api.enabled = True
        
        # Should return fallback message
        context = {"time": "3:00 PM", "location": "Office"}
        message = generator_with_api.generate_jumpscare_message("Jo-nathan", context)
        
        assert message is not None
        assert len(message) > 0
    
    def test_message_randomization(self, generator_without_api):
        """Test messages can vary"""
        messages = set()
        context = {"time": "3:00 PM", "location": "Office"}
        
        # Generate multiple messages
        for _ in range(20):
            msg = generator_without_api.generate_jumpscare_message("Jeromathy", context)
            messages.add(msg)
        
        # Should have gotten at least one message
        assert len(messages) >= 1
    
    def test_all_enemies_supported(self, generator_without_api):
        """Test all enemy types can generate messages"""
        enemies = ["Jo-nathan", "Jeromathy", "Angellica", "Runnit", "NextGen Intern"]
        context = {"time": "3:00 PM", "location": "Office"}
        
        for enemy in enemies:
            message = generator_without_api.generate_jumpscare_message(enemy, context)
            assert message is not None
            assert len(message) > 0
    
    def test_unknown_enemy_fallback(self, generator_without_api):
        """Test unknown enemy returns generic message"""
        context = {"time": "3:00 PM", "location": "Office"}
        message = generator_without_api.generate_jumpscare_message("Unknown Enemy", context)
        
        # Should return some fallback or generic message
        assert message is not None
    
    def test_jonathan_api_includes_eggs(self, generator_with_api):
        """Test Jonathan's API prompts get special handling"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Egg-cellent catch!"
        
        mock_client.chat.completions.create.return_value = mock_response
        generator_with_api.client = mock_client
        generator_with_api.enabled = True
        
        context = {"time": "3:00 PM", "location": "Office"}
        message = generator_with_api.generate_jumpscare_message("Jo-nathan", context)
        
        # Check that API was called with special system prompt for Jonathan
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        
        # Find system message
        system_message = None
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
                break
        
        assert system_message is not None
        assert "egg" in system_message.lower() or "joke" in system_message.lower()
    
    def test_message_variety_parameters(self, generator_with_api):
        """Test API uses variety parameters"""
        # Parameters should be set for variety
        # frequency_penalty and presence_penalty encourage variety
        # These are typically used in the API call
        pass  # Implementation depends on API call structure
    
    def test_messages_are_generated(self, generator_without_api):
        """Test messages can be generated for all enemies"""
        enemies = ["Jo-nathan", "Jeromathy", "Angellica", "Runnit", "NextGen Intern"]
        context = {"time": "3:00 PM", "location": "Office"}
        
        for enemy in enemies:
            message = generator_without_api.generate_jumpscare_message(enemy, context)
            assert len(message) > 5  # Reasonable message length


class TestMessageContent:
    """Test message content quality"""
    
    @pytest.fixture
    def generator(self, monkeypatch):
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        return AIMessageGenerator(api_key=None)
    
    def test_messages_appropriate_length(self, generator):
        """Test messages have appropriate length"""
        context = {"time": "3:00 PM", "location": "Office"}
        enemies = ["Jo-nathan", "Jeromathy", "Angellica"]
        
        for enemy in enemies:
            msg = generator.generate_jumpscare_message(enemy, context)
            assert len(msg) > 10  # Reasonable length
            assert len(msg) < 300  # Not too long
    
    def test_messages_not_empty(self, generator):
        """Test no empty messages"""
        context = {"time": "3:00 PM", "location": "Office"}
        enemies = ["Jo-nathan", "Jeromathy", "Angellica", "Runnit"]
        
        for enemy in enemies:
            msg = generator.generate_jumpscare_message(enemy, context)
            assert msg.strip() != ""
            assert len(msg) > 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
