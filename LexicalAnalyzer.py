# coding:utf-8

import re
from Symbol import *

keywords = ['if', 'else', 'while', 'int', 'return', 'void']                 # 关键字
operator = ['+', '-', '*', '/', '<', '>', '<=', '>=', '!=', '=', '==']      # 运算符
delimiters = ['{', '}', '(', ')', ',', ';']                                 # 界符

class LexicalAnalyzer:

    def __init__(self, filepath):
        self.tokens = []          # 词法分析处理结果：标识符集合
        self.filepath = filepath  # 源文件路径
        self.source = ''          # 源文件内容
        self.processed = ''       # 预处理后文件的内容

    # 函数功能：预处理文件，删除注释
    def preprocessing(self):
        with open(self.filepath, 'r') as f:
            self.source = f.read()
        self.processed = self.source
        # 将单行注释删除
        comments = re.findall(r'//.*?\n', self.processed)
        if len(comments) > 0:
            for i in comments:
                self.processed = self.processed.replace(i, "")
        # 将多行注释删除，DOTALL表示 . 将匹配包括换行符的任意字符
        comments = re.findall(r'/\*.*?\*/', self.processed, flags=re.DOTALL)
        if len(comments) > 0:
            for i in comments:
                self.processed = self.processed.replace(i, "")
        # 消除换行符
        self.processed = self.processed.strip()

    # 打印出预处理过后的文件
    def display(self):
        print('预处理后的源文件:\n%s' % self.processed)
        print('词法分析器的结果:')
        for i in self.tokens:
            print(i.no, end=' ')
        print('')

    # 词法分析器处理的主体的函数
    def processing(self):
        self.preprocessing()                # 预处理
        target = self.processed
        # 给界符和运算符前加个空格,确保能正确分割字符串
        results = re.findall(r'({|}|\(|\)|,|;|\+|-|\*|/|>=|<=|>|<|==|!=|=)', target)
        index = 0
        for i in target:
            if i in delimiters or operator and i == results[0]:
                results.pop(0)
                target = target[:index] + f' {i} ' + target[index+1:]
                index += 2
            elif i+target[index+1] == results[0]:
                results.pop(0)
                target = target[:index] + f' {i+target[index+1]} ' + target[index+2:]
                index += 2
            index += 1
        # 利用空格分组,但是最后总是有一个空格产生
        self.tokens = re.split(r'\s+', target)
        del self.tokens[len(self.tokens) - 1]
        # 分好组后将标识符和数字替换成ID和NUM，并录入到符号表中
        # 这里需要注意：词法分析器处理后以及语法分析器中识别到的都是ID NUM 这是不足以识别出变量和常量的
        # 在 SymbolTable 中存储的是以 IDn 或 NUMn 为key的 Symbol 对象，其中ID/NUM的下标n是其出现的顺序
        # 在生成中间代码的时候，因为是顺序读入词法分析器处理后的tokens，所以当读到第m个ID时就在符号表中找以
        # IDm 为key在SymbolTable寻找Symbol对象
        ptr = 0
        for j in self.tokens:
            # 替换标识符并录入到符号表中
            if re.match(r'([a-zA-Z][a-zA-Z0-9_]*)', j) and j not in keywords:
                symbol = Symbol('ID', j, len(SymbolTable))
            # 替换数字并录入到符号表中
            elif re.match(r'(\d+)', j):
                symbol = Symbol('NUM', j, len(SymbolTable))
                symbol.value = int(j)
            else:
                symbol = Symbol(j, j, len(SymbolTable))
            SymbolTable.append(symbol)
            self.tokens[ptr] = symbol
            ptr += 1


if __name__ == '__main__':
    test = LexicalAnalyzer("测试文件/code.txt")
    test.processing()
    test.display()
    for i in test.tokens:
        print(i.no, i.index, i.lexeme, i.value)
