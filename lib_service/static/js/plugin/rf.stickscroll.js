(function($) {
    $.fn.stickScroll = function() {
        var target = this;

        var SCROLL_DOWN = -1;
        var SCROLL_UP = 1;
        var lastTopPostion = 0;
        var targetInitTop = target.offset().top;
        
        function scroll() {

            var y = $(window).scrollTop();
            var verticalScroll = isVerticalScroll(y);
            if (verticalScroll) {
                var targetHeight = target.outerHeight(true);
                var documentHeight = $(document).height();
                var winHeight = $(window).height();
                
                var scrollDirection = getScrollDirection(y);

                if (y >= targetInitTop) {
                    if (targetHeight <= winHeight) {
                        target.css({
                            position: "relative",
                            top: y - targetInitTop
                        });

                    } else {
                        if (scrollDirection == SCROLL_DOWN) {
                            var isBottom = y + winHeight >= targetInitTop + targetHeight;
                            if (isBottom) {
                                target.css({ 
                                    position: "relative",
                                    top: y + winHeight - targetHeight - targetInitTop
                                });
                            }
                        } else if (scrollDirection == SCROLL_UP){
                            var targetTop = target.offset().top; 
                            var isTop = y <= targetTop;
                            if (isTop) {
                                target.css({ 
                                    position: "relative",
                                    top: y - targetInitTop
                                });
                            }
                        }
                    }
                } else {
                    target.css({ 
                        position: "",
                        top: targetInitTop 
                    });
                }
                lastTopPostion = y;
            }
       }

        function isVerticalScroll(pNewScrollTop) {
            return pNewScrollTop != lastTopPostion;
        }
        
        function getScrollDirection(pNewScrollTop) {
            if (pNewScrollTop > lastTopPostion) {
                return SCROLL_DOWN;
            } else {
                return SCROLL_UP;
            }
        }
        
        function init() {
            $(window).scroll(scroll);
            $(window).resize(scroll);
        }
        init();
    };
    
    $.fn.floatFix = function(pParentId) { //Added for CR 146109ESPE02. Wang Fuqiang 2014.8.18
        var target = this;

        var lastTopPostion = 0;
        
        var targetInitTop = target.offset().top;

        var targetInitLeft = target.offset().left;

        var parent = null;
        if (pParentId) {
            parent = $( pParentId );
        }
        
        //var targetInitWidth = parent.outerWidth() - 2 * targetInitLeft;
        var targetInitWidth = parent.width();
        
        function scroll() {
            var x = $(window).scrollLeft();
            var y = $(window).scrollTop();

            var verticalScroll = isVerticalScroll(y);
            if (verticalScroll) {
                if (y >= targetInitTop) {
                    target.css({ 
                        position: "fixed",
                        top: 0,
                        left: targetInitLeft - x,
                        width: targetInitWidth
                    });
                } else {
                    target.css({ 
                        position: "",
                        top: targetInitTop,
                        width: ""
                    });
                }
                lastTopPostion = y;
            } else {
                target.css({ 
                    left: targetInitLeft - x,
                    width: targetInitWidth
                });
            }
        }

        function isVerticalScroll(pNewScrollTop) {
            return pNewScrollTop != lastTopPostion;
        }

        function resize() {
            if (parent) {
                //targetInitWidth = parent.outerWidth() - 2 * targetInitLeft;
                targetInitWidth = parent.width();
            }
            
            scroll();
        }

        function init() {
            $(window).scroll(scroll);
            $(window).resize(resize);
        }
        init();
    };
})(jQuery);