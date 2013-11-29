---
layout: post.html
title: 'three little birds'
tagline: 'playing with combinators'
---

Simple functions can be very surprising. With functional programming on the rise more and more of my time has been dedicated to understanding functions. In doing so I've discovered their deep and rich history in practical mathematics, in particular [Combinatory Logic](http://en.wikipedia.org/wiki/Combinatory_logic) and [Lambda Calculus](http://en.wikipedia.org/wiki/Lambda_calculus). Understanding the contributions from these fields can help immensely when trying to reason about complex function chains, which are encountered more and more often in modern programing. 

### Introductions
*Lambda calculus is the use of anonymous function application for calculation* and is defined in terms of simple substitution and conversion rules.
For an excellent introduction to the lambda calculus I recommend Bret Victor's [Alligator Eggs](http://worrydream.com/AlligatorEggs/)

*Combinatory logic is the use of functions to combine functions.* A combinator is a function whose input are functions and whose body is defined only in terms of function application. This is another way of saying that a combinator cannot introduct anything new, it can only combine.
For an introduction to Combinatory Logic you can do no better than Smullyan's [To Mock a Mockingbird](http://en.wikipedia.org/wiki/To_Mock_a_Mockingbird) or any of the various [books](https://leanpub.com/u/raganwald) or [posts](http://braythwayt.com/) by [@raganwald](https://twitter.com/raganwald). 

While all of this might sound complex, when viewed in the context of our everyday programming it is rather simple, though the implications are profound. 

In *To Mock a Mockingbird*, Smullyan refers to the functions in combinatory logic as birds, and those of us whom wish to understand them as curious birdwatchers. (As we will see, the birds are quite curious themselves). The premise of the metaphor surrounds a birdwatcher who makes bird calls out to some bird in a forest, which responds back with a bird noise of its own. With some imagination, we can use this to represent function application.

### Borrowing the metaphor
There are a few important but subtle points around this metaphor that must be understood to see why it represents combinatory logic in particular (as opposed to general function application). 

The first is that birds only speak in the language of the birds, so if you call out to them in some foreign tongue they may have unusual responses! If a bird is a combinator and a combinator is a higher order function (a function that operates on functions), then this implies that we should generally only pass functions to our birds (I'll be using the terms interchangeably). 
Another key point lies hidden in the simplicity of the metaphor. If we make a bird noise and it responds with a noise in turn, assuming we made the bird call properly what the other bird hears would be indistinguishable from the bird we are imitating. If the response is a bird noise as well, then it is the same sort of thing as we supplied, a bird! If we can make a given bird noise, we have the *essence* of the thing, a first class reference. *There is no distinction between a birds name and a birds sound*. To understand what this means we can look at a notion called [referential transparency](http://en.wikipedia.org/wiki/Referential_transparency_%28computer_science%29) which says that any time a name is used it can be swapped out with the value of the thing it names and maintain the same meaning. In the forest, if you can respond with the sound a bird makes you have may as well be the bird yourself. In summary, *birds are those functions whose parameters are functions, who are defined in terms of function application, and whose resulting application yields a function*!

I think this metaphor is marvelous for functional programming since many higher level abstractions don't have suitable names, and remember, as all good wizards know: [to name a thing is to have power over it.](http://en.wikipedia.org/wiki/True_name)

####A digression

This post introduces a number of functional programming techniques in order to provide some context for combinators. Uncle Bob has said that functional programming is [programming without assignments](http://pragprog.com/magazines/2013-01/functional-programming-basics). Whether or not this is the case it does serve to introduce a curious problem. Some concepts like recursion rely on assignment (what Bob calls the quintessential side-effect). How can we achieve truly functional, side-effect free recursion? Interestingly, the answer is within Smullyan's forest.

##Entering the forest
As we enter the lush forest the first bird we see is one which many are too quick to judge. It's called the **idiot bird** or the [identity bird](http://en.wikipedia.org/wiki/Identity_function) and when you make a bird call to it the idiot responds with the very same noise. Amazingly, this bird can make *any* possible sound! Can you? In javascript it would look like this:

~~~~{js}
// Ix = x
function idiot(x) {
  return x;
};
~~~~

This bird seems useless, a function that takes a parameter only to spit it back at us! What an idiot! Some have speculated that the idiot is actually deeply enamoured with other birds and so only mimics them out of appreciation.

As we continue our stroll, the next bird we encounter is the **mockingbird**. The mockingbird is a mystical bird which has the interesting property of duplicating its input (it takes one x in, but somehow has two copies of x in its body). While this is commonplace in programming it is not so common in the world of combinators. Because of this ones that do are in a special class called *duplicative combinators*. If you call some bird x to the mockingbird it will respond as if the bird x had called out to itself (or what is the same, the function x applied to itself). In javascript:

~~~~{js}
// Mx = xx
function mockingbird(x) {
  return x(x);
}
~~~~

What use is this bird?
It's easy to find useless things we can do with it, for instance if you make the noise the idiot bird makes to the mockingbird it will call out the idiot bird back to you. That seems like the behavior of the idiot bird itself, however if you call the mockingbird to the mockingbird it will never stop trying to figure out what it should say about itself! We can demonstrate this by reducing:

~~~~{js}
MI = II = I
MM = MM = MM = MM = ..
~~~~

Even with this, it's hard to conceptualize a clear use case for this peculiar bird. The mockingbird lies at the heart of combinatory logic. *Sometimes called the _U combinator_, the mockingbird is the primary tool for self application*, which can be used to simulate recursion. Without recursion simple languages like Lambda or Combinator Calculus are not expressive enough for universal computation. Lucky they have the mockingbird!

##Talking to the mockingbird
If it suits our fancy we can even engineer our own mechanical bird to calculate a factorial. It's not quite a real bird (a classical combinator) since it does more than simply combine its input, but it's close enough for our purposes. Since we've heard the rumour that the mockingbird enables anonymous recursion, we might try to build something that proves this. Many birdwatchers spoke to this magical bird chiefly for this purpose. Our bird doesn't have to follow all the rules of classical combinators but it satisfies the chief property: being a function which takes in a function and returns a function.

~~~~{js}
var strangeFact = function(fact) {
  return function (n) {
    if (n === 1) return n;
    var strangerFact = mockingbird(fact);    
    return n * strangerFact(n - 1);
  };
};
// var myFact = mockingbird(strangeFact);
// myFact(23);
// mockingbird(strangeFact) is strangeFact(strangeFact)
~~~~

Initially we call the strange factorial out to the mockingbird, or what is the same, strangeFact is applied to itself, which returns the bird from line 2. If we inspect the mechanics of our bird, we can see that `fact` bound to `strangeFact`, since strangeFact returns the factorial calculator, it only needs to ask should it ever require a copy. (We ask for a copy at line 8 initially, and line 4 if needed subsequently) I encourage you to take the time to understand what is happening above; while it may seem trivial it is the core mechanism of anonymous recursion. Consider the following:

~~~~{js}
var factorial = strangeFact();
// factorial is now the inner function of strangeFact; 
factorial(1) // 1;
// this works, because 1 is less than 2
factorial(2); // Error
// this blows up since fact is undefined in strangeFact()
var idiotFact = strangeFact(idiot);
idiotFact(3); // 6
// this works, because 3*2 === 3*2*1
idiotFact(4); // 12
// it thought 'fact' meant the same thing as 'idiot'
// first iteration: (return 4 * 3)
~~~~

If the mockingbird can give us a version of our bird that knows about itself, when we define our mechanical bird in terms of the mockingbird we also gain the ability to create functions with references to themselves. 

This works but is very... strange. In modern javascript, we could write less code with fewer dependencies and wind up with something that is easier to use, simpler to reason about, and more performant to boot!

~~~~{js}
var factorial = function(n) {
  if (n == 1) return n;
  return n * factorial(n - 1);
};
// factorial(23);
~~~~

Observing this, we can now take great comfort in knowing that we no longer need to use anonymous recursion. While the use of the U combinator style recursion may seem outdated in modern programming parlance its impact on computer science cannot be overstated. Combinator and Lambda Calculus are much simpler notations than javascript which owes its higher level abstractions to the work of those who spoke to birds like these long before us.

###Problems with the mockingbird
As a birdwatcher who hopes to fashion birds of our own using the mockingbird to simulate recursion is awkward at best. We have to know about the mockingbird inside of our function and manually handle the self application at each step along the way, what's more our bird must also be returned from the mockingbird. What we'd like is a way to be flexible enough in our bird creation to not have to worry about this technical detail and be free to focus on only the problem itself. Perhaps there is another bird who can help us achieve what we want.

##Bluebirds
The next bird we encounter, the most immediately practical of these strange birds is the **bluebird**. If you call out some bird x to the bluebird, it'll call back to you with an entirely new bird which knows all about the bird x. This means it gives you back a new function with x in the environment's scope. This new bird has the curious property that if you call out some bird y to it, it will return some even newer bird that knows about the birds x and y. And now we have both x and y in our functions environment. If you give this final bird some bird z, the bluebirds work will be done and it will return what results from calling out bird z to bird y, and calling the resulting bird out to the bird x. This is what is referred to as a closure, because each successive function closes over the value of one parameter.
Having trouble picturing it? 

~~~~{js}
function bluebird(x) {
  // Bxyz = (x∘y)z = x(yz) 
  return function(y) {
    return function(z) {
      return x(y(z));
    };
  };
};
~~~~

The above is a special [curried](http://en.wikipedia.org/wiki/Currying) way to say:

~~~~{js}
function bluebird(x, y, z) {
  // Bxyz = (x∘y)z = x(yz) 
  return x(y(z));
}
~~~~

The difference is that the first definition allows you to define a bluebird with only an x or only an x and y, rather than only with x y and z. This technique is called *partial application*. While the first of these functions all take in a single value, because it is their grouping that we are interested in we can say that bluebird simply takes three inputs (xyz). 

The bluebird is also known in many circles as **compose** and can be used to thread some value through arbitrary function sequences. Traditionally in combinatory logic the threaded value is a function itself but as we will see it doesn't have to be.
*The core of the bluebirds functionality is that it defers the application of x in favor of first applying y.*
Here is an example of using the bluebird to construct increasingly complex functions.

~~~~{js}
var compose = bluebird,
    times = function(n) { return function(x) { return x * n; }; },
    times6 = compose(times(2))(times(3)),
    invert = times(-1),
    timesNeg6 = compose(invert)(times6);

timesNeg6(-6); // 36
~~~~

Here we have times being a closure that returns a fn with the value of n closed over. With `times6` being a bluebird, we can reduce the above invocation by following the rule of `Bxyz = (x·y)z = x(yz)` where **x** is `invert`, **y** is `times6` and **z** is `-6`.

~~~~{js}
(invert∘times6)-6 
invert(times6(-6))
invert((times2∘times3)-6)
invert(times2(times3(-6)))
invert(times2(-18))
invert(-36) = 36
~~~~

The bluebird allows for some remarkably beautiful chaining, and we've only begun to scratch the surface with this example. 

##Birds of a feather
Continuing along, the next pair of birds we meet are the strangest yet. They seem to have much more in common with the mockingbird than the bluebird though in actuality they are simply a hybrid of the two. These birds are both dear friends of the mockingbird and in fact are defined in terms of it!
The first of the pair is called the **lark**. When you call out some birds x and y to the lark, it will respond by calling the sound of y out to the mockingbird, then taking the response and calling it out to the bird x, or what is the same, applying y to the mockingbird then applying that resulting bird to x.

~~~~{js}
function lark(x) {
  // Lxy = x(My) = x(yy)
  return function(y) {
    return x(mockingbird(y));
  };
};
~~~~

Given the lark we can show that the lark given identity is the same as the mockingbird, `LI = M` and the lark given the lark is something like two strange mockingbirds: `LLxy = Mx(My)`

~~~~{js}
// Taking I for x:
LIy = I(My) = I(yy) = yy

// Taking L for x:
LLy = L(My)z = My(zz) = (yy)(zz);
~~~~

*The lark is a way to compose some function with self application.*
Given this and our knowledge of bluebirds, we could also define the lark as:

~~~~{js}
function lark(x) {
  // Lxy = BxMy = x(My) = x(yy)
  return bluebird(x)(mockingbird);
};
~~~~

Next is the **meadowlark**. When you call out some x and y to the meadowlark, it will respond by calling out y to the mockingbird of x

~~~~{js}
function meadowlark(x) {
  // Mₑxy = Mxy = xxy
  return function(y) {
    return mockingbird(x)(y);
  };
};
~~~~

Note: This bird was unnecessary in combinator calculus because it can also be written as Mxy. 
So how can we use the meadowlark?

Given the meadowlark we can show that `MₑI = I`:

~~~~{js}
// Taking I for x:
MₑIy = MIy = IIy = Iy = y

// Taking Mₑ for x:
MₑMₑy = MMₑy = MₑMₑy = MMₑy = ...
~~~~

Interestingly *the meadowlark behaves much like the mockingbird* duplicating for all time. In fact, *this bird differs from mockingbird only in that it ensures that there is a y.*.

While interesting, both larks seem to be devoid of any practical use. It's as if they took the good parts about the bluebird (generalized function composition), and tangled them up with the notion of the mockingbird. What we will see however, is that these birds are the primary methods of composing self application. (x(yy) or xxy). Why would we want to compose self application? If self application can be used to simulate recursion, then we can use higher order functions to *compose our functions with the notion of recursion*! Perhaps the there is a bird who can do this for us somewhere deeper in the combinator forest.

##Finding Curry's Sage Bird
There are special birds in the combinator forest called **Sage birds**. Sage birds are particularly useful *for finding the fixed points of other birds*, where a fixed point is the element when called out to some bird will results in the element itself. That is, `f(x) = x`. Everything is a fixed point of identity, but finding the fixed points of other birds is much harder to reason about. So why is it useful to have a bird to help you find these invariant points? Well, having a fixed point means you have found the limit of the function, also known as the convergence. In recursive functions, the convergence is of particular importance since it is often the only way to terminate evaluation (those functions who never terminate are said to have diverged).  Can you see why locating a convergence can be useful if we want to represent recursion abstractly? Consider how `strangeFact` uses the mockingbird to advance computation by a step. Can you see how we can use the lark and meadowlark to abstract these steps?

###The Y Combinator
[Haskell Curry](http://en.wikipedia.org/wiki/Haskell_Curry) saw this clearly and created the most popular of all sage birds, dubbed the [Y combinator](http://en.wikipedia.org/wiki/Fixed-point_combinator#Y_combinator). Remember that phrase curried from earlier? That particular style of partial application, where one element is applied at a time, as well as the [Haskell](http://www.haskell.org/haskellwiki/Haskell) programming language both get their namesake from the very same! 
In the lambda calculus it would look like this: 

~~~~{js}
λf.(λx.f (x x)) (λx.f (x x))
~~~~

If you look carefully you might notice that there are some familiar friends here, in particular the mockingbird `(x)(x)` and the lark `x(yy)` in the inner form resulting in `(x(yy))(x(yy))`. Can you find any other birds here? 

First, here's what it would look if we and translated the lambda terms literally:

~~~~{js}
function sage(f) {
  return (function(x) {
    return f(x(x));
  })(function(x) {
    return f(x(x));    
  });
};
~~~~

This is a bit dizzying, but we can simplify it by recognizing that we are invoking a function with itself. This is the same thing as passing the function to the mockingbird.

~~~~{js}
function sage(f) {
  return mockingbird(function(x) {
    return f(x(x));
  });
};
~~~~

And by realizing that the inner function is applying the mockingbird of x to some f, or what is the same, that the inner function is the lark of f.

~~~~{js}
function sage(f) {
  return mockingbird(lark(f));
};
~~~~

And by realizing the above is simply a means of composing f (threading it through lark and then mockingbird):

~~~~{js}
bluebird(mockingbird)(lark);
~~~~

This is fantastic! We've shown that *the famous Y combinator can be represented as the combination of three little birds*!
The only problem is that the above code doesn't actually work.

While we can show that it is mathematically sound, with `Θ` as the sage bird:

~~~~{js}
Θx = BMLx = M(Lx) = Lx(Lx) = x(Lx(Lx)) = ..
~~~~

The last two reductions can be flipped and viewed as `x(Lx(Lx)) = Lx(Lx)`, or `x(y) = y` where `y = Lx(Lx)` which shows that we have found the fixed point! The problem is that in modern programming environments, we can expand `Lx(Lx)` infinitely. Languages like javascript do.

~~~~{js}
Lx(Lx) = x(Lx(Lx)) = x(x(Lx(Lx))) = x(x(x(Lx(Lx)))) = ...
~~~~

This successful reduction strategy above is referred to as 'normal order' (call by name), which means we substitute the parameters before evaluating them, where the one expanding forever is called 'applicative order' (call by value) which instead reduces its parameters into values before expanding a functions body. In call by name systems we can simply call this thing by the name `Lx(Lx)`, but in call by value languages (like javascript and most popular languages) we get lost when asking for the value, similar to a mockingbird attempting to mock itself. Maybe we can find a different bird that works in call by value systems.

###Introducing the Z combinator
Seeing the shortcomings of the Y combinator, we can see that if we can somehow defer evaluation of the lark we can avoid blowing up the stack, and thus make a sage bird that works with applicative order. So rather than invoking the lark at `sage(x)` we can defer this until we have some z to call it with. This means the z of bluebird should be the actual argument to the function *returned* by the this new combinator, not the function provided to it. This is a subtle note, but an important one. It means we will have to return a bird which returns partially applied bluebird rather than returning a partially applied bluebird ourselves.

~~~~{js}
function sage(x) {
  // x = computation step, y = higher order fn
  // Θx = M(BxMₑ) = M(x∘Mₑ) = (x∘Mₑ)(x∘Mₑ) => (x(Mₑy))(x(Mₑy)) => (x(yy))(x(yy))
  return mockingbird(bluebird(x)(meadowlark));
};
~~~~

The above combinator is known as the **Z Combinator**, though *sometimes it is called the Y combinator since it reduces to Y*. (Remember the meadowlark ensures the presence of some y). While the Z combinator is a bit more cumbersome and harder to reason about, it properly combines the pieces to work with a call by value system by using the meadowlark to manually defer evaluation. I encourage you to write down the reductions yourself in order to see what's going on, it's quite interesting!

Having seen this new bird, let's revisit our strange factorial.

~~~~{js}
function factorial(recur) {
  return function(n) {
    return (n === 1) ? 1 : n * recur(n - 1);
  };
};
~~~~

If we know we are working with a fixed point combinator we can forget the mockingbird from our previous version and focus our attention on the inner function alone (the actual factorial function), all thanks to higher order abstractions. Amazingly, our version of the factorial takes in the idea of what it means to recur! Let's see it in action:

~~~~{js}
var sageFactorial = sage(factorial);
sageFactorial(1)  // 1
sageFactorial(12) // 479001600
~~~~

And without assignment:

~~~~{js}
(function(mockingbird, meadowlark, bluebird) {
  return function(fGenerator) { 
    // Θx = .. => (x(yy))(x(yy))
    return mockingbird(bluebird(fGenerator, meadowlark));
  };
})(function(x) { return (x)(x); },                          
   function(x) { return function(y) { return (x)(x)(y); }}, 
   function(x,                                              
            y) { return function(z) { return x(y(z)); }}
)(function(recur) {
  return function(n) {
    return (n === 1) ? n : n * recur(n - 1);
  };
})(23);
// 2.585201673888498e+22
~~~~

The Z combinator or "the mockingbird of the bluebird of f and the meadowlark" can calculate all the way down to the fixed point of f by *trampolining a functions invocation with its definition.*. Unlike our U combinator, the Y and Z combinators also takes care of self application so we don't have to worry about using the mockingbird to rebind our name inside our function. The above birds are achingly clever, and yet built of out relatively simple parts! 

##Heading home
What a fantastic example of the power of combinators. Given such a massive problem as "how can we support recursion without assignment?" we've seen how combinators can be used not only to simplify the problem itself, but also serve to provide us with a tool for understanding larger concepts by breaking them down into simple ideas. 
I hope I've helped elucidate some small corner of the wonderful world of combinators for you, as others have done for me. I've heard it said that *if classes are the nouns of programming and functions are the verbs then combinators are the adverbs.*
We've demonstrated how we can use these combinators to factor out common patterns from our functions or as building blocks in and of themselves. Even something as opaque as the infamous Y combinator can be reduced in terms of it's simpler components.

It may surprise you to learn that there are an infinite number of sage birds to be found by combining simple combinators, can you find any others?
