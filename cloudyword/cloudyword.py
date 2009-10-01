""" word cloud generator by dunkfordyce@gmail.com """

import sys
from math import sqrt
from random import randint, seed, shuffle
from string import punctuation
from operator import itemgetter
import time

import cairo

try:
    import psyco
    psyco.full(1)
except ImportError:
    print >>sys.stderr, "if you installed psyco this would be ~4x faster..."


class Edge(object):
    __slots__ = ['p1', 'p2', 'n', 'l', 'weight', 'fail_count']

    def __init__(self, p1, p2, n, l=None, weight=None):
        self.p1, self.p2, self.n, self.l, self.weight = p1, p2, n, l, weight
        self.fail_count = 0 
        if self.l is None:
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            self.l = sqrt(dx*dx + dy*dy)


class Word(object):
    def __init__(self, word, importance, font_size, width, height, text_offset_x, text_offset_y):
        self.word = word
        self.importance = importance
        self.font_size = font_size
        self.width = width 
        self.height = height 
        self.area = width*height
        self.x = None
        self.y = None
        self.rotate = 0
        self.text_offset_x = text_offset_x
        self.text_offset_y = text_offset_y

    def __str__(self):
        return "(R %sx%s %sx%s)" % (self.x, self.y, self.width, self.height)

    def collides_with(self, other):
        # this function is the bottle neck - to make this script faster
        # this needs to be called less!
        # pick a space division algorithm... :)
        return not (
                self.x+self.width <= other.x or
                self.x >= other.x+other.width or 
                self.y+self.height <= other.y or 
                self.y >= other.y+other.height
        )

    def edges(self):
        p1, p2, p3, p4 = (
            (self.x, self.y), 
            (self.x+self.width, self.y),
            (self.x+self.width, self.y+self.height),
            (self.x, self.y+self.height),
        )
        edges = (
            (p1, p2),
            (p2, p3),
            (p3, p4),
            (p4, p1),
        )

        ret = []
        for p1, p2 in edges:
            # could forget about normalizing the normal here and just 
            # detect n.<x|y> > 0 in the main loop 
            dx = (p2[0] - p1[0])
            dy = (p2[1] - p1[1])
            l = sqrt(dx*dx + dy*dy)
            norm = dy/l, -dx/l
            ret.append(Edge(p1, p2, norm, l))
        return ret


class Cloud(object):
    def __init__(self, 
            # list of Items to process
            items,
            # width and height of canvas
            width, height, 
            # clockwise, counterclockwise, shortest, longest, random 
            edge_selection="clockwise",
            # any combination of top, left, right, bottom - missing item will presume center
            initial_placement="center",
            # min font size to use
            min_font_size=10,
            # max font size to use
            max_font_size=40,
            # padding around each item 
            padding=0,
            # start, end, or replace
            insert_new_edges='end',
            # insert new edges cause by overlap 
            add_new_edges=False,
            # maximum times we try to use an edge before its removed from the list 
            # higher numbers will increase quality
            max_edge_fails=1000,
            # maximum times we try to place words and fail before we quit 
            # higher numbers will increas quality
            max_placement_fails=10,
        ):
        self.placed_words = []
        self.edges = []
        self.width = width 
        self.height = height 
        self.padding = padding

        self.edge_selection = edge_selection
        self.initial_placement = initial_placement
        self.insert_new_edges = insert_new_edges
        self.add_new_edges = add_new_edges
        self.max_edge_fails = max_edge_fails
        self.max_placement_fails = max_placement_fails
        self.placement_fails = 0 

        self.min_font_size = min_font_size
        self.max_font_size = max_font_size
        
        self.add_items(items)

    def add_items(self, items):
        items.sort(key=lambda i: i[1], reverse=True)

        max_importance = items[0][1]
        min_importance = items[-1][1]
        diff_importance = max_importance - min_importance
        diff_font_size = self.max_font_size - self.min_font_size
        font_size_ratio = diff_font_size / float(diff_importance)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        ctx = cairo.Context(surface)

        for word, importance in items:
            font_size = self.min_font_size + (font_size_ratio * importance)
            ctx.set_font_size(font_size)
            x_bearing, y_bearing, txt_width, txt_height, x_advance, y_advance = \
                    ctx.text_extents(word)
            if txt_width == 0 or txt_height == 0:
                raise ValueError("bad item '%s'" % word)
            item = Word(
                    word, 
                    importance, 
                    font_size,
                    txt_width+(self.padding*2), txt_height+(self.padding*2),
                    x_bearing, y_bearing,
            )
            self.add(item)

    def add(self, word):
        """ add the Word object `word` to the cloud
        probably only usefull when called internally
        """
        if not self.placed_words:
            word.x = (self.width / 2) - (word.width / 2)
            word.y = (self.height / 2) - (word.height / 2)
            initial_placement = set(
                    p.strip().lower() for p in self.initial_placement.split(' ')
            )
            if len(initial_placement) > 2:
                raise ValueError("initial placement should have at most two words")
            if 'left' in initial_placement:
                word.x = 0
            elif 'right' in initial_placement:
                word.x = self.width - word.width
            if 'top' in initial_placement:
                word.y = 0
            elif 'bottom' in initial_placement:
                word.y = self.height - word.height
            self.placed_words.append(word)
            self.edges = word.edges()
            return True

        sel_edge = 0

        # just use the natural order of edges 
        if self.edge_selection == "clockwise":
            edge_selection = self.edges
        # use the reverse natural order of edges
        elif self.edge_selection == "counterclockwise":
            edge_selection = self.edges[::-1]
        # use a random edge
        elif self.edge_selection == "random":
            edge_selection = self.edges[:]
            shuffle(edge_selection)
        # try the shortest edges first 
        elif self.edge_selection == "shortest":
            edge_selection = self.edges[:]
            edge_selection.sort(key=lambda e: e.l)
        # try the longest edges first 
        elif self.edge_selection == "longest":
            edge_selection = self.edges[:]
            edge_selection.sort(key=lambda e: e.l, reverse=True)
        # use edges closest to the center of the canvas 
        elif self.edge_selection == 'center_weighted':
            edge_selection = self.edges[:]
            hwidth = self.width / 2
            hheight = self.height / 2
            for edge in edge_selection:
                d1x = edge.p1[0] - hwidth
                d1y = edge.p1[1] - hheight
                # dont need to sqrt here as we're only comparing them ...
                d1s = (d1x*d1x + d1y*d1y)
                d2x = edge.p2[0] - hwidth
                d2y = edge.p2[1] - hheight
                d2s = (d2x*d2x + d2y*d2y)
                ds = min(d1s, d2s)
                edge.weight = ds
            edge_selection.sort(key=lambda x: x.weight)
                
        else:
            raise ValueError("invalid edge_selection value %s" % self.edge_selection)

        to_remove = []

        while True:
            try:
                edge = edge_selection[sel_edge]
            except IndexError:
                #print "cant place", word
                return False
            sel_edge += 1

            rotate = False

            if edge.n[1] == -1.0:
                offset = (0, -word.height)
                remove = 2
            elif edge.n[1] == 1.0:
                offset = (-word.width, 0)
                remove = 0
            elif edge.n[0] == -1.0:
                offset = (-word.width, -word.height)
                remove = 1
            elif edge.n[0] == 1.0:
                offset = (0, 0)
                remove = 3

            word.x = edge.p1[0] + offset[0]
            word.y = edge.p1[1] + offset[1]

            #print "checking", rect

            # check out of bounds
            if (word.x < 0 or word.y < 0 
                or word.x+word.width > self.width or word.y+word.height > self.height):
                continue

            # check collisions with other shapes 
            collides = False
            for other in self.placed_words:
                if word.collides_with(other):
                    #print "collide", other
                    collides = True
                    break
            if not collides:
                break

            edge.fail_count += 1
            if edge.fail_count > self.max_edge_fails:
                to_remove.append(edge)


        edge_index = self.edges.index(edge)
        split_edge = self.edges[edge_index]
        del self.edges[edge_index]
        self.placed_words.append(word)
        
        rect_edges = word.edges()
        used_word_edge = rect_edges[remove]
        del rect_edges[remove]

        if to_remove:
            for edge in to_remove:
                self.edges.remove(edge)

        # add in new extra edges 
        # this should add in the extra edges caused by overlaps 
        if self.add_new_edges:
            new_edge = Edge(
                split_edge.p1,
                used_word_edge.p2,
                split_edge.n,
            )
            if new_edge.l:
                self.edges.append(new_edge)
            new_edge = Edge(
                used_word_edge.p1,
                split_edge.p2,
                split_edge.n,
            )
            if new_edge.l:
                self.edges.append(new_edge)

        if self.insert_new_edges == 'replace':
            # insert the new edges where we removed the matching one 
            self.edges = self.edges[:edge_index] + rect_edges + self.edges[edge_index:]
        elif self.insert_new_edges == 'end':
            # append new edges
            self.edges.extend(rect_edges)
        elif self.insert_new_edges == 'start':
            self.edges = rect_edges + self.edges
        else:
            raise ValueError("invalid insert_new_edges values '%s'" % self.insert_new_edges)

        return True

    def get_bounding_box(self):
        """ gets the bounding box of the whole image """
        min_x = min(r.x for r in self.placed_words)
        min_y = min(r.y for r in self.placed_words)
        max_x = max(r.x + r.width for r in self.placed_words)
        max_y = max(r.y + r.height for r in self.placed_words)

        return min_x, min_y, max_x, max_y

    def center(self, edges=False):
        """ center the image to the canvas """
        min_x, min_y, max_x, max_y = self.get_bounding_box()
        h_width = (max_x - min_x) / 2
        h_height = (max_y - min_y) / 2
    
        for word in self.placed_words:
            word.x -= min_x + h_width
            word.y -= min_y + h_height 

        if edges:
            for edge in self.edges:
                edge.p1 = edge.p1[0] - (min_x + h_width), edge.p1[1] - (min_y + h_height)
                edge.p2 = edge.p2[0] - (min_x + h_width), edge.p2[1] - (min_y + h_height)

    def draw(self, filename="out.png", debug=False):
        """ save the cloud to `filename`. if `debug` is True draw 
        extra debug information 
        """
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        ctx = cairo.Context(surface)
        ctx.set_source_rgb(0.0, 0.0, 0.0)
        ctx.paint()

        #ctx.translate(width/2, height/2)

        for word in self.placed_words:
            if debug:
                ctx.rectangle(word.x, word.y, word.width, word.height)
                ctx.set_source_rgb(1.0, 0.0, 0.0)
                ctx.fill_preserve()
                ctx.set_source_rgb(1.0, 1.0, 0.0)
                ctx.stroke()
            ctx.set_source_rgb(1.0, 1.0, 1.0)
            ctx.set_font_size(word.font_size)
            ctx.move_to(
                    word.x-word.text_offset_x+self.padding, 
                    word.y-word.text_offset_y+self.padding,
            )
            ctx.show_text(word.word)

        if debug:
            ctx.set_source_rgb(0.0, 0.0, 1.0)
            for idx, edge in enumerate(self.edges):
                ctx.move_to(*edge.p1)
                ctx.line_to(*edge.p2)
                ctx.stroke()

        surface.write_to_png(filename)


class SVGCloud(Cloud):
    def add_items(self, items):
        items.sort(key=lambda i: i[1], reverse=True)

        max_importance = items[0][1]
        min_importance = items[-1][1]
        diff_importance = max_importance - min_importance
        diff_font_size = self.max_font_size - self.min_font_size
        font_size_ratio = diff_font_size / float(diff_importance)

        # some numbers got from seeing how big one char is at 1px high
        font_scaler_x = 0.625 
        font_scaler_y = 1.25

        for word, importance in items:
            font_size = self.min_font_size + (font_size_ratio * importance)
            txt_width = font_size * len(word)
            txt_height = font_size 

            txt_width *= font_scaler_x
            #txt_height *= font_scaler_y            

            x_bearing, y_bearing = 0, 0
            if txt_width == 0 or txt_height == 0:
                raise ValueError("bad item '%s'" % word)
            item = Word(
                    word, 
                    importance, 
                    font_size,
                    txt_width+(self.padding*2), txt_height+(self.padding*2),
                    x_bearing, y_bearing,
            )
            added = self.add(item)
            if not added:
                self.placement_fails += 1
                if self.placement_fails > self.max_placement_fails:
                    break

    def draw(self, filename="out.svg", debug=False, as_string=False):
        out = [       
            '<?xml version="1.0" standalone="no"?>',
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"',
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
            '<svg width="%spx" height="%spx" version="1.1"' % (self.width, self.height),
            'xmlns="http://www.w3.org/2000/svg">',
        ]

        for word in self.placed_words:
            out.append('''
                <text 
                    x="%s" y="%s" 
                    font-family="Fixed, monospace" 
                    font-size="%spx"
                    font-weight="bold"
                    style="border: 1px solid blue;"
                >''' % (word.x+self.padding, word.y+word.height-self.padding, word.font_size))
            out.append(word.word.replace('&', '&amp;'))
            out.append('</text>')
            if debug:
                out.append(' <rect x="%s" y="%s" width="%s" height="%s" fill="none" stroke="blue" stroke-width="2" />' % (word.x, word.y, word.width, word.height))

        
        out.append('</svg>')
        if as_string:
            return "\n".join(out)
        open(filename, 'w').write("\n".join(out))
        


common_words = set("a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your".split(','))

def text_to_items(text, limit=None):
    """ returns a list of (word, count) for `text` with common words removed"""

    words = {}

    words_gen = (word.strip(punctuation).lower().strip() for word in text.split())

    for word in words_gen:
        if not word or word in common_words: continue
        words[word] = words.get(word, 0) + 1

    top_words = sorted(words.iteritems(), key=itemgetter(1), reverse=True)
    if limit:
        top_words = top_words[:limit]
    return top_words


def run():
    if False:
        items = [
            ('kuya', 100),
            ('rules', 50),
            ('python', 40),
            #('cairo', 10),
        ]
    else:
        text = sys.stdin.read()
        items = text_to_items(text, 200)
        #items = [(word.upper(), imp) for word, imp in items]


    # a surely too complicated way to make it "easy" to 
    # run this function profiled or not 

    clouds = []

    def gen_cloud():
        t = time.time()
        cloud = Cloud(items, 
            500, 500, 
            max_font_size=50, 
            initial_placement='center',
            edge_selection='center_weighted',
            padding=2,
        )

        print "time to generate cloud", time.time()-t, "with", len(items), "items"
        clouds.append(cloud)

    if '--profile' in sys.argv:
        import cProfile
        cProfile.runctx("gen_cloud()", locals(), globals())
    else:
        gen_cloud()

    t = time.time()
    clouds[0].draw(debug='--debug' in sys.argv)
    print "time to generate image", time.time()-t, "with", len(clouds[0].placed_words), "words"



if __name__ == '__main__':
    run()

