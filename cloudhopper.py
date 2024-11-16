import pgzrun
import pygame
import random
import time

# Constants
NAME="NOAH"
WIDTH = 800
HEIGHT = 600
PLAYER_GRAVITY = 1
PLAYER_JUMP_STRENGTH = 15
PLATFORM_SPEED = 5
transitioning = False
transition_step = 0
loaded = False
anups = 0
keycount = 0

ldisplay = Actor('1')
ldisplay.x = 50
ldisplay.y = 50
ldisplay._surf = pygame.transform.scale(ldisplay._surf, (200, 80))

bgcloud = Actor('bgcloud')
bgcloud.x = -300
bgcloud.y = 100
bgcloud._surf = pygame.transform.scale(bgcloud._surf, (96, 48))
bgcloud2 = Actor('bgcloud')
bgcloud2.x = -200
bgcloud2.y = 400
bgcloud2._surf = pygame.transform.scale(bgcloud2._surf, (96, 48))

# Game Objects
player = Actor('guy')  # Replace with (image: player)
player.x = 50
player.y = HEIGHT - 100
player.vel_y = 0
player.on_ground = False
level = 1

portal = Actor('portaldark')
portal.x = 750
portal.y = 320

b1 = Actor('blackscreen1')
b1.x = -1300
b1.y = 100
b2 = Actor('blackscreen2')
b2.x = -1000
b2.y = 300
b3 = Actor('blackscreen3')
b3.x = -800
b3.y = 500

keydisplay = Actor('nokeys')
keydisplay.x = 710
keydisplay.y = 560

# Platforms by level
platforms = {
    1: [(50, 550), (120, 550), (190, 550), (280, 460), (350, 460), (420, 460), \
        (510, 370), (680, 370), (750, 370)],
    2: [(50, 550), (120, 470), (190, 390), (120, 310), (190, 230), (260, 230), \
        (470, 550), (540, 550), (610, 510), (680, 470), (750, 430)],  # Future levels can be added here
    3: [(750, 100), (540, 140), (470, 380), (330, 140), (120, 140), (680, 380)],
    4: [(50, 550)],
}

portals = [(0, 0), (0, 0), (750, 380), (400, 400), (400, 300)]
guys = [(0, 0), (50, 500), (50, 500), (750, 50), (50, 500)]
keys = {
    1: [(120, 520), (350, 430), (600, 260)],
    2: [(120, 440), (260, 200), (460, 380)],
    3: [(120, 110), (150, 110), (470, 340)],
    4: [(50, 550)],
}
spikes = {
    1: [(600, 550)],
    2: [],
    3: [],
    4: [],
}
pads = {
    1: [(500, 400)],
    2: [],
    3: [],
    4: [],
}

# Create platform actors for a given level
def create_platforms(level):
    if level not in platforms:
        print(f"Error: Level {level} does not exist.")
        return []
    
    return [create_platform(x, y) for x, y in platforms[level]]

def create_keys(level):
    if level not in keys:
        print(f"Error: Level {level} does not exist.")
        return []
    
    return [create_key(x, y) for x, y in keys[level]]

def create_spikes(level):
    if level not in spikes:
        print(f"Error: Level {level} does not exist.")
        return []
    
    return [create_spike(x, y) for x, y in spikes[level]]

def create_pads(level):
    if level not in pads:
        print(f"Error: Level {level} does not exist.")
        return []
    
    return [create_pad(x, y) for x, y in pads[level]]

def create_platform(x, y):
    platform = Actor('cloud')
    platform.x = x
    platform.y = y
    return platform

def create_key(x, y):
    key = Actor('key')
    key.x = x
    key.y = y
    return key

def create_spike(x, y):
    spike = Actor('spike')
    spike.x = x
    spike.y = y
    return spike

def create_pad(x, y):
    pad = Actor('bouncepad')
    pad.x = x
    pad.y = y
    return pad

# Initialize platforms for current level
current_platforms = create_platforms(1)
current_keys = create_keys(1)
current_spikes = create_spikes(1)
current_pads = create_pads(1)

def next_level():
    global level
    global current_platforms
    global current_keys
    global current_spikes
    global current_pads
    global transitioning
    global transition_step
    global keycount
    
    transitioning = True  # Start the transition
    transition_step = 0  # Reset the step

def update():
    global transitioning
    global transition_step
    global current_platforms
    global current_keys
    global current_spikes
    global current_pads
    global level
    global loaded
    global anups
    global keycount

    # Do transition effect
    if transitioning:
        if transition_step == 0:
            pygame.mixer.init()
            pygame.mixer.music.load('Music/transition.wav')
            pygame.mixer.music.play()
            transition_step += 1
        elif 1 <= transition_step <= 60:
            b1.x += 30
            b2.x += 25
            b3.x += 20
            transition_step += 1
            if transition_step == 60:
                if not loaded:
                    pygame.mixer.music.load('Music/transitionback.wav')
                    pygame.mixer.music.play()
                    level += 1
                    loaded = True
                    portal.pos = portals[level]
                    portal.angle = 0
                    portal.image = 'portaldark'
                    player.pos = guys[level]
                    current_platforms = create_platforms(level)
                    current_keys = create_keys(level)
                    current_spikes = create_spikes(level)
                    current_pads = create_pads(level)
                    ldisplay.image = '%s' % (level)
                    ldisplay._surf = pygame.transform.scale(ldisplay._surf, (150, 80))
                    keycount = 0
                    keydisplay.image = 'nokeys'
        elif 61 <= transition_step <= 122:
            b1.x -= 30
            b2.x -= 25
            b3.x -= 20
            transition_step += 1
        elif transition_step > 122:
            # Reset transition for the next use
            transition_step = 0
            transitioning = False
            loaded = False  # Reset loaded state for next transition
    
    # Player gravity       
    if not transitioning:
        player.vel_y += PLAYER_GRAVITY
        player.y += player.vel_y
    
    # Collision with platforms
    player.on_ground = False
    for platform in current_platforms:
        if player.colliderect(platform) and player.y < platform.y:
            player.y = platform.y - player.height
            player.vel_y = 0
            player.on_ground = True
            break
        if player.colliderect(platform) and player.y >= platform.y:
            player.vel_y = 3
            break

    # Keep the player in bounds
    if player.y > HEIGHT:
        pygame.mixer.init()
        pygame.mixer.music.load('Music/die.wav')
        pygame.mixer.music.play()
        reset_player()

    # Check for inputs
    if not transitioning:
        if keyboard.right:
            player.x += 5
        if keyboard.left:
            player.x -= 5
        if keyboard.up and player.on_ground:
            player.vel_y -= PLAYER_JUMP_STRENGTH
        if keyboard.r:
            reset_player()

    # Animate portal and keys
        if anups == 30:
            for key in current_keys:
                key.y -= 4
            for spike in current_spikes:
                spike.image = 'spikedark'
        if anups == 60:
            for key in current_keys:
                key.y += 4
            for spike in current_spikes:
                spike.image = 'spike'
            anups = 0
        if keycount == 3:
            portal.image = 'portal'
            portal.angle += 2.5

    # Check collision with keys, portal and spikes
        if player.colliderect(portal) and not transitioning and keycount > 2:
            next_level()
        for key in current_keys:
            if player.colliderect(key):
                pygame.mixer.music.load('Music/keycollect.wav')
                pygame.mixer.music.play()
                key.x = -600
                key.y = -600
                keycount += 1
        for spike in current_spikes:
            if player.colliderect(spike):
                pygame.mixer.music.load('Music/die.wav')
                pygame.mixer.music.play()
                reset_player()

        for pad in current_pads:
            if player.colliderect(pad):
                pygame.mixer.music.load('Music/bounce.wav')
                pygame.mixer.music.play()
                player.vel_y = -25

        if keycount == 0:
            keydisplay.image = 'nokeys'
        elif keycount == 1:
            keydisplay.image = 'onekey'
        elif keycount == 2:
            keydisplay.image = 'twokeys'
        else:
            keydisplay.image = 'threekeys'

    anups += 1
    bgcloud.x += 1
    bgcloud2.x += 1
    if bgcloud.x > 900:
        bgcloud.x = random.randint(-200, -100)
        bgcloud.y = random.randint(50, 250)
    if bgcloud2.x > 900:
        bgcloud2.x = random.randint(-400, -300)
        bgcloud2.y = random.randint(350, 550)

def reset_player():
    """Reset player to starting position."""
    global level
    global keycount
    player.pos = guys[level]
    player.vel_y = 0
    keycount = 0
    portal.angle = 0
    portal.image = 'portaldark'
    for key, (x, y) in zip(current_keys, keys[level]):
        key.pos = (x, y)

def draw():
    """Draw all game objects."""
    screen.clear()
    screen.blit('sky', (0, 0))
    bgcloud.draw()
    ldisplay.draw()
    keydisplay.draw()
    for spike in current_spikes:
        spike.draw()
    for platform in current_platforms:
        platform.draw()
    for key in current_keys:
        key.draw()
    for pad in current_pads:
        pad.draw()
    portal.draw()
    player.draw()
    b1.draw()
    b2.draw()
    b3.draw()

# Run the game
pgzrun.go()
