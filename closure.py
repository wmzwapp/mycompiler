# coding:utf-8

# 闭包类：
class closure:
    def __init__(self):
        self.waited=[]          # 在计算闭包集的时候保存尚未计算过的非终结符
        self.waited_produc={}   # 在计算闭包集的时尚未计算过的非终结符对应的项目
        self.used=[]            # 在计算闭包集的时候保存计算过的非终结符
        self.items=[]           # 保存了该项目集的所有项目
        # 共有三个状态,'r/s/acc',每个闭包只能处于三个状态的其中之一，否则发生冲突，文法不属于LR1文法
        # r:该闭包中的项目都是归约项目；s:该闭包中的项目都是移进项目; acc:接收状态(唯一)
        self.__flag=''
        self.__error=False

    def __eq__(self,other):
        if len(self.items)==len(other.items):
            i=0
            while i<len(self.items):
                if self.items[i]!=other.items[i]:
                    return False
                i+=1
            return True
        return False

    def add_item(self,item):
        self.items.append(item)

    def show(self, fd):
        for i in self.items:
            i.show(fd)

    def set_flag(self,flag):
        if flag not in ['r','s','acc']:
            print('flag not accept! (allowed flag: r/s/acc)')
        elif len(self.__flag) and self.__flag!=flag:
           self.__error=True
        else: self.__flag=flag

    def get_flag(self):
        return self.__flag

    def check(self):
        return self.__error


