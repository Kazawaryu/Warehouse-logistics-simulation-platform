import numpy as np
import pandas as pd
import random
import time

import manager as ma

if __name__ == '__main__':
    generator = ma.RandomStoreGenerator(13,15,0)
    store = generator.generate_store()
    generator.generate_goods(store)
    generator.generate_supplys(store)
    rb_generator = ma.RandomRobotGenerator(store, 0, store.start_ms[0], 5, 4)
    robot = rb_generator.generate_robot()
    
    # store.start_tasks()
    # store.start_supply()
    store.round_robin(min_rate=0.5, max_rate=0.51,visual=False)
    print(store.get_info_by_col()) # 返回字典，key为列号，value为该列存储的货物信息
    print(store.get_steps())