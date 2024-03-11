import numpy as np
import pandas as pd

class Grid:
    def __init__(self, n:int, m:int, map:np.array, param={}):
        self.pos = (n,m)
        self.params = param
        self.vis = ' '
        self.map = map
        map[n,m] = self

    def __str__(self):
        return self.vis

class Road(Grid):
    def __init__(self, n, m, map, param={}):
        super().__init__(n, m, map, param)
        self.vis = '.'

class Robot(Grid):
    def __init__(self, n, m, map, param):
        super().__init__(n, m, map, param)
        self.vis = '#'
        self.skus = param['skus']

    def seek_col(self):
        n,m = self.map.shape
        valid_cols = []
        shelf_col = [j for j in range(m) if isinstance(self.map[self.pos[0],j], Shelves)]
        for i in range(1,n-1):
            for j in shelf_col:
                if self.map[i,j].sku in self.skus:
                    valid_cols.append((i,j))

        if len(valid_cols) == 0:
            return -1
        else:
            valid_cols.sort(key=lambda x: abs(x[1]-self.pos[1]))
            return valid_cols[0][1] 
      

class Shelves(Grid):
    def __init__(self, n, m, map, param):
        super().__init__(n, m, map, param)
        self.vis = 'O'
        self.sku = param['sku']
        self.qty = param['qty']
        self.typ = param['typ']

def visualize(store):
    n,m = store.shape
    for i in range(n):
        for j in range(m):
            print(store[i,j], end=' ')
        print()


def create_demo_store():
    # . . . . . . . . . . . 
    # . O . O O . O O . O . 
    # . O . O O . O O . O . 
    # . O . O O . O O . O . 
    # . O . O O . O O . O . 
    # . O . O O . O O . O . 
    # . O . O O . O O . O . 
    # . O . O O . O O . O . 
    # . O . O O . O O . O . 
    # . . . . . . . . . . . 
    n = 10
    m = 11

    shelves_col = [1,3,4,6,7,9]
    road_col = [0,2,5,8,10]

    store = np.empty((n,m), dtype=object)
    for i in range(n):
        for j in range(m):
            store[i,j] = Grid(i,j,store)

    for i in [0,n-1]:
        for j in range(m):
            Road(i,j,store)

    for i in range(1,n-1,1):
        for j in shelves_col:
            Shelves(i,j,store,{'sku':'A','qty':10,'typ':'A'})
        for j in road_col:
            Road(i,j,store,{})

    return store

if __name__ == '__main__':
    store = create_demo_store()
    rob = Robot(5,0,store,{'skus':['A']})
    visualize(store)
    print(rob.seek_col())