# coding:utf-8

import LexicalAnalyzer
import production as PRO
import re
import copy
import closure as CLO

# 语法分析器类
class SyntacticAnalyzer:
    def __init__(self):
        self.productions = []           # 一个产生式对应list中的一个str
        self.terminals = {}             # 终结符集，存储为一个dict
        self.nonterminals = {}          # 非终结符集，存储为一个dict
        self.allsymbols = []            # 文法全体符号，终结符+非终结符
        self.startsymbol= ''             # 开始符号
        self.endsymbol= ''               # 终结符号
        self.nullsymbol= ''              # 空字符
        self.firstset={}                # first集
        self.closures=[]                # LR1项目集族，每个元素都是一个closure
        self.error=False                # 发生冲突，该文法不是LR1文法
        self.ACTION=[]                  # action表
        self.GOTO=[]                    # goto表
        self.GO=[]                      # go函数

    # 读取文件中的非终结符、终结符、产生式，并将产生式转化为项目（读取语法规则）
    # 输入：语法规则文件路径
    # 输出：无
    def readfile(self, filepath):
        with open(filepath, 'r') as f:
            allin = f.read()               # 一次性全部读取
        allin = re.split('\nseparator\n?', allin)
        tmp_nonterminals = allin[0]
        tmp_terminals = allin[1]
        tmp_productions = allin[2]
        tmp_symbols = allin[3]
        tmp_nonterminals = re.split('\n', tmp_nonterminals)   # 得到了非终结符的集合
        tmp_terminals = re.split('\n', tmp_terminals)         # 得到了终结符的集合
        tmp_productions = re.split('\n', tmp_productions)     # 得到了产生式字符串的集合
        tmp_symbols = re.split('\n', tmp_symbols)
        # 获得源程序开始符号、结束符号和空字符
        self.startsymbol = tmp_symbols[0]
        self.endsymbol = tmp_symbols[1]
        self.nullsymbol = tmp_symbols[2]
        # 获得非终结符集、终结符集、产生式集和所有符号的first集
        self.get_terminals(*tmp_terminals)
        self.get_nonterminals(*tmp_nonterminals)
        self.allsymbols = list(self.nonterminals.values()) + list(self.terminals.values())
        self.get_productions(*tmp_productions)
        self.create_first()

    # 获取终结符集，以空格划分
    def get_terminals(self,*tmp_terminals):
        for temp in tmp_terminals:
            temp=re.split(r'\s',temp)
            self.terminals[int(temp[1])]=temp[0]    #将终结符按照dict存储，每个数字(key)都对应唯一的终结符(value)

    # 获取非终结符集
    def get_nonterminals(self,*tmp_nonterminals):
        for temp in tmp_nonterminals:
            temp=re.split(r'\s',temp)
            self.nonterminals[int(temp[1])]=temp[0]    #同上

    # 产生式有一个特点，右部的每个符号之间都有一个空格隔开，因此我们可以利用这个来得到右部的每一个符号
    def get_productions(self, *tmp_productions):
        length = len(tmp_productions)
        i = 0
        while i < length:
            tmp_produc = PRO.production()
            temp = tmp_productions[i]
            temp = re.split('::=', temp)
            tmp_right = re.split(r'\s', temp[1])
            tmp_produc.set_left(temp[0])
            tmp_produc.set_right(tmp_right)
            self.productions.append(tmp_produc)
            i += 1

    # 用于构造全体符号的first集，并保存在类成员firstset当中，每个非终结符(key)对应一组set(values)
    # 非递归方法，因此比较长
    def create_first(self):
        self.initset()
        change=True               # 判断整个first集是否变化
        while change:
            change=False
            for nonterm in self.nonterminals.values():    # 对于每一个非终结符
                if nonterm in self.firstset:              # 判断nonterm的first集是否为空
                    empty=False
                else:
                    empty=True
                for produc in self.productions:           # 遍历所有的产生式寻找该非终结符在左边的产生式
                    if nonterm==produc.get_left():
                        tmp_right=produc.get_right()
                        length=len(tmp_right)
                        i=0
                        findnext=True
                        if empty:      # check用于检查nonterm的first集是否变化
                            check=0
                        else: check=len(self.firstset[nonterm])
                        # 如果没超过产生式右部的长度且可以继续下去(遇到终结符或遇到的非终结符的first集含空)
                        while i < length and findnext:
                            # 如果产生式右部第i个字符是非终结符且此非终结符first集不为空
                            if tmp_right[i] in self.nonterminals.values() and tmp_right[i] in self.firstset:
                                if empty:    # nonterm 的 first 集为空
                                    self.firstset[nonterm] = copy.deepcopy(self.firstset[tmp_right[i]])
                                    empty = False
                                else:
                                    self.firstset[nonterm] = self.firstset[nonterm] | self.firstset[tmp_right[i]]  # 并集
                                # 如果tmp[i]的first集包含空且temp[i]不是产生式右部的最后一个字符,针对产生式 produc 继续搜索，并将空字符从first集删除
                                if self.nullsymbol in self.firstset[tmp_right[i]] and i != length-1:
                                    findnext = True
                                    self.firstset[nonterm].remove(self.nullsymbol)
                                else:
                                    findnext = False
                            # 如果产生式右部的第i个字符是终结符
                            elif tmp_right[i] in self.terminals.values():
                                self.firstset[nonterm].add(tmp_right[i])
                                findnext=False
                            # 产生式右部的第i个非终结符first集为空
                            else:
                                findnext=False
                            i += 1
                        # 判断nonterm的first集是否改变
                        if not empty:
                            if check != len(self.firstset[nonterm]):
                                change = True

    # 用于初始化部分first集：
    # 即仅针对产生式右部第一个字符是终结符的情况，将该终结符加入到产生式左部的非终结符的first集当中
    # 对于所有的终结符，其first集就是自己
    def initset(self):
        for nonterm in self.nonterminals.values():
            for produc in self.productions:
                if nonterm==produc.get_left():
                    tmp=produc.get_right()
                    if tmp[0] in self.terminals.values():
                        # 将first集保存为set，可用交并集
                        if nonterm in self.firstset:
                            self.firstset[nonterm].add(tmp[0])
                        else: self.firstset[nonterm]={tmp[0]}
        for term in list(self.terminals.values())+[self.endsymbol]:
            self.firstset[term]={term}

    # 用于构造LR1文法项目集规范族
    # 从第一个项目集出发，扫描其项目后得到初步的项目集，然后送入get_closure进行完善
    # 同时完善go函数的值
    def create_closures(self):
        # 首先创建初始状态集
        self.get_firstclosure()
        num = -1    # 状态的序号
        # 对于闭包集中的每一个闭包，因为list是有序的，因此总是可以循环完
        for closure in self.closures:
            if self.error:
                break
            num += 1
            golist = {}
            # 每输入一个字符就有可能转移到别的状态，可以理解为循环一次就得到一个新的状态
            # 跳过全是规约项目和接收项目的闭包集
            if closure.get_flag() == 'r' or closure.get_flag() == 'acc':
                self.GO.append(golist)
                continue
            # 每次输入一个符号，遍历该闭包集中的所有项目，查看是否能拓展出新的闭包集
            for symbol in self.allsymbols:
                if self.error:
                    break
                if symbol == self.nullsymbol:
                    continue
                new_closure = CLO.closure()
                for item in closure.items:
                    temp_right = item.get_right()
                    dot = item.get_dotposition()
                    if temp_right[dot] == symbol:
                        # 将该项目向后展望一个字符（dot+1）得到新项目，同时判断新项目的类型，赋予新闭包状态类型
                        temp_item = copy.deepcopy(item)
                        temp_item.set_dot(dot+1)
                        new_closure.add_item(temp_item)
                        # 对于acc和r这两种类型我们可以直接填写action表了
                        if temp_item.get_rightnum() == dot+1:
                            if item.get_left() == self.startsymbol:
                                new_closure.set_flag('acc')
                            else: 
                                new_closure.set_flag('r')
                        else: 
                            new_closure.set_flag('s')
                        # 判断新的闭包集（状态集）是否存在矛盾状态
                        if new_closure.check():
                            self.error=True
                            print('conflic occured, the closure:')
                            new_closure.show()
                            break
                        # 判断完毕，将必要信息加入到new_closure中
                        if new_closure.get_flag() == 's':
                            if temp_right[dot+1] in self.nonterminals.values():
                                if temp_right[dot+1] not in new_closure.waited:
                                    new_closure.waited.append(temp_right[dot+1])
                                if temp_right[dot+1] in new_closure.waited_produc:
                                    new_closure.waited_produc[temp_right[dot+1]].append(temp_item)
                                else:
                                    new_closure.waited_produc[temp_right[dot+1]]=[temp_item]
                # 构造新的状态集，同时补充go函数
                if len(new_closure.items):
                    next_num = self.get_closure(new_closure)
                    golist[symbol] = next_num
                else:
                    golist[symbol] = 'none'
            # 当前状态的go函数
            self.GO.append(golist)

    # 用于构造一个完整项目集,与get_firstclosure()思路一致
    def get_closure(self, closure):
        while len(closure.waited):
            target = closure.waited.pop()
            # if len(closure.waited_produc[target])==0:
            #     del closure.waited_produc[target]
            #     target=closure.waited.pop()
            # 求first(target之后的一个字符),若first集含空，则将first(next)也加入
            # 若target之后的一个字符不存在，则算first(next)
            # temp_item=closure.waited_produc[target].pop()
            temp_item = closure.waited_produc[target].pop()
            dot=temp_item.get_dotposition()
            # target之后的第一个字符不存在，即target是temp_item右部的最后一个字符
            if temp_item.get_rightnum()==dot+1:
                temp_next=copy.deepcopy(temp_item.get_next())
            # target之后还有字符，顺势求出next
            else:
                temp_right=temp_item.get_right()
                temp_next=copy.deepcopy(self.firstset[temp_right[dot + 1]])
                if self.nullsymbol in temp_next:
                    temp_next.remove(self.nullsymbol)
                    for next in temp_item.get_next():
                        temp_next=temp_next | self.firstset[next]
            # 将所有以target为左部的产生式加上刚求出的next作为新的item加入到closure中
            for i in self.productions:
                if i.get_left()==target:
                    temp=copy.deepcopy(i)
                    temp.set_dot(0)
                    temp.set_next(temp_next)
                    if temp not in closure.items:
                        closure.add_item(temp)
                    # 同时记录下一个target和waited_produc
                    if i.get_right()[0] in self.nonterminals.values():
                        next_target=i.get_right()[0]
                        if next_target not in closure.used and next_target!=target and next_target not in closure.waited:
                            closure.waited.append(next_target)
                            closure.waited_produc[next_target]=[temp]
                            # if next_target in closure.waited_produc and temp not in closure.waited_produc[next_target]:
                            #     closure.waited_produc[next_target].append(temp)
                            # else: closure.waited_produc[next_target]=[temp]
            closure.used.append(target)
        num=self.check_closure(closure)
        # closure不存在原闭包集中
        if num==-1:
            self.closures.append(closure)
            return len(self.closures) - 1
        else: return num

    # 根据GO函数计算action表和goto表
    def get_action_goto(self):
        num = 0
        for closure in self.closures:
            # 构造action表
            actionlist = {}
            for term in list(self.terminals.values()) + [self.endsymbol]:
                # action 表中不包含空字符
                if term == self.nullsymbol:
                    continue
                # 遍历项目集规范簇中每一个项目
                for item in closure.items:
                    dot = item.get_dotposition()
                    right_len = len(item.get_right())
                    # 满足 A->S., term 或者 A->._, term
                    if dot == right_len or (item.get_right()[dot] == self.nullsymbol and dot == 0):
                        if term in item.get_next():
                            tmp_produc = copy.deepcopy(item)
                            tmp_produc.item2produc()
                            if closure.get_flag() != 'acc':
                                actionlist[term] = 'r' + str(self.productions.index(tmp_produc))
                            else:
                                actionlist[term] = 'acc'
                            break
                        else:
                            actionlist[term] = 'none'
                    # 满足 A->B.term C, b 或者 A->B.term, b
                    elif dot < right_len:
                        if term == item.get_right()[dot]:
                            actionlist[term] = 's' + str(self.GO[num][term])
                            break
                        else:
                            actionlist[term] = 'none'

                    else:
                        actionlist[term] = 'none'
            self.ACTION.append(actionlist)
            # 构造goto表
            goto = {}
            for nonterm in self.nonterminals.values():
                if nonterm == self.startsymbol:
                    continue
                if closure.get_flag() == 's' and self.GO[num][nonterm] != 'none':
                    goto[nonterm] = self.GO[num][nonterm]
                else:
                    goto[nonterm] = 'none'
            self.GOTO.append(goto)
            num += 1

    # 用于创造第一个项目集
    def get_firstclosure(self):
        firstclosure = CLO.closure()
        for i in self.productions:
            if i.get_left() == self.startsymbol:
                temp = copy.deepcopy(i)
                temp.set_dot(0)
                temp.set_next(self.endsymbol)  # 构造第一个项目
                break
        firstclosure.add_item(temp)         # 将该项目加入到项目集中
        firstclosure.waited.append(temp.get_right()[0])         # 将未计算过的非终结符加入到waited中
        firstclosure.waited_produc[temp.get_right()[0]]=[temp]   # 将该项目记录下来，用于计算next
        while len(firstclosure.waited):
            target=firstclosure.waited.pop()
            # 求first(target之后的一个字符),若first集含空，则将first(next)也加入
            # 若target之后的一个字符不存在，则算first(next)
            temp_item = firstclosure.waited_produc[target].pop()
            dot = temp_item.get_dotposition()
            # target之后的第一个字符不存在，即target是temp_item右部的最后一个字符
            if temp_item.get_rightnum() == dot+1 or temp_item.get_rightnum() == dot:
                temp_next = copy.deepcopy(temp_item.get_next())
            # target之后还有字符，顺势求出next
            else: 
                temp_right = temp_item.get_right()
                temp_next = copy.deepcopy(self.firstset[temp_right[dot + 1]])
                if self.nullsymbol in temp_next:
                    temp_next.remove(self.nullsymbol)
                    for next in temp_item.get_next():
                        temp_next = temp_next | self.firstset[next]
            # 将所有以target为左部的产生式加上刚求出的next作为新的item加入到closure中
            for i in self.productions:
                if i.get_left() == target:
                    temp = copy.deepcopy(i)
                    temp.set_dot(0)
                    temp.set_next(temp_next)
                    if temp not in firstclosure.items:
                        firstclosure.add_item(temp)
                    # 同时记录下一个target和waited_produc
                    if i.get_right()[0] in self.nonterminals.values():
                        next_target=i.get_right()[0]
                        if next_target not in firstclosure.used and next_target!=target and next_target not in firstclosure.waited:
                            firstclosure.waited.append(next_target)
                            firstclosure.waited_produc[next_target]=[temp]
                            # if next_target in firstclosure.waited_produc and temp not in firstclosure.waited_produc[next_target]:
                            #     firstclosure.waited_produc[next_target].append(temp)
                            # else: firstclosure.waited_produc[next_target]=[temp]
            firstclosure.used.append(target)
            # del firstclosure.waited_produc[target]
        # 第一个状态里的项目全都是移进项目，因为是拓广文法
        firstclosure.set_flag('s')
        self.closures.append(firstclosure)

    # 用于检查closure是否已经存在于闭包集closures中,若存在则返回序号，不存在则返回-1
    def check_closure(self, closure):
        for closure_a in self.closures:
            if closure_a == closure:
                return self.closures.index(closure_a)
        return -1

    def display_symbols(self):
        print(self.nonterminals)
        print(self.terminals)

    def display_productions(self):
        print('these are productions:')
        for i in self.productions:
            i.show()

    def display_first(self):
        print('these are first_set:')
        for i in self.firstset:
            print('%s:%s' % (i, self.firstset[i]))

    def display_closures(self):
        print('closure num = %d' % len(self.closures))
        fd = open("result/closure.txt", 'w')
        for i in self.closures:
            fd.write('closure %d:\n' % self.closures.index(i))
            i.show(fd)
        fd.close()

    def display_go(self):
        num = 0
        for i in self.GO:
            print('\n状态编号:%d ' % num, end='')
            for j in i:
                print('%s:%s ' % (j, i[j]), end='')
            num += 1

    def display_action(self):
        fd = open("result/action表.txt", 'w')
        count = 0
        for i in self.ACTION:
            fd.write('status%d: %s\n' % (count, i))
            count += 1
        fd.close()

    def display_goto(self):
        fd = open('result/goto表.txt', 'w')
        count = 0
        for i in self.GOTO:
            fd.write('status%d: %s\n' % (count, i))
            count += 1
        fd.close()

    def analyze(self, filepath):
        # 读入语法规则
        self.readfile(filepath)
        # 构造项目集规范族
        self.create_closures()
        if not self.error:
            # 构造action表和goto表
            self.get_action_goto()


if __name__ == '__main__':
    toy = SyntacticAnalyzer()
    toy.analyze('测试文件/easyrule.txt')
    toy.display_closures()
    toy.display_action()
    toy.display_goto()
    toy.display_productions()




  