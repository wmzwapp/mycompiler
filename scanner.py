# coding=utf8
import Symbol
from SyntacticAnalyzer import *
from LexicalAnalyzer import *
from Symbol import *
import re

# # 符号类,包含一个符号的信息
# class Symbol:
#     def __init__(self):
#         self.name = None        # 符号的标识符
#         self.type = None        # 类型
#         self.size = None        # 占用字节数
#         self.offset = None      # 内存偏移量
#         self.place = None       # 对应的中间变量
#         self.function = None    # 所在函数

# # 函数符号
# class FunctionSymbol:
#     def __init__(self):
#         self.name = None        # 函数的标识符
#         self.type = None        # 返回值类型
#         self.label = None       # 入口处的标签
#         self.params = []        # 形参列表
#         self.temp = []          # 局部变量列表


# 语法分析栈
GA_Stack = []
# 语义分析栈
SA_Stack = []
# 中间代码
middle_code = []

def scan(input_chars, analyzer):
    # 在尾部压入结束符
    symbol = Symbol(analyzer.endsymbol, analyzer.endsymbol, len(SymbolTable))
    SymbolTable.append(symbol)
    input_chars.append(symbol)
    GA_Stack.append(symbol)                     # 初始分析栈底存有结束符号
    status = [0]                                # 初始状态栈底为状态0
    action = analyzer.ACTION                    # action表
    goto = analyzer.GOTO                        # goto表
    productions = analyzer.productions          # 文法产生式
    next_char = input_chars[0]                  # 即将输入的字符
    fd = open('result/parser_processing.txt', 'w')
    while len(input_chars):
        # 如果分析成功
        if action[status[-1]][next_char.no] == 'acc':
            fd.write('分析成功！\n')
            break
        # 如果需要进行规约
        elif re.match(r'r\d+', action[status[-1]][next_char.no]):
            pro_index = int(action[status[-1]][next_char.no][1:])
            production = productions[pro_index]
            # 将分析栈中长度为 right_len 的内容弹出，将状态栈中 right_len 个状态弹出
            # 注意空字符长度为0，此时我们不应该 pop stack 和 status 中的内容
            if production.get_right()[0] != analyzer.nullsymbol:
                right_len = production.get_rightnum()
                # 进行语义分析并产生中间代码
                semantic_analyzer(production.get_left(), GA_Stack[-right_len:])
                del GA_Stack[-right_len:]
                del status[-right_len:]
            else:
                semantic_analyzer(production.get_left(), [])
            # 压入产生式左部的字符
            GA_Stack.append(Symbol(production.get_left(), production.get_left(), -1))
            # 从goto表中找下一个状态
            next_status = goto[status[-1]][GA_Stack[-1].no]
            status.append(next_status)
            fd.write('使用产生式%d:%s规约 stack=%s   status=%s\n' % (pro_index, production.get_production_str(),
                                                              (lambda y: x.no for x in GA_Stack), status))
        # 将新的状态和即将输入的字符分别压进状态栈和分析栈
        elif re.match(r's\d+', action[status[-1]][next_char.no]):
            next_status = int(action[status[-1]][next_char.no][1:])
            status.append(next_status)
            # 压入语法分析栈
            GA_Stack.append(next_char)
            # 压入语义分析栈
            SA_Stack.append(next_char)
            del input_chars[0]
            next_char = input_chars[0]
            fd.write('移进  stack=%s  status=%s next_char=%s\n' % ((lambda y: x.no for x in GA_Stack), status, next_char.no))
        else:
            fd.write('在action表中找不到相应的动作,分析退出！\n')
            fd.write('status=%d,next_char=%s\n' % (status[-1], next_char.no))
            break

# 语义分析子程序，同时生成目标代码
def semantic_analyzer(proc_left, proc_right):
    # 先为规约的产生式左部创建一个 Symbol 对象,index 为-1表示不加到符号表中，中间的临时变量没必要加到符号表
    symbol = Symbol(proc_left, proc_left, -1)
    if len(proc_right) == 0:
        kong = Symbol('空', '', -1)
        kong.value = 0
        proc_right.append(kong)
    # <赋值语句> ::= ID = <表达式>
    if proc_left == '<赋值语句>':
        proc_right[0].value = proc_right[2].value
        middle_code.append(f'{proc_right[0].lexeme} = {proc_right[2].lexeme}')
    # <表达式> ::= <加法表达式> <表达式>'
    elif proc_left == '<表达式>' and proc_right[0].no == '<加法表达式>':
        # 如果 <表达式>' 推导为空
        if not proc_right[1].value:
            symbol.value = proc_right[0].value
            symbol.lexeme = proc_right[0].lexeme
    # <加法表达式> := <项> <加法表达式>'
    elif proc_left == '<加法表达式>' and proc_right[0].no == '<项>':
        if proc_right[1].value:
            symbol.value = proc_right[0].value + proc_right[1].value
            symbol.lexeme = proc_right[0].lexeme + proc_right[1].lexeme
            middle_code.append(f'{symbol.lexeme} = {proc_right[0].lexeme} + {proc_right[1].lexeme}')
    # <加法表达式>' ::= + <加法表达式> 或 <加法表达式>' ::= - <加法表达式>
    elif proc_left == '<加法表达式>\'' and (proc_right[0].no == '+' or proc_right[0].no == '-'):
        if proc_right[0].no == '+':
            symbol.value = proc_right[1].value
            middle_code.append(f'{symbol.lexeme} = {proc_right[1].lexeme}')
        else:
            symbol.value = - proc_right[1].value
            middle_code.append(f'{symbol.lexeme} = - {proc_right[1].lexeme}')
    # <项> ::= <因子> <项>'
    elif proc_left == '<项>' and proc_right[0] == '<因子>':
        if proc_right[1].value:
            # 注意了，本程序只支持整数类型，因此这里要强转一下
            symbol.value = int(proc_right[0].value * proc_right[1].value)
            middle_code.append(f'{symbol.lexeme} = {proc_right[0].lexeme} * {proc_right[1].lexeme}')
    # <项>' ::= * <项> 或 <项>' ::= / <项>
    elif proc_left == '<项>\'':
        if proc_right[0] == '*':
            symbol.value = proc_right[1].value
            middle_code.append(f'{symbol.lexeme} = {proc_right[1].lexeme}')
        elif proc_right[0] == '/':
            symbol.value = 1 / proc_right[1].value
            middle_code.append(f'{symbol.lexeme} = 1/{proc_right[1].lexeme}')
    # <因子> := NUM 或 <因子> ::= ( <表达式> )
    elif proc_left == '<因子>':
        if proc_right[0].no == 'NUM':
            symbol.value = proc_right[0].value
            middle_code.append(f'{symbol.lexeme} = {proc_right[0].value}')
        elif proc_right[1].no == '(':
            symbol.value = proc_right[1].value
    # 将产生式右部的字符弹出语义分析栈并将产生式左部的字符压入分析栈
    if proc_right[0].no != '空':
        del SA_Stack[-len(proc_right):]
    SA_Stack.append(symbol)


if __name__ == '__main__':
    code_path = '测试文件/code.txt'
    grammar_path = '测试文件/newrule.txt'
    # 初始化词法分析器
    analyzerL = LexicalAnalyzer(code_path)
    analyzerL.processing()
    token = copy.deepcopy(analyzerL.tokens)
    # 初始化语法分析器
    analyzerS = SyntacticAnalyzer()
    analyzerS.analyze(grammar_path)
    # 展示语法分析后的结果
    analyzerS.display_closures()
    analyzerS.display_goto()
    analyzerS.display_action()
    # 扫描器开始分析程序
    scan(token, analyzerS)
    for i in middle_code:
        print(i)
