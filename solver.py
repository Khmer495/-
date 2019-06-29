import re
import sys
import pyperclip
import pandas as pd

question_data = pd.read_csv('question_data.csv')
#print(question_data)

answering_number = list(range(1,len(question_data)+1))
ans_system = ''

#system = input()
#system_name = 'EvalNatExp'
#input = input()
#judged = 'Z + S(S(Z)) evalto S(S(Z))'

nat_pattern = r'\(*(S\()*Z\)*'
nat_pattern = re.compile(nat_pattern)
ml_pattern = r'\(*-*\d+\)*|\(*true\)*|\(*false\)*'
ml_pattern = re.compile(ml_pattern)
int_pattern = r'-*\d+'
int_pattern = re.compile(int_pattern)
op_lang = {'plus':'plus','minus':'minus','times':'times','is less than':'is_less_than','evalto':'evalto','--->':'_z_l','-*->':'_o_l','-d->':'_d_l','less than':'less_than','|-':'l_','->':'_l','==>':'zzl','=>':'zl','>>':'ll'}
op_symb_list = ['+','*','-','<']
op_nomean_list = ['is','if','then','else']
system_list = {'Nat':'nat','CompareNat1':'nat','CompareNat2':'nat','CompareNat3':'nat','EvalNatExp':'nat','ReduceNatExp':'nat','EvalML1':'ml','EvalML1Err':'ml','EvalML2':'ml'}
bool_list = ['true','false']
var_list = ['x','y']

def solve(question_number,system_name,judged,correct_derivation):
    print('Q{} {},{}:'.format(question_number,system_name,judged),end="")

    if system_name not in system_list:
        print('{} is wrong system'.format(system_name))
        sys.exit()

    if system_list[system_name] == 'nat':
        x_pattern = nat_pattern
    else:
        x_pattern = ml_pattern

    judged = judged.replace('is less than','is_less_than').replace('less_than','less_than').replace(',',' ,')
    judged_word = judged.split()
    judged_split = []

    for i in range(len(judged_word)):
        ###opの追加
        judged_word[i] = judged_word[i].replace('is_less_than','is less than').replace('less_than','less than')
        if judged_word[i] in op_lang:
            op = op_lang[judged_word[i]]

        left_cnt = judged_word[i].count('(')
        right_cnt = judged_word[i].count(')')
        if left_cnt > right_cnt:
            for _ in range(left_cnt-right_cnt):
                judged_split.append('(')
            judged_split.append(judged_word[i][left_cnt-right_cnt:])
        elif left_cnt < right_cnt:
            judged_split.append(judged_word[i][:-(right_cnt-left_cnt)])
            for _ in range(right_cnt-left_cnt):
                judged_split.append(')')
        else:
            judged_split.append(judged_word[i])

    #print(op,judged_split)
    system_class = eval('{}'.format(system_name))()
    ans = eval('system_class.{}'.format(op))(judged_split)
    ans = ans.replace(' ,',',')

    if correct_derivation != correct_derivation:
        print('correct derivation does not exist')
        print(ans)
        pyperclip.copy('{}\n'.format(repr(ans)[1:-1]))
        input()
    elif repr(ans)[1:-1] == correct_derivation:
        print('correct')
        #print(ans)
    else:
        print('wrong')
        print(ans)

class tool():
    def judged_ordering(self,judged):
        env_exist = False
        if '|-' in judged:
            env_exist = True
            env, judged = self.judged_ordering_env(judged)
            #print(2222,env,judged)
            let, judged = self.judged_ordering_let(judged)
            #print(3333,let,judged)
        judged = self.judged_ordering_branket(judged)
        #print(judged)
        judged = self.judged_ordering_if(judged)
        #print(judged)
        judged = self.judged_ordering_times(judged)
        #print('times',judged)
        judged = self.judged_ordering_plus_minus(judged)
        #print('pm',judged)
        judged = self.judged_ordering_less_than(judged)
        #print('lt',judged)
        if env_exist:
            return(env,let,judged)
        else:
            return(judged)

    def judged_ordering_env(self,judged):
        index_env = judged.index('|-')
        env_tmp = judged[:index_env]
        judged = judged[index_env+1:]
        env = []
        if len(env_tmp) > 0:
            while ',' in env_tmp:
                comma_index = env_tmp.index(',')
                env.append(env_tmp[:comma_index])
                env_tmp = env_tmp[comma_index+1:]
            env.append(env_tmp)
        return(env, judged)

    def judged_ordering_let(self,judged):
        let = []
        while 'let' in judged:
            #print(judged)
            cnt = 1
            for i in range(1,len(judged)):
                if judged[i] == 'let':
                    cnt += 1
                elif judged[i] == 'in':
                    cnt -= 1
                if cnt == 0:
                    in_index = i
                    break
            let.append(judged[1:in_index])
            judged = judged[in_index+1:]
        return(let, judged)

    def judged_ordering_branket(self,judged):
        #print(judged)
        while '(' in judged:
            #print(judged)
            left_index = judged.index('(')
            cnt = 1
            for i in range(left_index+1,len(judged)):
                if judged[i] == '(':
                    cnt += 1
                elif judged[i] == ')':
                    cnt -= 1
                if cnt == 0:
                    right_index = i
                    break
            judged = judged[:left_index] + [['{',self.judged_ordering_branket(judged[left_index+1:right_index]),'}']] + judged[right_index+1:]

        return(judged)

    def judged_ordering_if(self,judged):
        while 'if' in judged:
            #print(judged)
            index_if = judged.index('if')
            '''
            cnt = 1
            for i in range(index_if+1,len(judged)):
                if judged[i] == 'if':
                    cnt += 1
                elif judged[i] == 'else':
                    cnt -= 1
                if cnt == 0:
                    index_else = i
                    break
            '''
            judged = judged[:index_if] + [judged[index_if:index_if+1] + self.judged_ordering_if(judged[index_if+1:])]

        return(judged)

        '''
        index_then = judged.index('then')
        if index_then == 2:
            pass
        else:
            judged = judged[:1] + [judged[1:index_then]] + judged[index_then:]

        index_else = judged.index('else')
        if index_else == 4:
            pass
        else:
            judged = judged[:3] + [judged[3:index_else]] +judged[index_else:]

        if len(judged[5:]) == 1:
            pass
        else:
            judged = judged[:5] + [judged[5:]]

        return(judged)
        '''

    def judged_ordering_times(self,judged):
        #print(judged)

        if len(judged) == 1 and type(judged[0]) is list:
            judged = [self.judged_ordering_times(judged[0])]
            return(judged)

        elif judged[0] == '{':
            judged = ['{',self.judged_ordering_times(judged[1]) ,'}']
            #print(judged)
            return(judged)

        else:###elif judged[1] in op_symb_list:
            for i in range(len(judged)):
                if type(judged[i]) is list:
                    judged = judged[:i] + [self.judged_ordering_times(judged[i])] + judged[i+1:]

            if len(judged) > 3 and '*' in judged:
                times_index = judged.index('*')
                judged = judged[:times_index-1] + [self.judged_ordering_times(judged[times_index-1:times_index+2])] + judged[times_index+2:]
                judged = self.judged_ordering_times(judged)
                return(judged)
            else:
                return(judged)

    def judged_ordering_plus_minus(self,judged):
        #print(judged)

        if len(judged) == 1 and type(judged[0]) is list:
            judged = [self.judged_ordering_plus_minus(judged[0])]
            return(judged)

        elif judged[0] == '{':
            judged = ['{',self.judged_ordering_plus_minus(judged[1]) ,'}']
            #print(judged)
            return(judged)

        else:###elif judged[1] in op_symb_list:
            for i in range(len(judged)):
                if type(judged[i]) is list:
                    judged = judged[:i] + [self.judged_ordering_plus_minus(judged[i])] + judged[i+1:]

            if len(judged) > 3 and ('+' in judged or '-' in judged):
                plus_index = len(judged)
                minus_index = len(judged)
                if '+' in judged:
                    plus_index = judged.index('+')
                if '-' in judged:
                    minus_index = judged.index('-')
                pm_index = min(plus_index,minus_index)
                judged = judged[:pm_index-1] + [self.judged_ordering_plus_minus(judged[pm_index-1:pm_index+2])] + judged[pm_index+2:]
                judged = self.judged_ordering_plus_minus(judged)
                return(judged)
            else:
                return(judged)

    def judged_ordering_less_than(self,judged):
        #print(judged)

        if len(judged) == 1 and type(judged[0]) is list:
            judged = [self.judged_ordering_less_than(judged[0])]
            return(judged)

        elif judged[0] == '{':
            judged = ['{',self.judged_ordering_less_than(judged[1]) ,'}']
            #print(judged)
            return(judged)

        else:###elif judged[1] in op_symb_list:
            for i in range(len(judged)):
                if type(judged[i]) is list:
                    judged = judged[:i] + [self.judged_ordering_less_than(judged[i])] + judged[i+1:]

            if len(judged) > 3 and '<' in judged:
                lt_index = judged.index('<')
                judged = judged[:lt_index-1] + [self.judged_ordering_less_than(judged[lt_index-1:lt_index+2])] + judged[lt_index+2:]
                judged = self.judged_ordering_less_than(judged)
                return(judged)
            else:
                return(judged)

    def search_can_calc(self,e):
        #print(e)
        if e[0] == '{':
            return([e[0]] + self.search_can_calc(e[1]) + [e[2]])
        if type(e[0]) is not list and type(e[2]) is not list:
            op_symb = e[1]
            if op_symb == '+':
                e1_s_num = e[0].count('S') + e[2].count('S')
                e_calced = 'S('*e1_s_num + 'Z' + ')'*e1_s_num
            elif op_symb == '*':
                e1_s_num = e[0].count('S') * e[2].count('S')
                e_calced = 'S('*e1_s_num + 'Z' + ')'*e1_s_num
            else:
                print('{} is wrong op'.format(op_symb))
                sys.exit()
            return([e_calced])
        if type(e[0]) is list:
            return(self.search_can_calc(e[0])+e[1:])
        if type(e[2]) is list:
            return(e[:2]+self.search_can_calc(e[2]))

    def syntax_check(self,x):
        if type(x) is list:
            return(True)
        else:
            if nat_pattern.match(x):
                return(True)
            else:
                return(False)

    def list_flatten(self,nested_list):
        flat_list = []
        fringe = [nested_list]

        while len(fringe) > 0:
            node = fringe.pop(0)
            if isinstance(node, list):
                fringe = node + fringe
            else:
                flat_list.append(node)

        return(flat_list)

    def list_to_string(self,nested_list):
        flat_list = self.list_flatten(nested_list)
        string = flat_list[0]
        for i in range(1,len(flat_list)):
            if flat_list[i-1] != '(' and flat_list[i] != ')':
                string += ' '
            string += flat_list[i]

        string = string.replace('{ ','(').replace(' }',')')
        return(string)

    def fix_judged_form(self,judged):
        fixed_judged = []
        for i in judged:
            if type(i) is list:
                if i[0] == '{':
                    fixed_judged += i[1]
                else:
                    fixed_judged += i
            else:
                fixed_judged.append(i)
        return(fixed_judged)

    def make_required_judged(self,required_op,x_list):
        method_name = sys._getframe().f_code.co_name

        ###test
        '''
        for x in x_list:
            if not self.syntax_check(x):
                print('error at {}: {} does not match syntax'.format(method_name,x))
                sys.exit()
        '''

        if required_op in ['plus','times','minus','less than']:
            '''
            for i in range(0,3):
                if nat_pattern.match(x_list[i]):
                    pass
                else:
                    print('error at {} {}: {} must be nat'.format(method_name,required_op,x_list[i]))
                    sys.exit()
            '''
            required_judged = [x_list[0],required_op,x_list[1],'is',x_list[2]]
            required_judged = self.fix_judged_form(required_judged)
            return(required_judged)

        elif required_op in ['is less than']:
            '''
            for i in range(0,2):
                if nat_pattern.match(x_list[i]):
                    pass
                else:
                    print('error at {} {}: {} must be nat'.format(method_name,required_op,x_list[i]))
                    sys.exit()
            '''
            required_judged = [x_list[0],required_op,x_list[1]]
            required_judged = self.fix_judged_form(required_judged)
            return(required_judged)

        elif required_op in ['evalto']:
            '''
            for i in range(1,2):
                if not nat_pattern.match(x_list[i]):
                    print('error at {} {}: {} must be nat'.format(method_name,required_op,x_list[i]))
                    sys.exit()
            '''
            required_judged = [x_list[0],required_op,x_list[1]]
            required_judged = self.fix_judged_form(required_judged)
            return(required_judged)

        elif required_op in ['--->','-d->','-*->']:
            required_judged = [x_list[0],required_op,x_list[1]]
            required_judged = self.fix_judged_form(required_judged)
            return(required_judged)

        else:
            print('{} op is still defined'.format(required_op))

    def make_derivation(self,nest,rule,judged,required):

        judged = self.list_to_string(judged)

        sub_derivation = []
        for required_op,x in required:
            if required_op == '':
                sub_derivation.append('')
            else:
                #print(required_op,x)
                required_judged = self.make_required_judged(required_op,x)
                sub_derivation.append(eval('self.{}'.format(op_lang[required_op]))(required_judged,nest+1))

        derivation = '{} by {} {{'.format(judged,rule)
        if len(sub_derivation) ==1 and sub_derivation[0] == '':
            derivation += '}'
        else:
            derivation += '\n'
            for i in range(len(sub_derivation)):
                derivation += '\t'*(nest+1) + '{}'.format(sub_derivation[i])
                if i == len(sub_derivation)-1:
                    derivation += '\n'
                else:
                    derivation += ';\n'
            derivation += '\t'*(nest) + '}'
        return(derivation)

    def make_nat(self,s_num):
        return('S('*s_num + 'Z' + ')'*s_num)

    def count_s(self,e):
        if type(e) is list:
            if e[0] == '{':
                return(self.count_s(e[1]))
            else:
                e0_s_num = self.count_s(e[0])
                e2_s_num = self.count_s(e[2])
                op_symb = e[1]
                if op_symb == '+':
                    return(e0_s_num+e2_s_num)
                elif op_symb == '*':
                    return(e0_s_num*e2_s_num)
                else:
                    print('{} is wrong op'.format(op_symb))
                    sys.exit()
        else:
            return(e.count('S'))

    def reduce_s(self,n,reduce_num=1):
        n = n[2*reduce_num:-reduce_num]
        return(n)

    def calc_evalto(self,judged):
        judged = judged[:]

        if judged[0] == 'let':
            cnt = 1
            for i in range(1,len(judged)):
                if judged[i] == 'let':
                    cnt += 1
                elif judged[i] == 'in':
                    cnt -= 1
                if cnt == 0:
                    in_index = i
                    break
            env = judged[1:in_index]
            judged = judged[in_index+1:]
            env_var = env[0]
            env_num = self.calc_evalto(env[2:])
            return(self.calc_evalto(self.subs(env_var,env_num,judged)))
        elif judged[0] == '{':
            return(self.calc_evalto(judged[1]))
        elif type(judged) is not list:
            return(judged)
        elif len(judged) == 1:
            return(judged[0])
        elif len(judged) == 3:
            e = [self.calc_evalto(judged[0]),self.calc_evalto(judged[2])]
            if e[0] in bool_list or e[1] in bool_list:
                return('error')
            else:
                e[0] = int(e[0])
                e[1] = int(e[1])
                op_symb = judged[1]
                if op_symb == '+':
                    return(str(e[0]+e[1]))
                elif op_symb == '-':
                    return(str(e[0]-e[1]))
                elif op_symb == '*':
                    return(str(e[0]*e[1]))
                elif op_symb == '<':
                    if e[0] < e[1]:
                        return('true')
                    else:
                        return('false')
        else:
            e = [judged[1],judged[3],judged[5]]
            if self.calc_evalto(e[0]) == 'true':
                return(e[1])
            else:
                return(e[2])

    def subs(self,env_var,env_num,judged):
        judged = judged[:]
        if type(judged) is not list:
            if judged == env_var:
                judged = env_num
        else:
            for i in range(len(judged)):
                if judged[i] == env_var:
                    judged[i] = env_num
        return(judged)

    def add_env(self,env,let,e):
        env_e = []
        if len(env) != 0:
            for env_i in env:
                env_e += env_i + [',']
            del env_e[-1]
        env_e += ['|-']
        if len(let) != 0:
            for let_i in let:
                env_e += ['let'] + let_i + ['in']
        if type(e) is not list:
            env_e = env_e + [e]
        else:
            env_e = env_e + e
        return(env_e)


class Nat(tool):
    def plus(self,judged,nest=0):
        if judged[0] == 'Z':
            return(self.P_Zero(judged,nest))
        else:
            return(self.P_Succ(judged,nest))

    def P_Zero(self,judged,nest):
        rule = 'P-Zero'
        if judged[2] != judged[4]:
            print('error at {}: required x1 == x2 but {} != {}'.format(rule,judged[2],judged[4]))
            sys.exit()

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def P_Succ(self,judged,nest):
        rule = 'P-Succ'
        n = [judged[0],judged[2],judged[4]]
        n[0] = self.reduce_s(n[0])
        n[2] = self.reduce_s(n[2])

        required = []
        required_op = 'plus'
        required_x = n
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def times(self,judged,nest=0):
        if judged[0] == 'Z' and judged[4] == 'Z':
            return(self.T_Zero(judged,nest))
        else:
            return(self.T_Succ(judged,nest))

    def T_Zero(self,judged,nest):
        rule = 'T-Zero'

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def T_Succ(self,judged,nest):
        rule = 'T-Succ'
        n =[judged[0],judged[2],judged[4],0]
        n[0] = self.reduce_s(n[0])
        n[3] = n[2]
        n[2] = self.make_nat(self.count_s(n[3]) - self.count_s(n[1]))

        required = []
        required_op = 'times'
        required_x = n[0:3]
        required.append([required_op,required_x])

        required_op = 'plus'
        required_x = n[1:4]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

class CompareNat1(tool):
    def is_less_than(self,judged,nest=0):
        n =[judged[0],judged[2],0]
        if n[0] == n[1][2:-1]:
            return(self.L_Succ(judged,nest,n))
        else:
            return(self.L_Trans(judged,nest,n))

    def L_Succ(self,judged,nest,n):
        rule = 'L-Succ'

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def L_Trans(self,judged,nest,n):
        rule = 'L-Trans'
        n[2] = n[1]
        n[1] = self.reduce_s(n[2])

        required = []
        required_op = 'is less than'
        required_x = n[0:2]
        required.append([required_op,required_x])

        required_op = 'is less than'
        required_x = n[1:3]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

class CompareNat2(tool):
    def is_less_than(self,judged,nest=0):
        if judged[0] == 'Z':
            return(self.L_Zero(judged,nest))
        else:
            return(self.L_SuccSucc(judged,nest))

    def L_Zero(self,judged,nest):
        rule = 'L-Zero'

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def L_SuccSucc(self,judged,nest):
        rule = 'L-SuccSucc'
        n =[judged[0],judged[2]]
        n[0] = self.reduce_s(n[0])
        n[1] = self.reduce_s(n[1])

        required = []
        required_op = 'is less than'
        required_x = n
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

class CompareNat3(tool):
    def is_less_than(self,judged,nest=0):
        if judged[0] == self.reduce_s(judged[2]):
            return(self.L_Succ(judged,nest))
        else:
            return(self.L_SuccR(judged,nest))

    def L_Succ(self,judged,nest):
        rule = 'L-Succ'

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def L_SuccR(self,judged,nest):
        rule = 'L-SuccR'
        n =[judged[0],judged[2]]
        n[1] = self.reduce_s(n[1])

        required = []
        required_op = 'is less than'
        required_x = n
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

class EvalNatExp(Nat):
    def evalto(self,judged,nest=0):
        judged_ordered = self.judged_ordering(judged[:-2]) + judged[-2:]
        if len(judged_ordered) == 3:
            return(self.E_Const(judged,nest,judged_ordered))
        else:
            op_symb = judged_ordered[1]
            if op_symb == '+':
                return(self.E_Plus(judged,nest,judged_ordered))
            elif op_symb == '*':
                return(self.E_Times(judged,nest,judged_ordered))
            else:
                method_name = sys._getframe().f_code.co_name
                print('error at {}: incorrect op {}'.format(method_name,op_symb))
                sys.exit()

    def E_Const(self,judged,nest,judged_ordered):
        rule = 'E-Const'
        if judged_ordered[0] != judged_ordered[2]:
            print('error at {}: required x1 == x2 but {} != {}'.format(rule,judged_ordered[0],judged_ordered[2]))
            sys.exit()

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Plus(self,judged,nest,judged_ordered):
        rule = 'E-Plus'
        e = [judged_ordered[0],judged_ordered[2]]
        n = [0,0,judged_ordered[4]]
        n[0] = self.make_nat(self.count_s(e[0]))
        n[1] = self.make_nat(self.count_s(e[1]))

        required = []
        required_op = 'evalto'
        required_x = [e[0],n[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],n[1]]
        required.append([required_op,required_x])

        required_op = 'plus'
        required_x = [n[0],n[1],n[2]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Times(self,judged,nest,judged_ordered):
        rule = 'E-Times'
        e = [judged_ordered[0],judged_ordered[2]]
        n = [0,0,judged_ordered[4]]
        n[0] = self.make_nat(self.count_s(e[0]))
        n[1] = self.make_nat(self.count_s(e[1]))

        required = []
        required_op = 'evalto'
        required_x = [e[0],n[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],n[1]]
        required.append([required_op,required_x])

        required_op = 'times'
        required_x = [n[0],n[1],n[2]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

class ReduceNatExp(Nat):
    def _z_l(self,judged,nest=0):
        #print(judged)
        op_index = judged.index('--->')
        judged_ordered = self.judged_ordering(judged[:op_index]) + [judged[op_index]] + self.judged_ordering(judged[op_index+1:])
        op_symb = judged_ordered[1]

        if len(judged_ordered) == 5:
            if op_symb == '+':
                return(self.R_Plus(judged,nest,judged_ordered))
            elif op_symb == '*':
                return(self.R_Times(judged,nest,judged_ordered))
        else:
            if op_symb == '+':
                if judged_ordered[2] == judged_ordered[6]:
                    return(self.R_PlusL(judged,nest,judged_ordered))
                elif judged_ordered[0] == judged_ordered[4]:
                    return(self.R_PlusR(judged,nest,judged_ordered))
            elif op_symb == '*':
                if judged_ordered[2] == judged_ordered[6]:
                    return(self.R_TimesL(judged,nest,judged_ordered))
                elif judged_ordered[0] == judged_ordered[4]:
                    return(self.R_TimesR(judged,nest,judged_ordered))
            else:
                print('{} is wrong op'.format(op_symb))
                sys.exit()

    def R_Plus(self,judged,nest,judged_ordered):
        rule = 'R-Plus'
        n = [judged_ordered[0],judged_ordered[2],judged_ordered[4]]

        required = []
        required_op = 'plus'
        required_x = n
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def R_Times(self,judged,nest,judged_ordered):
        rule = 'R-Times'
        n = [judged_ordered[0],judged_ordered[2],judged_ordered[4]]

        required = []
        required_op = 'times'
        required_x = n
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def R_PlusL(self,judged,nest,judged_ordered):
        rule = 'R-PlusL'
        e = [judged_ordered[0],judged_ordered[4]]

        required = []
        required_op = '--->'
        required_x = e
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def R_PlusR(self,judged,nest,judged_ordered):
        rule = 'R-PlusR'
        e = [judged_ordered[2],judged_ordered[6]]

        required = []
        required_op = '--->'
        required_x = e
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def R_TimesL(self,judged,nest,judged_ordered):
        rule = 'R-TimesL'
        e = [judged_ordered[0],judged_ordered[4]]

        required = []
        required_op = '--->'
        required_x = e
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def R_TimesR(self,judged,nest,judged_ordered):
        rule = 'R-TimesR'
        e = [judged_ordered[2],judged_ordered[6]]

        required = []
        required_op = '--->'
        required_x = e
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def _d_l(self,judged,nest=0):
        #print(judged)
        op_index = judged.index('-d->')
        judged_ordered = self.judged_ordering(judged[:op_index]) + [judged[op_index]] + self.judged_ordering(judged[op_index+1:])
        op_symb = judged_ordered[1]

        if len(judged_ordered) == 5:
            if op_symb == '+':
                return(self.DR_Plus(judged,nest,judged_ordered))
            elif op_symb == '*':
                return(self.DR_Times(judged,nest,judged_ordered))
        else:
            if op_symb == '+':
                if judged_ordered[2] == judged_ordered[6]:
                    return(self.DR_PlusL(judged,nest,judged_ordered))
                elif judged_ordered[0] == judged_ordered[4]:
                    return(self.DR_PlusR(judged,nest,judged_ordered))
            elif op_symb == '*':
                if judged_ordered[2] == judged_ordered[6]:
                    return(self.DR_TimesL(judged,nest,judged_ordered))
                elif judged_ordered[0] == judged_ordered[4]:
                    return(self.DR_TimesR(judged,nest,judged_ordered))
            else:
                print('{} is wrong op'.format(op_symb))
                sys.exit()

    def DR_Plus(self,judged,nest,judged_ordered):
        rule = 'DR-Plus'
        n = [judged_ordered[0],judged_ordered[2],judged_ordered[4]]

        required = []
        required_op = 'plus'
        required_x = n
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def DR_Times(self,judged,nest,judged_ordered):
        rule = 'DR-Times'
        n = [judged_ordered[0],judged_ordered[2],judged_ordered[4]]

        required = []
        required_op = 'times'
        required_x = n
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def DR_PlusL(self,judged,nest,judged_ordered):
        rule = 'DR-PlusL'
        x = [judged_ordered[0],judged_ordered[4]]

        required = []
        required_op = '-d->'
        required_x = x
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def DR_PlusR(self,judged,nest,judged_ordered):
        rule = 'DR-PlusR'
        x = [judged_ordered[2],judged_ordered[6]]

        required = []
        required_op = '-d->'
        required_x = x
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def DR_TimesL(self,judged,nest,judged_ordered):
        rule = 'DR-TimesL'
        x = [judged_ordered[0],judged_ordered[4]]

        required = []
        required_op = '-d->'
        required_x = x
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def DR_TimesR(self,judged,nest,judged_ordered):
        rule = 'DR-TimesR'
        x = [judged_ordered[2],judged_ordered[6]]

        required = []
        required_op = '-d->'
        required_x = x
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def _o_l(self,judged,nest=0):

        op_index = judged.index('-*->')
        e_left = self.judged_ordering(judged[:op_index])
        e_right = self.judged_ordering(judged[op_index+1:])
        judged_ordered = e_left + [judged[op_index]] + e_right
        #print(judged_ordered)
        #print(e_left,e_right)

        e = [e_left,e_right,0]
        #print(e)

        if e[0] == e[1]:
            rule = 'MR-Zero'

            required = []
            required_op = ''
            required_x = ''
            required.append([required_op,required_x])

            derivation = self.make_derivation(nest,rule,judged,required)
            return(derivation)

        else:
            judged_flat = self.list_flatten(judged_ordered)
            op_index_flat = judged_flat.index('-*->')
            left_op_num = (op_index_flat-1)//2
            right_op_num = (len(judged_flat)-op_index_flat-2)//2

            if left_op_num == right_op_num + 1:
                rule = 'MR-One'

                required = []
                required_op = '--->'
                required_x = [e[0],e[1]]
                required.append([required_op,required_x])

                derivation = self.make_derivation(nest,rule,judged,required)
                return(derivation)

            else:
                rule = 'MR-Multi'
                #print(judged)
                e[2] = e[1]
                e[1] = self.search_can_calc(e_left)
                #print(e[1])

                required = []
                required_op = '-*->'
                required_x = [e[0],e[1]]
                required.append([required_op,required_x])

                required_op = '-*->'
                required_x = [e[1],e[2]]
                required.append([required_op,required_x])

                derivation = self.make_derivation(nest,rule,judged,required)
                return(derivation)

class EvalML1(tool):
    def evalto(self,judged,nest=0):
        judged_ordered = self.judged_ordering(judged[:-2]) + judged[-2:]

        if len(judged_ordered) == 3:
            if type(judged_ordered[0]) is not list:
                if int_pattern.match(judged_ordered[0]):
                    return(self.E_Int(judged,nest,judged_ordered))
                elif judged_ordered[0] in bool_list:
                    return(self.E_Bool(judged,nest,judged_ordered))
                ###if
            else:
                bool_e0 = self.calc_evalto(judged_ordered[0][1])
                if bool_e0 == 'true':
                    return(self.E_IfT(judged,nest,judged_ordered))
                else:
                    return(self.E_IfF(judged,nest,judged_ordered))

        elif len(judged_ordered) == 5:
            op_symb = judged_ordered[1]
            if op_symb == '+':
                return(self.E_Plus(judged,nest,judged_ordered))
            elif op_symb == '-':
                return(self.E_Minus(judged,nest,judged_ordered))
            elif op_symb == '*':
                return(self.E_Times(judged,nest,judged_ordered))
            elif op_symb == '<':
                return(self.E_Lt(judged,nest,judged_ordered))
            else:
                method_name = sys._getframe().f_code.co_name
                print('error at {}: incorrect op {}'.format(method_name,op_symb))
                sys.exit()

    def E_Int(self,judged,nest,judged_ordered):
        rule = 'E-Int'
        if judged_ordered[0] != judged_ordered[2]:
            print('error at {}: required x1 == x2 but {} != {}'.format(rule,judged_ordered[0],judged_ordered[2]))
            sys.exit()

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Bool(self,judged,nest,judged_ordered):
        rule = 'E-Bool'
        if judged_ordered[0] != judged_ordered[2]:
            print('error at {}: required x1 == x2 but {} != {}'.format(rule,judged_ordered[0],judged_ordered[2]))
            sys.exit()

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_IfT(self,judged,nest,judged_ordered):
        rule = 'E-IfT'
        e = [judged_ordered[0][1],judged_ordered[0][3]]
        v = [judged_ordered[2]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'true']
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],v[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_IfF(self,judged,nest,judged_ordered):
        rule = 'E-IfF'
        e = [judged_ordered[0][1],judged_ordered[0][5]]
        v = [judged_ordered[2]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'true']
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],v[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Plus(self,judged,nest,judged_ordered):
        rule = 'E-Plus'
        e = [judged_ordered[0],judged_ordered[2]]
        i = [self.calc_evalto(e[0]),self.calc_evalto(e[1]),judged_ordered[4]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],i[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],i[1]]
        required.append([required_op,required_x])

        required_op = 'plus'
        required_x = i
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Minus(self,judged,nest,judged_ordered):
        rule = 'E-Minus'
        e = [judged_ordered[0],judged_ordered[2]]
        i = [self.calc_evalto(e[0]),self.calc_evalto(e[1]),judged_ordered[4]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],i[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],i[1]]
        required.append([required_op,required_x])

        required_op = 'minus'
        required_x = i
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Times(self,judged,nest,judged_ordered):
        rule = 'E-Times'
        e = [judged_ordered[0],judged_ordered[2]]
        i = [self.calc_evalto(e[0]),self.calc_evalto(e[1]),judged_ordered[4]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],i[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],i[1]]
        required.append([required_op,required_x])

        required_op = 'times'
        required_x = i
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Lt(self,judged,nest,judged_ordered):
        rule = 'E-Lt'
        e = [judged_ordered[0],judged_ordered[2]]
        i = [self.calc_evalto(e[0]),self.calc_evalto(e[1]),judged_ordered[4]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],i[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],i[1]]
        required.append([required_op,required_x])

        required_op = 'less than'
        required_x = i
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def plus(self,judged,nest=0):
        return(self.B_Plus(judged,nest))

    def B_Plus(self,judged,nest):
        rule = 'B-Plus'
        i = [judged[0],judged[2],judged[4]]

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def minus(self,judged,nest=0):
        return(self.B_Minus(judged,nest))

    def B_Minus(self,judged,nest):
        rule = 'B-Minus'
        i = [judged[0],judged[2],judged[4]]

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def times(self,judged,nest=0):
        return(self.B_Times(judged,nest))

    def B_Times(self,judged,nest):
        rule = 'B-Times'
        i = [judged[0],judged[2],judged[4]]

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def less_than(self,judged,nest=0):
        return(self.B_Lt(judged,nest))

    def B_Lt(self,judged,nest):
        rule = 'B-Lt'
        i = [judged[0],judged[2],judged[4]]

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

class EvalML1Err(EvalML1):
    def evalto(self,judged,nest=0):
        judged_ordered = self.judged_ordering(judged[:-2]) + judged[-2:]
        #print(1111,judged_ordered)

        if len(judged_ordered) == 3:
            if int_pattern.match(judged[0]):
                return(self.E_Int(judged,nest,judged_ordered))
            elif judged[0] in bool_list:
                return(self.E_Bool(judged,nest,judged_ordered))
            ###if
            else:
                evalto_e0 = self.calc_evalto(judged_ordered[0][1])
                if evalto_e0 in bool_list:
                    if evalto_e0 == 'true':
                        evalto_e1 = self.calc_evalto(judged_ordered[0][3])
                        if evalto_e1 == 'error':
                            return(self.E_IfTError(judged,nest,judged_ordered))
                        else:
                            return(self.E_IfT(judged,nest,judged_ordered))

                    else:
                        evalto_e2 = self.calc_evalto(judged_ordered[0][5])
                        if evalto_e2 == 'error':
                            return(self.E_IfFError(judged,nest,judged_ordered))
                        else:
                            return(self.E_IfF(judged,nest,judged_ordered))

                elif int_pattern.match(evalto_e0):
                    return(self.E_IfInt(judged,nest,judged_ordered))

                elif evalto_e0 == 'error':
                    return(self.E_IfError(judged,nest,judged_ordered))

        elif len(judged_ordered) == 5:
            e = [judged_ordered[0],judged_ordered[2]]
            e[0] = self.calc_evalto(e[0])
            e[1] = self.calc_evalto(e[1])
            i = [judged_ordered[4]]
            op_symb = judged_ordered[1]
            if op_symb == '+':
                if e[0] in bool_list:
                    return(self.E_PlusBoolL(judged,nest,judged_ordered))
                elif e[1] in bool_list:
                    return(self.E_PlusBoolR(judged,nest,judged_ordered))
                elif e[0] == 'error':
                    return(self.E_PlusErrorL(judged,nest,judged_ordered))
                elif e[1] == 'error':
                    return(self.E_PlusErrorR(judged,nest,judged_ordered))
                else:
                    return(self.E_Plus(judged,nest,judged_ordered))
            elif op_symb == '-':
                if e[0] in bool_list:
                    return(self.E_MinusBoolL(judged,nest,judged_ordered))
                elif e[1] in bool_list:
                    return(self.E_MinusBoolR(judged,nest,judged_ordered))
                elif e[0] == 'error':
                    return(self.E_MinusErrorL(judged,nest,judged_ordered))
                elif e[1] == 'error':
                    return(self.E_MinusErrorR(judged,nest,judged_ordered))
                else:
                    return(self.E_Minus(judged,nest,judged_ordered))
            elif op_symb == '*':
                if e[0] in bool_list:
                    return(self.E_TimesBoolL(judged,nest,judged_ordered))
                elif e[1] in bool_list:
                    return(self.E_TimesBoolR(judged,nest,judged_ordered))
                elif e[0] == 'error':
                    return(self.E_TimesErrorL(judged,nest,judged_ordered))
                elif e[1] == 'error':
                    return(self.E_TimesErrorR(judged,nest,judged_ordered))
                else:
                    return(self.E_Times(judged,nest,judged_ordered))
            elif op_symb == '<':
                if e[0] in bool_list:
                    return(self.E_LtBoolL(judged,nest,judged_ordered))
                elif e[1] in bool_list:
                    return(self.E_LtBoolR(judged,nest,judged_ordered))
                elif e[0] == 'error':
                    return(self.E_LtErrorL(judged,nest,judged_ordered))
                elif e[1] == 'error':
                    return(self.E_LtErrorR(judged,nest,judged_ordered))
                else:
                    return(self.E_Lt(judged,nest,judged_ordered))
            else:
                method_name = sys._getframe().f_code.co_name
                print('error at {}: incorrect op {}'.format(method_name,op_symb))
                sys.exit()

    def E_PlusBoolL(self,judged,nest,judged_ordered):
        rule = 'E-PlusBoolL'
        e = [judged_ordered[0]]
        b = [self.calc_evalto(e[0])]

        required = []
        required_op = 'evalto'
        required_x = [e[0],b[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_PlusBoolR(self,judged,nest,judged_ordered):
        rule = 'E-PlusBoolR'
        e = [judged_ordered[2]]
        b = [self.calc_evalto(e[0])]

        required = []
        required_op = 'evalto'
        required_x = [e[0],b[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_PlusErrorL(self,judged,nest,judged_ordered):
        rule = 'E-PlusErrorL'
        e = [judged_ordered[0]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_PlusErrorR(self,judged,nest,judged_ordered):
        rule = 'E-PlusErrorR'
        e = [judged_ordered[2]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_MinusBoolL(self,judged,nest,judged_ordered):
        rule = 'E-MinusBoolL'
        e = [judged_ordered[0]]
        b = [self.calc_evalto(e[0])]

        required = []
        required_op = 'evalto'
        required_x = [e[0],b[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_MinusBoolR(self,judged,nest,judged_ordered):
        rule = 'E-MinusBoolR'
        e = [judged_ordered[2]]
        b = [self.calc_evalto(e[0])]

        required = []
        required_op = 'evalto'
        required_x = [e[0],b[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_MinusErrorL(self,judged,nest,judged_ordered):
        rule = 'E-MinusErrorL'
        e = [judged_ordered[0]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_MinusErrorR(self,judged,nest,judged_ordered):
        rule = 'E-MinusErrorR'
        e = [judged_ordered[2]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_TimesBoolL(self,judged,nest,judged_ordered):
        rule = 'E-TimesBoolL'
        e = [judged_ordered[0]]
        b = [self.calc_evalto(e[0])]

        required = []
        required_op = 'evalto'
        required_x = [e[0],b[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_TimesBoolR(self,judged,nest,judged_ordered):
        rule = 'E-TimesBoolR'
        e = [judged_ordered[2]]
        b = [self.calc_evalto(e[0])]

        required = []
        required_op = 'evalto'
        required_x = [e[0],b[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_TimesErrorL(self,judged,nest,judged_ordered):
        rule = 'E-TimesErrorL'
        e = [judged_ordered[0]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_TimesErrorR(self,judged,nest,judged_ordered):
        rule = 'E-TimesErrorR'
        e = [judged_ordered[2]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_LtBoolL(self,judged,nest,judged_ordered):
        rule = 'E-LtBoolL'
        e = [judged_ordered[0]]
        b = [self.calc_evalto(e[0])]

        required = []
        required_op = 'evalto'
        required_x = [e[0],b[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_LtBoolR(self,judged,nest,judged_ordered):
        rule = 'E-LtBoolR'
        e = [judged_ordered[2]]
        b = [self.calc_evalto(e[0])]

        required = []
        required_op = 'evalto'
        required_x = [e[0],b[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_LtErrorL(self,judged,nest,judged_ordered):
        rule = 'E-LtErrorL'
        e = [judged_ordered[0]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_LtErrorR(self,judged,nest,judged_ordered):
        rule = 'E-LtErrorR'
        e = [judged_ordered[2]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_IfInt(self,judged,nest,judged_ordered):
        rule = 'E-IfInt'
        e = [judged_ordered[0][1]]
        i = [self.calc_evalto(e[0])]

        required = []
        required_op = 'evalto'
        required_x = [e[0],i[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_IfError(self,judged,nest,judged_ordered):
        rule = 'E-IfInt'
        e = [judged_ordered[0][1]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_IfTError(self,judged,nest,judged_ordered):
        rule = 'E-IfTError'
        e = [judged_ordered[0][1],judged_ordered[0][3]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'true']
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_IfFError(self,judged,nest,judged_ordered):
        rule = 'E-IfFError'
        e = [judged_ordered[0][1],judged_ordered[0][5]]

        required = []
        required_op = 'evalto'
        required_x = [e[0],'false']
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [e[1],'error']
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

class EvalML2(EvalML1):
    def evalto(self,judged,nest=0):
        env, let, judged_ordered = self.judged_ordering(judged[:-2])
        judged_ordered += judged[-2:]
        #print('evalto',env,let,judged_ordered)
        env_var_list = [i[0] for i in env]

        if len(let) != 0:
            return(self.E_Let(judged,nest,env,let,judged_ordered))

        elif len(judged_ordered) == 3:
            if type(judged_ordered[0]) is not list:
                if int_pattern.match(judged_ordered[0]):
                    return(self.E_Int(judged,nest,env,let,judged_ordered))
                elif judged_ordered[0] in bool_list:
                    return(self.E_Bool(judged,nest,env,let,judged_ordered))
                elif judged_ordered[0] in var_list:
                    if judged_ordered[0] in env_var_list:
                        if judged_ordered[0] == env_var_list[-1]:
                            return(self.E_Var1(judged,nest,env,let,judged_ordered))
                        else:
                            return(self.E_Var2(judged,nest,env,let,judged_ordered))
                    else:
                        print('var:{} not in env:{}'.format(judged_ordered[0],env_var_list))
                        sys.exit()
            # if
            else:
                bool_e0 = self.calc_evalto(judged_ordered[0][1])
                for env_i in range(len(env)):
                    env_var = env[env_i][0]
                    env_num = self.calc_evalto(env[env_i][2:])
                    for env_j in range(env_i+1,len(env)):
                        env[env_j] = self.subs(env_var,env_num,env[env_j])
                    if  env_var == judged_ordered[0][1]:
                        bool_e0 = self.calc_evalto(self.subs(env_var,env_num,judged_ordered[0][1]))

                if bool_e0 == 'true':
                    return(self.E_IfT(judged,nest,env,let,judged_ordered))
                else:
                    return(self.E_IfF(judged,nest,env,let,judged_ordered))

        elif len(judged_ordered) == 5:
            op_symb = judged_ordered[1]
            if op_symb == '+':
                return(self.E_Plus(judged,nest,env,let,judged_ordered))
            elif op_symb == '-':
                return(self.E_Minus(judged,nest,env,let,judged_ordered))
            elif op_symb == '*':
                return(self.E_Times(judged,nest,env,let,judged_ordered))
            elif op_symb == '<':
                return(self.E_Lt(judged,nest,env,let,judged_ordered))
            else:
                method_name = sys._getframe().f_code.co_name
                print('error at {}: incorrect op {}'.format(method_name,op_symb))
                sys.exit()

    def E_Int(self,judged,nest,env,let,judged_ordered):
        rule = 'E-Int'
        if judged_ordered[0] != judged_ordered[2]:
            print('error at {}: required x1 == x2 but {} != {}'.format(rule,judged_ordered[0],judged_ordered[2]))
            sys.exit()

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Bool(self,judged,nest,env,let,judged_ordered):
        rule = 'E-Bool'
        if judged_ordered[0] != judged_ordered[2]:
            print('error at {}: required x1 == x2 but {} != {}'.format(rule,judged_ordered[0],judged_ordered[2]))
            sys.exit()

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Var1(self,judged,nest,env,let,judged_ordered):
        rule = 'E-Var1'
        #print('E_Var1',env,judged_ordered)
        env_var = env[-1][0]
        env_num = self.calc_evalto(env[-1][2:])
        judged_ordered_subs = self.subs(env_var,env_num,judged_ordered)

        if judged_ordered_subs[0] != judged_ordered_subs[2]:
            print('error at {}: required x1 == x2 but {} != {}'.format(rule,judged_ordered_subs[0],judged_ordered_subs[2]))
            sys.exit()

        required = []
        required_op = ''
        required_x = ''
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Var2(self,judged,nest,env,let,judged_ordered):
        rule = 'E-Var2'
        var = judged_ordered[0]
        v = judged_ordered[2]
        #print('E_Var2',env,judged_ordered,v)
        env_required = env[:-1]

        required = []
        required_op = 'evalto'
        required_x = [self.add_env(env_required,let,var), v]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Plus(self,judged,nest,env,let,judged_ordered):
        rule = 'E-Plus'
        e = [judged_ordered[0],judged_ordered[2]]
        i = [self.calc_evalto(e[0]),self.calc_evalto(e[1]),judged_ordered[4]]
        env_tmp = env[:]
        for env_i in range(len(env_tmp)):
            env_var = env_tmp[env_i][0]
            env_num = self.calc_evalto(env_tmp[env_i][2:])
            for env_j in range(env_i+1,len(env_tmp)):
                if env_tmp[env_j][0] != env_var:
                    env_tmp[env_j] = self.subs(env_var,env_num,env_tmp[env_j])
        for env_i in range(len(env_tmp))[::-1]:
            env_var = env_tmp[env_i][0]
            env_num = self.calc_evalto(env_tmp[env_i][2:])
            for i_i in range(len(i)):
                if env_var in i[i_i]:
                    i[i_i] = self.calc_evalto(self.subs(env_var,env_num,i[i_i]))

        required = []
        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[0]),i[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[1]),i[1]]
        required.append([required_op,required_x])

        required_op = 'plus'
        required_x = i
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Minus(self,judged,nest,env,let,judged_ordered):
        rule = 'E-Minus'
        e = [judged_ordered[0],judged_ordered[2]]
        i = [self.calc_evalto(e[0]),self.calc_evalto(e[1]),judged_ordered[4]]
        env_tmp = env[:]
        for env_i in range(len(env_tmp)):
            env_var = env_tmp[env_i][0]
            env_num = self.calc_evalto(env_tmp[env_i][2:])
            for env_j in range(env_i+1,len(env_tmp)):
                if env_tmp[env_j][0] != env_var:
                    env_tmp[env_j] = self.subs(env_var,env_num,env_tmp[env_j])
        for env_i in range(len(env_tmp))[::-1]:
            env_var = env_tmp[env_i][0]
            env_num = self.calc_evalto(env_tmp[env_i][2:])
            for i_i in range(len(i)):
                if env_var in i[i_i]:
                    i[i_i] = self.calc_evalto(self.subs(env_var,env_num,i[i_i]))

        required = []
        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[0]),i[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[1]),i[1]]
        required.append([required_op,required_x])

        required_op = 'minus'
        required_x = i
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Times(self,judged,nest,env,let,judged_ordered):
        rule = 'E-Times'
        e = [judged_ordered[0],judged_ordered[2]]
        i = [self.calc_evalto(e[0]),self.calc_evalto(e[1]),judged_ordered[4]]
        env_tmp = env[:]
        for env_i in range(len(env_tmp)):
            env_var = env_tmp[env_i][0]
            env_num = self.calc_evalto(env_tmp[env_i][2:])
            for env_j in range(env_i+1,len(env_tmp)):
                if env_tmp[env_j][0] != env_var:
                    env_tmp[env_j] = self.subs(env_var,env_num,env_tmp[env_j])
        for env_i in range(len(env_tmp))[::-1]:
            env_var = env_tmp[env_i][0]
            env_num = self.calc_evalto(env_tmp[env_i][2:])
            for i_i in range(len(i)):
                if env_var in i[i_i]:
                    i[i_i] = self.calc_evalto(self.subs(env_var,env_num,i[i_i]))

        required = []
        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[0]),i[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[1]),i[1]]
        required.append([required_op,required_x])

        required_op = 'times'
        required_x = i
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Lt(self,judged,nest,env,let,judged_ordered):
        rule = 'E-Lt'
        e = [judged_ordered[0],judged_ordered[2]]
        i = [self.calc_evalto(e[0]),self.calc_evalto(e[1]),judged_ordered[4]]
        env_tmp = env[:]
        for env_i in range(len(env_tmp)):
            env_var = env_tmp[env_i][0]
            env_num = self.calc_evalto(env_tmp[env_i][2:])
            for env_j in range(env_i+1,len(env_tmp)):
                if env_tmp[env_j][0] != env_var:
                    env_tmp[env_j] = self.subs(env_var,env_num,env_tmp[env_j])
        for env_i in range(len(env_tmp))[::-1]:
            env_var = env_tmp[env_i][0]
            env_num = self.calc_evalto(env_tmp[env_i][2:])
            for i_i in range(len(i)):
                if env_var in i[i_i]:
                    i[i_i] = self.calc_evalto(self.subs(env_var,env_num,i[i_i]))

        required = []
        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[0]),i[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[1]),i[1]]
        required.append([required_op,required_x])

        required_op = 'less than'
        required_x = i
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_IfT(self,judged,nest,env,let,judged_ordered):
        rule = 'E-IfT'
        e = [judged_ordered[0][1],judged_ordered[0][3]]
        v = [judged_ordered[2]]

        required = []
        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[0]), 'true']
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[1]), v[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_IfF(self,judged,nest,env,let,judged_ordered):
        rule = 'E-IfF'
        e = [judged_ordered[0][1],judged_ordered[0][5]]
        v = [judged_ordered[2]]

        required = []
        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[0]), 'true']
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [self.add_env(env,let,e[1]), v[0]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

    def E_Let(self,judged,nest,env,let,judged_ordered):
        rule = 'E-Let'
        #print(rule,env,let,judged_ordered)
        e = [let[0][2:],judged_ordered[:-2]]
        if len(set(var_list) & set(e[0])) == 0:
            v_0 = self.calc_evalto(e[0])
        elif e[0][0] == 'let':
            v_0 = self.calc_evalto(e[0])
        else:
            env_tmp = env[:]
            for env_i in range(len(env_tmp)):
                env_var = env_tmp[env_i][0]
                env_num = self.calc_evalto(env_tmp[env_i][2:])
                for env_j in range(env_i+1,len(env_tmp)):
                    env_tmp[env_j] = self.subs(env_var,env_num,env_tmp[env_j])
            for env_i in range(len(env_tmp))[::-1]:
                env_var = env_tmp[env_i][0]
                env_num = self.calc_evalto(env_tmp[env_i][2:])
                if env_var in e[0]:
                    v_0 = self.calc_evalto(self.subs(env_var,env_num,e[0]))

        v = [v_0,judged_ordered[-1]]
        env_add = env + [[let[0][0], '=', v[0]]]

        required = []
        required_op = 'evalto'
        required_x = [self.add_env(env,let[:0],e[0]), v[0]]
        required.append([required_op,required_x])

        required_op = 'evalto'
        required_x = [self.add_env(env_add,let[1:],e[1]), v[1]]
        required.append([required_op,required_x])

        derivation = self.make_derivation(nest,rule,judged,required)
        return(derivation)

question_data = question_data[question_data.question_number.isin(answering_number)]
if ans_system != '':
    question_data = question_data[question_data.system_name == ans_system]
#print(question_data)
for _,question in question_data.iterrows():
    #print(question)
    question_number = question['question_number']
    system_name = question['system_name']
    judged = question['judged']
    correct_derivation = question['derivation']
    solve(question_number,system_name,judged,correct_derivation)
