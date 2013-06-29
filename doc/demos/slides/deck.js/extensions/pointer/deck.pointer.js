(function($, deck, undefined) {
    var $d = $(document);

    $.extend(true, $[deck].defaults, {
        classes: {
            pointer: 'deck-pointer'
        },

        keys: {
            pointer: 80 // p
        }
    });


    $[deck]('extend', 'showPointer', function() {
        $[deck]('getContainer').addClass($[deck]('getOptions').classes.pointer);
        $[deck]('getContainer').unbind('mousemove.deckpointer').bind('mousemove.deckpointer', function(e){
            pointer = $('<div>').attr({'class':'pointer'});

            $[deck]('getContainer').append(pointer); 
 
            pointer.css({
                top: e.pageY,
                left: e.pageX
            }).fadeOut(1500, function(){
                $(this).remove();
            });   
        });
    });

    $[deck]('extend', 'hidePointer', function() {
        $[deck]('getContainer').removeClass($[deck]('getOptions').classes.pointer);
        $[deck]('getContainer').unbind('mousemove.deckpointer');
    });

    $[deck]('extend', 'togglePointer', function() {
        $[deck]('getContainer').hasClass($[deck]('getOptions').classes.pointer) ?
        $[deck]('hidePointer') : $[deck]('showPointer');
    });

    $d.bind('deck.init', function() {
        var opts = $[deck]('getOptions');

        $d.unbind('keydown.deckpointer').bind('keydown.pointer', function(e) {
            if (e.which === opts.keys.pointer || $.inArray(e.which, opts.keys.pointer) > -1) {
                $[deck]('togglePointer');
                e.preventDefault();
            }
        });
    });
})(jQuery, 'deck');
