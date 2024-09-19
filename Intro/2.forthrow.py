def forloopie():
    arr = [5,4]
    for i in arr:
        print(i)
    print(arr)

    for i in range(3):
        print(i)
    # a = 1
    # while a < 3:
    #     print(a)
    #     a += 1

    names = ["Joyce", 'Hannah', 'Manny', 'Manoj', 'Ezekiel']
    for name in names:
        if 'j' in name.lower():
            continue
        print(name)

def main():
    try:
        a = input("Enter a: ")
        if(int(a) > 4):
            print("yatta")
    except:
        print("a should an integer")
    finally: # always print
        print("The end!")

    print("Still rollin")

if __name__ == '__main__':
    main()
