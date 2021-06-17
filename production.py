# coding:utf-8

# 产生式类：语法规则中
#
class production:
    def __init__(self):
        self.__isitem = False     # 默认为产生式
        self.__left = ''
        self.__right = []
        # 我们并不需要把点真的表示出来，用个数字表示即可
        # 其中0表示形如S->.A的项目
        self.__dot = -1           # -1表示没有点，即产生式
        self.__next = []          # 下一字符

    # 用于项目间的比较  __eq__:==
    def __eq__(self, other):
        return self.__isitem == other.__isitem and self.__left == other.__left and self.__dot == other.__dot and\
               self.__right == other.__right and self.__next == other.__next

    def set_left(self, left):
        self.__left = left

    def set_right(self, right):
        self.__right = right

    def set_dot(self, position):
        self.__dot = position
        self.__isitem = True

    def set_next(self, Next):
        self.__next = Next

    def get_rightnum(self):
        return len(self.__right)

    def get_left(self):
        return self.__left

    def get_right(self):
        return self.__right

    def get_next(self):
        return self.__next

    def get_dotposition(self):
        return self.__dot

    def item2produc(self):
        self.__dot = -1
        self.__isitem = False
        self.__next = []

    def show(self, fd):
        fd.write('%s ->' % self.__left)
        if self.__isitem:
            length = len(self.__right)
            i = 0
            while i <= length:
                if i == self.__dot:
                    fd.write('.')
                if i != length:
                    fd.write(self.__right[i])
                i += 1
            if len(self.__next):
                # print(' ,%s'%self.__next,end='')
                fd.write(' ,')
                for i in self.__next:
                    fd.write('%s '%i)
        else:
            for i in self.__right:
                fd.write(i)
        fd.write('\n')    # 相当于一个换行符

    def get_production_str(self):
        return f'{self.__left}->{self.__right}'

    def isnull(self, nullsymbol):
        return self.__right[0] == nullsymbol
