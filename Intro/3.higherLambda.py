def comprehension():
    # x = [x for x in range(5)] # [0,1,2,3,4]
    # x = [x + 3 for x in range(5)] # [3,4,5,6,7]
    # x = [x % 3 for x in range(5)] # [0,1,2,0,1]
    # x = [x for x in range(2) for x in range(5)] # [0,1,2,3,4,0,1,2,3,4]
    x = [x for x in range(5) if x % 2 == 0] # [0,2,4]
    print(x)

def higher():
    nums = [1, 2, 3, 4, 5]

    # map()
    # returns a new list after applying given lambda function to each item in list
    squared = list(map(lambda a : a ** 2, nums))
    print(squared)

    # filter()
    # creates new list of elements for which given lambda function returns True
    odd = list(filter(lambda a : a % 2 == 0, nums))
    print(odd)

    # sorted()
    # uses lambda fns as keys for custom sorting
    rev = sorted(nums, key=lambda x : -x) # reverses nums
    print(rev)

    students = [('A', 18), ('B', 15), ('A', 12)]
    roll = sorted(students, key=lambda x : x[1]) # sorts based on index 1
    print(roll)


def lmb():
    sum = lambda a, b: a + b
    greet = lambda name : f'hello, {name}'
    print(sum(3,5))
    print(greet("himanshu"))


def main():
    # lmb()
    higher()

if __name__ == '__main__':
    main()
