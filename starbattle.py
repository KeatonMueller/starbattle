from img_detection import read_img
from solver import solve
import game

import argparse

# create arg parser
parser = argparse.ArgumentParser(description = 'run star battle solver')
# add args for filename, size of grid, and number of stars
parser.add_argument('-f', '--file', type=str, default='grid.png', help='file path of image to analyze')
parser.add_argument('-d', '--dimension', type=int, default=10, help='dimension of the grid')
parser.add_argument('-s', '--stars', type=int, default=2, help='number of stars')

args = parser.parse_args()

# set the game properties based on the args
game.GRID_SIZE = args.dimension
game.STAR_COUNT = args.stars

# read the image and attempt a solve
grid = read_img(args.file)

print('extracted the following grid:')
print(grid)

print('solving...')
if solve(grid):
    print('done!')
    print(grid)
else:
    print('no solution found :(')
