(function($) {

$.fn.vapourword = function() {
    var all_text = '';

    this.each(function() {
        all_text += $(this).text();
    });

    var words = all_text.split(/[^a-zA-Z0-9]/);

    var counts = {};
    for( var i=0; i!= words.length; i++ ) {
        if( words[i] ) {
            counts[words[i]] = (counts[words[i]] || 0) + 1;
        }
    }

    var ret = [];
    for( var w in counts ) {
        ret.push([w, counts[w]]);
    }

    return ret;
};

$.fn.vapourcloud = function(settings) {
    if( !settings ) settings = {};

    this.each(function() {
        var items = settings.items || $(settings.source || this).vapourword();
        $(this).css({width: 500, height: 500}).html('');
        var cloud = new vapourword.Cloud(items, 500, 500, {
            output: vapourword.output_html,
            output_target: this,
            max_font_size: 50,
        });
    });

    return this;
};

})(jQuery);

