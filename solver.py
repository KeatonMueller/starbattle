import game

def solve(grid):
    '''
    solve the grid using recursive backtracking
    '''
    stars_left = game.GRID_SIZE * game.STAR_COUNT

    # only need to try the first row since every row gets stars
    for col in range(game.GRID_SIZE):
        if solve_helper(grid, 0, col, stars_left):
            return True

    # no solution found
    return False

def solve_helper(grid, row, col, stars_left):
    '''
    star the given coordinate and terminate if doing so makes stars_left
    equal 0 while being a valid grid

    otherwise it try all subsequent positions to the given location

    return the grid unchanged, or in the solved position
    '''

    # save current board state
    grid.push_history()

    # star this position
    grid.star(row, col)
    stars_left -= 1
    
    # restore old state and return False if grid is invalid
    if not grid.validate(row):
        grid.pop_history()
        return False

    # return True if placed all the stars
    if stars_left == 0:
        return True

    # for all subsequent locations
    loc = (row * game.GRID_SIZE) + col
    for idx in range(loc + 1, game.GRID_SIZE * game.GRID_SIZE):
        next_row = idx // game.GRID_SIZE
        next_col = idx % game.GRID_SIZE
        # skip over filled boxes
        if grid.get_box(next_row, next_col).value != game.Values.EMPTY:
            continue

        # return True if this location led to the solution
        if solve_helper(grid, next_row, next_col, stars_left):
            return True
    
    # no solution possible on this path
    # restore old state and return False
    grid.pop_history()
    return False
    