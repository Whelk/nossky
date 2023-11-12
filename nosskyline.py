#!/usr/bin/python
"""
Randomly generate a starry skyline with tall office buildings.
Watch the stars twinkle and the office windows blink on and off
as the occupants go about doing whatever it is they're doing.
"""

import random
import sys
import os
import pygame
import pygame.freetype

pygame.init()

os.chdir(sys.path[0])

GAME_FONT = pygame.freetype.Font(None, 12)

VERSION = 1.0

QUIT_MESSAGE = "Quitting Nostalgia skyline. See you next time!"

infoObject = pygame.display.Info()


class Skyline:
    screen = None
    window_x = 700
    window_y = 500
    window_x_max = infoObject.current_w
    window_y_max = infoObject.current_h
    stars = []
    max_stars = (window_x * window_y) / 350
    buildings = []
    meteoroid = None
    flashers = True  # do you want the tallest building to have a blinking flasher light up top?
    fullscreen = False
    display_message = None

    tunes = os.listdir("tunes")
    for t in tunes:
        if t[-4:].lower() not in [".mp3", ".ogg"]:
            tunes.remove(t)
    current_tune = (
        pygame.mixer.music.load("tunes/%s" % random.choice(tunes)) if tunes else None
    )
    play_tunes = False


skyline = Skyline()


def display_message(message, display_time=75, print_msg=True):
    """
    Add a message to be displayed on-screen.
    """
    if print_msg:
        print(message)
    skyline.display_message = {
        "message": message,
        "display_time": display_time,
        "displayed": False,
    }


KEYS_MESSAGE = "f: toggle fullscreen, m: toggle music, q: quit, r: reset skyline"
display_message(KEYS_MESSAGE, display_time=200)

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg in ["-f", "--fullscreen"]:
            skyline.fullscreen = True
            print("Starting in fullscreen mode.")
        elif arg in ["-m", "--music"]:
            skyline.play_tunes = True
            if skyline.tunes:
                print("Starting with music on.")
                pygame.mixer.music.play(-1)
            else:
                print("No musicfiles in /tunes directory!")
        else:
            print("Invalid argument: %s" % arg)

star_colors = [
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (171, 252, 240),  # cyan
    (252, 247, 156),  # yellow
    (227, 237, 35),  # d yellow
    (100, 179, 252),  # l blue
    (18, 112, 201),  # d blue
]

# Define some colors
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (252, 252, 10)


def behind_building(coord_x, coord_y):
    """
    Check if the specified coordinates are already occupied by a buliding.
    """
    for building in skyline.buildings:
        if coord_x in range(
            building["position_x"], building["position_x"] + building["width"]
        ):
            if coord_y in range(
                skyline.window_y - building["height"], skyline.window_y
            ):
                return True
    return False


def make_meteoroid(sleeptime=0):
    """
    Set up a meteoroid to zip across the sky.
    """
    meteoroid = {
        "coords": [random.randint(0, skyline.window_x), 0, 3, 3],
        "sleeptime": sleeptime
        if sleeptime
        else random.randint(
            20, 360
        ),  # time until next meteoroid after this one goes offscreen
        "direction": random.choice(["left", "right"]),
        "angle": random.randint(3, 7),
    }
    return meteoroid


def make_building(position_x=0):
    """
    Set up the properties of buildings to populate our starry skyline.
    """
    building_max_height = int(skyline.window_y * 0.7)
    building_min_height = int(skyline.window_y * 0.1)
    building_max_width = 200 if skyline.fullscreen else int(skyline.window_x * 0.15)
    building_min_width = 50 if skyline.fullscreen else int(skyline.window_x * 0.1)

    height = random.randint(building_min_height, building_max_height)
    width = random.randint(building_min_width, building_max_width)
    window_width_min = 2
    window_height_min = 3
    window_height = random.randint(window_height_min, 6)
    window_width = random.randint(window_width_min, 4)
    window_spacing_x = random.randint(4, 8)
    window_spacing_y = random.randint(4, 12)

    if skyline.buildings:
        previous_building = skyline.buildings[-1]
        # avoid buildings of extremely similar height next to one another
        if height in range(
            previous_building["height"] - 20, previous_building["height"] + 20
        ):
            height = int(previous_building["height"] * 0.5)
        # avoid buildings with exact same window sizes next to one another
        if (window_width, window_height) == (
            previous_building["window_width"],
            previous_building["window_height"],
        ):
            if window_width > window_width_min:
                window_width = window_width_min
            elif window_height > window_height_min:
                window_height = window_width_min
            else:
                window_height += 1

    if window_width >= window_height:
        window_width = window_height - 1  # windows wider than they are high look derpy

    office_grid = []
    for yloop in range(height):
        if yloop % (window_height + window_spacing_y):
            continue

        for xloop in range(width):
            if xloop % (window_width + window_spacing_x):
                continue
            if behind_building(xloop + position_x, skyline.window_y - yloop):
                continue
            office_grid.append(
                (
                    xloop + position_x,
                    skyline.window_y - yloop,
                    window_width,
                    window_height,
                )
            )

    return {
        "height": height,
        "width": width,
        "offices_dark": office_grid,
        "offices_light": [],
        "window_height": window_height,
        "window_width": window_width,
        "position_x": position_x,
        "color": BLACK,  # for debugging
        "max_population": int(len(office_grid) * random.randint(50, 90) * 0.01),
    }


def set_screen(fullscreen=False):
    """
    Set the display screen.
    """
    if fullscreen:
        pygame.mouse.set_visible(False)
        fullscreen = pygame.FULLSCREEN
        skyline.window_x = skyline.window_x_max
        skyline.window_y = skyline.window_y_max
    else:
        pygame.mouse.set_visible(True)
    skyline.screen = pygame.display.set_mode(
        (skyline.window_x, skyline.window_y), fullscreen
    )
    skyline.screen.fill(BLACK)


def building_setup():
    """
    Take all the buildings and draw them on the skyline.
    """
    #####
    # build all the buildings
    more_buildings = True  # keep building more buildings while this is true
    skyline_filled = (
        False  # building maker won't stop until the skyline is filled horizontally
    )
    while more_buildings:
        if not skyline.buildings:
            position_x = 0
        else:
            last = skyline.buildings[-1]
            position_x = last["position_x"] + (last["width"] + random.randint(-20, 10))

        if position_x > skyline.window_x:
            skyline_filled = True
        if skyline_filled:
            more_buildings = False
        skyline.buildings.append(make_building(position_x))
    # build all the buildings
    #####

    for b in skyline.buildings:
        b["surface"] = pygame.Surface((b["width"], b["height"]))
        b["surface"].fill(b["color"])
        skyline.screen.blit(
            b["surface"], (b["position_x"], skyline.window_y - b["height"])
        )

    #####
    # find tallest building and add a flasher
    if skyline.flashers:
        tallest = {}
        for b in skyline.buildings:
            if (b["position_x"] + (b["width"] * 0.5)) > skyline.window_x:
                continue
            if not tallest or b["height"] > tallest["height"]:
                tallest = b
        tallest["flasher"] = {
            "on": 0,
            "coords": (
                int(tallest["position_x"] + int(tallest["width"] * 0.5)) - 2,
                skyline.window_y - tallest["height"] - 10,
                4,
                4,
            ),
        }
    # find tallest building and add a flasher
    #####


set_screen(fullscreen=skyline.fullscreen)
building_setup()

pygame.display.set_caption("Nostalgia Skyline v%s" % VERSION)

# Loop until the user clicks the close button.
program_done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# -------- Main Program Loop -----------
while not program_done:
    # --- Main event loop
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            display_message(QUIT_MESSAGE)
            program_done = True  # Flag that we are done so we exit this loop
        elif event.type == pygame.KEYDOWN:
            # --- fullscreen toggle
            if event.key == pygame.K_f:
                if skyline.fullscreen:
                    display_message("Windowed mode.")
                    skyline.fullscreen = False
                    skyline.window_x = 700
                    skyline.window_y = 500
                else:
                    display_message("Fullscreen mode.")
                    skyline.fullscreen = True
                    skyline.window_x = skyline.window_x_max
                    skyline.window_y = skyline.window_y_max
                set_screen(fullscreen=skyline.fullscreen)

                skyline.buildings = []
                skyline.stars = []
                building_setup()
            # --- reset skyline
            elif event.key == pygame.K_r:
                display_message("Resetting skyline.")
                set_screen(fullscreen=skyline.fullscreen)
                skyline.buildings = []
                skyline.stars = []
                building_setup()
            # --- music toggle
            elif event.key == pygame.K_m:
                if not skyline.tunes:
                    display_message("No musicfiles in /tunes directory!")
                elif skyline.play_tunes:
                    display_message("Music off.")
                    pygame.mixer.music.stop()
                    skyline.play_tunes = False
                else:
                    display_message("Music on.")
                    pygame.mixer.music.play(-1)
                    skyline.play_tunes = True
            # --- quit
            elif event.key == pygame.K_q:
                program_done = True
                display_message(QUIT_MESSAGE)
            else:
                display_message(KEYS_MESSAGE, display_time=200)

    #####
    # add stars
    found_good_spot = False
    while not found_good_spot:
        star_x = random.randint(0, skyline.window_x)
        star_y = random.randint(0, skyline.window_y)
        if not behind_building(star_x, star_y):
            found_good_spot = True
    star = {"coords": [star_x, star_y, 1, 1], "color": random.choice(star_colors)}
    skyline.stars.append(star)
    pygame.draw.rect(skyline.screen, star["color"], star["coords"])
    # add stars
    #####

    #####
    # remove stars
    if len(skyline.stars) > skyline.max_stars:
        remove_star = random.choice(skyline.stars)
        skyline.stars.remove(remove_star)
        pygame.draw.rect(skyline.screen, BLACK, remove_star["coords"])
    # remove stars
    #####

    #####
    # shooting stars
    if not skyline.meteoroid:
        skyline.meteoroid = make_meteoroid()
    if skyline.meteoroid["sleeptime"]:
        skyline.meteoroid["sleeptime"] -= 1
    else:
        pygame.draw.ellipse(skyline.screen, BLACK, skyline.meteoroid["coords"])
        side = 10 - skyline.meteoroid["angle"]
        down = 10 - side
        skyline.meteoroid["coords"][1] += down * 5
        if skyline.meteoroid["direction"] == "right":
            skyline.meteoroid["coords"][0] += side * 5
        else:
            skyline.meteoroid["coords"][0] -= side * 5

        if not behind_building(
            skyline.meteoroid["coords"][0], skyline.meteoroid["coords"][1]
        ):
            pygame.draw.ellipse(skyline.screen, WHITE, skyline.meteoroid["coords"])

        if (
            skyline.meteoroid["coords"][1] > skyline.window_y
            or skyline.meteoroid["coords"][0] > skyline.window_x
            or skyline.meteoroid["coords"][0] < 0
        ):
            skyline.meteoroid = None
    # shooting stars
    #####

    #####
    # buildings
    for bldg in skyline.buildings:
        #####
        # flashers
        if "flasher" in bldg:
            if bldg["flasher"]["on"] == 1:
                pygame.draw.ellipse(skyline.screen, RED, bldg["flasher"]["coords"])
            bldg["flasher"]["on"] += 1
            if bldg["flasher"]["on"] >= 40:
                pygame.draw.ellipse(skyline.screen, BLACK, bldg["flasher"]["coords"])
                bldg["flasher"]["on"] = -40
        # flashers
        #####

        if (
            len(bldg["offices_light"]) > bldg["max_population"] - 1
            and random.randint(1, 10) > 1
        ):
            continue

        #####
        # add offices
        if bldg["offices_dark"] and random.randint(1, 10) > 5:
            office = random.choice(bldg["offices_dark"])
            bldg["offices_dark"].remove(office)
            bldg["offices_light"].append(office)
            pygame.draw.rect(skyline.screen, YELLOW, office)
        # add offices
        #####

        #####
        # remove offices
        if len(bldg["offices_light"]) > bldg["max_population"]:
            office = random.choice(bldg["offices_light"])
            bldg["offices_light"].remove(office)
            bldg["offices_dark"].append(office)
            pygame.draw.rect(skyline.screen, BLACK, office)
        # remove offices
        #####

    # buildings
    #####

    if skyline.display_message:
        pygame.draw.rect(skyline.screen, BLACK, (10, 10, skyline.window_x, 15))
        GAME_FONT.render_to(
            skyline.screen,
            (10, 10),
            skyline.display_message["message"],
            (255, 255, 255),
        )
        skyline.display_message["display_time"] -= 1
        if skyline.display_message["display_time"] < 1:
            skyline.display_message = None
            pygame.draw.rect(skyline.screen, BLACK, (10, 10, skyline.window_x, 15))

    pygame.display.update()

    # --- Limit FPS
    clock.tick(30)

# Close the window and quit.
pygame.quit()
