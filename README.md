# starbattle

This is a project to solve the game of Star Battle.

The rules of Star Battle are quite simple. In each row, column, and region
of an NxN grid, you must place a specified number of stars. In addition, no
star may be adjacent to any other, even diagonally.

The game is most often played on a 10x10 grid with 2 stars per row/column/region.

This project is written in Python and uses OpenCV to analyze an image of a Star
Battle game and output a solution.

## How to use it

To use the program, run:

`python starbattle.py -f [FILENAME]`

where `FILENAME` is a path to an image of a Star Battle puzzle.

A sample image is included in the repo named `grid.png` which is the first
level from [this](https://krazydad.com/tablet/starbattle/) website.

Images should be cropped to only include the grid, and the grid lines
should be as close to perfectly horizontal/vertical as possible.

Run

`python starbattle.py --help`

for more information.

## How it works

This program finds a solution using simple recursive backtracking.

However, since a standard game is 10x10 with 20 total stars, the number of ways
to place the stars is 100 choose 20, which is on the order of 10^20.

This is too large a search space to explore in a reasonable amount of time, so
some basic optimizations were made using the standard rules of Star Battle.

Firstly, placing a star automatically crosses out the 8 surrounding squares
to enforce the adjacency constraint.

In addition, when a placed star reaches the quota for a row/column/region, then
the rest of the row/column/region is automatically crossed out as well.

With these two basic optimizations, the recursive backtracking algorithm is able
to find solutions for easy games in a few seconds, and for harder games it takes
about 10-20 seconds.

The program generalizes to bigger board sizes with more stars, but it may be
prohibitively slow in this situations.
