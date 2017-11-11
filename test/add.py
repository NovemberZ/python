# coding=UTF-8
print(100 / 3.0)
print(True)
print(1 > 2)

a = 123
print(a)
a = 'ABC'
print(a)
print('包含中文的str')

classmates = ['Michael', 'Bob', 'Tracy']

print(classmates[-1])

p = ['asp', 'php']
s = ['python', 'java', p, 'scheme']
print(s)

t = (1, 2)
print(t)
print(t[0])

age = 20
if age >= 18:
    print('your age is', age)
    print('adult')


age = 3
if age >= 18:
    print('your age is', age)
    print('adult')
else:
    print('your age is', age)
    print('teenager')

names = ['Michael', 'Bob', 'Tracy']
for name in names:
    print(name)

print(range(5))

# input("xxxx:")

d = {'Michael': 95, 'Bob': 75, 'Tracy': 85}
print(d['Michael'])

s = set([1, 1, 2, 2, 3, 3])
print(s)

print(1 != 2)
