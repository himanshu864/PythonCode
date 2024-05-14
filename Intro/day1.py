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