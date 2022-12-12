from copy import deepcopy

class Expression:
    
    def __init__(self, key='', value=True):
        self.key = key
        self.value = value
    
    def __str__(self):
        prefix = "" if self.value else '-'
        return f'{prefix + self.key}'#prefixf'({}'prefix + self.name

    def evaluate(self):
        return self.value
    
    def Not(self):
        return Expression(self.key, not self.value)


    def __eq__(self, o):
        if o.__class__ != Expression:
            return False
        return self.key == o.key and self.value == o.value

    def resolution(self, o):
        if o.__class__ == Expression and self.Not() == o:
            return Expression("NULL")

        if o.__class__ == Or:
            t = self.Not()
            if t in o.items:
                l = deepcopy(o.items)
                l.remove(t)
                
                if len(l) == 1:
                    return l[0]
                elif len(l) == 0:
                     return Expression("NULL")
                else:
                    return Or(*l)
        return None    
    def isStandard(self):
        return True

class And(Expression):
    def __init__(self, *args):
        self.items = []
        for x in args:
            if x.__class__ == And:
                for k in x.items:
                    if k not in self.items:
                        self.items.append(k)        
            elif x not in self.items:
                self.items.append(x)

        if len(self.items) < 2:
            raise Exception("And phải có 2 đối số duy nhất trở lên")
        
    def evaluate(self):
        for x in self.items:
            if not x.evaluate():
                return False
        return True

    def Not(self):
        return Or(*list(map(lambda x: x.Not(), self.items)))
        
    def __str__(self):
        return '(' + ' and '.join(map(lambda x: x.__str__(), self.items)) + ')'
    
    def __eq__(self, o):
        if o.__class__ != And or len(self.items) != len(o.items):
            return False
        for x in self.items:
            if x not in o.items:
                return False
        return True
    
    def resolution(self, o):
        return None

    def isStandard(self):
        return False
    
    def standard(self):
        return tuple(self.items)
    
    
class Or(Expression):
    def __init__(self, *args):
        self.items = []
        for x in args:
            if x.__class__ == Or:
                for k in x.items:
                    if k not in self.items:
                        self.items.append(k)        
            elif x not in self.items:
                self.items.append(x)
        if len(self.items) < 2:
            print(self.items[0])
            raise Exception("Or phải có 2 đối số duy nhất trở lên.")

    def evaluate(self):
        for x in self.items:
            if x.evaluate():
                return True
        return False

    def Not(self):
        return And(*list(map(lambda x: x.Not(), self.items)))

    def __str__(self):
         return '('+' or '.join(map(lambda x: x.__str__(), self.items)) +')'
    
    def __eq__(self, o):
        if o.__class__ != Or or len(self.items) != len(o.items):
            return False
        for x in self.items:
            if x not in o.items:
                return False
        return True
    
    def isStandard(self):
            if len(self.items) == 1:
                return False

            for i in self.items:
                if not i.isStandard():
                    return False
            return True

    def standard(self):
        if len(self.items) == 1:
                return self.items[0]
        rs = []
        t = None
        for x in self.items:
            if not x.isStandard(): # chan chan say ra
                t = x
                self.items.remove(x)
                break

        st = t.standard()
        for x in st:
            try:
                o = Or(*self.items, x)
                rs.append(o)
            except:
                rs.append(x)
        self.items.append(t)
        return rs# chua triet de ngay
    
    def resolution(self, o):
        if o.__class__ == Expression:
            return o.resolution(self)

        elif o.__class__ == Or:
            
            l = deepcopy(self.items)
            for x in l:
                t = x.Not()
                if t in o.items:
                    l.remove(x)
                    
                    for i in o.items:
                        if i != t and i not in l:
                            l.append(i)
                    if len(l) == 0:
                        return Expression("NULL")
                    if len(l) == 1:
                        return l[0]
                    return Or(*l)                       
        return None

class  Deduce(Expression):

    def __init__(self, *args):
        if len(args) != 2:
            raise Exception("Deduce chỉ có thể có chính xác hai đối số.")
        self.items = args
        
    def evaluate(self):
        if self.items[0].evaluate() and not self.items[1].evaluate():
            return False
        return True
        
    def Not(self):
        #(a=>b) = -a or b = not (a => b) = a and -b
        return And(self.items[0], self.items[1].Not())

    def __str__(self):
        return f'({self.items[0]} => {self.items[1]})'
    
    def standard(self):# chi chuan hoa mot bac
        # a => b: -a or b
        #(a and b) or (c and d) = (c and d) or a, (c and d) or b 
        return (Or(self.items[0].Not(), self.items[1]),)
    
    def resolution(self, o):
        return None
    
    def __eq__(self, o):
        if o.__class__ != Deduce:
            return False
        return self.items[0] == o.items[0] and self.items[1] == o.items[1]
    
    def isStandard(self):
        return False


class Equivalent(Expression):

    def __init__(self, *args):
        if len(args) != 2:
            raise Exception("Deduce chỉ có thể có chính xác hai đối số.")
        self.items = args
        
    def evaluate(self):
        if self.items[0].evaluate() and not self.items[1].evaluate():
            return False
        if self.items[1].evaluate() and not self.items[0].evaluate():
            return False
        return True
        
    def Not(self):
        #a <=> b = a =>b and b => a
        #(a=>b) = -a or b => not (a => b) = a and -b
        #not (b => a) = b and -a 
        return (Or(And(self.items[0], self.items[1].Not()), And(self.items[1], self.items[0].Not())), )

    def __str__(self):
        return f'({self.items[0]} <=> {self.items[1]})'
    
    def standard(self):
        # a <=> b = (-a v b) and (-b v a) 
        return Or(self.items[0].Not(), self.items[1]), Or(self.items[1].Not(), self.items[0])
    
    def resolution(self, o):
        return None
    
    def __eq__(self, o):
        if o.__class__ != Equivalent:
            return False
        return self.items[0] == o.items[0] and self.items[1] == o.items[1]
    
    def isStandard(self):
        return False


NULL_EXPRESSION = Expression("NULL")

def resolutions_util(g):
         
      #  tra ve ket qua phan giai va vi tri hai toans hang neu ton tai cap co the phan giai
        #  tra ve None neu khong phan giai duoc nua
  
    rs = []
    l = len(g)
    for i in range(l - 1):
        for j in range(i+ 1, l):
            t = g[i].resolution(g[j])
            if t == NULL_EXPRESSION:
                return t,i,j
            elif t != None:
                rs.append((t,i,j))
    if len(rs) != 0:
        return rs[0]            
    return None # khong phan giai duoc nua

def standard(g = []):
    i = 0
    while i < len(g):
        if not g[i].isStandard():
            t = g[i].standard()
            g.remove(g[i])
            g.extend(t)
        else:
            i += 1
    return g
            
def show(g, text= ""):
    print(text, end = "")
    for x in g:
        print(x, end=" ")
    print(" ")
    

def ronbinson(g , h=None):
    """
    input: + g = cac cong thuc
           + h = ket luan
    output:
        True: neu tu g co the suy ra h
        False: neu tu g khong suy ra dc h
    """
    g.append(h.Not())
    t = None
    t2= None

    show(g, "G sau khi them phu h: ")
    g = standard(g)
    show(g, "G sau khi dua ve dang chuan: ")

    while len(g) != 0:
        t = resolutions_util(g)
        if t == None:# khong phan giai duoc nua
            print("Khong phan giai duoc nua")
            show(g, "G sau khi khong phan giai duoc nua:")
            break
        
        show(t, "Ket qua phan giai: ")
        if t[0] == NULL_EXPRESSION:
            print("Phan giai ra cau :")
             
            
            return True

        t2 = g[t[2]]
        g.remove(g[t[1]])
        g.remove(t2)
        g.append(t[0])
        show(g, "G sau khi them ket qua phan giai: ")
    
    show(g)

    return False




# Bệnh ngoài da

a= Expression("A") # Mụn trứng cá
b= Expression("B")  # Viêm da dị ứng
c= Expression("C")  # Địa y phẳng
d= Expression("D")  # Nấm móng
e= Expression("E")  # Nấm da đầu
f= Expression("F")  # Vảy nến
g= Expression("G")  # Viêm da tiết bã nhờn
h= Expression("H")  # Viêm da cơ địa

# Triệu chứng
i= Expression("I") # mụn đâu đen
j= Expression("J") # mụn đầu trắng
k= Expression("K") # u nang
l= Expression("L") # da khô
m= Expression("M") # da gà
n = Expression("N") # da nứt nẻ dày lên
o= Expression("O") # móng dày
p = Expression("P") # vết sưng phẳng màu tím
q = Expression("Q") # vết loét đau trong miệng hoặc âm đạo
r = Expression("R") # móng có mùi hôi
s= Expression("S")  # đổi màu móng tay
t= Expression("T") # biến dạng hình dạng móng tay
u= Expression("U") # các mảng da có chấm đen
v= Expression("V") # các vùng màu xám hoặc đỏ có vảy
w = Expression("W") # da khô, nứt nẻ, chảy máu, ngứa ngáy
x= Expression("X") # xuất hiện nhiều mảng da đỏ
y= Expression("Y") # xuất hiện vảy dày óng ánh bạc
z= Expression("Z") # Móng tay dày có vết lõm hoặc đường rãnh
z= Expression("z") # ngứa ngáy khó chịu mức độ nhẹ
a1= Expression("A1") # trời nóng ra mồ hôi cơn ngứa tăng lên
b1= Expression("B1") # vùng da biij bệnh có màu đỏ cam bên trên phủ vảy xám trắng hoặc mỡ nhờn
c1= Expression("C1") # xuất hiện ban đỏ
d1= Expression("D1") # trên da có mụn nước nhỏ nông
e1= Expression("E1")# vùng da bị tổn thương thâm sạm,dày sừng,nứt nẻ

#dữ liệu logic
# i,j,k => a 
# l,m,n =>b 
# o,p,q =>c
# r,s,t=>d
# u,v=>e
# w,x,y,z =>f
# a1,b1,c1 =>g
# d1,e1,f1 => h

from collections import namedtuple

Test = namedtuple("Test", "g,h")

#g = (i and j) => a, (m ^ b => b), -m, -l  |||  h = (a or b)
test1 = Test([Deduce(And(i,j),a),Deduce(And(m,n),b),l.Not(),m,i,j], Or(a,b)) 

if __name__ == "__main__":    
    rs = ronbinson(test1.g, test1.h)
    print(rs)
 