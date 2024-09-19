def fns():
    x = 5
    y = 3
    x /= y # 1.66667
    if bool('True') == True and not(x == 1):
        print("Ya" + ("ta" * 3) + "!")
    else:
        print("nu uh")

def intro():
    age = input('Enter age: ')
    print('age = ', age)
    print(f'age = {age}')
    if int(age) > 18:
        print('Cheers')
    elif int(age) > 0:
        print('Grow up shinji')
    else:
        print('Norobo')
        
    name = input('Kimi wa? ')
    print('Hello {}' .format(name))

def temp():
    degree = str(98.3)
    cal = float(32)
    print(type(degree))
    print(cal)
    hot = bool(40)
    print(hot)

def main():
    print('Hello')
    # intro()
    temp()

if __name__ == '__main__':
    main()