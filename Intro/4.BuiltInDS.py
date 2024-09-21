def sets():
    s1 = {'himanshu', 2, 234.2, 'b', 2}
    print(s1)

    # set() create set from list removing duplicates
    lst = ['a', 'b', 3, 3]
    s2 = set(lst)
    print(s2)

    # use in to check if value exists
    print('himanshu' in s1)
    print('himanshu' in s2)

    # immutable but can add unique elements
    s2.add('c')

    # union() joins iterable object with existing object
    print(s1.union(s2))
    # Note: s1 doesn't update
    print(s1)

    # update() take any iterable object (tuple, lists, dictionaries, sets)
    # and adds object to existing set
    s1.update(s2)
    print(s1)
    # s1.update(lst)

    # removes existing element from set
    s1.remove('himanshu')
    print(s1)

    # set is iteratable hence for loop
    for x in s2:
        print(x)

def dict():
    d = {
        'h' : 'himanshu',
        2 : [3,2,'a'],
        ('x', 'y') : {6 : 9}
    }
    print(d['h']) # access

    d['h'] = 'aggarwal' # update
    print(d)

    d[2].append(0) # modify value
    d[3] = 5 # add new
    print(d)

    print(len(d))

    dp = {'a' : 3, 2 : 5}
    d.update(dp) # adds dp to d. updates existing keys and adds new
    print(d)

    print(d.keys())
    print(d.values())

    del d['h']
    print(d)

def tuply():
    t = ('abc', 34, 'd', -4, 5.5, (3,7,4))
    print(t)
    print(t[0]) # indexing works
    print(t[1:3]) # slicing works
    print(len(t)) # length
    print(max(t[5])) # returns max when tuple of same data type

    tp = ('abc', 'a', 'b', 'acb', 'a')
    print(min(tp))
    print(sorted(tp))

    print(tp.index('a')) # returns index of first occ. of arg.
    print(tp.count('a')) # returns freq. of arg.

def listy():
    l = ['abc', 123, "v", 4.27, ['x', 4]] # flexible

    print(l[4][0])
    print(l[0:2]) # slicing works
    print(len(l)) # lengh

    l.append('hello') # appends argument to end
    print(l)

    l.remove(4.27) # removes 4.27
    print(l)

    l.pop(1) # pops 1st index
    print(l)

def stringy():
    s = "My name is Himanshu!"
    print(s[0])
    print(s[3:7]) # slice - start index : end index + 1
    print(s[11:]) # from 11th index to end

    # negative index to print letters from back
    print(s[-1]) # first from back
    print(s[-9:]) # 9th from back to end
    print(s[-9:-1]) # 9th from back to 2nd from back

    print(len(s)); # length

    print(s.upper()) # returns string after converting all letters capital
    print(s.lower())
    print(s.title()) # Capitalize first letter of all words

    # split() : splits string into list of strings at argument
    print(s.split('a'))

def main():
    # stringy()
    # listy()
    # tuply()
    dict()
    # sets()

if __name__ == '__main__':
    main()
