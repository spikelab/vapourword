Overview
========
Tag clouds (or word clouds) are generally associated with web 2.0 and
made popular by blogs, but a word cloud is a powerful way to represent
any generic list of items to which is possible to associate a
weight. Tag clouds are generally very simple cases where the weight is
represented by the frequency of a word, but far more complicated
functions can be applied to represent relationships and importance of
different words/items in a cloud.

[wordle][1] is both an example of how word clouds can be used to
get a different perspective on several subjects and a great visual
improvement over the classic tag cloud. Unfortunately, altho you can
create your own cloud through the website, the project is not open
source with obvious implication.

What is vapourword
==================
Vapourword aims at being a completely FLOSS replacement for wordle and
more. The project is structured around two modules:
* vw-wordlist - core generating the list of weighted words
* vw-draw - graphical engine to render the list of weighted words

Vapourword design
=================
vw-wordlist
-----------
This is a python application in charge of generating a list of
weighted words. It is designed with a modular approach and a plugin
interface is provided so that user can create their on functions to
create the list and calculate weights depending on the meaning of the
input.
For language processing vw-worldlist is relying on the [nltk][2]
library and the default plugin will support basic lists word:weight
comparable to wordle.net.
Multiple languages and different weighting criteria will be added

vw-draw
-------
Currently an implementation in C++ is scheduled, but it might
eventually move to python with [pyglet][3] and maybe bits done with
[ctype][4]. Ideally a library will be created supporting algorithms for 2D
bin packing since there doesn't seem to be an existing one freely
available.

Roadmap
=======
vw-worldlist
------------
1. Implement a skeleton with support for python plugins to calculate weights and helper functions to deal with input/output
2. Write a plugin to generate list of weighted words based on word frequency
3. Add spell checking support (English only)
4. Add stemming support

vw-draw
-------
1. More to be added here

License
=======
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Authors
=======
Spike & Gabriel ;)

[1]: http://www.wordle.net/ "Wordle.net"
[2]: http://www.nltk.org/ "Natural Language Toolkit"
[3]: http://www.pyglet.org/ "a cross-platform windowing and multimedia library for Python"
[4]: http://docs.python.org/library/ctypes.html "A foreign function library for Python"
