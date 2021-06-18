import cv2
import numpy as np

import game

def get_dimensions(img):
    '''
    determine the dimensions of the given image

    return location of grid boundaries, as well as
    the dimensions of an individual box, in the form
    (top, left, bottom, right, width, height)
    '''
    # find width
    left, right = 0, img.shape[1] - 1
    row = img.shape[0] // 2
    
    while img[row][left][0] == 255:
        left += 1
    while img[row][right][0] == 255:
        right -= 1

    width = round((right - left) / game.GRID_SIZE)

    # find height
    top, bottom = 0, img.shape[0] - 1
    col = img.shape[1] // 2

    while img[top][col][0] == 255:
        top += 1
    while img[bottom][col][0] == 255:
        bottom -=1

    height = round((bottom - top) / game.GRID_SIZE)

    # return data
    return top, left, bottom, right, width, height

def extract_grid_lines(img_path):
    '''
    extract the grid lines from the image located at the given file path

    based heavily on: https://medium.com/coinmonks/a-box-detection-algorithm-for-any-image-containing-boxes-756c15d7ed26
    '''
    # read in the image
    img = cv2.imread(img_path)
    # threshold the image
    thresh, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
    # invert the image
    img_bin = 255 - img_bin
    # cv2.imwrite('img_bin.jpg', img_bin)

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
    # cv2.imwrite('lines_vert.jpg', img_lines_vert)

    # extract horizontal lines
    img_temp1 = cv2.erode(img_bin, kernel_horiz, iterations=3)
    img_lines_horiz = cv2.dilate(img_temp1, kernel_horiz, iterations=3)
    # cv2.imwrite('lines_horiz.jpg', img_lines_horiz)

    # add the two images together
    img_final_bin = cv2.addWeighted(img_lines_vert, 0.5, img_lines_horiz, 0.5, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel_ones, iterations=1)
    thresh, img_final_bin = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY)
    cv2.imwrite('img_final_bin.jpg', img_final_bin)
    
    return img_final_bin

def detect_line(img, coord0, coord1_start, coord1_end, dir='horiz'):
    '''
    detect if there's a line in the image between the given coordinates

    dir dictates the direction the changing coordinate moves in

    i.e. 'horiz' means coord1 is moving horizontally, 'vert' means
    coord1 is moving vertically
    '''
    # loop through given range
    for coord1 in range(coord1_start, coord1_end):
        # if dir is horiz, coord1 controls the column
        if dir == 'horiz':
            if img[coord0][coord1][0] == 0:
                return True
        # if dir is vert, coord1 controls the row
        elif dir == 'vert':
            if img[coord1][coord0][0] == 0:
                return True
    return False

def detect_walls(img):
    '''
    check every box boundary for the existence of a wall

    if no wall is found, record adjacent boxes as neighbors
    '''
    # get dimensions from the extracted line data
    top, left, bottom, right, width, height = get_dimensions(img)

    # note: grids automatically have walls everywhere
    grid = game.Grid()

    # loop over all boxes
    for row in range(game.GRID_SIZE):
        for col in range(game.GRID_SIZE):
            # find pixel location of center of this box
            row_px = round(top + (row * height) + (height / 2))
            col_px = round(left + (col * width) + (width / 2))
            
            # if not last col, check if there's a wall to the right 
            if col < game.GRID_SIZE - 1 and not detect_line(img, row_px, col_px, col_px + width, 'horiz'):
                grid.join_right(row, col)

            # if not last row, check if there's a wall to the bottom 
            if row < game.GRID_SIZE - 1 and not detect_line(img, col_px, row_px, row_px + height, 'vert'):
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

def read_img(img_path):
    '''
    read in the raw image located at img_path and extract grid lines,
    detect walls, and label the regions
    '''
    img = extract_grid_lines(img_path)
    grid = detect_walls(img)
    label_regions(grid)
    print(grid)
    
