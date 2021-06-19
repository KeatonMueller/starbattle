from collections import defaultdict

GRID_SIZE = 10
STAR_COUNT = 2

class Values():
    EMPTY = '-' 
    CROSS = ' '
    STAR = 'X'

class Grid:
    def __init__(self):
        self._boxes = [[Box(row, col) for col in range(GRID_SIZE)] for row in range(GRID_SIZE)]
        self._regions = defaultdict(lambda: set())
        self._history = []

    def _validate_boxes(self, boxes):
        '''
        validate that the given group of boxes does not contain
        more than STAR_COUNT stars, and does not contain more
        than len(boxes) - STAR_COUNT crosses
        '''
        num_stars, num_crosses = 0, 0
        for box in boxes:
            if box.value == Values.STAR:
                num_stars += 1
            elif box.value == Values.CROSS:
                num_crosses += 1

        return num_stars <= STAR_COUNT and num_crosses <= len(boxes) - STAR_COUNT

    def validate(self, check_row=0):
        '''
        validate that the current grid state does not violate
        any of the rules of star battle

        if check_row is supplied, validate that all rows prior to given
        row have exactly STAR_COUNT stars in them
        '''
        # check the constraint that every row, column, and region
        # must have at most STAR_COUNT stars
        for i in range(GRID_SIZE):
            # validate each row
            if not self._validate_boxes(self._get_row(i)):
                return False
            # validate each column
            if not self._validate_boxes(self._get_col(i)):
                return False

        # validate each region
        for region in self._regions.values():
            if not self._validate_boxes(region):      
                return False

        # check the constraint that no star may neighbor another star
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # for each star
                if self._boxes[row][col].value == Values.STAR:
                    # check the surrounding 8 locations for any stars
                    for adj_box in self._get_adjacent(row, col):
                        if adj_box.value == Values.STAR:
                            return False

        # check that all rows prior to check_row have STAR_COUNT stars 
        for row in range(check_row):
            if len([box for box in self._get_row(row) if box.value == Values.STAR]) != STAR_COUNT:
                return False

        # every check has passed, the grid is valid
        return True

    def _get_adjacent(self, row, col):
        '''
        get the 8 adjacent boxes to the given box location,
        checking for boundary errors
        '''
        adjacent = []
        for dr, dc in [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]:
            new_row = row + dr
            new_col = col + dc
            # if it's a valid location, add it to the adjacent list
            if new_row < GRID_SIZE and new_row >= 0 and \
                new_col < GRID_SIZE and new_col >= 0:
                adjacent.append(self._boxes[new_row][new_col])

        return adjacent

    def join_right(self, row, col):
        '''
        for the given box, add to its neighbors the box to the right,
        and vice versa
        '''
        self._boxes[row][col].neighbors.add(self._boxes[row][col + 1])
        self._boxes[row][col + 1].neighbors.add(self._boxes[row][col])

    def join_down(self, row, col):
        '''
        for the given box, add to its neighbors the box below it,
        and vice versa
        '''
        self._boxes[row][col].neighbors.add(self._boxes[row + 1][col])
        self._boxes[row + 1][col].neighbors.add(self._boxes[row][col])

    def get_region_id(self, row, col):
        return self._boxes[row][col].region_id

    def get_box(self, row, col):
        return self._boxes[row][col]

    def _get_row(self, row):
        return self._boxes[row]

    def _get_col(self, col):
        return [self._boxes[row][col] for row in range(GRID_SIZE)]

    def _get_region(self, row, col):
        return self._regions[self.get_region_id(row, col)]

    def cross(self, row, col):
        '''
        cross off the box at the given location
        '''
        self._boxes[row][col].cross()

    def star(self, row, col):
        '''
        star the box at the given location
        automatically cross out surrounding 8 boxes,
        as well as the row/column/region if they've reached
        the maximum number of stars
        '''
        self._boxes[row][col].value = Values.STAR

        # cross out adjacent boxes
        for box in self._get_adjacent(row, col):
            box.cross()

        # check row, column, and region and cross out if they've reached STAR_COUNT
        groups = [self._get_row(row), self._get_col(col), self._get_region(row, col)]
        for group in groups:
            num_stars = len([box for box in group if box.value == Values.STAR])
            if num_stars == STAR_COUNT:
                for box in group:
                    box.cross()

    def label(self, box, region_id):
        '''
        label the given box with the given region id
        '''
        box.region_id = region_id
        self._regions[region_id].add(box)

    def push_history(self):
        '''
        add current grid state to the history stack
        '''
        self._history.append(repr(self))

    def pop_history(self):
        '''
        set grid state to the top of the history stack
        '''
        state = self._history.pop()
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                idx = (row * GRID_SIZE) + col
                self._boxes[row][col].value = state[idx]

    def __repr__(self):
        '''
        return a repr of the current grid state, capturing if each box
        is a star, cross, or empty. wall data is assumed to always
        be preserved so it is not stored
        '''
        return ''.join(''.join(str(box) for box in row) for row in self._boxes)

    def __str__(self):
        '''
        return a readable string representation of the board
        '''
        # list to collect each line of the grid in
        lines = []
        
        # top horizontal border
        border_horiz = '-' * ((GRID_SIZE * 3) + (GRID_SIZE - 1) + 2)
        lines.append(border_horiz)

        # for each row
        for row in range(GRID_SIZE):
            line = []
            # add left border
            line.append('|')
            # for each box in the row
            for col in range(GRID_SIZE):
                # add ' X ' where X is the box's value
                line.append(' ' + str(self._boxes[row][col]) + ' ')

                # if not the final box, check the right neighbor
                # add a | divider if not neighbors, else add a ' '
                if col < GRID_SIZE - 1:
                    if self._boxes[row][col] in self._boxes[row][col + 1].neighbors:
                        line.append(' ')
                    else:
                        line.append('|')
                # the final box adds the right border
                else:
                    line.append('|')

            # add this line to the lines
            lines.append(''.join(line))

            # if not the final row, add the bottom borders
            if row < GRID_SIZE - 1:
                line = []
                # add left border
                line.append('|')
                # for each box in the row
                for col in range(GRID_SIZE):
                    # check the bottom neighbor
                    # add a --- divider if not neighbors, else add '   '
                    if self._boxes[row][col] in self._boxes[row + 1][col].neighbors:
                        line.append('   ')
                    else:
                        line.append('---')
                    # if not final box, add a dot
                    if col < GRID_SIZE - 1:
                        line.append('·')
                    # the final box adds the right border
                    else:
                        line.append('|')

                # add this line to the lines
                lines.append(''.join(line))
        
        # add the bottom horizontal border
        lines.append(border_horiz)
        
        # return the lines
        return '\n'.join(lines)
        
class Box: 
    def __init__(self, row, col):
        self.value = Values.EMPTY
        self.region_id = -1
        self._hash = (row * GRID_SIZE) + col

        # neighbors for graph traversal
        self.neighbors = set()

    def cross(self):
        '''
        cross out this box only if its value is not a star
        '''
        if self.value != Values.STAR:
            self.value = Values.CROSS

    def __str__(self):
        return self.value

    def __hash__(self):
        return self._hash
        