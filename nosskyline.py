#!/usr/bin/python3

import pygame
import math
import random
import time
import sys

pygame.init()

version_number = 0.1

window_x = 700
window_y = 500
max_stars = (window_x * window_y) / 350
size = (window_x, window_y)
screen = pygame.display.set_mode(size)

star_colors = [
    ( 255, 255, 255),
    ( 255, 255, 255),
    ( 255, 255, 255),
    ( 255, 255, 255),
    ( 171, 252, 240), # cyan
    ( 252, 247, 156), # yellow
    ( 227, 237,  35), # d yellow
    ( 100, 179, 252), # l blue
    (  18, 112, 201), # d blue
]

# Define some colors
BLACK    = (   0,   0,   0)
GRAY     = (  50,  50,  50)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)
YELLOW   = ( 252, 252,  10)



meteoroid = None
star_flicker = False # stars will flicker between all star colors if true

stars = []

offices = []

flashers = True

buildings = []
building_min = 6#4
building_max = 12#10
building_max_height = int(window_y * .7)
building_min_height = int(window_y * .1)
building_max_width = int(window_x * .15)
building_min_width = int(window_x * .1)
building_max_overlap = 30 # unused

def makeMeteoroid(sleeptime=0):
    meteoroid = {
        'coords':[
            random.randint(0, window_x),
            0, 
            3, 
            3
        ],
        'sleeptime':sleeptime if sleeptime else random.randint(20, 360),
        'direction':random.choice(['left','right']),
        'angle':random.randint(0, 10)
    }
    return meteoroid

def makeBuilding(position_x=0):
    height             = random.randint( building_min_height, building_max_height)
    width              = random.randint( building_min_width, building_max_width)
    window_height      = random.randint( 3, 6)
    window_width       = random.randint( 2, 4)
    border_width       = random.randint( 2, 4)
    window_spacing_x   = random.randint( 4, 8)
    window_spacing_y   = random.randint( 4, 12)
    

    if window_width >= window_height: window_width = window_height-1 # windows wider than they are high look derpy

    office_grid = []
    for yloop in range( height):
        if yloop % ( window_height+window_spacing_y): continue

        for xloop in range(width):
            if xloop % ( window_width+window_spacing_x): continue
            office_grid.append( ( xloop+position_x, window_y-yloop, window_width, window_height))

    return {
        "height":          height,
        "width":           width,
        "offices_dark":    office_grid,
        "offices_light":   [],
        "window_height":   window_height,
        "window_width":    window_width,
        "position_x":      position_x,
        "color":           BLACK, # for debugging
        "max_population":  int(len(office_grid) * random.randint( 50, 90) * .01)
    }

#####
# build all the buildings
more_buildings = True # keep building more buildings while this is true
skyline_filled = False # building maker won't stop until the skyline is filled horizontally
extra_buildings_threshold = 9 # The higher it is, the more likely to add extra buildings in front of existing ones after the skyline is filled
while more_buildings:
    if not buildings:
        position_x = 0
    else:
        last = buildings[-1]
        position_x = last['position_x'] + ( last['width'] + random.randint( 
            0-int(last['width']*.25),
            int(last['width'])
            ))

    if position_x > window_x:
        skyline_filled=True
    if skyline_filled:
        if random.randint(1, 10) > extra_buildings_threshold:
            more_buildings = False
        extra_buildings_threshold -= 1
        position_x = random.randint(0, int(window_x*.25))
    buildings.append( makeBuilding(position_x))
# build all the buildings
#####

#####
# find tallest building and add a flasher
if flashers:
    tallest = None
    for b in buildings:
        if not tallest or b['height'] > tallest['height']:
            tallest = b
    tallest['flasher'] = {
        'on':0,
        'coords':( int(tallest['position_x']+int(tallest['width']*.5)), window_y-tallest['height']-10, 4, 4)
    }
# find tallest building and add a flasher
#####

pygame.display.set_caption( "Nostalgia Skyline v%s" % version_number)

# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            print("Goodbye!")
            done = True # Flag that we are done so we exit this loop
        elif event.type == pygame.KEYDOWN: print( 'key down!')
        elif event.type == pygame.KEYUP: print( 'key up.')
        elif event.type == pygame.MOUSEBUTTONDOWN: print( 'mouse clickdown')
        elif event.type == pygame.MOUSEBUTTONUP: print( 'mouse uparoo.')
 
    # --- Game logic should go here
 
    # --- Drawing code should go here

    screen.fill(BLACK)


    #####
    # add stars
    star_x = random.randint(0, window_x)
    star_y = random.randint(0, window_y)
    star = {
        'coords': [star_x, star_y, 1, 1],
        'color': random.choice(star_colors)
    }
    stars.append(star)
    for star in stars:
        color = random.choice(star_colors) if star_flicker else star['color']
        pygame.draw.rect(screen, color, star['coords'])
    # add stars
    #####

    #####
    # shooting stars
    if not meteoroid:
        meteoroid = makeMeteoroid()
    if meteoroid['sleeptime']:
        meteoroid['sleeptime'] -= 1
    else:

        pygame.draw.ellipse(screen, WHITE, meteoroid['coords'])
        side = 10 - meteoroid['angle']
        down = 10 - side

        meteoroid['coords'][1] += down*5
        if meteoroid['direction'] == 'right':
            meteoroid['coords'][0] += side*5
        else:
            meteoroid['coords'][0] -= side*5
        if meteoroid['coords'][1] > window_y or meteoroid['coords'][0] > window_x or meteoroid['coords'][0] < 0:
            meteoroid = None#makeMeteoroid(sleeptime=random.randint(20,150))
    # shooting stars
    #####

    #####
    # buildings
    for b in buildings:
        pygame.draw.rect(screen, b['color'], [ b['position_x'], window_y, b['width'], -(b['height']) ])

        #####
        # flashers
        if 'flasher' in b:
            if b['flasher']['on'] > 0:
                pygame.draw.ellipse( screen, RED, b['flasher']['coords'])
            b['flasher']['on'] += 1
            if b['flasher']['on'] >= 40:
                b['flasher']['on'] = -40
        # flashers
        #####

        for o in b['offices_light']:
            pygame.draw.rect(screen, YELLOW, o)

        if len( b['offices_light']) > b['max_population']-1:
            if random.randint(1, 10) > 1: continue

        #####
        # add offices
        if b['offices_dark'] and random.randint(1,10) > 5:
            office = random.choice(b['offices_dark'])
            b['offices_dark'].remove(office)
            b['offices_light'].append(office)
        # add offices
        #####

        #####
        # remove offices
        if len(b['offices_light']) > b['max_population']:
            rando = random.choice(b['offices_light'])
            b['offices_light'].remove(rando)
            b['offices_dark'].append(rando)
        # remove offices
        #####

    # buildings
    #####

    if len(stars) > max_stars:
        stars.remove(random.choice(stars))

    # --- Go ahead and update the screen with what we've drawn.
    # pygame.display.flip()
    pygame.display.update()
 
    # --- Limit FPS
    clock.tick(30)

# Close the window and quit.
pygame.quit()
