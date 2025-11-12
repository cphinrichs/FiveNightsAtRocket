# Panoramic camera pan using Pygame and break_room.jpg
import pygame
import sys

# Initialize Pygame mixer for sound
pygame.mixer.init()

# Initialize Pygame
pygame.init()

# Set the camera (window) size
CAMERA_WIDTH = 800  # Change as needed
CAMERA_HEIGHT = 600  # Change as needed
screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT))
pygame.display.set_caption('Panoramic Room Camera')


# List of room images
room_images = ['images/break_room.jpg', 'images/hall_one.jpg']
current_room = 0

def load_room_image(index):
	original_image = pygame.image.load(room_images[index])
	original_rect = original_image.get_rect()
	scale_factor = CAMERA_HEIGHT / original_rect.height
	scaled_width = int(original_rect.width * scale_factor)
	scaled_height = CAMERA_HEIGHT
	image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
	image_rect = image.get_rect()
	return image, image_rect

image, image_rect = load_room_image(current_room)

# Load camera pan sound (placeholder)
idle_sound = pygame.mixer.Sound('sounds/idle.mp3')
idle_sound.set_volume(0.5)  # Adjust volume as needed
idle_channel = idle_sound.play(loops=-1)  # Loop indefinitely


# Camera position and direction
camera_x = 0
camera_speed = 2  # Pixels per frame
direction = 1  # 1 for right, -1 for left

# Room box selector properties
room_box_width = 100
room_box_height = 60
room_box_margin = 20
room_box_color = (200, 200, 200)
room_box_hover_color = (255, 255, 0)
room_box_active_color = (100, 200, 255)
font = pygame.font.SysFont(None, 36)

clock = pygame.time.Clock()


running = True
while running:
	mouse_pos = pygame.mouse.get_pos()
	mouse_pressed = pygame.mouse.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			# Room selector boxes
			num_rooms = len(room_images)
			total_width = num_rooms * room_box_width + (num_rooms - 1) * room_box_margin
			start_x = (CAMERA_WIDTH - total_width) // 2
			y = CAMERA_HEIGHT - room_box_height - 20
			for i in range(num_rooms):
				box_rect = pygame.Rect(start_x + i * (room_box_width + room_box_margin), y, room_box_width, room_box_height)
				if box_rect.collidepoint(mouse_pos):
					current_room = i
					image, image_rect = load_room_image(current_room)
					camera_x = 0
					direction = 1
					break

	# Pan camera left and right
	camera_x += camera_speed * direction
	if camera_x + CAMERA_WIDTH >= image_rect.width:
		camera_x = image_rect.width - CAMERA_WIDTH
		direction = -1  # Reverse to left
	elif camera_x <= 0:
		camera_x = 0
		direction = 1  # Reverse to right

	# Draw the current camera view
	screen.blit(image, (0, 0), (camera_x, 0, CAMERA_WIDTH, CAMERA_HEIGHT))


	# Draw room selector boxes at the bottom
	num_rooms = len(room_images)
	total_width = num_rooms * room_box_width + (num_rooms - 1) * room_box_margin
	start_x = (CAMERA_WIDTH - total_width) // 2
	y = CAMERA_HEIGHT - room_box_height - 20
	for i in range(num_rooms):
		box_rect = pygame.Rect(start_x + i * (room_box_width + room_box_margin), y, room_box_width, room_box_height)
		if i == current_room:
			color = room_box_active_color
		elif box_rect.collidepoint(mouse_pos):
			color = room_box_hover_color
		else:
			color = room_box_color
		pygame.draw.rect(screen, color, box_rect)
		label = font.render(f'Room {i+1}', True, (0, 0, 0))
		label_rect = label.get_rect(center=box_rect.center)
		screen.blit(label, label_rect)

	pygame.display.flip()
	clock.tick(60)

pygame.quit()
sys.exit()

# Stop the sound when quitting
if idle_channel:
	idle_channel.stop()
