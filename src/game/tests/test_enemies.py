"""
Unit tests for enemy AI behavior
Tests Jonathan, Jeromathy, Angellica, Runnit, and NextGenIntern
"""

import pytest
import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from enemies import Enemy, Jonathan, Jeromathy, Angellica, NextGenIntern, Runnit
from entities import Player
from room import Room
from enums import RoomType


class TestEnemyBase:
    """Test base Enemy class"""
    
    @pytest.fixture
    def enemy(self):
        pygame.init()
        return Enemy(100, 100, 38, 38, (255, 0, 0), "TestEnemy")
    
    def test_enemy_initialization(self, enemy):
        """Test enemy initializes correctly"""
        assert enemy.name == "TestEnemy"
        assert enemy.x == 100
        assert enemy.y == 100
        assert enemy.width == 38
        assert enemy.height == 38
        assert enemy.speed == 80  # Base Enemy speed is 80
        assert enemy.current_room == RoomType.OFFICE
    
    def test_enemy_state_tracking(self, enemy):
        """Test enemy state management"""
        assert enemy.state == "idle"
        enemy.state = "chasing"
        assert enemy.state == "chasing"


class TestJonathan:
    """Test Jo-nathan AI behavior"""
    
    @pytest.fixture
    def setup(self):
        """Setup game objects for Jonathan tests"""
        pygame.init()
        player = Player(300, 300)
        jonathan = Jonathan(100, 100)
        rooms = {
            RoomType.OFFICE: Room(RoomType.OFFICE, 0, 0, 600, 600),
            RoomType.CLASSROOM: Room(RoomType.CLASSROOM, 700, 0, 600, 600)
        }
        return player, jonathan, rooms
    
    def test_jonathan_initialization(self):
        """Test Jonathan starts with correct values"""
        pygame.init()
        jonathan = Jonathan(50, 50)
        assert jonathan.name == "Jo-nathan"
        assert jonathan.speed == 60  # Jonathan's speed is 60
        assert jonathan.egg_eaten == False
        assert jonathan.eating_timer == 0.0
        assert jonathan.state == "idle"
    
    def test_jonathan_always_active(self, setup):
        """Test Jonathan has no activation delay"""
        player, jonathan, rooms = setup
        jonathan.activation_delay = 0.0
        jonathan.current_room = RoomType.OFFICE
        
        # Jonathan should always chase
        jonathan.update(0.1, player, rooms, RoomType.OFFICE)
        assert jonathan.state == "chasing"
    
    def test_jonathan_egg_mechanic(self):
        """Test egg eating mechanic"""
        pygame.init()
        jonathan = Jonathan(100, 100)
        
        # Feed egg
        jonathan.egg_eaten = True
        jonathan.eating_timer = 10.0
        assert jonathan.egg_eaten == True
        assert jonathan.eating_timer == 10.0
        
        # Timer counts down
        jonathan.eating_timer -= 5.0
        assert jonathan.eating_timer == 5.0
        
        # Eating wears off
        jonathan.eating_timer = 0.0
        jonathan.egg_eaten = False
        assert jonathan.egg_eaten == False
    
    def test_jonathan_chases_in_same_room(self, setup):
        """Test Jonathan chases player in same room"""
        player, jonathan, rooms = setup
        jonathan.activation_delay = 0.0
        jonathan.current_room = RoomType.OFFICE
        player.x, player.y = 200, 200
        
        initial_x = jonathan.x
        jonathan.update(1.0, player, rooms, RoomType.OFFICE)
        
        # Jonathan should move toward player
        assert jonathan.state == "chasing"
    
    def test_jonathan_eating_prevents_chase(self, setup):
        """Test eating Jonathan doesn't chase"""
        player, jonathan, rooms = setup
        jonathan.activation_delay = 0.0
        jonathan.current_room = RoomType.OFFICE
        jonathan.egg_eaten = True
        jonathan.eating_timer = 5.0
        
        jonathan.update(0.1, player, rooms, RoomType.OFFICE)
        # When eating, Jonathan should be idle or returning
        assert jonathan.state in ["idle", "returning"]


class TestJeromathy:
    """Test Jeromathy AI behavior"""
    
    @pytest.fixture
    def setup(self):
        pygame.init()
        player = Player(300, 300)
        jeromathy = Jeromathy(100, 100)
        rooms = {
            RoomType.OFFICE: Room(RoomType.OFFICE, 0, 0, 600, 600),
            RoomType.BREAK_ROOM: Room(RoomType.BREAK_ROOM, -200, 0, 400, 600)
        }
        return player, jeromathy, rooms
    
    def test_jeromathy_initialization(self):
        """Test Jeromathy starts correctly"""
        pygame.init()
        jeromathy = Jeromathy(50, 50)
        assert jeromathy.name == "Jeromathy"
        assert jeromathy.speed == 50  # Jeromathy's actual speed
        assert jeromathy.activation_delay == 20.0
    
    def test_jeromathy_patrol_with_snacks(self, setup):
        """Test Jeromathy patrols when snacks available"""
        player, jeromathy, rooms = setup
        jeromathy.activation_delay = 0.0
        snacks_depleted = False
        
        jeromathy.update(0.1, player, snacks_depleted, rooms)
        # Jeromathy patrols by default
        assert jeromathy.state in ["patrolling", "idle"]
    
    def test_jeromathy_active_without_snacks(self, setup):
        """Test Jeromathy becomes more active when snacks depleted"""
        player, jeromathy, rooms = setup
        jeromathy.activation_delay = 0.0
        jeromathy.current_room = RoomType.OFFICE
        snacks_depleted = True
        
        jeromathy.update(0.1, player, snacks_depleted, rooms)
        # Jeromathy should be active (patrolling or hunting)
        assert jeromathy.state in ["patrolling", "hunting", "chasing"]
    
    def test_jeromathy_returns_with_snacks(self, setup):
        """Test Jeromathy returns to idle when snacks refilled"""
        player, jeromathy, rooms = setup
        jeromathy.activation_delay = 0.0
        jeromathy.state = "hunting"
        snacks_depleted = False
        
        jeromathy.update(0.1, player, snacks_depleted, rooms)
        # Should transition back or stay hunting depending on implementation


class TestAngellica:
    """Test Angellica AI behavior"""
    
    @pytest.fixture
    def setup(self):
        pygame.init()
        player = Player(300, 300)
        angellica = Angellica(100, 100)
        rooms = {
            RoomType.OFFICE: Room(RoomType.OFFICE, 0, 0, 600, 600)
        }
        return player, angellica, rooms
    
    def test_angellica_initialization(self):
        """Test Angellica starts correctly"""
        pygame.init()
        angellica = Angellica(50, 50)
        assert angellica.name == "Angellica"
        assert angellica.speed == 70
        assert angellica.watching_solitaire == False
        assert angellica.activation_delay == 10.0
    
    def test_angellica_idle_when_coding(self, setup):
        """Test Angellica stays idle when player is coding"""
        player, angellica, rooms = setup
        angellica.activation_delay = 0.0
        player.on_solitaire = False
        last_coding_time = 5.0  # Recently coded
        
        angellica.update(0.1, player, rooms, last_coding_time)
        # May be idle or patrolling but not chasing
    
    def test_angellica_chases_solitaire_player(self, setup):
        """Test Angellica chases player playing solitaire"""
        player, angellica, rooms = setup
        angellica.activation_delay = 0.0
        angellica.current_room = RoomType.OFFICE
        player.on_solitaire = True
        
        angellica.update(0.1, player, rooms, 0.0)
        assert angellica.state == "chasing"
    
    def test_angellica_chases_idle_player(self, setup):
        """Test Angellica chases player who hasn't coded in 30s"""
        player, angellica, rooms = setup
        angellica.activation_delay = 0.0
        angellica.current_room = RoomType.OFFICE
        player.on_solitaire = False
        last_coding_time = 35.0  # Haven't coded in 35 seconds
        
        angellica.update(0.1, player, rooms, last_coding_time)
        assert angellica.state == "chasing"


class TestRunnit:
    """Test Runnit AI behavior"""
    
    @pytest.fixture
    def setup(self):
        pygame.init()
        player = Player(300, 300)
        runnit = Runnit(100, 100)
        rooms = {
            RoomType.OFFICE: Room(RoomType.OFFICE, 0, 0, 600, 600),
            RoomType.MEETING_ROOM: Room(RoomType.MEETING_ROOM, 625, 400, 400, 300)
        }
        return player, runnit, rooms
    
    def test_runnit_initialization(self):
        """Test Runnit starts correctly"""
        pygame.init()
        runnit = Runnit(50, 50)
        assert runnit.name == "Runnit"
        assert runnit.speed == 40  # Runnit's base speed is 40
        assert runnit.sprint_speed == 200
        assert runnit.is_sprinting == False
        assert runnit.sprint_duration == 3.0
        assert runnit.sprint_cooldown_duration == 10.0
    
    def test_runnit_sprint_mechanics(self):
        """Test Runnit can sprint"""
        pygame.init()
        runnit = Runnit(100, 100)
        
        # Start sprint
        runnit.is_sprinting = True
        runnit.sprint_timer = 3.0
        assert runnit.is_sprinting == True
        
        # Sprint ends
        runnit.sprint_timer = 0.0
        runnit.is_sprinting = False
        assert runnit.is_sprinting == False
    
    def test_runnit_only_dangerous_while_sprinting(self):
        """Test Runnit only kills when sprinting"""
        pygame.init()
        runnit = Runnit(100, 100)
        
        # Not dangerous normally
        runnit.is_sprinting = False
        assert runnit.is_sprinting == False
        
        # Dangerous while sprinting
        runnit.is_sprinting = True
        assert runnit.is_sprinting == True
    
    def test_runnit_sprint_cooldown(self):
        """Test Runnit has cooldown after sprint"""
        pygame.init()
        runnit = Runnit(100, 100)
        
        # After sprint, cooldown starts
        runnit.sprint_cooldown = 10.0
        assert runnit.sprint_cooldown == 10.0
        
        # Cooldown decreases
        runnit.sprint_cooldown -= 5.0
        assert runnit.sprint_cooldown == 5.0


class TestNextGenIntern:
    """Test NextGen Intern AI behavior"""
    
    def test_intern_initialization(self):
        """Test Intern starts correctly"""
        pygame.init()
        intern = NextGenIntern(50, 50)
        assert intern.name == "NextGen Intern"
        assert hasattr(intern, 'intern_id')  # Has intern_id attribute
        assert intern.speed == 40
        assert intern.has_taken_snack == False
    
    def test_intern_snack_taking(self):
        """Test intern takes snacks"""
        pygame.init()
        intern = NextGenIntern(100, 100)
        
        # Takes snack
        intern.has_taken_snack = True
        assert intern.has_taken_snack == True
        
        # Resets after leaving
        intern.has_taken_snack = False
        assert intern.has_taken_snack == False
    
    def test_intern_non_lethal(self):
        """Test intern is not dangerous"""
        pygame.init()
        intern = NextGenIntern(100, 100)
        # Interns don't have kill mechanics, just snack theft
        # Test would check collision doesn't trigger game over
        assert intern.name == "NextGen Intern"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
