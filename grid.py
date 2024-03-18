import time

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
        self.vis = 'P'

class Road(Grid):
    def __init__(self, n, m,param={}):
        super().__init__(n, m, param)
        self.vis = '.'

class Robot(Grid):
    def __init__(self, n, m,param={}):
        super().__init__(n, m, param)
        self.startPos = (-1,-1)
        self.vis = '#'
        self.tasks = param['tasks']
        self.update_task()

    def update_task(self):
        self.nums = []
        self.skus = []
        if len(self.tasks) == 0:
            return False
        task = self.tasks[0]
        self.tasks = self.tasks[1:]
        self.startPos = task[0]
        for item in task[1].items():
            self.nums.append(item[1])
            self.skus.append(item[0])

        return True

    def seek_col(self):
        n,m = self.map.shape
        valid_cols = []
        shelf_col = [j for j in range(m) if isinstance(self.map[self.pos[0],j], Shelves)]
        for i in range(1,n-1):
            for j in shelf_col:
                if self.map[i,j].num in self.nums:
                    valid_cols.append((i,j))

        if len(valid_cols) == 0:
            return -1
        else:
            valid_cols.sort(key=lambda x: abs(x[1]-self.pos[1]))
            return valid_cols[0][1] 
      
    def show_current_task(self):
        return list(zip(self.skus, self.nums))

class Shelves(Grid):
    def __init__(self, n, m,param={}):
        super().__init__(n, m, param)
        self.upper = param['upper']
        self.vis = 'O'
        self.sku = param['sku']

def visualize(store):
    n,m = store.shape
    for i in range(n):
        for j in range(m):
            print(store[i,j], end=' ')
        print()
    print('='*40)
    time.sleep(0.5)
 