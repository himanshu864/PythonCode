import random

def main():
    # randomly generate 15 numbers in the range of 5 to 55
    # st = {int(5 + 50 * random.random()) for _ in range(15)}
    st = set(random.randint(5, 55) for _ in range(15))
    print(st)
    print(f"Size of set: {len(st)}")

    # count numbers in set smaller than 35
    # s = sum(1 for num in numbers_set if num < 35)
    # s = {num for num in st if num < 35}
    s = set(filter(lambda i: i < 35, st))
    print(f"Count of numbers smaller than 35: {len(s)}")

    # Delete all numbers that are smaller than 35
    t = st - s
    print(t)

if __name__ == '__main__':
    main()