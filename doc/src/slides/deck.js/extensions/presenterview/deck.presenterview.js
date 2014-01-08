if (window.$ !== undefined) {
    /**
    * When the presentation loads, the path to all included stylesheets is written to the localStorage, so we can
    * show a smaller version of the slide in the presenterView. After that the presenterView launchs as a popup.
    */
    $(document).bind('deck.init', function() {
        // write css links to localStorage
        presenterView.writeAllCssPathsToLocalStorage();

        // open popup, 3 args: link to open, windows name, width + height
        var presenter = window.open(presenterView.getLinkToPresenterView(), 
                                    'deck.js - presenterView', 
                                    'width=' + screen.width + ', height=' + screen.height);
    });

    /**
    * Note: This event is also triggered when the presentation is loaded!
    * When the current slide changes, the current item is determined in order to grab its content and extract
    * the html commentaries. If this slide is a section (what means it's a new slide, not just a nested element), 
    * we grab the html commentaries and the content and store it in the localSession which gets read by the 
    * presenterView.
    */
    $(document).bind('deck.change', function(event, from, to) {
        presenterView.setCurrentItem(document.getElementById(location.hash.substring(1)));

        if (presenterView.currentItemIsFromTypeSection()) {
            // prepare
            presenterView.storeNotes();
            presenterView.storeNextSlide();

            // write prepared content to localStorage
            presenterView.write();
        }
    });
}
    
/**
 * presenterView object, does all the work. Methods are called by the events above.
 */
var presenterView = (function() {
    "use strict";
    // private
    var currentItem = null;
    var currentItemsContent = null;
    var writeToLocalStorage = [];
    
    /**
     * Creates the link to the presenterView, based on the current location (this is needed because nobody
     * knows how the very much appreciated user names his presentation).
     */
    var createLinkToPresenterView = function() {
        var hrefArr        = window.location.href.split('/');
        var lastElemsIndex = hrefArr.length - 1;

        delete hrefArr[lastElemsIndex];
        delete hrefArr[lastElemsIndex - 1];

        var baseUrl = hrefArr.join('/');
        var urlToPresenterView = baseUrl + 'extensions/presenterview/deck.presenterview.html';
        
        return urlToPresenterView;
    };
    
    var addItemToLocalStorageArray = function(identifier, item) {
        writeToLocalStorage[identifier] = item;
    };
    
    /**
     * Extracts the html commentary from the current items content.
     */
    var getNotes = function() {
        var startOfComment = currentItemsContent.indexOf('<!--');
        var endOfComment   = currentItemsContent.indexOf('-->');

        if (startOfComment !== -1 && endOfComment !== -1) {
            return currentItemsContent.substring(startOfComment + 4, endOfComment);
        }
        
        return '';
    };
    
    /**
     * Checks if there's a next slide (another section in the markup below the current) and returns
     * the content if so.
     */
    var getNextSlide = function() {
        if (currentItem.nextElementSibling.nodeName === 'SECTION') {
            return currentItem.nextElementSibling.innerHTML;
        } else {
            return '';
        }
    };

    // public
    return {
        /**
         * Loops trough all stylesheets that are included in the presentation and writes them to the localStorage.
         */
        writeAllCssPathsToLocalStorage: function() {
            if (document.styleSheets.length > 0) {
                var styleArr = [];
                
                for (var i = 0; i < document.styleSheets.length - 1; i++) {
                    styleArr.push(document.styleSheets[i].href);
                }
                
                localStorage.setItem('stylesheets', JSON.stringify(styleArr));
            }
        },

        getLinkToPresenterView: function() {
            return createLinkToPresenterView();
        },
        
        /**
         * Check if the current item is a slide or just a nested element in a slide.
         */
        currentItemIsFromTypeSection: function() {
            return currentItem.nodeName === 'SECTION';
        },
        
        /**
         * Write the current Item (DomNode) to the objects store to do some stuff with it.
         */
        setCurrentItem: function(DomNode) {
            currentItem = DomNode;
            currentItemsContent = DomNode.innerHTML;
        },
        
        /**
         * Called to get and store the html commentary of the current slide.
         */
        storeNotes: function() {
            addItemToLocalStorageArray('notes', getNotes());
        },
        
        /**
         * Called to get and store the html markup of the next slide.
         */
        storeNextSlide: function() {
            addItemToLocalStorageArray('next_slide', getNextSlide());
        },
        
        /**
         * Writes the items that are stored in writeToLocalStorage[] to the localStorage - should be called after 
         * writeToLocalStorage[] has been filled with values. :)
         */
        write: function() {
            if (writeToLocalStorage.notes !== 'undefined') {
                localStorage.setItem('notes', writeToLocalStorage['notes']);
            }
            
            if (writeToLocalStorage.next_slide !== 'undefined') {
                localStorage.setItem('next_slide', writeToLocalStorage['next_slide']);
            }
        }
    }
})();