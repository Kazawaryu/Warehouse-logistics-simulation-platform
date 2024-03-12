import numpy as np
import pandas as pd
import random
import time

import grid_object as go

class Store:
    def __init__(self, n:int, m:int):
        self.store = np.empty((n,m), dtype=object)
        self.store = self.store.astype(object)
        self.n = n
        self.m = m
        self._robot = None
        self.movable_cols = set()
        self.shelev_cols = set()

        self.stage = 'init'

    def __str__(self):
        return go.visualize(self.store)
    
    def create_shelevs(self, col):
        for i in range(1, self.n-1):
            for j in col:
                self.store[i,j] = go.Shelves(i,j,{'sku':[],'typ':[]})
        self.stage = 'shelves_created'
        self.movable_cols = set([i for i in range(self.m) if i not in col])
        self.shelev_cols = set(col)

    def create_road(self):
        if self.stage != 'shelves_created':
            raise ValueError('Shelves not created yet')

        for i in range(self.n):
            for j in range(self.m):
                if not isinstance(self.store[i,j], go.Shelves):
                    self.store[i,j] = go.Road(i,j)
        self.stage = 'road_created'

    def create_start_pos(self, n, m):
        if self.stage != 'road_created':
            raise ValueError('Shelves not created yet')
        if not isinstance(self.store[n,m], go.Road):
            raise ValueError('Start position must be placed on a road')
        self.store[n,m] = go.StratPos(n,m)
        self.stage = 'start_pos_created'

        return self.store[n,m]

    def create_robot(self, startpos:go.StratPos, task):
        if self.stage != 'start_pos_created':
            raise ValueError('Start position not created yet')
        self.store[startpos.pos] = go.Robot(startpos.pos[0],startpos.pos[1],task)
        self._robot = self.store[startpos.pos]
        self.stage = 'robot_created'

        return self.store[startpos.pos]

    def visualize(self):
        go.visualize(self.store)

    def setup_shelves(self,n, m ,sku, typ):
        if not isinstance(self.store[n,m], go.Shelves):
            raise ValueError('Shelves not created yet')
        self.store[n,m].sku = sku
        self.store[n,m].typ = typ
        self.store[n,m].vis = '0'

    def seek_next_postion(self):
        valid_cols = set()
        for i in range(1,self.n-1):
            for j in self.shelev_cols:
                if self.store[i,j].typ in self._robot.typs and self.store[i,j].sku > 0:
                    valid_cols.add(j)
        if len(valid_cols) == 0:
            return -1
        
        valid_cols = list(valid_cols)
        valid_cols.sort(key=lambda x: abs(x-self._robot.pos[1]))
        return valid_cols[0]
    
    def move_robot(self, next_col):
        pre_col = []
        if next_col-1 in self.movable_cols:
            pre_col.append(next_col-1)
        if next_col+1 in self.movable_cols:
            pre_col.append(next_col+1)
        col_step = min([x - self._robot.pos[1] for x in pre_col])
        row_step = self._robot.pos[0] - int(self.n / 2) + 1

        self.store[self._robot.pos] = go.Road(self._robot.pos[0],self._robot.pos[1])
        self._robot.pos = (self._robot.pos[0]+row_step, self._robot.pos[1]+col_step)
        self.store[self._robot.pos] = self._robot

        return col_step, row_step, np.abs(col_step) + np.abs(row_step)

    def collect_sku_by_col(self):
        pre_col = []
        if self._robot.pos[1] - 1 in self.shelev_cols:
            pre_col.append(self._robot.pos[1]-1)
        if self._robot.pos[1] + 1 in self.shelev_cols:
            pre_col.append(self._robot.pos[1]+1)

        typs_col = [self.store[i,x].typ for x in pre_col for i in range(1,self.n-1)]
        skus_col = [self.store[i,x].sku for x in pre_col for i in range(1,self.n-1)]
        
        print(skus_col)


        return


def create_demo_store():
    store = Store(10,11)
    store.create_shelevs([1,3,4,6,7,9])
    store.create_road()
    startpos = store.create_start_pos(2,5)
    store.create_robot(startpos,{'skus':[4,5,6],'typs':[1,2,3]})
    store.setup_shelves(5,3,2,1)
    store.visualize()
    print(store.move_robot(store.seek_next_postion()))
    store.collect_sku_by_col()
    store.visualize()
    
if __name__ == '__main__':
    create_demo_store()