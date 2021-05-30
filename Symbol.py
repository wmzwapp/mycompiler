# coding=utf8

# 单词符号表
SymbolTable = []

# Symbol类的一个实例表示一类单词符号
class Symbol:
    def __init__(self, id, type):
        self.no = len(SymbolTable)        # 单词编号
        self.id = id                        # 单词符号的属性值
        self.type = type                    # 单词种别
