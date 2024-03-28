import numpy as np
import pandas as pd
import random
import time

import grid as go

class Store:
    def __init__(self, n:int, m:int, upper:int):
        self.store = np.empty((n,m), dtype=object)
        self.store = self.store.astype(object)
        self.n = n
        self.m = m
        self._robot = None
        self.movable_cols = set()
        self.shelev_cols = set()
        self.start_ms = []
        self.upper = upper
        self.out_num = 0
        self.out_step = 0

        self.goods = {}
        self.leek_goods = {}
        self.task_steps = []
        self.supply_steps = []

        self.supplys = []


    def __str__(self):
        return go.visualize(self.store)
    
    def show_goods(self):
        return sorted(self.goods.items(), key=lambda x: x[0])

    
    def create_shelevs(self, col, upper):
        for i in range(1, self.n-1):
            for j in col:
                self.store[i,j] = go.Shelves(i,j,{'sku':[], 'upper':upper})

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

    def setup_shelves(self,n, m , sku):
        if not isinstance(self.store[n,m], go.Shelves):
            raise ValueError('Shelves not created yet')
        self.store[n,m].sku = sku
        self.store[n,m].vis = 'X'
        for s in sku:
            if s not in self.goods:
                self.goods[s] = 1
            else:
                self.goods[s] += 1
    
    def add_goods(self, n, m, sku):
        if not isinstance(self.store[n,m], go.Shelves):
            raise ValueError('Shelves not created yet')
        for s in sku:
            if s not in self.goods:
                self.goods[s] = 1
            else:
                self.goods[s] += 1
        self.store[n,m].sku.append(sku)
        self.store[n,m].vis = 'X'
        

    def seek_next_postion(self):
        valid_cols = set()
        for i in range(1,self.n-1):
            for j in self.shelev_cols:
                for sku in self.store[i,j].sku:
                    if sku in self._robot.skus:
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
    
    def move_2_startPos(self, startPos):
        target_n = startPos[0]
        target_m = startPos[1]
        col_step = target_m - self._robot.pos[1]
        row_step = target_n - self._robot.pos[0]

        self.store[self._robot.pos] = go.Road(self._robot.pos[0],self._robot.pos[1])
        self._robot.pos = (target_n, target_m)
        self.store[self._robot.pos] = self._robot

        print('\nMove to start position', startPos)
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
            for sku in self.store[entity.pos].sku:
                if sku in self._robot.skus:
                    idx = self._robot.skus.index(sku)
                    # remove the sku from the robot's task
                    self.goods[sku] -= 1
                    self._robot.skus.pop(idx)
                    self.out_num += 1
                if len(entity.sku) == 0:
                    entity.vis = 'O'
                    entity.sku = [-1]

        self.store[self._robot.pos] = go.Road(self._robot.pos[0],self._robot.pos[1])
        self._robot.pos = (self.n - self._robot.pos[0] - 1, self._robot.pos[1])
        self.store[self._robot.pos] = self._robot
    
        return self.n -1
    
    def get_steps(self):
        return self.task_steps, self.supply_steps
    
    def get_goods_rate(self):
        # 返回保留率
        all_goods = sum(self.goods.values())
        rate = all_goods / (self.upper * len(self.shelev_cols) * (self.n-2))
        return round(rate, 4)
    
    def start_tasks(self,min_rate, max_rate, visual):
        print('==== Start tasks ====', self.get_goods_rate())
        _,_,sum_step = self.move_2_startPos(self._robot.startPos)
        self.route_stratgy(sum_step, min_rate, max_rate, visual)
    
    def start_supply(self,min_rate, max_rate, visual):
        print('==== Start supply ====', self.get_goods_rate())
        if self.get_goods_rate() == 1:
            print('All goods are full')
            return
        elif self.get_goods_rate() > max_rate:
            print('Goods rate is more than', max_rate)
            return self.start_tasks(min_rate, max_rate, visual)

        supply = self.supplys[0]
        self.supplys = self.supplys[1:]
        _,_,sum_step = self.move_2_startPos(supply[0][0])
        if visual:
            self.visualize()
        target_col = supply[0][1]
        _,_, add_step =  self.move_robot(target_col)
        sum_step += add_step

        for i in range(1, self.n-1):
            # 从上到下遍历货架，如果货架上有空位则补货（按supply顺序依次取），同时更新supply和goods
            # supply: [((start_n, start_m),target),items]
            # items: {sku:1,sku:1,...}
            

            # 用while实现，是因为迭代中supply[1]会发生变化
            while len(self.store[i,target_col].sku) < self.upper:
                self.store[i,target_col].vis = 'X'
                if len(supply[1]) == 0:
                    break
                # 从supply中取出一个sku，放入货架
                self.store[i,target_col].sku.append(list(supply[1].keys())[0])
                # 更新supply和goods
                sku = list(supply[1].keys())[0]
                if sku not in self.goods:
                    self.goods[sku] = 1
                else:
                    self.goods[sku] += 1
                supply[1].pop(sku)
            if len(supply[1]) == 0:
                break

        self.supply_steps.append(sum_step+self.n-1)
        # 更新robot的位置，经过一个col后，robot的位置在最下面或者最上面
        self.store[self._robot.pos] = go.Road(self._robot.pos[0],self._robot.pos[1])
        self._robot.pos = (self.n - self._robot.pos[0] - 1, self._robot.pos[1])
        self.store[self._robot.pos] = self._robot

        if len(supply[1]) != 0:
            self.supplys.append(supply)

        if visual:
            print('Supply',supply)
            self.visualize()

        if len(self.supplys) == 0:
            print('No supplys')
            return
        return self.start_supply(min_rate,max_rate,visual)
        
    def route_stratgy(self, sum_step,min_rate, max_rate, visual):
        print('Goods',self.show_goods())
        print('Tasks',self._robot.show_current_task(),'\n')

        # 保留率小于min_rate时，进行补货
        if self.get_goods_rate() < min_rate:
            print('Goods rate is less than', min_rate)
            return self.start_supply(min_rate, max_rate,visual)

        # 无效订单直接取消的策略，保留该段以使用策略，注释掉则会尽量满足无效订单 #
        for sku, num in self._robot.show_current_task():
            if sku not in self.goods or self.goods[sku] < num:
                self.task_steps.append(0)
                print(f'No enough goods for {sku}, {num}')
                self.leek_goods[sku] = self.leek_goods.get(sku, 0) + num
                cont = self._robot.update_task()
                if not cont:
                    print('All tasks finished')
                    print('Leek goods', self.leek_goods)
                    return
                return self.start_tasks(visual)
        ###############################################################


        while True:
            next_col = self.seek_next_postion()
            if next_col == -1:
                self.task_steps.append(sum_step)
                if len(self._robot.show_current_task()) != 0:
                    for sku, num in self._robot.show_current_task():
                        print(f'No enough goods for {sku}, {num}')
                        self.leek_goods[sku] = self.leek_goods.get(sku, 0) + num
                
                cont = self._robot.update_task()
                if not cont:
                    print('All tasks finished')
                    print('Leek goods', self.leek_goods)
                    return
                
                return self.start_tasks(min_rate, max_rate, visual)
            col_step, row_step, total_step = self.move_robot(next_col)
            sum_step += total_step
            if visual:
                print(f'col_step: {col_step}, row_step: {row_step}, sum_step: {sum_step}')
                self.visualize()

            col_step, row_step= 0, self.collect_col_goods()
            sum_step += row_step
            if visual:
                print(f'col_step: {col_step}, row_step: {row_step}, sum_step: {sum_step}')
                self.visualize()

    def get_info_by_col(self):
        res = {}
        for col in self.shelev_cols:
            res[col] = []
            for i in range(1,self.n-1):
                sku = self.store[i,col].sku
                for s in sku:
                    if s != -1:
                        res[col].append(s)
        return res



    def round_robin(self, min_rate, max_rate, visual):
        # 任务和补货轮询，当库存小于一定值时，进行补货
        self.start_tasks(min_rate, max_rate, visual)
        