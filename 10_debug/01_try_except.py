#!/usr/bin/env python3
# -*- coding:utf-8 -*-


"""
@version: ??
@usage: 错误处理
Python所有的错误都是从BaseException类派生的，常见的错误类型和继承关系看这里：

https://docs.python.org/3/library/exceptions.html#exception-hierarchy


@author: kHRYSTAL
@license: Apache Licence 
@contact: khrystal0918@gmail.com
@site: https://github.com/kHRYSTAL
@software: PyCharm
@file: 01_try_except.py
@time: 16/5/17 下午3:05
"""
def foo():
    def some_function():
        pass
    r = some_function()
    if r==(-1):
        return (-1)
    return r

def bar():
    def foo():
        pass
    r = foo()
    if r == (-1):
        print('Error')
    else:
        pass

'''
一旦出错，还要一级一级上报，直到某个函数可以处理该错误（比如，给用户输出一个错误信息）。

所以高级语言通常都内置了一套try...except...finally...的错误处理机制，Python也不例外。
'''



try:
    print('try...')
    r = 10/0
    print('result:',r)
except ZeroDivisionError as e:
    print('except:',e)
finally:
    print('finally...')
print('END')
'''
当我们认为某些代码可能会出错时，就可以用try来运行这段代码，如果执行出错，则后续代码不会继续执行，而是直接跳转至错误处理代码，即except语句块，执行完except后，如果有finally语句块，则执行finally语句块，至此，执行完毕。

上面的代码在计算10 / 0时会产生一个除法运算错误
'''
try:
    print('try...')
    r = 10/2
    print('result:',r)
except ZeroDivisionError as e:
    print('except',e)
finally:
    print('finally...')
print('END')

'''
由于没有错误发生，所以except语句块不会被执行，但是finally如果有，则一定会被执行（可以没有finally语句）。

你还可以猜测，错误应该有很多种类，如果发生了不同类型的错误，应该由不同的except语句块处理。没错，可以有多个except来捕获不同类型的错误
'''

'''
int()函数可能会抛出ValueError，所以我们用一个except捕获ValueError，用另一个except捕获ZeroDivisionError。

此外，如果没有错误发生，可以在except语句块后面加一个else，当没有错误发生时，会自动执行else语句
'''
try:
    print('try...')
    r = 10 / int('a')
    print('result:',r)
except ValueError as e:
    print('ValueError:',e)
except ZeroDivisionError as e:
    print('ZeroDivisionError',e)
else:
    print('no error!')
finally:
    print('finally...')
print('END')

'''
Python的错误其实也是class，所有的错误类型都继承自BaseException，所以在使用except时需要注意的是，它不但捕获该类型的错误，还把其子类也“一网打尽”。比如：

try:
    foo()
except ValueError as e:
    print('ValueError')
except UnicodeError as e:
    print('UnicodeError')
第二个except永远也捕获不到UnicodeError，因为UnicodeError是ValueError的子类，如果有，也被第一个except给捕获了。
'''


'''
使用try...except捕获错误还有一个巨大的好处，
就是可以跨越多层调用，比如函数main()调用foo()，
foo()调用bar()，结果bar()出错了，这时，只要main()捕获到了，就可以处理：
'''
def foo(s):
    return 10/int(s)
def bar(s):
    return foo(s) * 2

def main():
    try:
        bar('0')
    except Exception as e:
        print('Error:',e)
    finally:
        print('finally...')
'''
也就是说，不需要在每个可能出错的地方去捕获错误，
只要在合适的层次去捕获错误就可以了。
这样一来，就大大减少了写try...except...finally的麻烦。
'''





'''
调用堆栈

如果错误没有被捕获，它就会一直往上抛，
最后被Python解释器捕获，打印一个错误信息，然后程序退出。
'''
def foo(s):
    return 10 / int(s)

def bar(s):
    return foo(s) * 2

def main():
    bar('0')

# main()


'''
记录错误

如果不捕获错误，自然可以让Python解释器来打印出错误堆栈，
但程序也被结束了。既然我们能捕获错误，就可以把错误堆栈打印出来，
然后分析错误原因，同时，让程序继续执行下去。
'''

import logging
def foo(s):
    return 10/int(s)
def bar(s):
    return foo(s) * 2
def main():
    try:
        bar('0')
    except Exception as e:
        logging.exception(e)
# main()
# print('END')


'''
抛出错误

因为错误是class，捕获一个错误就是捕获到该class的一个实例。因此，错误并不是凭空产生的，而是有意创建并抛出的。Python的内置函数会抛出很多类型的错误，我们自己编写的函数也可以抛出错误。

如果要抛出错误，首先根据需要，可以定义一个错误的class，
'''

class FooError(ValueError):
    pass

def foo(s):
    n = int(s)
    if n == 0:
        raise FooError('invalid value: %s' %s)
    return 10/0

#print('START')
#foo('0')

'''
Traceback (most recent call last):
  File "01_try_except.py", line 193, in <module>
    foo('0')
  File "01_try_except.py", line 189, in foo
    raise FooError('invalid value: %s' %s)
__main__.FooError: invalid value: 0

'''





def foo(s):
    n = int(s)
    if n==0:
        raise ValueError('invalid value: %s' % s)
    return 10 / n

def bar():
    try:
        foo('0')
    except ValueError as e:
        print('ValueError!')
        raise

#bar()
'''
在bar()函数中，我们明明已经捕获了错误，但是，打印一个ValueError!后，又把错误通过raise语句抛出去了，这不有病么？

其实这种错误处理方式不但没病，而且相当常见。捕获错误目的只是记录一下，便于后续追踪。但是，由于当前函数不知道应该怎么处理该错误，所以，最恰当的方式是继续往上抛，让顶层调用者去处理。好比一个员工处理不了一个问题时，就把问题抛给他的老板，如果他的老板也处理不了，就一直往上抛，最终会抛给CEO去处理。

raise语句如果不带参数，就会把当前错误原样抛出。此外，在except中raise一个Error
'''




try:
    10/0
except ZeroDivisionError:
    raise ValueError('input error!')

#只要是合理的转换逻辑就可以，但是，决不应该把一个IOError转换成毫不相干的ValueError。










def func():
    pass


class Main():
    def __init__(self):
        pass


if __name__ == '__main__':
    pass