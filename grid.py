import numpy as np
import pandas as pd

class Grid:
    def __init__(self, n:int, m:int, param={}):
        self.pos = (n,m)
        self.params = param
        self.vis = '_'

    def __str__(self):
        return self.vis
    
class StratPos(Grid):
    def __init__(self, n, m,param={}):
        super().__init__(n, m, param)
        self.vis = 'S'

class Road(Grid):
    def __init__(self, n, m,param={}):
        super().__init__(n, m, param)
        self.vis = '.'

class Robot(Grid):
    def __init__(self, n, m,param={}):
        super().__init__(n, m, param)
        self.vis = '#'
        self.skus = param['skus']
        self.typs = param['typs']

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
    def __init__(self, n, m,param={}):
        super().__init__(n, m, param)
        self.vis = 'O'
        self.sku = param['sku']
        self.typ = param['typ']

def visualize(store):
    n,m = store.shape
    for i in range(n):
        for j in range(m):
            print(store[i,j], end=' ')
        print()
    print('='*40)


def create_demo_store():
    n,m = 10,11
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
            Shelves(i,j,store,{'sku':'4','typ':'1'})
        for j in road_col:
            Road(i,j,store,{})

    return store

if __name__ == '__main__':
    pass