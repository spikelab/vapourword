(function() {

if( !window.vapourword ) {
    window.vapourword = vapourword = {};
} else {
    vapourword = window.vapourword;
}

vapourword.output_html = output_html = {};

if( !vapourword.defaults.output ) { 
    vapourword.defaults.output = output_html;
}

output_html.defaults = {
    output_target: null,
}

output_html.init = function(cloud) {
    var old_opts = cloud.options;
    cloud.options = vapourword.util.obj_clone(output_html.defaults);
    vapourword.util.obj_merge(cloud.options, old_opts);
    ($(cloud.options.output_target)
        .css({
            width: cloud.options.width+"px",
            height: cloud.options.height+"px",
        })
    );
}

output_html.calc_size = function(cloud, word) {
    word.data = ($('<div></div>')
        .css({
            position: "absolute",
            "font-size": word.font_size + "px",
        })
        .text(word.word)
        .hide()
    );
    $(cloud.options.output_target).append(word.data);
    word.width = word.data.width();
    word.height = word.data.height();
    return word;
}

output_html.render_word = function(cloud, word) {
    if( word.added ) {
        word.data.css({left: word.x+'px', top: word.y+'px'}).show();
    } else {
        word.data.remove();
    }
}

})();
