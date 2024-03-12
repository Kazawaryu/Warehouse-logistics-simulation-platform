import numpy as np
import pandas as pd
import random
import time

import grid as go
import store as st

class RandomStoreGenerator:
    def __init__(self, n:int, m:int):
        self.n = n
        self.m = m
        self.shelves = []

    def generate_store(self):
        store = st.Store(self.n, self.m)
        i = 1 
        while i < self.m - 1:
            cont = random.choice([True, False])
            if cont and i + 1 < self.m - 1:
                self.shelves.append(i)
                self.shelves.append(i+1)
                i += 3
            else:
                self.shelves.append(i)
                i += 2
        store.create_shelevs(self.shelves)
        store.create_road()
        
        return store
    
    def generate_goods(self, store:st.Store):
        print(self.shelves)
        goods_kinds = random.randint(5,10)
        goods_typs = [i for i in range(1, goods_kinds+1)]
        goods_skus = [random.randint(10,20) for _ in range(goods_kinds)]
    
        # random generate the shelves position to place the goods
        # row:(1,self.n-1), col:(self.shelves)
        for sku, typ in zip(goods_skus, goods_typs):
            col = random.choice(self.shelves)
            row = random.randint(1, self.n-1)
            print(row, col, sku, typ)
            store.setup_shelves(row, col, sku, typ)

        return
    
class RandomRobotGenerator:
    def __init__(self) -> None:

        pass

    def generate_robot(self):

        return




if __name__ == '__main__':
    generator = RandomStoreGenerator(13,15)
    store = generator.generate_store()
    store.visualize()
    generator.generate_goods(store)
    store.visualize()
    


    # stores = [RandomStoreGenerator(13,15).generate_store() for _ in range(10)]
    # for store in stores:
    #     store.visualize()