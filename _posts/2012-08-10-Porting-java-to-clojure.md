---
layout: post.html
title: 'porting java to clojure'
tagline: 'distilling functionality'
---

Hi everyone!

I wanted to share some interesting things I found while porting a hashing function from java over to clojure.  I needed to translate some unique identifiers from one format over to a different, universal, and shared format for some quick reports I was trying to pull; luckily this had already been done and was available as a simple standalone class.  I could have (and arguably should have) just used the class file itself and not written a lick of code, but I like understanding how things worked and I figured porting it into native clojure would be a good chance to both understand it as well as learn a bit about clojure in the process!

So heres the original java class:

~~~~{java}
import java.math.BigInteger;
public class HashUtil {

    static final BigInteger u64max = new BigInteger("ffffffffffffffff", 16).add(BigInteger.ONE);
    static final BigInteger prime = new BigInteger("100000001b3", 16);
    static final BigInteger max  = new BigInteger("1000000000000");

    public static long hash(String key) {
        BigInteger hash = new BigInteger("01234567890abcde", 16);
        char[] c = key.toCharArray();
        for (int i = 0; i < c.length; i++) {
            hash = hash.multiply(prime).mod(u64max);
            hash = hash.xor(BigInteger.valueOf(c[i]));
        }
        return hash.mod(max).longValue();
    }

    public static void main(String[] args) {
        for (String arg : args) {
            System.out.println("original: ", arg, " :|: checksum: ", hash(arg));
        }
    }
}
~~~~

It's pretty simple, first it creates some number boundaries, one the upper bounds of an unsigned 64 int represented as hex and secondly the upper limit of the universal identifiers.  It also specifies a prime number in order to get a broader distribution of keys per character. I know this isn't sha1, but it's what we had currently in use, and so it was what I was going to replicate.  My interest was porting it, but first I had to grok it.

The main work happens in the 'hash' method, which returns a long given a string.  It generates a hash seed as an initial value and then proceeds to multiply this value by the prime declared earlier; it then finds the modulus between that new hash value and the u64-max-int (ensuring it is within bounds), followed by a bitwise exclusive or between the accumulated value and the value of the current character; repeating this process for each character in the given string.  Finally it takes this newly built checksum and ensures that it's within the bounds of the max universal ids, returning as a long. Whew!

This may or may not be the best way to create a hash within the limits of the universal id boundaries, but it seems to have worked so far. The syntax and notation above should hopefully be familiar to anyone who has used a c-style language.

So let's take a look at the clojure (and lispy) equivalent.

~~~~{clj}
(def u64-max (-> (BigInteger. "ffffffffffffffff" 16) (.add ,, BigInteger/ONE)))
(def ups-max (BigInteger. "1000000000000"))
(def prime (BigInteger. "100000001b3" 16))
(def seed (BigInteger. "0123456789abcde" 16))

;; private fn to return the control code for a given hashable entity
(defn- code-for [x] (BigInteger/valueOf (long (hash x))))

;; hashing function and reducer; takes in a current checksum value
;; and some hashable entity by which to alter it via bitwise-xor
(defn- ups-hash
  [checksum hashable]
  (-> checksum
      (.multiply ,, prime)
      (.mod ,, u64-max)
      (.xor ,, (code-for hashable))))

(defn to-universal-id
  [coll]
  (let [checksum (reduce ups-hash seed coll)]
    (-> checksum (.mod ,, ups-max) (.longValue ,,))))
~~~~

This probably looks very strange at first, but I think it's a uniquely elegant way to represent transformations over data (in our particular case, the transformation is the one that turns a string id into a universal integer id).  If you are new to clojure `(def x 1)` is the same as `x = 1` and `(defn my-fn [args] (use args))` can be read as `function my-fn (args) {use(args);`  The first four lines equate to the static final fields in the java class, with the exception of the seed being extracted out of the hashing method (since it is unchanging).  

The other caveat is the `->` operator.  This function is actually a macro, which says *take the value of the first parameter provided to me, and slip it in as the first parameter to the following statement, then take the result of that statement and slide it in as the first parameter to the following statement...* etc.

Above I represent where the prior value would be inserted as two commas (which the clojure reader interperates as whitespace).  An example for this would be a transformation where `"hello   ".toUpperCase().strip();` is translated as `(-> "hello   " (.toUpperCase) (.strip))`.  This is called the `thrush operator` or the `thread-first macro` and it is unique to lisp.

Following along, on line 7 I pull out what was previously an inline parameter in our java class (a simple call to `BigInteger.valueOf(charArray[i])`), generalizing it into a function which can generate a hashcode for any clojure object. 

I think the next section was a particular revelation for me, wherein I realized that __every for-each body is intended for one of three things__.

- to derive some single value from a series -- `reduce`
- to produce an entirely new collection of values -- `map`, `filter`
- to perform a series of sequential side effects. -- `doseq`, `forEach`

It's only recently that I'm realizing I don't need that last one to achieve the former. Reading over the body of the for-each loop, it was obvious that a new value was gradually being built up by iterating over the character array. I know that the reduce function is intended for just this purpose, so I sought out to see how I might write a reducing function that implemented the same functionality as the for-each body.

It was surpisingly simple once I saw the pattern, and the thrushing operator made the transformation so incredibly readable!
*Take the provided checksum value, multiply it by our prime, find the modulus of the u64 max, and perform the xor against the hash of the hashable.*

Wow! This is exactly how we would describe this in english! The instance method invocation style offered by clojure allows for some really astonishing composition and generalization. I also believe that __naming things forces you to think about their proper abstraction__.  Finally, we have our function to actually convert some collection (like a collection of characters, but really *any collection*) into a checksum.  We get the checksum value by using our reducing function, providing it our seed as an init value and finally we ensure this number is within the universal id boundaries via mod and return it as a long.

I'm continually impressed by not only how enjoyable clojure is to work with, but how powerful and general the abstractions of functional programming are. So, do you prefer one of the above styles to the other? Why? I think it's pretty obvious which camp I am in. :D
