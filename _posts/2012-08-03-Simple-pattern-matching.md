---
layout: post.html
title: 'pattern matching & clojure'
tagline: 'represent your ideas simply'
---

#Pattern Matching

Lately, I've been fascinated by [clojure](http://clojure.org), a dynamically typed lisp hosted on the JVM. Clojure is known for its immutable data types and list processing capabilities, but as it turns out it's really good at representing abstract ideas, too.  A while back I came upon this [gist](https://gist.github.com/2594296) by [david nolen](http://dosync.posterous.com) (who happens to have authored quite a number of awesome gists), and was reminded of it today while talking about different ways to structure some validation methods.

The gist shows user/pass validation using pattern matching in two languages, clojure and javascript. But more than that, it shows how sometimes all you need are simple case expressions. To explain it however, I think we may need a small primer in clojure.

If you don't know clojure, or lisp, the syntax is pretty simple.  Everything is a expression (called s-expression or s-exp), expressions are defined by parentheses, and the first thing in a expression is a function where the rest are the parameters to be supplied to that function.  

So instead of saying `printf("Hello, %s!", "world")`
you would say `(printf "Hello, %s!" "world")`.

Since everything in clojure is just a function with parameters if you want to describe something you must realize it, or evaluate the code.  A expression like `(+ 1 (+ 3 4))` follows relatively simply; *The function + is called with 1 and some form. That form is the value of the + function called with 3 and 4.* When + finally returns the value of 7, the outer function can continue and realize its value of 8.

Consider the following:

~~~~{js}
var x = 1,
    y = 2;
console.log("My coordinates are: ", x, y);
x += 1;
y += -1;
console.log("After moving southeast, I've arrived at: ", x, y)
~~~~

How could we even explain this simple bit of code with our previous set of syntax rules? It's impossible! This is because the previous problem of summing 1, 3, and 4 could be described as a pure function (which is a special way to say that the function is referentially transparent, or that given the same inputs it will always return the same outputs), while our javascript example involves simple mutable state. But do we need this state? When is it time to come and clean up the vars x and y? Are we done using them yet? Will we ever be? 

We could represent the previous snippet in clojure like this:

~~~~{clj}
(let [x 1
      y 2]
  (println "My coordinates are: " x y)
  (let [x (inc x)
        y (dec y)]
    (println "After moving southeast, I've arrived at: " x y)))
~~~~

This may look odd if you've never used a lisp before, but let's try to apply our previous set of syntax rules to this single expression.
The first part of the expression is the function `let`, invoked with 3 parameters; the value of some vector, and two `s-exp`s (one is the println fn, and another is the let fn). These forms are all at the same level, so we can continue by taking the values from them sequentially.  There's a problem however, if we try to take the value of **any** of them, we will realize that we don't yet have the value of x or y! (try it yourself).  Clearly this *'everything is a function'* stuff is a lie, if the syntax were only that simple, we wouldn't be able to represent even the simplest of problems!

But we've yet to address the problem of the side effects; specifically, why does our javascript code have them while the same code in clojure does not? The reason for this is that the act of assignment itself is necessarily a side effect. Its entire purpose is to provide a particular value which other functions can reference at some other point in time. However, unchecked assignment is not always ideal as anyone familiar with concurrent assignment and referencing can tell you. And so, in order to resolve this issue once and for all, God invented the `macro`.

A `macro` is a special kind of `fn` that doesn't immediately evaluate the parameters it receives.  Instead it's defined in terms of a special function recipe in which it reorganizes or modifies the expressions provided to it, transforming and evaluating the values it requires while substituting the values of others.

So then, `let` is a macro which doesn't immediately evaluate its forms.  Instead it takes as its first parameters a binding vector, containing an even amount of elements to be considered as keys and values.  It then walks all subsequent forms, evaluating them and substituting the value of the required key any time it is asked for. So we could describe the previous snippet as follows:

*Invoke the let macro with the binding vector where `x` is 1 and `y` is 2. With values in hand, continue walking the forms and evaluating, supplying the value of any given symbol should it be bound to some value.* --  The let macro has no problems when the lets are nested and shadows the old values for x and y while incrementing and decrementing them to get the new values to be bound only for the inner expressions!
 
Onwards to the code!

~~~~{clj}
(defn validates-credentials [username password]
  (let [uc (count username)
        pc (count password)
        less-than-3? (fn [n] (< n 3))
        less-than-4? (fn [n] (< n 4))]
    (match [username uc password pc]
       [(:or nil "") _ _ _]             {:error "No username given" :field "name"}
       [_ _ (:or nil "") _]             {:error "No password given" :field "pass"}
       [_ (_ :when [less-than-3?]) _ _] {:error "Username less than 3 characters" :field "pass"}
       [_ _ _ (_ :when [less-than-4?])] {:error "Password less than 4 characters" :field "pass"}
       [#"^([a-z0-9-_]+)$" _ _ _]       {:error "Username contains invalid characters" :field "name"}
       :else true)))
~~~~

I'm sure the first thing you realize is that there is an awful lot of weird characters in this, as if someone were holding their shift key while sweeping their fingers around the keyboard; but don't worry, the important thing is that each of those characters has a syntactic meaning!

The first line just invokes the `defn` macro, which names a function that takes some parameter list defined in the binding vector and subsequently, the form to bind the values of the parameters to.  In our case the function is named `validate-credentials`, and it takes two arguments: `username` and `password`.  It then uses let to get the shorthand for four symbols, `uc`, defined as the count of the characters in username, `pc` defined as the count of the characters in the password, a `less-than-3?` fn to determine whether a given number is less than 3, and the respective fn for `less-than-4?`. It then invokes the pattern matching macro supplying pairs of patterns to match and expressions to evaluate upon successful match.  What it says on line 6 is to match against the values for the four symbols username, uc, password, and pc, in that specific order.  Those _ are actually variables names, where the variables could be used in the following expession. Using an underscore as a variable name is a common idiom for saying 'throw away this value'.

The first expression says: 
*If the username is nil or the empty string, and the rest of the values are anything, give a no username given error.*

The second expression says:
*If the password is nil or the empty string, and the rest of the values are anything, give a no password given error.*

The third expression says:
*I don't care about the values for anything, but when the value of the username count is is less than 3, give a bad usercount error.*

The fourth expression says:
*If the passcount is less than 4, return the respective error.*

The fifth expression says:
*I care only that the username is in alphanumeric.*

Once your eyes uncross from trying to read all those funny characters, the solution is really quite elegant. Things are always just defined in terms of simple pairs, a binding vector and the code to evaluate with those symbols bound, from the let form to the defn form to the matching form.  Once you know how to read the pattern matcher, you don't even need to think about how to implement your control flow, you simply describe the shape of your interesting cases and dispatch off of them. The [core.match](https://github.com/clojure/core.match) library shown above enables vastly richer pattern matching than simple case or conditional expressions, holding onto variables in a similar way to let, allowing for a refreshingly clear and succinct representation of complex scenarios.  

But enough about musing about how great clojure is, let's look at the javascript version!

~~~~{js}
var user = {
  validateCredentials: function (username, password) {
    return (
        (!(username += '') || username === '') ? { error: "No Username Given.", field: 'name' }
      : (!(password += '') || password === '') ? { error: "No Password Given.", field: 'pass' }
      : (username.length < 3)                  ? { error: "Username is less than 3 Characters.", field: 'name' }
      : (password.length < 4)                  ? { error: "Password is less than 4 Characters.", field: 'pass' }
      : (!/^([a-z0-9-_]+)$/i.test(username))   ? { error: "Username contains invalid characters.", field: 'name' }
      : true
    );
  }
};

var results = user.validateCredentials('Nijikokun','somepassword');
console.log(results);
~~~~

Note: If you are less than familiar with javascript (and specifically [ternary operators](https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Operators/Conditional_Operator)), you should check out mozilla's awesome [tutorial](https://developer.mozilla.org/en-US/docs/JavaScript/Guide/Values,_variables,_and_literals).  

The first thing a few of my js hacker friends said when they saw this snippet was how readable and elegant it was for a validator in javascript, and I don't disagree; but even still I want to take a closer look at it. It starts by defining an object named user, who has one attribute, a method named `validateCredentials`.  This method also takes two parameters: username and password. Besides the extra concept of the `Object`, by line 2 we are still remarkably similar to the earlier clojure implementation.  Line 3 specifies that the following expression is the return value of the function (clojure didn't need to state this because the last form inside of a defn is implicitly the return value).

Finally, it begins its pattern matching rules by leveraging nested ternary expressions, or nested `if ? then : else` expressions.  But wait, what's going on in our first pattern? 

If we try to convert that first pattern matching form to english it becomes something like:
*If the boolean opposite of the username plus the empty string or if the username is the empty string then give the no username given error*

Wait, the opposite of the username plus the empty string? What does this even mean?! It turns out that in javascript, simple nil checks aren't exactly simple, with the nil being possibly undefined or possibly some other falsey value (which may cause some unexpected behavior), and so in order to get at a boolean value, we coerce it into a string type by adding it to the empty string, then coerce it further into its boolean opposite using the `!` operator. Since an empty string will evaluate as false the boolean opposite of this evaluation is true, causing the if expression to succeed, and giving our failure message! -- *Whew!* Now in order to understand line 4 we must understand `Ternaries`, `Type coercion`, and `Objects`, as well as the short circuit logic of the `||` operator.  Before we only needed to understand functions, macros and the shape of some data!

Once we know some rules about javascript the rest follow easily and clearly, save for the usage of the regular expression (which was also used in the clojure example). My point is that once you understand the idiosyncrasies of the language you are using, you forget what it is like to not have to deal with them.  You say *ah yes, this is simple because I know how to do it, it is clear because I can read it*, and things like the above js pattern matching appear beautiful and elegant to you, regardless of their incidental complexity. And it is elegant javascript; it imports a simple idea into a language with complicated syntax. That is a good thing.

But wouldn't you rather just use a language where the simple syntax made it trivial to represent your ideas, whether simple or complex?  For more, I highly recommend watching author of clojure, Rich Hickey's amazing talk on this sort of simplicity, [Simple Made Easy](http://www.infoq.com/presentations/Simple-Made-Easy).  Oh, also, if you made it this far, drop me a line and tell me what you thought! [twitter](http://twitter.com/omniegg/) or [g+](http://gplus.to/egghead/)
