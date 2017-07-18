#############################
#target:tranfer c++ file to right c++ style
#author:hdz
#time:2014-12-30 14:54:29
USAGE="python code_check.py cfile ofile coding"
#############################
import re
import sys
import time
tab_width=4
braces_style=0
#0: XXXX() {     1: xxx()
#       NNN         {
#   }                   NNN
#                   }
#default_coding='gbk'

bak_time=time.strftime("%m_%d_%H_%M", time.localtime())
num=re.compile('^-?[0-9.]+')
para=re.compile('^[a-zA-Z_][a-zA-Z_0-9:.]*')
num_2=re.compile('^-?[0-9.]+$')
para_2=re.compile('^[a-zA-Z_][a-zA-Z_0-9:.]*$|^\(|^"|\)$')

operator1=re.compile('^\++|^--|^~|^\*|^&')
operator2=re.compile('^==|^%=|^/=|^\+=|^-=|^!=|^\*=|^<<|^>>|^~=|^\|\||^&&|^\+|^-|^\*|^/|^=|^>|^<')
operator2_2=re.compile('^==$|^%=$|^/=$|^\+=$|^-=$|^!=$|^\*=$|^<<$|^>>$|^~=$|^\|\|$|^&&$|^\+$|^-$|^\*$|^/$|^=$|^>$|^<$')
operator3=re.compile('^\.\*|^->\*|^\.|^->|^::')
key_with_blank=['if','switch','while','for','catch','else','case']
ignore=['/*','**','*/','//','#','}']
p_yinhao=re.compile('^"[^"]+"|^\'[^\']+\'')
p_jianhao=re.compile('^<[^<>]+>')
p_comment=re.compile('^//.+')
key_word=['int','char','struct','double','float','long','class','string',\
        'bool','this','void','return','size_t','wchar_t','bchar_t',\
         'time_t','clock_t','int8_t','int16_t','int32_t','int64_t',\
         'uint8_t','uint16_t','uint32_t','uint64_t','char16_t','char32_t']
stl_word=['vector','map','array','deque','list','set','stack','pair',\
         'forward_list','unordered_map','unordered_set']
#std_stl_word=['std::'+x for x in stl_word]
#stl_word.extend(std_stl_word)
other_word=['static','register','auto','volatile','extern','const']
def get_item(line):
    w=p_comment.findall(line)
    if w!=[]:
        return line
    w=num.findall(line)
    if w!=[]:
        return w[0]
    w=para.findall(line)
    if w!=[]:
        return w[0]
    w=operator2.findall(line)
    if w!=[]:
        return w[0]
    w=operator1.findall(line)
    if w!=[]:
        return w[0]
    w=operator3.findall(line)
    if w!=[]:
        return w[0]
    w=p_yinhao.findall(line)
    if w!=[]:
        return w[0]
    w=p_jianhao.findall(line)
    if w!=[]:
        return w[0]
    return line[0]
def get_all_item(line):
    res=[]
    i=0
    while i<len(line):
        if line[i] in [' ','\t']:
            res.append(line[i])
            i+=1
        else:
            item=get_item(line[i:])
            res.append(item)
            i+=len(item)
    return res
def check_is_pointer(l):
    joinl=''.join(l).strip()
    if joinl=='':
        return True
    if len(l)<2 or joinl.endswith('/'):
        return False
    if l[-1]==' ':
        l=l[:-1]
    if l[-1].endswith('=') or l[-1] == '(' or l[-1]=='<<' or\
            l[-1]=='>>' or l[-1]==',':
        return True
    if para_2.search(l[-1]):
        if joinl==l[-1]:
            return True
        if l[-2]==' ' or l[-2]=='(':
            if len(l)>=3 and para_2.search(l[-3]):
                return True
        if len(l)>=3 and l[-2]==' ' and l[-3]==',':
            return True
    if l[-1] in key_word:
        return True
    if len(l)>=3 and l[-2]==' ' and l[-3] in key_word:
        return True
    return False
def check_is_para_num(x1,x2):
    if not para_2.search(x1):
        if not num_2.search(x1):
            if x1!=' ' and x1!=']':
                return False
    if not para_2.search(x2):
        if not num_2.search(x2):
            if x2!=' ' and not p_yinhao.search(x2) and x2!='*':
                return False
            if x2=='*' and x1=='/':
                return False
    return True
def check_first_in_key_word(l):
    l=[x.strip() for x in l if x.strip()!='']
    if len(l)>0 and l[0] in key_word:
        return True
    return False
def get_new_ll(ll):
    nll=[]
    i=0
    brk=0
    for x in ll:
        if x=='(' or x=='<':
            brk+=1
        elif x==')' or x=='>':
            brk-=1
        if x in key_with_blank:#if ()
            nll.append(x)
            if i+1<len(ll) and ll[i+1]!=' ':
                nll.append(' ')
        elif x in [',',';'] and (brk>0 or check_first_in_key_word(ll)):
            #, xx
            nll.append(x)
            if i+1<len(ll) and ll[i+1]!=' ':
                nll.append(' ')
        elif operator2_2.search(x) and ((len(nll)>0 and\
                nll[-1]!=' ') or\
                (i+1<len(ll) and ll[i+1]!=' ')):
            #a + b
            if x=='*' and check_is_pointer(nll):
                nll.append(x)
                i+=1
                continue
            if x=='*' and ''.join(nll).rstrip().endswith('/'):
                # /**/in normal sen
                while len(nll)>0 and nll[-1]==' ':
                    nll=nll[:-1]
                nll.append(x)
                i+=1
                continue
            if len(nll)>0 and i+1<len(ll) and\
                    check_is_para_num(nll[-1],ll[i+1]):
                if nll[-1]!=' ':
                    nll.append(' ')
                nll.append(x)
                if ll[i+1]!=' ':
                    nll.append(' ')
            else:
                nll.append(x)
        elif x in ['(','[']:
            #(XX
            if len(nll)>2 and nll[-1]==' ' and\
                    nll[-2] not in key_word and\
                    nll[-2] not in key_with_blank and\
                    para_2.search(nll[-2]):
                #FFF()
                nll=nll[:-1]
            nll.append(x)
            if i+1<len(ll) and ll[i+1]==' ':
                ll[i+1]=''
                #print ''.join(ll)
                #i+=1
        elif x in [')',']']:
            #XX)
            if i-1>=0 and nll[-1]==' ':
                nll[-1]=x
            else:
                nll.append(x)
        else:
            nll.append(x)
        i+=1
    return nll
def filter_ll(l):
    nl=[]
    i=0
    while i<len(l) and l[i] in [' ','\t']:
        if l[i]==' ':
            nl.append(' ')
        else:
            nl.append('    ')#\t=4*' '
        i+=1
    blk=False
    while i<len(l):#delete mroe blank,delete para-1 -> para - 1
        if l[i]==' ':
            if blk==False:
                blk=True
            else:
                i+=1
                continue
        else:
            blk=False
        nl.append(l[i])
        if para_2.search(l[i]) and i+1<len(l) and\
                num_2.search(l[i+1]) and l[i+1][0]=='-':
            nl.append(' - ')
            nl.append(l[i+1][1:])
            i+=2
            continue
        #nl.append(l[i])
        i+=1
    return nl
def deal_stl(l):
    nl=[]
    i=0
    brk=0
    in_stl=False
    while i<len(l):
        if l[i] in stl_word or\
           (l[i].find('::')!=-1 and l[i].split('::')[-1] in stl_word):
            in_stl=True
        if l[i] == '<':
            if in_stl:
                brk+=1
                if nl[-1]==' ':
                    nl=nl[:-1]
                    while len(nl)>0 and nl[-1]==' ':
                        nl=nl[:-1]
                    nl.append(l[i])
                    if i+1<len(l) and l[i+1]==' ':
                        i+=2
                        continue
        elif l[i] == '>':
            if in_stl:
                brk-=1
                while len(nl)>0 and nl[-1]==' ':
                    nl=nl[:-1]
                if len(nl)>0 and nl[-1]=='>':
                    nl.append(' ')
            if brk==0:
                in_stl=False
        nl.append(l[i])
        i+=1
    return nl
def deal_line(line):
    add_comment=False
    xl=line.lstrip()
    lenth=len(line)-len(xl)
    if len(xl)==0:
        return [line]
    if xl[:2]=='//' and len(xl[2:].strip())>2:#comment
        line=xl[2:]
        add_comment=True
    elif xl[:2] in ignore or xl[0] in ignore:
        return [line]
    #if 'cin>>' in line or 'cout<<' in line:
    #    return [line]
    ll=get_all_item(line)
    ll=filter_ll(ll)
    ll=get_new_ll(ll)
    ll=deal_stl(ll)
    if add_comment:
        ll.insert(0,'//')
        ll.insert(0,' '*lenth)
    return ll
    #return ''.join(ll)
def check_braces(l):#{}
    nl=[]
    i=0
    while i<len(l):
        while len(l[i])>0 and l[i][-1]==' ':#delete blank end
            l[i]=l[i][:-1]
        if len(l[i])==0:
            i+=1
            continue
        #if l[i][0][:2]=='//' or (len(l[i])>1 and\
        if l[i][0][:2].lstrip()=='//' or (len(l[i])>1 and\
                l[i][0].strip()=='' and l[i][1][:2]=='//'):
            pass
        elif l[i][-1]=='{':
            if len(''.join(l[i]).strip())==1:
                if braces_style==1:
                    if nl[-1][-1]==' ':
                        nl[-1]=nl[:-1]
                    pass
                elif braces_style==0:
                    if nl[-1][-1]==')':
                        nl[-1].append(' {')
                        i+=1
                        continue
                    elif nl[-1][-1][:2]=='//':#()//
                        if len(nl[-1])>2:
                            if nl[-1][-2]==' ' and nl[-1][-3]==')':
                                nl[-1].insert(-1,'{')
                                i+=1
                                continue
                            elif nl[-1][-2]==')':
                                nl[-1].insert(-1,' {')
                                i+=1
                                continue
            elif len(''.join(l[i]).strip())>1:
                if braces_style==0:
                    if l[i][-2]!=' ':
                        l[i].insert(-1,' ')
                elif braces_style==1:
                    l[i]=l[i][:-1]
                    if l[i][-1]==' ':
                        l[i]=l[i][:-1]
                    lenth=len(''.join(l[i]))-len(''.join(l[i]).lstrip())
                    newl=[' '*lenth+'{']
                    nl.append(l[i])
                    nl.append(newl)
                    i+=1
                    continue
        elif l[i][-1][:2]=='//':
            #print l[i][-1].encode('gbk')
            ind=len(l[i])-2
            while ind>0 and l[i][ind]!='{' and l[i][ind]==' ':
                ind-=1
            if ind>0 and l[i][ind]=='{':
                if len(''.join(l[i][:ind+1]).strip())==1:
                    if braces_style==1:
                        pass
                    elif braces_style==0:
                        if nl[-1][-1]==')':
                            nl[-1].append(' {')
                            l[i][ind]=' '
                            nl.append(l[i])
                            i+=1
                            continue
                        elif nl[-1][-1][:2]=='//':#()//
                            if len(nl[-1])>2:
                                if nl[-1][-2]==' ' and nl[-1][-3]==')':
                                    nl[-1].insert(-1,'{')
                                    l[i][ind]=' '
                                    nl.append(l[i])
                                    i+=1
                                    continue
                                elif nl[-1][-2]==')':
                                    nl[-1].insert(-1,' {')
                                    l[i][ind]=' '
                                    nl.append(l[i])
                                    i+=1
                                    continue
                elif len(''.join(l[i][:ind+1]).strip())>1:
                    if braces_style==0:
                        if l[i][ind-1]!=' ':
                            l[i].insert(ind,' ')
                    elif braces_style==1:
                        #l[i]=l[i][:-1]
                        lenth=len(''.join(l[i][:ind+1]))-\
                                len(''.join(l[i][:ind+1]).lstrip())
                        l[i][ind]=' '
                        newl=[' '*lenth+'{']
                        nl.append(l[i])
                        nl.append(newl)
                        i+=1
                        continue
        nl.append(l[i]) 
        i+=1
    return nl
def get_end(line, end_char):
    end_flag=False
    if not line.startswith('//') and not line.startswith('/*'):
        if line.split('//')[0].strip()[-1] in end_char or\
                line.split('/*')[0].strip()[-1] in end_char:
            end_flag=True
            # end_char=False
    return end_flag
def check_braces_blank(res):
    bnum=0
    bflag=False  #{}
    no_end=False #,\
    pubpri=0
    nres=[]
    line_num = 1
    for line in res:
        line_num += 1
        if bnum<0:
            sys.stderr.write(str(line_num)+'bnum<0:'+line+'\n')
            bnum=0
        line=line.lstrip().replace('\t',' '*tab_width)
        if len(line)==0:
            nres.append(line)
            continue
        if line.split(' ')[0] in key_with_blank: #[else if...]
            bflag=True
            nres.append(' '*tab_width*bnum+line)
            if line.find('{')!=-1:
                bflag=False
                if line.find('}')==-1:
                    bnum+=1
                else:
                    pass
            no_end=get_end(line,["\\",","])
            if get_end(line,["}",";"]):
                bflag=False
            continue
        if line.strip()=='break;' and len(nres)>2 and\
           nres[-2].lstrip().startswith('case ') and\
           nres[-2].find('{')==-1:
            nres.append(' '*tab_width*(bnum+1)+line)
            continue
        if line.find('{')!=-1:
            nres.append(' '*tab_width*bnum+line)
            if line.lstrip()[:2]=='//':
                continue
            elif line.find('}')==-1:
                bnum+=1
            else:
                bnum+=line.count('{')-line.count('}')
            bflag=False
            continue
        if line.find('}')!=-1:
            if line[0]=='}':
                bnum-=1
                if bnum<pubpri:
                    pubpri=0
                    bnum-=1
                nres.append(' '*tab_width*bnum+line)
            else:
                nres.append(' '*tab_width*bnum+line)
                if line.lstrip()[:2]=='//':
                    continue
                bnum-=1
                if bnum<pubpri:
                    pubpri=0
                    bnum-=1
            continue
        if line.startswith('#'):
            nres.append(line)
            continue
        if line.strip() in ['public:','private:','protected']:
            if pubpri==0:
                bnum+=1
            nres.append(' '*tab_width*(bnum-1)+line)
            pubpri=bnum
            continue
        if bflag==True:
            bnum+=1
        if no_end==True:
            if bflag==True:
               nres.append(' '*tab_width*(bnum+1)+line)
            else:
               nres.append(' '*tab_width*(bnum+2)+line)
        else:
            nres.append(' '*tab_width*bnum+line)
        no_end=get_end(line,["\\",","])
        if bflag==True:
            bnum-=1
            if no_end==False:
               bflag=False
        if line.strip()=='default:':
            bflag=True
    if bnum!=0:
        sys.stderr.write('bnum!=0:'+line+'\n')
    return nres
def code_check_main(f1,f2):
    res=[]
    for x in file(f1):
        line=x.rstrip('\n').decode(default_coding)
        newline=deal_line(line)
        res.append(newline)
    res=check_braces(res)
    res=[''.join(x).rstrip() for x in res]
    res=check_braces_blank(res)
    if f1==f2:
        ff1=open(f1,'rU')
        ff1_str=ff1.read()
        ff1.close()
        bak_file = f1+'.bak.'+bak_time
        with open(bak_file,'wb') as ff2:
            ff2.write(ff1_str)
    with open(f2,'wb') as ff:
        ff.write('\n'.join(res).encode(default_coding))

if __name__=='__main__':
    global default_coding
    default_coding='gbk'
    if len(sys.argv) not in [3,4]:
        print USAGE
        print 'if srcfile==out_file,then new a bak for src_file'
        exit(-1)
    src_file=sys.argv[1]
    out_file=sys.argv[2]
    if len(sys.argv)==4 and sys.argv[3].lower() in ['gbk','utf8','utf-8','gb2312']:
        default_coding=sys.argv[3]
    code_check_main(src_file,out_file)
    argv = sys.argv
    if src_file==out_file:
        argv[1]=src_file+'.bak.'+bak_time
    print argv
    # print 'done'
