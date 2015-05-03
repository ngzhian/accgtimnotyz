CodeStats (aka accgtimnotyz)
============================

6 things you didn't know about your javascript variables!

This was built as part of TechCrunch Discrupt Hackathon (NY) 2015.

What?
-----

Looks at variable names and spits out some interesting statistics about them!

For example:

 - are you a concise or verbose programmer (based on length of your variable names)
 - camel case or underscore?

How?
----

Parsing is handled by the [Closure Compiler](https://github.com/google/closure-compiler/).
This is a custom (slightly modified) build that adds a compiler pass that emits
output that I am interested in.

I use python to call the compiler as a subprocess and capture the stdout.
It then massages the compiler output to get a list of all variable names.

Use [pandas](http://pandas.pydata.org/) to calculate statistics like mean median etc.

Spit it out onto the template and display it!

Source structure
----------------

```
|-- static  # static assests used for the web app
|-- templates  # templates for the web app
|-- analyse.py  # analysis of variable
|-- codestats.py  # flask web app, takes in js snippet or url to js file
|-- compiler.jar  # custom build of closure compiler
|-- parser.py  # calls closure compiler as a subprocess and parses its output
|-- test_analyse.py  # tests for analyse
|-- test_codestats.py  # tests for codestats
|-- test_parser.py  # tests for parser
|-- test_snippet.js  # javascript file used for tests
```

License
-------

MIT
