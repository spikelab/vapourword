(function() {

if( !window.vapourword ) {
    window.vapourword = vapourword = {};
} else {
    vapourword = window.vapourword;
}

vapourword.util = {};
vapourword.util.obj_clone = function(obj) {
    var i, newObj = {};
    for (i in obj) {
        newObj[i] = obj[i];
    } 
    return newObj;
};
vapourword.util.obj_merge = function(obja, objb) {
    var i;
    for(i in objb) {
        obja[i] = objb[i];
    }   
};

vapourword.Edge = function (p1, p2, n, l, weight) {
    this.p1 = p1;
    this.p2 = p2;
    this.n = n;
    this.l = l;
    this.weight = weight;
    this.fail_count = 0;
}


vapourword.Word = function (word, importance, font_size) {
    this.word = word;
    this.importance = importance;
    this.font_size = font_size;
    this.width = null;
    this.height = null;
    this.data = null;
    this.x = null;
    this.y = null;

    this.collides_with = function(other) {
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
            var edge = new vapourword.Edge(p1, p2, norm, l);
            ret.push(edge);
        };    

        return ret;
    };
}


vapourword.defaults = {
    max_font_size: 100,
    min_font_size: 10,
    add_chunk_size: 10,
    add_chunk_time: 200,
    output: null,
    max_fails: 10,
};


vapourword.Cloud = function(items, width, height, options) {
    this.add = function(word) {
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
        var to_remove = [];

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

            edge.fail_count ++;
            if( edge.fail_count > 5 ) {
                to_remove.push(edge.original_index);
            }
            
        }

        if( to_remove.length ) {
            for( var i=to_remove.length-1; i>0; i-- ) {
                this.edges.splice(to_remove[i], 1);
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
    this.options = vapourword.util.obj_clone(vapourword.defaults);
    vapourword.util.obj_merge(this.options, options);

    this.options.output.init(this);

    this.fails = 0;
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
    var font_size_ratio = diff_font_size / diff_importance;

    var start_index = 0;

    function add_chunk(cloud) {
        var i = start_index;
        var stop = false;
        while( i < start_index +cloud.options.add_chunk_size && i < items.length ) {
            var word = items[i][0];
            var importance = items[i][1];

            var font_size = cloud.options.min_font_size + (font_size_ratio * (importance-min_importance));
            
            var item = new vapourword.Word(
                word, 
                importance, 
                font_size
            )

            cloud.options.output.calc_size(cloud, item);
            if( !(item.added = cloud.add(item)) ) {
                cloud.fails ++;   
                if( cloud.fails > cloud.options.max_fails ) {
                    stop = true;
                }
            }
            cloud.options.output.render_word(cloud, item);
            i++;
        }
        start_index += cloud.options.add_chunk_size;
        if( !stop && (start_index < items.length) ) {
            window.setTimeout(
                function(){ add_chunk(cloud); }, 
                cloud.options.add_chunk_time
            );
        } else {
            //console.log('done');
            if( cloud.options.on_complete ) {
                cloud.options.on_complete(cloud);
            }
        }
    }

    add_chunk(this);
}



})();
