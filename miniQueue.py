import numpy as np
class miniQueue():
    
    def __init__(self, maxBuff = 10):#, currBuff = 0):
        self.data = []
        self.maxBuff = maxBuff
        # self.currBuff = currBuff
        # if currBuff == 0:
        #     self.currBuff = maxBuff
        
    def put(self,x):
        if self.size() == self.maxBuff:
            self.data.pop(0)

        self.data.append(x)
            
    def get(self):
        if len(self.data)>0:
            return self.data.pop()
    def allData(self):
        return self.data
    def size(self):
        return len(self.data)
    def full(self):
        return len(self.data)==self.maxBuff
    def erase(self):
        self.data=[]
    def mean(self):
        # if self.size() > self.currBuff:
        #     # print -self.currBuff, self.size()
        #     ret = np.mean(self.data[-self.currBuff:self.size()])
        ret = 0
        if self.size() > 0: 
            ret = np.mean(self.data)
        return ret
    def setBuffSize(self, buffSize):
        if buffSize < len(self.data):
            self.data = self.data[-buffSize:]
        self.maxBuff = buffSize
    def back(self):
        ret = 0
        if len(self.data) > 0:
            ret = self.data[-1]
        return ret
    # def getData(self):
    #     ret = []
    #     if self.size() > self.currBuff:
    #         ret = self.data[-self.currBuff:self.size()]
    #     else:
    #         ret = self.data
    #     return ret
