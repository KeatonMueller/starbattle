from enum import Enum
from collections import defaultdict

GRID_SIZE = 10

class BoxValues(Enum):
    EMPTY = '0'
    CROSS = '1'
    STAR = '2'

class Grid:
    def __init__(self):
        self._boxes = [[Box(row, col) for col in range(GRID_SIZE)] for row in range(GRID_SIZE)]
        self._regions = defaultdict(lambda: set())

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

    def label(self, box, region_id):
        '''
        label the given box with the given region id
        '''
        box.region_id = region_id
        self._regions[region_id].add(box)

    def __str__(self):
        return '\n'.join('\t'.join(str(box) for box in row) for row in self._boxes)
        
class Box: 
    def __init__(self, row, col):
        self.value = BoxValues.EMPTY
        self.region_id = -1
        self._row = row
        self._col = col

        # neighbors for graph traversal
        self.neighbors = set()

    def cross(self):
        if self.value != BoxValues.STAR:
            self.value = BoxValues.CROSS

    def __str__(self):
        return str(self.region_id)
        # return self.value.value

    def __hash__(self):
        return (self._row * GRID_SIZE) + self._col
