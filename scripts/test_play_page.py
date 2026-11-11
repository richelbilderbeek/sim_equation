#!/usr/bin/env python3
"""Play the WebAssembly game on the 'Play' page of a built website.

Usage: test_play_page.py <URL of the play page>

Compares what the browser shows to the images of the game:
the game must show up without a title bar, the equation must disappear
over time and clicking must bring it back.
"""
import io
import sys
import time

from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright

GAME_SIZE = (1815, 818)  # width, height, see game_dialog.ui
GIRL_POS = (9, 9)
EQUATION_LABEL = (578, 241, 1228, 461)  # x, y, width, height
START_TIMEOUT_SECS = 60
# The equation disappears with a chance of 1 in 10 per second
EQUATION_TIMEOUT_SECS = 120
MAX_DIFF = 6  # Average difference per color channel, from 0 to 255
MAX_OFFSET = 2  # Pixels, as a screenshot of an element can be a bit bigger
# Ignore the edge of the label, as it has a frame when there is an equation
FRAME_MARGIN = 3


def diff(image_a, image_b):
    """Average difference per color channel between two images."""
    stat = ImageStat.Stat(ImageChops.difference(image_a, image_b))
    return sum(stat.mean) / len(stat.mean)


def find_offset(shot, expected, box):
    """Find where in a screenshot the expected image fits best."""
    best = (255.0, 0, 0)
    for delta_y in range(-MAX_OFFSET, MAX_OFFSET + 1):
        for delta_x in range(-MAX_OFFSET, MAX_OFFSET + 1):
            moved = (box[0] + delta_x, box[1] + delta_y,
                     box[2] + delta_x, box[3] + delta_y)
            best = min(best, (diff(shot.crop(moved), expected),
                              delta_x, delta_y))
    return best


def expected_equation(background, filename, frame_width):
    """What the part of the game with the (lack of) equation looks like."""
    x, y, width, height = EQUATION_LABEL
    # The QLabel scales its pixmap to fit within its frame
    image = Image.open(filename).convert("RGBA").resize(
        (width - 2 * frame_width, height - 2 * frame_width))
    result = background.crop((x, y, x + width, y + height)).convert("RGBA")
    result.alpha_composite(image, (frame_width, frame_width))
    inner = (FRAME_MARGIN, FRAME_MARGIN,
             width - FRAME_MARGIN, height - FRAME_MARGIN)
    box = (x + FRAME_MARGIN, y + FRAME_MARGIN,
           x + width - FRAME_MARGIN, y + height - FRAME_MARGIN)
    return result.crop(inner).convert("RGB"), box


def main():
    url = sys.argv[1]
    girl = Image.open("girl.png").convert("RGBA")
    # The game has a white background, see game_dialog.ui
    background = Image.new("RGBA", GAME_SIZE, (255, 255, 255, 255))
    background.alpha_composite(girl, GIRL_POS)
    with_equation, box = expected_equation(background, "equation.png", 1)
    no_equation, _ = expected_equation(background, "no_equation.png", 0)
    # The part of the girl that is never covered by anything
    girl_box = (9, 400, 570, 800)
    expected_girl = background.crop(girl_box).convert("RGB")

    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 2200, "height": 1300})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda m: print(f"console: {m.text}"))
        page.goto(url)
        frame = page.locator("iframe")

        def screenshot():
            data = frame.screenshot()
            return Image.open(io.BytesIO(data)).convert("RGB")

        def equation_state():
            shot = screenshot()
            return (find_offset(shot, with_equation, box)[0],
                    find_offset(shot, no_equation, box)[0])

        print("Waiting for the game to show up")
        deadline = time.time() + START_TIMEOUT_SECS
        girl_diff = 255.0
        while time.time() < deadline and girl_diff > MAX_DIFF:
            shot = screenshot()
            girl_diff = diff(shot.crop(girl_box), expected_girl)
            print(f"Difference with the expected girl: {girl_diff:.1f}")
            time.sleep(1)
        assert girl_diff <= MAX_DIFF, "Game not shown at the expected spot"
        assert not errors, errors

        # The equation may already be gone by now
        eq_diff, no_eq_diff = equation_state()
        print(f"Start: {eq_diff:.1f} from equation, "
              f"{no_eq_diff:.1f} from none")
        assert min(eq_diff, no_eq_diff) <= MAX_DIFF, "Equation not recognized"

        print("Clicking to get an equation")
        # The state of the game is the image it resembles most
        frame.click(position={"x": 100, "y": 100})
        time.sleep(1)
        eq_diff, no_eq_diff = equation_state()
        assert eq_diff < no_eq_diff, "Click gave no equation"

        print("Waiting for the equation to disappear")
        deadline = time.time() + EQUATION_TIMEOUT_SECS
        while time.time() < deadline and no_eq_diff > eq_diff:
            time.sleep(1)
            eq_diff, no_eq_diff = equation_state()
        assert no_eq_diff < eq_diff, "Equation stayed"

        print("Clicking to get an equation again")
        frame.click(position={"x": 100, "y": 100})
        time.sleep(1)
        eq_diff, no_eq_diff = equation_state()
        assert eq_diff < no_eq_diff, "Click gave no equation"
        assert not errors, errors
        browser.close()
    print("OK: the game can be played")


if __name__ == "__main__":
    main()
