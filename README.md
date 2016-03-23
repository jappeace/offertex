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
