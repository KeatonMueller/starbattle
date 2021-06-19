import cv2
import numpy as np
from math import ceil

import game

def get_color(img, x, y, flip=False):
    '''
    get the color from the image at the given pixel location

    rgb values are averaged, then converted to 0 or 255
    '''
    rgb = img[y][x] if flip else img[x][y]
    if sum(rgb) / 3 >= 128:
        return 255
    return 0

def get_dimensions(img):
    '''
    determine the dimensions of the given image

    return location of grid boundaries, the dimensions
    of an individual box, and the border thickness in
    the form
    (top, left, bottom, right, width, height, thickness)
    '''
    # find width
    left, right = 0, img.shape[1] - 1
    row = img.shape[0] // 2
    
    while get_color(img, row, left) == 255:
        left += 1
    while get_color(img, row, right) == 255:
        right -= 1

    width = round((right - left) / game.GRID_SIZE)

    # find height
    top, bottom = 0, img.shape[0] - 1
    col = img.shape[1] // 2

    while get_color(img, top, col) == 255:
        top += 1
    while get_color(img, bottom, col) == 255:
        bottom -=1

    height = round((bottom - top) / game.GRID_SIZE)

    # determine thickness of outer border
    thickness = left
    row = top + (height // 2)
    while get_color(img, row, thickness) == 0:
        thickness += 1
    thickness -= left

    # return data
    return top, left, bottom, right, width, height, thickness

def extract_grid_lines(img_path, debug):
    '''
    extract the grid lines from the image located at the given file path

    based heavily on: https://medium.com/coinmonks/a-box-detection-algorithm-for-any-image-containing-boxes-756c15d7ed26
    '''
    # read in the image
    img = cv2.imread(img_path)
    # threshold the image
    thresh, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
    # invert the image if light theme
    if img_bin.mean() >= 128:
        img_bin = 255 - img_bin
    if debug: cv2.imwrite('img_bin.jpg', img_bin)

    # create kernels
    kernel_len = np.array(img).shape[1] // 80
    # vertical kernel (1 x kernel_len)
    kernel_vert = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
    # horizontal kernel (kernel_len x 1)
    kernel_horiz = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
    # (3 x 3) kernel of ones
    kernel_ones = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))

    # extract vertical lines
    img_temp0 = cv2.erode(img_bin, kernel_vert, iterations=3)
    img_lines_vert = cv2.dilate(img_temp0, kernel_vert, iterations=3)
    if debug: cv2.imwrite('lines_vert.jpg', img_lines_vert)

    # extract horizontal lines
    img_temp1 = cv2.erode(img_bin, kernel_horiz, iterations=3)
    img_lines_horiz = cv2.dilate(img_temp1, kernel_horiz, iterations=3)
    if debug: cv2.imwrite('lines_horiz.jpg', img_lines_horiz)

    # add the two images together
    img_final_bin = cv2.addWeighted(img_lines_vert, 0.5, img_lines_horiz, 0.5, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel_ones, iterations=1)
    thresh, img_final_bin = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY)
    if debug: cv2.imwrite('img_final_bin.jpg', img_final_bin)
    
    return img_final_bin

def find_max_black(img, coord0, coord1_start, coord1_end, flip):
    '''
    find the largest stretch of black pixels between coord1_start and
    coord1_end in img
    '''
    state = 'not found'
    max_size = -1
    size = 0
    # loop through the range
    for coord1 in range(coord1_start, coord1_end):
        # if pixel is black
        if get_color(img, coord0, coord1, flip) == 0:
            # start tracking a new size, or increase existing size
            if state == 'not found':
                state = 'found'
                size = 1
            else:
                size += 1
        # if pixel is white
        else:
            # update max_size
            if state == 'found':
                state = 'not found'
                max_size = max(max_size, size)

    return max_size

def detect_line(img, coord0, coord1_start, coord1_end, thickness, delta, dir='horiz'):
    '''
    detect if there's a line in the image between the given coordinates

    detected line must be within 10% of the thickness value to be registered

    delta is an offset to coord0 because the line must be detected in three locations

    dir dictates the direction coord1 moves in

    e.g. 'horiz' means coord1 is moving horizontally, 'vert' means
    coord1 is moving vertically
    '''
    # if direction is vertical, then coord1 should control the row i.e. be
    # the first coordinate, so calls to get_color should be flipped
    flip = dir == 'vert'

    # find the largest stretch of black pixels for all three locations
    maxes = []
    for c0 in [coord0, coord0 - delta, coord0 + delta]:
        maxes.append(find_max_black(img, c0, coord1_start, coord1_end, flip))

    # ensure the min of the maxes is within the threshold of the required thickness
    size = min(maxes)
    if ceil(size * 1.1) >= thickness:
        return True
    return False

def detect_walls(img):
    '''
    check every box boundary for the existence of a wall

    if no wall is found, record adjacent boxes as neighbors
    '''
    # get dimensions from the extracted line data
    top, left, bottom, right, width, height, thickness = get_dimensions(img)
    quarter_height = height // 4
    quarter_width = width // 4

    # note: grid automatically has walls everywhere, so they only need to be removed
    grid = game.Grid()

    # loop over all boxes
    for row in range(game.GRID_SIZE):
        for col in range(game.GRID_SIZE):
            # find pixel location of center of this box
            row_px = round(top + (row * height) + (height / 2))
            col_px = round(left + (col * width) + (width / 2))
            
            # if not last col, check if there's a wall to the right 
            if col < game.GRID_SIZE - 1 and not detect_line(img, row_px, col_px, col_px + width, thickness, quarter_height, 'horiz'):
                grid.join_right(row, col)

            # if not last row, check if there's a wall to the bottom 
            if row < game.GRID_SIZE - 1 and not detect_line(img, col_px, row_px, row_px + height, thickness, quarter_width, 'vert'):
                grid.join_down(row, col)

    # return the grid
    return grid

def bfs(grid, row, col, region_id):
    '''
    perform a breadth-first search on the grid starting at the given
    row and column, labelling each reached vertex with the given id
    '''
    queue = [grid.get_box(row, col)]

    while len(queue) != 0:
        box = queue.pop(0)
        # label this box with the region_id
        grid.label(box, region_id)
        # enqueue any neighbors that are unlabelled
        for neighbor in box.neighbors:
            if neighbor.region_id == -1:
                queue.append(neighbor)

def label_regions(grid):
    '''
    perform BFS for each region in the grid to determine
    which boxes are in which regions
    '''
    region_id = 0

    for row in range(game.GRID_SIZE):
        for col in range(game.GRID_SIZE):
            if grid.get_region_id(row, col) != -1:
                continue
            bfs(grid, row, col, region_id)
            region_id += 1

def read_img(img_path, debug):
    '''
    read in the raw image located at img_path and extract grid lines,
    detect walls, and label the regions

    return the Grid object corresponding to the image
    '''
    img = extract_grid_lines(img_path, debug)
    grid = detect_walls(img)
    label_regions(grid)
    
    return grid
