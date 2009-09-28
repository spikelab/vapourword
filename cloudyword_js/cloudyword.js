function Edge(p1, p2, n, l, weight) {
    this.p1 = p1;
    this.p2 = p2;
    this.n = n;
    this.l = l;
    this.weight = weight;
}


function Word(word, importance, font_size, width, height, el) {
    this.word = word;
    this.importance = importance;
    this.font_size = font_size;
    this.width = width;
    this.height = height;
    this.el = el;
    
    this.x = null;
    this.y = null;

    this.area = width * height;

    this.collides_with = function(other) {
        if( false ) {
        console.log(this.x, this.y, this.width, this.height, other.x, other.y, other.width, other.height);

        var l = $('<div style="position:absolute; border: 1px solid grey;"></div>');
        l.css({left: this.x, top: this.y, width: this.width, height: this.height});
        $('#cloud').append(l);
        }

        return !((this.y >= other.y+other.height) || (this.y+this.height <= other.y) ||
                 (this.x >= other.x+other.width) || (this.x+this.width <= other.x));
    };

    this.edges = function() {
        var p1 = [this.x, this.y];
        var p2 = [this.x+this.width, this.y];
        var p3 = [this.x+this.width, this.y+this.height];
        var p4 = [this.x, this.y+this.height];

        var edges = [
            [p1, p2],
            [p2, p3],
            [p3, p4],
            [p4, p1]
        ];

        var ret = [];
    
        for( var i=0; i!= edges.length; i++ ) {
            var p1 = edges[i][0];
            var p2 = edges[i][1];

            var dx = p2[0] - p1[0];
            var dy = p2[1] - p1[1];
            var l = Math.sqrt(dx*dx + dy*dy);
            var norm = [dy/l, -dx/l];
            var edge = new Edge(p1, p2, norm, l);
            //edge.word = this;
            ret.push(edge);
        };    

        return ret;
    };
}


function Cloud(items, width, height, options) {
    this.add = function(word) {
        //console.log('add', word);

        if( this.placed_words.length == 0 ) {
            word.x = (this.width / 2) - (word.width / 2);
            word.y = (this.height / 2) - (word.height / 2);

            this.placed_words.push(word);
            this.edges = this.edges.concat(word.edges());
            return true;
        }

        var edge_selection = this.edges.slice(0);

        var hwidth = this.width / 2;
        var hheight = this.height / 2;
        var cx, cy, dx, dy, edge;
        for( var i=0; i!= edge_selection.length; i++ ) {
            edge = edge_selection[i];
            edge.original_index = i;
            ds=null;
            cx = (edge.p1[0] + edge.p2[0]) / 2;
            cy = (edge.p1[1] + edge.p2[1]) / 2;
            dx = cx - hwidth;
            dy = cy - hheight;
            edge.weight = (dx*dx + dy*dy);
        }

        edge_selection = edge_selection.sort(function(a, b) {
            return a.weight - b.weight;
        });

        var sel_edge = 0;
        var edge = null;

        while(true) {
            if( sel_edge >= edge_selection.length ) {
                console.warn('cant place', word);
                return false;
            }

            edge = edge_selection[sel_edge];
            //console.log('trying edge', edge);
            sel_edge += 1;

            var offset, remove;

            if( edge.n[1] == -1.0 ) {
                offset = [0, -word.height];
                remove = 2;
            } else if( edge.n[1] == 1.0 ) {
                offset = [-word.width, 0];
                remove = 0;
            } else if( edge.n[0] == -1.0 ) {
                offset = [-word.width, -word.height];
                remove = 1;
            } else if( edge.n[0] == 1.0 ) {
                offset = [0, 0];
                remove = 3;
            } else {
                console.warn('didnt match normal', edge, edge.n);
            }

            word.x = edge.p1[0] + offset[0];
            word.y = edge.p1[1] + offset[1];

            if (word.x < 0 || word.y < 0 || word.x+word.width > this.width || word.y+word.height > this.height) {
                //console.log('collide border');
                continue;
            }
            
            var collides = false;
            for( var j=0; j!= this.placed_words.length; j++ ) {
                if( word.collides_with(this.placed_words[j]) ) {
                    collides = true;
                    //console.log('collide', this.placed_words[j]);
                    break;
                }
            }

            if( !collides ) {
                break;
            }
        }

        //console.log('chose', edge);

        this.edges.splice(edge.original_index, 1);
        this.placed_words.push(word);

        //word.sph_x = word.x + word.width / 2;
        //word.sph_y = word.y + word.height / 2;
        //word.sph_r = word.width > word.height ? word.width / 2 : word.height / 2;

        var rect_edges = word.edges();
        rect_edges.splice(remove, 1);

        this.edges = this.edges.concat(rect_edges);
        return true;
    }

    this.width = width;
    this.height = height;
    this.options = options;

    $('#cloud').css({width: width, height: height});

    this.placed_words = [];
    this.edges = [];
    
    items = items.sort(function(a, b) {
        return b[1] - a[1];
    });

    //items = items.splice(0, 10);

    var max_importance = items[0][1];
    var min_importance = items[items.length-1][1];
    var diff_importance = max_importance - min_importance;
    var diff_font_size = this.options.max_font_size - this.options.min_font_size;
    //var font_size_ratio = diff_font_size / diff_importance;
    var font_size_ratio = diff_font_size / diff_importance;


    for( var i=0; i!=items.length; i++ ) {
        var word = items[i][0];
        var importance = items[i][1];

        var font_size = this.options.min_font_size + (font_size_ratio * (importance-min_importance));
        var el = $('<div style="position: absolute; font-size:'+font_size+'px; padding: 4px;">'+word.toUpperCase()+'</div>');
        $('#cloud').append(el);
        
        var item = new Word(
            word, 
            importance, 
            font_size,
            el.width(),
            el.height(),
            el
        )

        if( this.add(item) ) {
            item.el.css({left: item.x+'px', top: item.y+'px'});
        } else {
            item.el.remove();
        }
    }

    if( false ) {
    for( var i=0; i!= this.edges.length; i++ ) {
        var l = $('<div style="position: absolute; border: 1px solid blue"></div>');

        var left = this.edges[i].p1[0];
        var top = this.edges[i].p1[1];
        var width = (this.edges[i].p2[0] - this.edges[i].p1[0]);
        var height = (this.edges[i].p2[1] - this.edges[i].p1[1]);

        if( width < 0 ) {
            width = - width;
            left = this.edges[i].p2[0];
        }

        if( height < 0 ) {
            height = - height;
            top = this.edges[i].p2[1];
        }

        l.css({'z-index': 100, left: left+'px', top: top+'px', width: width+'px', height: height+'px'});
        $('#cloud').append(l);
    }

    var l = $('<div style="position:absolute; border: 1px solid green"></div>');
    l.css({'z-index': 200, left: this.width/2+'px', top: this.height/2, width: 1, height: 1});
    }
    $('#cloud').append(l);
}



