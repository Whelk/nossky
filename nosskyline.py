#!/usr/bin/python3

import pygame
import random

pygame.init()

version_number = 1.0

quit_message = "Quitting Nostalgia Skyline. See you next time!"

class Settings():
    infoObject = pygame.display.Info()
    window_x_max = infoObject.current_w
    window_y_max = infoObject.current_h
    window_x = 700
    window_y = 500
    max_stars = (window_x * window_y) / 350
    star_flicker = False # stars will flicker between all star colors if true (it wasn't a bug, it was a feature)
    flashers = True # do you want the tallest building to have a blinking flasher light up top?
    fullscreen = False

class Skyline():
    stars = []
    buildings = []
    meteoroid = None

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

def behindBuilding(x,y):
    for b in Skyline.buildings:
        if x in range(b['position_x'], b['position_x']+b['width']):
            if y in range(Settings.window_y-b['height'], Settings.window_y):
                return True

def makeMeteoroid(sleeptime=0):
    meteoroid = {
        'coords':[
            random.randint(0, Settings.window_x),
            0,
            3,
            3
        ],
        'sleeptime':sleeptime if sleeptime else random.randint(20, 360),
        'direction':random.choice(['left','right']),
        'angle':random.randint(3,7)
    }
    return meteoroid

def makeBuilding(position_x=0):

    building_max_height = int(Settings.window_y * .7)
    building_min_height = int(Settings.window_y * .1)
    building_max_width  = 200 if Settings.fullscreen else int(Settings.window_x * .15)
    building_min_width  = 50 if Settings.fullscreen else int(Settings.window_x * .1)

    height              = random.randint( building_min_height, building_max_height)
    width               = random.randint( building_min_width, building_max_width)
    window_height       = random.randint( 3, 6)
    window_width        = random.randint( 2, 4)
    border_width        = random.randint( 2, 4)
    window_spacing_x    = random.randint( 4, 8)
    window_spacing_y    = random.randint( 4, 12)

    if Skyline.buildings and height in range( Skyline.buildings[-1]['height']-20, Skyline.buildings[-1]['height']+20):
        height = int(Skyline.buildings[-1]['height'] * .5) # avoid buildings of extremely similar height next to one another

    if window_width >= window_height: window_width = window_height-1 # windows wider than they are high look derpy

    office_grid = []
    for yloop in range( height):
        if yloop % ( window_height+window_spacing_y): continue

        for xloop in range(width):
            if xloop % ( window_width+window_spacing_x): continue
            if behindBuilding(xloop+position_x, Settings.window_y-yloop): continue
            office_grid.append( ( xloop+position_x, Settings.window_y-yloop, window_width, window_height))

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

def setScreen(fullscreen=False):
    global screen
    if not fullscreen:
        screen = pygame.display.set_mode( ( Settings.window_x, Settings.window_y))
    else:
        screen = pygame.display.set_mode(( Settings.window_x, Settings.window_y), pygame.FULLSCREEN)
    screen.fill(BLACK)



def buildingSetup():
    #####
    # build all the buildings
    more_buildings = True # keep building more buildings while this is true
    skyline_filled = False # building maker won't stop until the skyline is filled horizontally
    extra_buildings_threshold = 9 # The higher it is, the more likely to add extra buildings in front of existing ones after the skyline is filled
    while more_buildings:
        if not Skyline.buildings:
            position_x = 0
        else:
            last = Skyline.buildings[-1]
            position_x = last['position_x'] + ( last['width'] + random.randint(
                -20, 10)
                )

        if position_x > Settings.window_x:
            skyline_filled=True
        if skyline_filled:
            # if random.randint(1, 10) > extra_buildings_threshold:
                more_buildings = False
            # extra_buildings_threshold -= 1
            # position_x = random.randint(0, int(Settings.window_x*.25))
        Skyline.buildings.append( makeBuilding(position_x))
    # build all the buildings
    #####

    for b in Skyline.buildings:
        b['surface'] = pygame.Surface((b['width'], b['height']))
        b['surface'].fill(b['color'])
        global screen
        screen.blit(b['surface'], ( b['position_x'], Settings.window_y-b['height']))

    #####
    # find tallest building and add a flasher
    if Settings.flashers:
        tallest = None
        for b in Skyline.buildings:
            if (b['position_x'] + (b['width']*.5)) > Settings.window_x:
                continue
            if not tallest or b['height'] > tallest['height']:
                tallest = b
        tallest['flasher'] = {
            'on':0,
            'coords':( int(tallest['position_x']+int(tallest['width']*.5))-2, Settings.window_y-tallest['height']-10, 4, 4)
        }
    # find tallest building and add a flasher
    #####

setScreen()
buildingSetup()

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
            print(quit_message)
            done = True # Flag that we are done so we exit this loop
        elif event.type == pygame.KEYDOWN:
            #####
            # fullscreen toggle
            if event.key == pygame.K_f:
                if Settings.fullscreen:
                    print("Windowed mode.")
                    Settings.fullscreen = False
                    Settings.window_x = 700
                    Settings.window_y = 500
                    setScreen()
                else:
                    print("Fullscreen mode.")
                    Settings.fullscreen = True
                    Settings.window_x = Settings.window_x_max
                    Settings.window_y = Settings.window_y_max
                    setScreen(fullscreen=True)

                Skyline.buildings = []
                Skyline.stars = []
                buildingSetup()
            # fullscreen toggle
            ####
            elif event.key == pygame.K_r:
                print("Resetting skyline.")
                setScreen(fullscreen=Settings.fullscreen)
                Skyline.buildings = []
                Skyline.stars = []
                buildingSetup()
            elif event.key == pygame.K_q:
                done = True
                print(quit_message)

        elif event.type == pygame.KEYUP: pass
        elif event.type == pygame.MOUSEBUTTONDOWN: pass
        elif event.type == pygame.MOUSEBUTTONUP: pass

    #####
    # add stars
    found_good_spot = False
    while not found_good_spot:
        star_x = random.randint(0, Settings.window_x)
        star_y = random.randint(0, Settings.window_y)
        if not behindBuilding(star_x, star_y):
            found_good_spot = True
    star = {
        'coords': [star_x, star_y, 1, 1],
        'color': random.choice(star_colors)
    }
    Skyline.stars.append(star)
    pygame.draw.rect(screen, star['color'], star['coords'])
    # add stars
    #####

    #####
    # remove stars
    if len(Skyline.stars) > Settings.max_stars:
        remove_star = random.choice(Skyline.stars)
        Skyline.stars.remove(remove_star)
        pygame.draw.rect(screen, BLACK, remove_star['coords'])
    # remove stars
    #####

    #####
    # shooting stars
    if not Skyline.meteoroid:
        Skyline.meteoroid = makeMeteoroid()
    if Skyline.meteoroid['sleeptime']:
        Skyline.meteoroid['sleeptime'] -= 1
    else:
        pygame.draw.ellipse(screen, BLACK, Skyline.meteoroid['coords'])
        side = 10 - Skyline.meteoroid['angle']
        down = 10 - side
        Skyline.meteoroid['coords'][1] += down*5
        if Skyline.meteoroid['direction'] == 'right':
            Skyline.meteoroid['coords'][0] += side*5
        else:
            Skyline.meteoroid['coords'][0] -= side*5

        if not behindBuilding(Skyline.meteoroid['coords'][0], Skyline.meteoroid['coords'][1]):
            pygame.draw.ellipse(screen, WHITE, Skyline.meteoroid['coords'])

        if Skyline.meteoroid['coords'][1] > Settings.window_y or Skyline.meteoroid['coords'][0] > Settings.window_x or Skyline.meteoroid['coords'][0] < 0:
            Skyline.meteoroid = None
    # shooting stars
    #####

    #####
    # buildings
    for b in Skyline.buildings:
        #####
        # flashers
        if 'flasher' in b:
            if b['flasher']['on'] == 1:
                pygame.draw.ellipse( screen, RED, b['flasher']['coords'])
            b['flasher']['on'] += 1
            if b['flasher']['on'] >= 40:
                pygame.draw.ellipse( screen, BLACK, b['flasher']['coords'])
                b['flasher']['on'] = -40
        # flashers
        #####

        if len( b['offices_light']) > b['max_population']-1:
            if random.randint(1, 10) > 1: continue

        #####
        # add offices
        if b['offices_dark'] and random.randint(1,10) > 5:
            office = random.choice(b['offices_dark'])
            b['offices_dark'].remove(office)
            b['offices_light'].append(office)
            pygame.draw.rect(screen, YELLOW, office)
        # add offices
        #####

        #####
        # remove offices
        if len(b['offices_light']) > b['max_population']:
            office = random.choice(b['offices_light'])
            b['offices_light'].remove(office)
            b['offices_dark'].append(office)
            pygame.draw.rect(screen, BLACK, office)
        # remove offices
        #####

    # buildings
    #####

    pygame.display.update()

    # --- Limit FPS
    clock.tick(30)

# Close the window and quit.
pygame.quit()
