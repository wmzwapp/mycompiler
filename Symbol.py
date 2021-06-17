# coding=utf8

# 单词符号表
# class SymbolTable:
#     def __init__(self):
#         self.T = {}
#         self.id_count = 0
#         self.num_count = 0
#         self.tmp_count = 0


# 全局变量，在整个编译过程使用到的符号表
SymbolTable = []

# # 往符号表中添加一个变量
# def add_symbol(no, lexeme):
#     symbol = Symbol()
#     symbol.no = no
#     symbol.lexeme = lexeme

# Symbol类的一个实例表示一类单词符号
class Symbol:
    def __init__(self, no, lexeme, index):
        self.no = no            # 符号经过词法分析处理之后的结果
        self.value = None       # 符号的值
        self.lexeme = lexeme    # 符号的表示
        self.index = index      # 符号的在符号表中的索引
        self.type = None        # 符号的类型

