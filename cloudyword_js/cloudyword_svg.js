(function() {

if( !window.vapourword ) {
    window.vapourword = vapourword = {};
} else {
    vapourword = window.vapourword;
}

vapourword.output_svg = output_svg = {};

if( !vapourword.defaults.output ) { 
    vapourword.defaults.output = output_svg;
}

output_svg.defaults = {
    output_target: null,
}

var svgNS = 'http://www.w3.org/2000/svg';

var makeNode = function(doc, parent, name, settings) {
    var node = doc.createElementNS(svgNS, name);
    for (var name in settings) {
        var value = settings[name];
        if (value != null && value != null && 
                (typeof value != 'string' || value != '')) {
            node.setAttribute(name, value);
        }
    }
    parent.appendChild(node);
    return node;
}


output_svg.init = function(cloud) {
    var old_opts = cloud.options;
    cloud.options = vapourword.util.obj_clone(output_svg.defaults);
    vapourword.util.obj_merge(cloud.options, old_opts);
    ($(cloud.options.output_target)
        .css({
            width: cloud.options.width+"px",
            height: cloud.options.height+"px",
        })
    );
}


output_svg.calc_size = function(cloud, word) {
    word.data = makeNode(
        cloud.options.output_target, 
        cloud.options.output_target.childNodes[0], 
        'text', 
        {
            "font-size": word.font_size + "px",
        }
    );
    word.data.appendChild(word.data.ownerDocument.createTextNode(word.word));
    
    var r = word.data.getBoundingClientRect();
    word.width = r.width;
    word.height = r.height;
    word.offset_x = r.left;
    word.offset_y = r.top;
}


output_svg.render_word = function(cloud, word) {
    if( word.added ) {
        $(word.data).attr({x: word.x-word.offset_x, y: word.y-word.offset_y}).show();
    } else {
        $(word.data).remove();
    }
}

})();
