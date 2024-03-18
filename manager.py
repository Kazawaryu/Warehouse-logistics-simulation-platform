import numpy as np
import pandas as pd
import random
import time

import grid as go
import store as st

class RandomStoreGenerator:
    def __init__(self, n:int, m:int, skip:int):
        self.n = n
        self.m = m
        self.skip = skip
        self.upper = 3
        self.shelves = []

    def generate_store(self):
        store = st.Store(self.n, self.m, self.upper)
        i,last,iter = 1, 0, 0
        start_ms = []
        while i < self.m - 1:
            if last + self.skip == iter:
                start_ms.append(i - 1)
                last = iter + 1
            cont = random.choice([True, False])
            if cont and i + 1 < self.m - 1:
                self.shelves.append(i)
                self.shelves.append(i+1)
                iter += 1
                i += 3
            else:
                self.shelves.append(i)
                iter += 1
                i += 2
        store.create_shelevs(self.shelves, self.upper)
        start_ms.append(self.shelves[-1]+1)
        store.create_road()
        store.fix_start_pos(start_ms)
        
        return store
    
    def generate_goods(self, store:st.Store, rate:float=0.5, keeping=0.8):
        goods_kinds = random.randint(5, 10)
        all_shelves = [(_n, _m) for _m in self.shelves for _n in range(1,self.n-2)]
        goods_shelves = random.sample(all_shelves, int(keeping*len(all_shelves)))
        goods_obj = [random.randint(1,goods_kinds) for _ in range(int(rate*self.upper*len(self.shelves)*(self.n-2)))]

        while len(goods_obj) > 0:
            _n, _m = random.choice(goods_shelves)
            sku = random.sample(goods_obj, min(random.randint(1,self.upper), len(goods_obj)))
            store.setup_shelves(_n, _m, sku)
            for _ in sku:
                goods_obj.remove(_)

        return
    
    def generate_supplys(self, store:st.Store, supply_num:int=5):
        # 暂时每个补货任务的商品数最大值为10
        item_num = random.randint(1, 10)

        for _ in range(supply_num):
            items = {}
            for _ in range(item_num):
                sku = random.randint(1,5)
                items[sku] = 1
            start_n = random.choice([0, store.n-1])
            start_m = random.choice(store.start_ms)
            target = random.choice(list(store.shelev_cols))
            store.supplys.append((((start_n, start_m),target),items))

        return   
    
class RandomRobotGenerator:
    def __init__(self, store:st.Store,n:int, m:int, task_num:int, u:int):
        self.store = store
        self.pos = (n,m)
        self.task_num = task_num
        self.u = u

    def generate_robot(self):
        tasks = self.generate_tasks()
        self.robot = self.store.create_robot(self.pos[0],self.pos[1], {'tasks': tasks})

        return self.robot

    def generate_tasks(self):
        tasks = []
        item_num = random.randint(1,self.u)
        for _ in range(self.task_num):
            items = {}
            for _ in range(item_num):
                sku = random.randint(1,5)
                items[sku] = 1
            start_n = random.choice([0, self.store.n-1])
            start_m = random.choice(self.store.start_ms)
            tasks.append(((start_n, start_m),items))

        return tasks
