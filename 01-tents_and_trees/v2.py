#!/usr/bin/env python3

"""
Improved version.

It takes digits (on the right side and at the bottom)
into account. It calls the program "ocrad" (can be installed with pacman)
to recognize digits.
"""

import sys
import time
from enum import Enum

import pyautogui
from PIL import Image, ImageDraw, ImageOps

import ocr

# red pixel
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

OUTPUT_FILENAME = "screenshot_with_dots.png"

##############################################################################


class CellValue(Enum):
    EMPTY = 230
    TREE = 105
    GRASS = 218
    TENT = 166


##############################################################################


class Grid:
    def __init__(self):
        self.top_left = (0, 0)  # will be set later
        self.bottom_right = (0, 0)  # will be set later
        self.unit = 0  # will be set later
        self.xn = 0  # will be set later; number of cells in x direction
        self.yn = 0  # will be set later; ; number of cells in y direction
        # ---
        self.pixels = None  # will be set later; pixels of the B&W image
        self.output_image = None  # will be set later; image with red dots (for debugging)
        # ---
        self.matrix: list[list[CellValue]]
        #
        self.digits_right: list[int] = []
        self.digits_bottom: list[int] = []

    def save_output_image(self) -> None:
        self.output_image.save(OUTPUT_FILENAME)

    def print_matrix(self) -> None:
        for row in self.matrix:
            for value in row:
                if value == CellValue.EMPTY:
                    sys.stdout.write(".")
                elif value == CellValue.TREE:
                    sys.stdout.write("T")
                elif value == CellValue.TENT:
                    sys.stdout.write("A")
                elif value == CellValue.GRASS:
                    sys.stdout.write("g")
                #
            #
            print()
        #

    def screen_position_of_cell(self, row: int, col: int) -> tuple[int, int]:
        half = self.unit // 2
        start_x, start_y = self.top_left[0] + half, self.top_left[1] + half
        start_x += col * self.unit
        start_y += row * self.unit
        return (start_x, start_y)

    def is_valid_cell(self, pos: tuple[int, int]) -> bool:
        return (0 <= pos[0] < self.yn) and (0 <= pos[1] < self.xn)

    def get_neighbors_of(self, row: int, col: int) -> list[CellValue]:
        result: list[CellValue] = []
        #
        i, j = row, col
        left = (i, j - 1)
        right = (i, j + 1)
        up = (i - 1, j)
        down = (i + 1, j)
        if self.is_valid_cell(left):
            result.append(self.matrix[left[0]][left[1]])
        if self.is_valid_cell(right):
            result.append(self.matrix[right[0]][right[1]])
        if self.is_valid_cell(up):
            result.append(self.matrix[up[0]][up[1]])
        if self.is_valid_cell(down):
            result.append(self.matrix[down[0]][down[1]])
        #
        return result

    def set_cell(self, i: int, j: int, new_value: CellValue) -> None:
        self.matrix[i][j] = new_value


##############################################################################


def add_colored_dot(img, pos: tuple[int, int], color=RED) -> None:
    width, height = img.size
    for i in range(-2, 3):
        for j in range(-2, 3):
            # Boundary check to avoid errors at the image edge
            dot_x, dot_y = pos[0] + i, pos[1] + j
            if 0 <= dot_x < width and 0 <= dot_y < height:
                img.putpixel((dot_x, dot_y), color)


# a pixel is "black" if its grayscale value is 0
def is_black(pixel) -> bool:
    return pixel == 0


def take_screenshot() -> Image.Image:
    # 1. Take a screenshot.
    print("Taking screenshot...")
    screenshot = pyautogui.screenshot()
    print("Screenshot captured successfully.")
    return screenshot


def find_digit(img: Image.Image, pA: tuple[int, int], pC: tuple[int, int]) -> Image.Image:
    offset = 3
    crop_box = (pA[0] + offset, pA[1] + offset, pC[0] - offset, pC[1] - offset)
    cropped_image = img.crop(crop_box)
    threshold = 128
    bw_img = cropped_image.point(lambda p: 255 if p > threshold else 0)  # type: ignore
    bw_img = bw_img.convert("1")
    inverted_image = ImageOps.invert(bw_img)
    bounding_box = inverted_image.getbbox()
    if bounding_box:
        padding = 2
        # Adjust the box to add padding, ensuring it doesn't go out of bounds.
        padded_box = (
            max(0, bounding_box[0] - padding),
            max(0, bounding_box[1] - padding),
            min(inverted_image.width, bounding_box[2] + padding),
            min(inverted_image.height, bounding_box[3] + padding),
        )
        bw_img = bw_img.crop(padded_box)
    #
    return bw_img


def process_digits(grid: Grid, pixels, img: Image.Image) -> None:
    output_file = "cropped/digit.png"
    # on the right side
    start_x, start_y = grid.bottom_right
    start_y -= grid.yn * grid.unit
    # now we are in the top right corner
    add_colored_dot(img, (start_x, start_y), color=GREEN)
    horizontal = int(grid.unit * 1.2)
    for i in range(grid.yn):
        pA = (start_x, start_y)
        pB = (start_x + horizontal, start_y)
        pC = (start_x + horizontal, start_y + grid.unit)
        pD = (start_x, start_y + grid.unit)
        draw = ImageDraw.Draw(img)
        draw.line([pA, pB], fill="red", width=1)
        draw.line([pB, pC], fill="red", width=1)
        draw.line([pC, pD], fill="red", width=1)
        #
        digit: Image.Image = find_digit(img, pA, pC)
        digit.save(output_file)
        result = int(ocr.recognize(output_file))
        grid.digits_right.append(result)
        #
        start_y = pD[1]
    #
    # at the bottom
    start_x, start_y = grid.bottom_right
    start_x -= grid.xn * grid.unit
    # now we are in the bottom left corner
    add_colored_dot(img, (start_x, start_y), color=GREEN)
    vertical = int(grid.unit * 1.1)
    for i in range(grid.xn):
        pA = (start_x, start_y)
        pB = (start_x + grid.unit, start_y)
        pC = (start_x + grid.unit, start_y + vertical)
        pD = (start_x, start_y + vertical)
        draw = ImageDraw.Draw(img)
        draw.line([pB, pC], fill="red", width=1)
        draw.line([pC, pD], fill="red", width=1)
        draw.line([pD, pA], fill="red", width=1)
        #
        digit: Image.Image = find_digit(img, pA, pC)
        digit.save(output_file)
        result = int(ocr.recognize(output_file))
        grid.digits_bottom.append(result)
        #
        start_x = pB[0]
    #


def process_screen(grid: Grid):
    screenshot: Image.Image = take_screenshot()

    # 2. Convert the image to black and white (grayscale).
    print("Converting image to black and white...")
    bw_image = screenshot.convert("L")
    print("Conversion complete.")

    # --- Visualization ---

    # Convert the B&W image back to RGB to allow for a color dot.
    output_image: Image.Image = bw_image.convert("RGB")
    grid.output_image = output_image

    # --- Pixel-Walking Algorithm ---
    pixels = bw_image.load()
    grid.pixels = pixels
    width, height = bw_image.size
    center_x, center_y = width // 2, height // 2

    add_colored_dot(output_image, (center_x, center_y))

    start_x, start_y = center_x, center_y
    while True:
        if is_black(pixels[start_x, start_y]):  # type: ignore
            start_x += 1
            start_y += 1
        else:
            break

    add_colored_dot(output_image, (start_x, start_y))

    while True:
        start_x -= 1
        if is_black(pixels[start_x, start_y]):  # type: ignore
            break

    add_colored_dot(output_image, (start_x, start_y))

    while True:
        start_y -= 1
        if not is_black(pixels[start_x, start_y]):  # type: ignore
            start_y += 1
            break

    add_colored_dot(output_image, (start_x, start_y))

    while True:
        start_x -= 1
        if not is_black(pixels[start_x, start_y]):  # type: ignore
            start_x += 1
            break

    add_colored_dot(output_image, (start_x, start_y))

    top_left = (start_x, start_y)
    grid.top_left = top_left

    while True:
        start_x += 1
        if not is_black(pixels[start_x, start_y]):  # type: ignore
            start_x -= 1
            break

    add_colored_dot(output_image, (start_x, start_y))

    while True:
        start_y += 1
        if not is_black(pixels[start_x, start_y]):  # type: ignore
            start_y -= 1
            break

    bottom_right = (start_x, start_y)
    grid.bottom_right = bottom_right

    add_colored_dot(output_image, (start_x, start_y))

    while True:
        start_y -= 1
        if is_black(pixels[start_x - 1, start_y]):  # type: ignore
            break

    add_colored_dot(output_image, (start_x, start_y))

    unit = bottom_right[1] - start_y
    print(f"Unit: {unit} pixels")
    grid.unit = unit

    xn = (bottom_right[0] - top_left[0]) // unit
    yn = (bottom_right[1] - top_left[1]) // unit
    print(f"XN: {xn}")
    print(f"YN: {yn}")
    grid.xn = xn
    grid.yn = yn

    process_digits(grid, pixels, output_image)

    # Save the final image.
    output_image.save(OUTPUT_FILENAME)
    print(f"Success! Image with red dots saved as '{OUTPUT_FILENAME}'")


def traverse_cells(grid: Grid) -> None:
    half = grid.unit // 2
    start_x, start_y = grid.top_left[0] + half, grid.top_left[1] + half
    grid.matrix = []
    for row_x in range(grid.yn):
        row: list[CellValue] = []
        for col_y in range(grid.xn):
            x = start_x + (col_y * grid.unit)
            y = start_y + (row_x * grid.unit)
            # print(grid.pixels[x, y], end=" ")
            row.append(CellValue(grid.pixels[x, y]))  # type: ignore
            add_colored_dot(grid.output_image, (x, y))
        #
        grid.matrix.append(row)
        # print()
    #
    grid.save_output_image()


def process_value(i: int, j: int, value: CellValue, grid: Grid) -> None:
    if value == CellValue.EMPTY:
        neighbors: list[CellValue] = grid.get_neighbors_of(row=i, col=j)
        if CellValue.TREE not in neighbors:
            pos = grid.screen_position_of_cell(row=i, col=j)
            pyautogui.moveTo(pos[0], pos[1], duration=0)
            pyautogui.rightClick(pos[0], pos[1])
            grid.set_cell(i, j, CellValue.GRASS)
        #
    #


def fill_row_with_grass(grid: Grid, i: int) -> None:
    row = grid.matrix[i]
    for j, value in enumerate(row):
        if value == CellValue.EMPTY:
            pos = grid.screen_position_of_cell(row=i, col=j)
            pyautogui.moveTo(pos[0], pos[1], duration=0)
            pyautogui.rightClick(pos[0], pos[1])
            grid.set_cell(i, j, CellValue.GRASS)


def fill_column_with_grass(grid: Grid, j: int) -> None:
    for i, row in enumerate(grid.matrix):
        value = row[j]
        if value == CellValue.EMPTY:
            pos = grid.screen_position_of_cell(row=i, col=j)
            pyautogui.moveTo(pos[0], pos[1], duration=0)
            pyautogui.rightClick(pos[0], pos[1])
            grid.set_cell(i, j, CellValue.GRASS)


def mark_grass_cells(grid: Grid) -> None:
    # fill 0 rows with grass
    for i, value in enumerate(grid.digits_right):
        if value == 0:
            fill_row_with_grass(grid, i)
    # fill 0 columns with grass
    for j, value in enumerate(grid.digits_bottom):
        if value == 0:
            fill_column_with_grass(grid, j)
    #
    for i, row in enumerate(grid.matrix):
        if i % 2 == 0:
            for j, value in enumerate(row):
                process_value(i, j, value, grid)
            #
        else:
            j = len(row) - 1
            while j >= 0:
                value = row[j]
                process_value(i, j, value, grid)
                #
                j -= 1
            #
    #


def main():
    # Add a short delay to give the user time to switch windows if needed.
    print(
        "The script will run in 3 seconds. You can switch to the window you want to capture.",
        flush=True,
    )
    time.sleep(3)

    grid = Grid()
    process_screen(grid)
    print("---")
    print(grid.top_left)
    print(grid.bottom_right)
    print(grid.unit)
    print(grid.xn)
    print(grid.yn)
    print("---")
    traverse_cells(grid)
    grid.print_matrix()

    mark_grass_cells(grid)


##############################################################################

if __name__ == "__main__":
    main()
