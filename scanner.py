# coding=utf8

from SyntacticAnalyzer import *
from LexicalAnalyzer import *
import re

def scan(input_chars, analyzer):
    input_chars.append(analyzer.endsymbol)      # 在尾部压入结束符
    stack = [analyzer.endsymbol]                # 初始分析栈底存有结束符号
    status = [0]                                # 初始状态栈底为状态0
    action = analyzer.ACTION                    # action表
    goto = analyzer.GOTO                        # goto表
    productions = analyzer.productions          # 文法产生式
    next_char = input_chars[0]                 # 即将输入的字符
    while len(input_chars):
        # 先查看action表
        # 如果分析成功
        if action[status[-1]][next_char] == 'acc':
            print('分析成功！')
            break
        # 如果需要进行规约
        elif re.match(r'r\d+', action[status[-1]][next_char]):
            pro_index = int(action[status[-1]][next_char][1:])
            production = productions[pro_index]
            # 将分析栈中长度为 right_len 的内容弹出，压入产生式左部的字符
            # 将状态栈中 right_len 个状态弹出
            right_len = production.get_rightnum()
            del stack[-right_len:]
            del status[-right_len:]
            stack.append(production.get_left())
            # 从goto表中找下一个状态
            next_status = goto[status[-1]][stack[-1]]
            status.append(next_status)
        # 将新的状态和即将输入的字符分别压进状态栈和分析栈
        elif re.match(r's\d+', action[status[-1]][next_char]):
            next_status = int(action[status[-1]][next_char][1:])
            status.append(next_status)
            stack.append(next_char)
            del input_chars[0]
            next_char = input_chars[0]
        else:
            print('在action表中找不到相应的动作,分析退出！')
            print('status=%d,next_char=%s' % (status[-1], next_char))
            break


if __name__ == '__main__':
    code_path = '../测试文件/code.txt'
    grammar_path = '../测试文件/rule.txt'
    # 初始化词法分析器
    analyzerL = LexicalAnalyzer(code_path)
    analyzerL.processing()
    token = analyzerL.tokens
    print(token)
    # 初始化语法分析器
    analyzerS = SyntacticAnalyzer()
    analyzerS.readfile(grammar_path)
    analyzerS.analyze(grammar_path)
    # 扫描器开始分析程序
    analyzerS.display_closures()
    analyzerS.display_goto()
    analyzerS.display_action()
    scan(token, analyzerS)
