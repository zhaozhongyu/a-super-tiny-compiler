#https://zhuanlan.zhihu.com/p/21830284
#-------------------------------------------------------------------------------
# Project:     mysite
# Name:        compiler
# Purpose:     
# Author:      zhaozhongyu
# Created:     2016/8/5 9:33
# Copyright:   (c) "zhaozhongyu" "2016/8/5 9:33" 
# Licence:     <your licence>
# -*- coding:utf-8 -*-
#-------------------------------------------------------------------------------
"""

"""

"""
/**
* 今天让我们来写一个编译器，一个超级无敌小的编译器！它小到如果把所有注释删去的话，大概只剩
* 200行左右的代码。
* 
* 我们将会用它将 lisp 风格的函数调用转换为 C 风格。
*
* 如果你对这两种风格不是很熟悉，下面是一个简单的介绍。
*
* 假设我们有两个函数，`add` 和 `subtract`，那么它们的写法将会是下面这样：
* 
*                  LISP                      C
*
*   2 + 2          (add 2 2)                 add(2, 2)
*   4 - 2          (subtract 4 2)            subtract(4, 2)
*   2 + (4 - 2)    (add 2 (subtract 4 2))    add(2, subtract(4, 2))
*
* 很简单对吧？
*
* 这个转换就是我们将要做的事情。虽然这并不包含 LISP 或者 C 的全部语法，但它足以向我们
* 展示现代编译器很多要点。
* 
*/

/**
* 大多数编译器可以分成三个阶段：解析（Parsing），转换（Transformation）以及代码
* 生成（Code Generation）
*
* 1.*解析*是将最初原始的代码转换为一种更加抽象的表示（译者注：即AST）。*
*
* 2.*转换*将对这个抽象的表示做一些处理，让它能做到编译器期望
*    它做到的事情。
*
* 3.*代码生成*接收处理之后的代码表示，然后把它转换成新的代码。
*/
"""
'''
/**
* 解析（Parsing）
* -------
*
* 解析一般来说会分成两个阶段：词法分析（Lexical Analysis）和语法分析（Syntactic Analysis）。
*
* 1.*词法分析*接收原始代码，然后把它分割成一些被称为 Token 的东西，这个过程是在词法分析
*    器（Tokenizer或者Lexer）中完成的。
*
*    Token 是一个数组，由一些代码语句的碎片组成。它们可以是数字、标签、标点符号、运算符，
*    或者其它任何东西。
*
* 2.*语法分析* 接收之前生成的 Token，把它们转换成一种抽象的表示，这种抽象的表示描述了代
*    码语句中的每一个片段以及它们之间的关系。这被称为中间表示（intermediate representation）
*    或抽象语法树（Abstract Syntax Tree， 缩写为AST）
*
*    抽象语法树是一个嵌套程度很深的对象，用一种更容易处理的方式代表了代码本身，也能给我们
*    更多信息。
*
* 比如说对于下面这一行代码语句：
*
*   (add 2 (subtract 4 2))
*
* 它产生的 Token 看起来或许是这样的：
*
*   [
*     { type: 'paren',  value: '('        },
*     { type: 'name',   value: 'add'      },
*     { type: 'number', value: '2'        },
*     { type: 'paren',  value: '('        },
*     { type: 'name',   value: 'subtract' },
*     { type: 'number', value: '4'        },
*     { type: 'number', value: '2'        },
*     { type: 'paren',  value: ')'        },
*     { type: 'paren',  value: ')'        }
*   ]
*
* 它的抽象语法树（AST）看起来或许是这样的：
*
*   {
*     type: 'Program',
*     body: [{
*       type: 'CallExpression',
*       name: 'add',
*       params: [{
*         type: 'NumberLiteral',
*         value: '2'
*       }, {
*         type: 'CallExpression',
*         name: 'subtract',
*         params: [{
*           type: 'NumberLiteral',
*           value: '4'
*         }, {
*           type: 'NumberLiteral',
*           value: '2'
*         }]
*       }]
*     }]
*   }
*/

/**
* 转换（Transformation）
* --------------
*
* 编译器的下一步就是转换。它只是把 AST 拿过来然后对它做一些修改。它可以在同种语言下操
* 作 AST，也可以把 AST 翻译成全新的语言。
*
* 下面我们来看看该如何转换 AST。
*
* 你或许注意到了我们的 AST 中有很多相似的元素，这些元素都有 type 属性，它们被称为 AST
* 结点。这些结点含有若干属性，可以用于描述 AST 的部分信息。
*
* 比如下面是一个“NumberLiteral”结点：
*
*   {
*     type: 'NumberLiteral',
*     value: '2'
*   }
*
* 又比如下面是一个“CallExpression”结点：
*
*   {
*     type: 'CallExpression',
*     name: 'subtract',
*     params: [...nested nodes go here...]
*   }
*
* 当转换 AST 的时候我们可以添加、移动、替代这些结点，也可以根据现有的 AST 生成一个全新
* 的 AST
*
* 既然我们编译器的目标是把输入的代码转换为一种新的语言，所以我们将会着重于产生一个针对
* 新语言的全新的 AST。
* 
*
* 遍历（Traversal）
* ---------
*
* 为了能处理所有的结点，我们需要遍历它们，使用的是深度优先遍历。
*
*   {
*     type: 'Program',
*     body: [{
*       type: 'CallExpression',
*       name: 'add',
*       params: [{
*         type: 'NumberLiteral',
*         value: '2'
*       }, {
*         type: 'CallExpression',
*         name: 'subtract',
*         params: [{
*           type: 'NumberLiteral',
*           value: '4'
*         }, {
*           type: 'NumberLiteral',
*           value: '2'
*         }]
*       }]
*     }]
*   }
*
* So for the above AST we would go:
* 对于上面的 AST 的遍历流程是这样的：
*
*   1. Program - 从 AST 的顶部结点开始
*   2. CallExpression (add) - Program 的第一个子元素
*   3. NumberLiteral (2) - CallExpression (add) 的第一个子元素
*   4. CallExpression (subtract) - CallExpression (add) 的第二个子元素
*   5. NumberLiteral (4) - CallExpression (subtract) 的第一个子元素
*   6. NumberLiteral (4) - CallExpression (subtract) 的第二个子元素
*
* 如果我们直接在 AST 内部操作，而不是产生一个新的 AST，那么就要在这里介绍所有种类的抽象，
* 但是目前访问（visiting）所有结点的方法已经足够了。
*
* 使用“访问（visiting）”这个词的是因为这是一种模式，代表在对象结构内对元素进行操作。
*
* 访问者（Visitors）
* --------
*
* 我们最基础的想法是创建一个“访问者（visitor）”对象，这个对象中包含一些方法，可以接收不
* 同的结点。
*
*   var visitor = {
*     NumberLiteral() {},
*     CallExpression() {}
*   };
*
* 当我们遍历 AST 的时候，如果遇到了匹配 type 的结点，我们可以调用 visitor 中的方法。
*
* 一般情况下为了让这些方法可用性更好，我们会把父结点也作为参数传入。
*/

/**
* 代码生成（Code Generation）
* ---------------
*
* 编译器的最后一个阶段是代码生成，这个阶段做的事情有时候会和转换（transformation）重叠，
* 但是代码生成最主要的部分还是根据 AST 来输出代码。
*
* 代码生成有几种不同的工作方式，有些编译器将会重用之前生成的 token，有些会创建独立的代码
* 表示，以便于线性地输出代码。但是接下来我们还是着重于使用之前生成好的 AST。
*
* 我们的代码生成器需要知道如何“打印”AST 中所有类型的结点，然后它会递归地调用自身，直到所
* 有代码都被打印到一个很长的字符串中。
* 
*/

/**
* 好了！这就是编译器中所有的部分了。
*
* 当然不是说所有的编译器都像我说的这样。不同的编译器有不同的目的，所以也可能需要不同的步骤。
*
* 但你现在应该对编译器到底是个什么东西有个大概的认识了。
*
* 既然我全都解释一遍了，你应该能写一个属于自己的编译器了吧？
*
* 哈哈开个玩笑，接下来才是重点 :P
*
* 所以我们开始吧...
*/
'''
'''
/**
* =======================================================================
*                              (/^▽^)/
*                       词法分析器（Tokenizer）!
* =======================================================================
*/

/**
* 我们从第一个阶段开始，即词法分析，使用的是词法分析器（Tokenizer）。
*
* 我们只是接收代码组成的字符串，然后把它们分割成 token 组成的数组。
*
*   (add 2 (subtract 4 2))   =>   [{ type: 'paren', value: '(' }, ...]
*/
'''

def tokenizer(string):
    #current 变量记录当前代码串的位置
    current = 0
    #tokens 放置token
    tokens = []
    #创建while循环，current变量在循环中自增
    while(current < len(string)):
        char = string[current]
        #检查是不是左括号
        if(char == '('):
            #如果是左括号，则加入到tokens
            tokens.append({"type": "paren", "value": "("})
            current += 1
            continue
        #检查是不是右括号
        if(char == ')'):
            tokens.append({"type": "paren", "value": ")"})
            current += 1
            continue
        #如果是空格，则跳过
        if(char.isspace()):
            current += 1
            continue
        #检查是否是数字
        if(char.isdigit()):
            value = ''
            #遍历后面的数字
            while(char.isdigit()):
                value += char
                current += 1
                char = string[current]
            tokens.append({"type": "number", "value": value})
            continue
        #检查是否字母，这个代表token类型为name
        if(char.isalpha()):
            value = ''
            while(char.isalpha()):
                value += char
                current += 1
                char = string[current]
            tokens.append({"type": "name", "value": value})
            continue


"""
/**
* =======================================================================
*                            ヽ/❀o  ͜ o\ﾉ
*                        语法分析器（Parser）!!!
* =======================================================================
*/

/**
*  语法分析器接受 token 数组，然后把它转化为 AST
*
*   [{ type: 'paren', value: '(' }, ...]   =>   { type: 'Program', body: [...] }
*/

"""

