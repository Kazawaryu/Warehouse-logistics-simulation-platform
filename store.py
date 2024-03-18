import numpy as np
import pandas as pd
import random
import time

import grid as go

class Store:
    def __init__(self, n:int, m:int):
        self.store = np.empty((n,m), dtype=object)
        self.store = self.store.astype(object)
        self.n = n
        self.m = m
        self._robot = None
        self.movable_cols = set()
        self.shelev_cols = set()
        self.start_ms = []

        self.goods = {}
        self.leek_goods = {}
        self.steps = []

        self.supply_tasks = []


    def __str__(self):
        return go.visualize(self.store)
    
    def show_goods(self):
        return sorted(self.goods.items(), key=lambda x: x[0])

    
    def create_shelevs(self, col):
        for i in range(1, self.n-1):
            for j in col:
                self.store[i,j] = go.Shelves(i,j,{'num':-1,'sku':-1})

        self.movable_cols = set([i for i in range(self.m) if i not in col])
        self.shelev_cols = set(col)

    def create_road(self):
        for i in range(self.n):
            for j in range(self.m):
                if not isinstance(self.store[i,j], go.Shelves):
                    self.store[i,j] = go.Road(i,j)


    def create_start_pos(self, n, m):
        if not isinstance(self.store[n,m], go.Road):
            raise ValueError('Start position must be placed on a road')
        self.store[n,m] = go.StratPos(n,m)
        self.store[n,m].vis = 'P'

        return self.store[n,m]
    
    def fix_start_pos(self, start_ms):
        self.start_ms = start_ms
        for m in self.start_ms:
            if not isinstance(self.store[0,m], go.Robot) and not isinstance(self.store[0,m], go.StratPos):
                self.create_start_pos(0,m)
            if not isinstance(self.store[self.n-1,m], go.Robot) and not isinstance(self.store[self.n-1,m], go.StratPos):
                self.create_start_pos(self.n-1,m)


    def create_robot(self, n,m, task):

        self.store[n,m] = go.Robot(n,m,task)
        self._robot = self.store[n,m]

        return self.store[n,m]

    def visualize(self):
        self.fix_start_pos(self.start_ms)
        go.visualize(self.store)

    def setup_shelves(self,n, m ,num, sku):
        if not isinstance(self.store[n,m], go.Shelves):
            raise ValueError('Shelves not created yet')
        self.store[n,m].num = num
        self.store[n,m].sku = sku
        self.store[n,m].vis = 'X'
        if sku not in self.goods:
            self.goods[sku] = num
        else:
            self.goods[sku] += num
        

    def seek_next_postion(self):
        valid_cols = set()
        for i in range(1,self.n-1):
            for j in self.shelev_cols:
                if self.store[i,j].sku in self._robot.skus and self.store[i,j].num > 0:
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
        
        idx = np.argmin([np.abs(x - self._robot.pos[1]) for x in pre_col])
        col_step = pre_col[idx] - self._robot.pos[1]

        row_step = - self._robot.pos[0] if self.n - 1 > 2 * self._robot.pos[0] else self.n - self._robot.pos[0] -1 
        self.store[self._robot.pos] = go.Road(self._robot.pos[0],self._robot.pos[1])
        self._robot.pos = (self._robot.pos[0]+row_step, self._robot.pos[1]+col_step)
        self.store[self._robot.pos] = self._robot

        return abs(col_step), abs(row_step), np.abs(col_step) + np.abs(row_step)
    
    def move_2_startPos(self):
        target_n = self._robot.startPos[0]
        target_m = self._robot.startPos[1]
        col_step = target_m - self._robot.pos[1]
        row_step = target_n - self._robot.pos[0]

        self.store[self._robot.pos] = go.Road(self._robot.pos[0],self._robot.pos[1])
        self._robot.pos = (target_n, target_m)
        self.store[self._robot.pos] = self._robot

        self.steps.append(np.abs(col_step) + np.abs(row_step))
        print('\nMove to start position')
        print(f'col_step: {col_step}, row_step: {row_step}, sum_step: {np.abs(col_step) + np.abs(row_step)}')
        
        return abs(col_step), abs(row_step), np.abs(col_step) + np.abs(row_step)

    def collect_col_goods(self):
        pre_col = []
        if self._robot.pos[1] - 1 in self.shelev_cols:
            pre_col.append(self._robot.pos[1]-1)
        if self._robot.pos[1] + 1 in self.shelev_cols:
            pre_col.append(self._robot.pos[1]+1)

        shelev_col = [self.store[i,x] for x in pre_col for i in range(1,self.n-1)]
        
        for entity in shelev_col:
            if entity.sku in self._robot.skus and entity.num > 0:
                idx = self._robot.skus.index(entity.sku)
                need_cnt = self._robot.nums[idx]
                if entity.num >= need_cnt:
                    self.goods[entity.sku] -= need_cnt
                    entity.num -= need_cnt
                    self._robot.nums.pop(idx)
                    self._robot.skus.pop(idx)
                else:
                    self.goods[entity.sku] -= entity.num
                    self._robot.nums[idx] -= entity.num
                    entity.num = 0
                if entity.num == 0:
                    entity.sku = -1.
                    entity.num = -1
                    entity.vis = 'O'

        self.store[self._robot.pos] = go.Road(self._robot.pos[0],self._robot.pos[1])
        self._robot.pos = (self.n - self._robot.pos[0] - 1, self._robot.pos[1])
        self.store[self._robot.pos] = self._robot
    
        return self.n -1
    
    def get_steps(self):
        return self.steps
    
    def start_tasks(self, visual=False):
        self.move_2_startPos()
        self.route_stratgy(visual)

    def route_stratgy(self, visual=False):
        print('Goods',self.show_goods())
        print('Tasks',self._robot.show_current_task(),'\n')

        # 无效订单直接取消的策略，保留该段以使用策略，注释掉则会尽量满足无效订单 #
        for sku, num in self._robot.show_current_task():
            if sku not in self.goods or self.goods[sku] < num:
                self.steps.append(0)
                print(f'No enough goods for {sku}, {num}')
                cont = self._robot.update_task()
                if not cont:
                    print('All tasks finished')
                    print('Leek goods', self.leek_goods)
                    return
                return self.start_tasks(visual)
        ###############################################################

        sum_step = 0
        while True:
            next_col = self.seek_next_postion()
            if next_col == -1:
                self.steps.append(sum_step)
                if len(self._robot.show_current_task()) != 0:
                    for sku, num in self._robot.show_current_task():
                        print(f'No enough goods for {sku}, {num}')
                        self.leek_goods[sku] = self.leek_goods.get(sku, 0) + num
                
                cont = self._robot.update_task()
                if not cont:
                    print('All tasks finished')
                    print('Leek goods', self.leek_goods)
                    return
                
                return self.start_tasks(visual)
            col_step, row_step, total_step = self.move_robot(next_col)
            sum_step += total_step
            if visual:
                print(f'col_step: {col_step}, row_step: {row_step}, sum_step: {sum_step}')
                self.visualize()
                time.sleep(0.5)
            col_step, row_step= 0, self.collect_col_goods()
            sum_step += row_step
            if visual:
                print(f'col_step: {col_step}, row_step: {row_step}, sum_step: {sum_step}')
                self.visualize()
                time.sleep(0.5)