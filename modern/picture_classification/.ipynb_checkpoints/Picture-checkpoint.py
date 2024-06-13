import os
import pickle
import cv2
import numpy as np

class Picture:
    def __init__(self,src):
        image = cv2.imread(src)
        self.data=np.array(image.reshape((-1,))/255,dtype="float64")
        self.label=np.zeros((3,),dtype="float64")
        self.label[int(os.path.split(src)[1].split("_")[0])-1]=1
        self.id=os.path.split(src)[1].split(".")[0]
    def save(self,target):
        with open(os.path.join(target,self.id),"wb") as f:
            pickle.dump(self,f)
    @staticmethod
    def load(src):
        with open(src,"rb") as f:
            return pickle.load(f)

if __name__ == "__main__":
    pass