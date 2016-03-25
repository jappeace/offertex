# Offertex
This is a python program that parses the offer.tex file.
When it encounters a variable marked by a PHP like dollar sign and in
all caps, because reasons. It'll ask the user to fill in this variable.

In the variables folder several constraints can be added to the variables.

Once a variable is filled in it will be remembered trough out the entire offer
tex document.

once every variable is filled in a copy of the in memory representation is written
to the automatically generated out directory.
In there the program will attempt to generate a pdf file from the newly created
latex file.

This program is useful for situation in which you want to be able to create lots
of almost similar documents. Currently the implementation part is in dutch
and has some hard dependencies but this should be relatively easily modify able.

## Future work

* Move out the hard dependencies to variable folders (KINDEREN in the options menu)
* Move the special variables (such as startplanning and activiteitdetails) into \*.py
files with the same name and let them be called as functions (in which probably
the symboltable is passed)
* Move all hardset configuration stuff in activity manager into its own folder and
let the menu be generated by a file structure.
* Some crazy ideas I had was add options for using standard output as output instead
of a file and also be able to load existing symboltables to speed up
certain kind of configs.
* Add a template system where multiple offer.tex files can be managed
* The configurable boolean in activity is bad, probably should make a subtype
 of that.

I'll probably keep developing this application for as long there is demand for it
(A local business owner asked me to do this, and since software isn't his
focus I decided to just opensource it, maybe somebody can get some use of it besides him)

# License stuff
Note that the offer.tex file itself isn't licensed under GPL, its just a
reference input file. Having to share changes to it would be rather annoying
because this is different for everyone else.

The variable folder is configuration to, so also not licensed under GPL.

This is also the reason why the hard dependencies should be moved out sooner
rather than later, because making changes to them would require  sharing, but they're
basically configuration. I'm not gonna do it now though because I have no
more time left.

