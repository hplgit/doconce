/*
 * searchtools.js_t
 * ~~~~~~~~~~~~~~~~
 *
 * Sphinx JavaScript utilities for the full-text search.
 *
 * :copyright: Copyright 2007-2015 by the Sphinx team, see AUTHORS.
 * :license: BSD, see LICENSE for details.
 *
 */


/* Non-minified version JS is _stemmer.js if file is provided */ 
var JSX={};(function(g){function i(b,e){var a=function(){};a.prototype=e.prototype;var c=new a;for(var d in b){b[d].prototype=c}}function G(c,b){for(var a in b.prototype)if(b.prototype.hasOwnProperty(a))c.prototype[a]=b.prototype[a]}function e(a,b,d){function c(a,b,c){delete a[b];a[b]=c;return c}Object.defineProperty(a,b,{get:function(){return c(a,b,d())},set:function(d){c(a,b,d)},enumerable:true,configurable:true})}function H(a,b,c){return a[b]=a[b]/c|0}var B=parseInt;var q=parseFloat;function I(a){return a!==a}var y=isFinite;var x=encodeURIComponent;var w=decodeURIComponent;var u=encodeURI;var t=decodeURI;var s=Object.prototype.toString;var r=Object.prototype.hasOwnProperty;function h(){}g.require=function(b){var a=m[b];return a!==undefined?a:null};g.profilerIsRunning=function(){return h.getResults!=null};g.getProfileResults=function(){return(h.getResults||function(){return{}})()};g.postProfileResults=function(a,b){if(h.postResults==null)throw new Error('profiler has not been turned on');return h.postResults(a,b)};g.resetProfileResults=function(){if(h.resetResults==null)throw new Error('profiler has not been turned on');return h.resetResults()};g.DEBUG=false;function A(){};i([A],Error);function b(a,b,c){this.G=a.length;this.R=a;this.U=b;this.J=c;this.I=null;this.V=null};i([b],Object);function j(){};i([j],Object);function d(){var a;var b;var c;this.F={};a=this.C='';b=this._=0;c=this.A=a.length;this.B=0;this.D=b;this.E=c};i([d],j);function v(a,b){a.C=b.C;a._=b._;a.A=b.A;a.B=b.B;a.D=b.D;a.E=b.E};function l(b,d,c,e){var a;if(b._>=b.A){return false}a=b.C.charCodeAt(b._);if(a>e||a<c){return false}a-=c;if((d[a>>>3]&1<<(a&7))===0){return false}b._++;return true};function k(b,d,c,e){var a;if(b._<=b.B){return false}a=b.C.charCodeAt(b._-1);if(a>e||a<c){return false}a-=c;if((d[a>>>3]&1<<(a&7))===0){return false}b._--;return true};function p(a,d,c,e){var b;if(a._>=a.A){return false}b=a.C.charCodeAt(a._);if(b>e||b<c){a._++;return true}b-=c;if((d[b>>>3]&1<<(b&7))===0){a._++;return true}return false};function o(a,d,c,e){var b;if(a._<=a.B){return false}b=a.C.charCodeAt(a._-1);if(b>e||b<c){a._--;return true}b-=c;if((d[b>>>3]&1<<(b&7))===0){a._--;return true}return false};function n(a,b,d){var c;if(a._-a.B<b){return false}if(a.C.slice((c=a._)-b,c)!==d){return false}a._-=b;return true};function f(d,m,p){var b;var g;var e;var n;var f;var k;var l;var i;var h;var c;var a;var j;var o;b=0;g=p;e=d._;n=d.B;f=0;k=0;l=false;while(true){i=b+(g-b>>1);h=0;c=f<k?f:k;a=m[i];for(j=a.G-1-c;j>=0;j--){if(e-c===n){h=-1;break}h=d.C.charCodeAt(e-1-c)-a.R.charCodeAt(j);if(h!==0){break}c++}if(h<0){g=i;k=c}else{b=i;f=c}if(g-b<=1){if(b>0){break}if(g===b){break}if(l){break}l=true}}while(true){a=m[b];if(f>=a.G){d._=e-a.G|0;if(a.I==null){return a.J}o=a.I(d);d._=e-a.G|0;if(o){return a.J}}b=a.U;if(b<0){return 0}}return-1};function C(a,b,d,e){var c;c=e.length-(d-b);a.C=a.C.slice(0,b)+e+a.C.slice(d);a.A+=c|0;if(a._>=d){a._+=c|0}else if(a._>b){a._=b}return c|0};function c(a,f){var b;var c;var d;var e;b=false;if((c=a.D)<0||c>(d=a.E)||d>(e=a.A)||e>a.C.length?false:true){C(a,a.D,a.E,f);b=true}return b};d.prototype.H=function(){return false};d.prototype.S=function(b){var a;var c;var d;var e;a=this.F['.'+b];if(a==null){c=this.C=b;d=this._=0;e=this.A=c.length;this.B=0;this.D=d;this.E=e;this.H();a=this.C;this.F['.'+b]=a}return a};d.prototype.stemWord=d.prototype.S;d.prototype.T=function(e){var d;var b;var c;var a;var f;var g;var h;d=[];for(b=0;b<e.length;b++){c=e[b];a=this.F['.'+c];if(a==null){f=this.C=c;g=this._=0;h=this.A=f.length;this.B=0;this.D=g;this.E=h;this.H();a=this.C;this.F['.'+c]=a}d.push(a)}return d};d.prototype.stemWords=d.prototype.T;function a(){d.call(this);this.I_x=0;this.I_p1=0};i([a],d);a.prototype.K=function(a){this.I_x=a.I_x;this.I_p1=a.I_p1;v(this,a)};a.prototype.copy_from=a.prototype.K;a.prototype.P=function(){var g;var d;var b;var e;var c;var f;var i;var j;var k;var h;this.I_p1=j=this.A;g=i=this._;b=i+3|0;if(0>b||b>j){return false}h=this._=b;this.I_x=h;this._=g;a:while(true){d=this._;e=true;b:while(e===true){e=false;if(!l(this,a.g_v,97,248)){break b}this._=d;break a}k=this._=d;if(k>=this.A){return false}this._++}a:while(true){c=true;b:while(c===true){c=false;if(!p(this,a.g_v,97,248)){break b}break a}if(this._>=this.A){return false}this._++}this.I_p1=this._;f=true;a:while(f===true){f=false;if(!(this.I_p1<this.I_x)){break a}this.I_p1=this.I_x}return true};a.prototype.r_mark_regions=a.prototype.P;function F(b){var h;var e;var c;var f;var d;var g;var j;var k;var m;var i;b.I_p1=k=b.A;h=j=b._;c=j+3|0;if(0>c||c>k){return false}i=b._=c;b.I_x=i;b._=h;a:while(true){e=b._;f=true;b:while(f===true){f=false;if(!l(b,a.g_v,97,248)){break b}b._=e;break a}m=b._=e;if(m>=b.A){return false}b._++}a:while(true){d=true;b:while(d===true){d=false;if(!p(b,a.g_v,97,248)){break b}break a}if(b._>=b.A){return false}b._++}b.I_p1=b._;g=true;a:while(g===true){g=false;if(!(b.I_p1<b.I_x)){break a}b.I_p1=b.I_x}return true};a.prototype.O=function(){var b;var h;var d;var i;var e;var g;var j;var l;var m;h=this.A-(j=this._);if(j<this.I_p1){return false}l=this._=this.I_p1;d=this.B;this.B=l;m=this._=this.A-h;this.E=m;b=f(this,a.a_0,29);if(b===0){this.B=d;return false}this.D=this._;this.B=d;switch(b){case 0:return false;case 1:if(!c(this,'')){return false}break;case 2:e=true;a:while(e===true){e=false;i=this.A-this._;g=true;b:while(g===true){g=false;if(!k(this,a.g_s_ending,98,122)){break b}break a}this._=this.A-i;if(!n(this,1,'k')){return false}if(!o(this,a.g_v,97,248)){return false}}if(!c(this,'')){return false}break;case 3:if(!c(this,'er')){return false}break}return true};a.prototype.r_main_suffix=a.prototype.O;function E(b){var d;var l;var e;var i;var g;var h;var m;var p;var j;l=b.A-(m=b._);if(m<b.I_p1){return false}p=b._=b.I_p1;e=b.B;b.B=p;j=b._=b.A-l;b.E=j;d=f(b,a.a_0,29);if(d===0){b.B=e;return false}b.D=b._;b.B=e;switch(d){case 0:return false;case 1:if(!c(b,'')){return false}break;case 2:g=true;a:while(g===true){g=false;i=b.A-b._;h=true;b:while(h===true){h=false;if(!k(b,a.g_s_ending,98,122)){break b}break a}b._=b.A-i;if(!n(b,1,'k')){return false}if(!o(b,a.g_v,97,248)){return false}}if(!c(b,'')){return false}break;case 3:if(!c(b,'er')){return false}break}return true};a.prototype.N=function(){var e;var g;var b;var h;var d;var i;var j;var k;var l;e=(h=this.A)-(d=this._);g=h-d;if(d<this.I_p1){return false}i=this._=this.I_p1;b=this.B;this.B=i;j=this._=this.A-g;this.E=j;if(f(this,a.a_1,2)===0){this.B=b;return false}this.D=this._;l=this.B=b;k=this._=this.A-e;if(k<=l){return false}this._--;this.D=this._;return!c(this,'')?false:true};a.prototype.r_consonant_pair=a.prototype.N;function D(b){var i;var j;var d;var g;var e;var k;var l;var m;var h;i=(g=b.A)-(e=b._);j=g-e;if(e<b.I_p1){return false}k=b._=b.I_p1;d=b.B;b.B=k;l=b._=b.A-j;b.E=l;if(f(b,a.a_1,2)===0){b.B=d;return false}b.D=b._;h=b.B=d;m=b._=b.A-i;if(m<=h){return false}b._--;b.D=b._;return!c(b,'')?false:true};a.prototype.Q=function(){var b;var e;var d;var g;var h;var i;e=this.A-(g=this._);if(g<this.I_p1){return false}h=this._=this.I_p1;d=this.B;this.B=h;i=this._=this.A-e;this.E=i;b=f(this,a.a_2,11);if(b===0){this.B=d;return false}this.D=this._;this.B=d;switch(b){case 0:return false;case 1:if(!c(this,'')){return false}break}return true};a.prototype.r_other_suffix=a.prototype.Q;function z(b){var d;var g;var e;var h;var i;var j;g=b.A-(h=b._);if(h<b.I_p1){return false}i=b._=b.I_p1;e=b.B;b.B=i;j=b._=b.A-g;b.E=j;d=f(b,a.a_2,11);if(d===0){b.B=e;return false}b.D=b._;b.B=e;switch(d){case 0:return false;case 1:if(!c(b,'')){return false}break}return true};a.prototype.H=function(){var g;var f;var h;var b;var c;var a;var d;var i;var j;var k;var l;var e;g=this._;b=true;a:while(b===true){b=false;if(!F(this)){break a}}i=this._=g;this.B=i;k=this._=j=this.A;f=j-k;c=true;a:while(c===true){c=false;if(!E(this)){break a}}e=this._=(l=this.A)-f;h=l-e;a=true;a:while(a===true){a=false;if(!D(this)){break a}}this._=this.A-h;d=true;a:while(d===true){d=false;if(!z(this)){break a}}this._=this.B;return true};a.prototype.stem=a.prototype.H;a.prototype.L=function(b){return b instanceof a};a.prototype.equals=a.prototype.L;a.prototype.M=function(){var c;var a;var b;var d;c='NorwegianStemmer';a=0;for(b=0;b<c.length;b++){d=c.charCodeAt(b);a=(a<<5)-a+d;a=a&a}return a|0};a.prototype.hashCode=a.prototype.M;a.serialVersionUID=1;e(a,'methodObject',function(){return new a});e(a,'a_0',function(){return[new b('a',-1,1),new b('e',-1,1),new b('ede',1,1),new b('ande',1,1),new b('ende',1,1),new b('ane',1,1),new b('ene',1,1),new b('hetene',6,1),new b('erte',1,3),new b('en',-1,1),new b('heten',9,1),new b('ar',-1,1),new b('er',-1,1),new b('heter',12,1),new b('s',-1,2),new b('as',14,1),new b('es',14,1),new b('edes',16,1),new b('endes',16,1),new b('enes',16,1),new b('hetenes',19,1),new b('ens',14,1),new b('hetens',21,1),new b('ers',14,1),new b('ets',14,1),new b('et',-1,1),new b('het',25,1),new b('ert',-1,3),new b('ast',-1,1)]});e(a,'a_1',function(){return[new b('dt',-1,-1),new b('vt',-1,-1)]});e(a,'a_2',function(){return[new b('leg',-1,1),new b('eleg',0,1),new b('ig',-1,1),new b('eig',2,1),new b('lig',2,1),new b('elig',4,1),new b('els',-1,1),new b('lov',-1,1),new b('elov',7,1),new b('slov',7,1),new b('hetslov',9,1)]});e(a,'g_v',function(){return[17,65,16,1,0,0,0,0,0,0,0,0,0,0,0,0,48,0,128]});e(a,'g_s_ending',function(){return[119,125,149,1]});var m={'src/stemmer.jsx':{Stemmer:j},'src/norwegian-stemmer.jsx':{NorwegianStemmer:a}}}(JSX))
var Stemmer = JSX.require("src/norwegian-stemmer.jsx").NorwegianStemmer;



/**
 * Simple result scoring code.
 */
var Scorer = {
  // Implement the following function to further tweak the score for each result
  // The function takes a result array [filename, title, anchor, descr, score]
  // and returns the new score.
  /*
  score: function(result) {
    return result[4];
  },
  */

  // query matches the full name of an object
  objNameMatch: 11,
  // or matches in the last dotted part of the object name
  objPartialMatch: 6,
  // Additive scores depending on the priority of the object
  objPrio: {0:  15,   // used to be importantResults
            1:  5,   // used to be objectResults
            2: -5},  // used to be unimportantResults
  //  Used when the priority is not in the mapping.
  objPrioDefault: 0,

  // query found in title
  title: 15,
  // query found in terms
  term: 5
};


/**
 * Search Module
 */
var Search = {

  _index : null,
  _queued_query : null,
  _pulse_status : -1,

  init : function() {
      var params = $.getQueryParameters();
      if (params.q) {
          var query = params.q[0];
          $('input[name="q"]')[0].value = query;
          this.performSearch(query);
      }
  },

  loadIndex : function(url) {
    $.ajax({type: "GET", url: url, data: null,
            dataType: "script", cache: true,
            complete: function(jqxhr, textstatus) {
              if (textstatus != "success") {
                document.getElementById("searchindexloader").src = url;
              }
            }});
  },

  setIndex : function(index) {
    var q;
    this._index = index;
    if ((q = this._queued_query) !== null) {
      this._queued_query = null;
      Search.query(q);
    }
  },

  hasIndex : function() {
      return this._index !== null;
  },

  deferQuery : function(query) {
      this._queued_query = query;
  },

  stopPulse : function() {
      this._pulse_status = 0;
  },

  startPulse : function() {
    if (this._pulse_status >= 0)
        return;
    function pulse() {
      var i;
      Search._pulse_status = (Search._pulse_status + 1) % 4;
      var dotString = '';
      for (i = 0; i < Search._pulse_status; i++)
        dotString += '.';
      Search.dots.text(dotString);
      if (Search._pulse_status > -1)
        window.setTimeout(pulse, 500);
    }
    pulse();
  },

  /**
   * perform a search for something (or wait until index is loaded)
   */
  performSearch : function(query) {
    // create the required interface elements
    this.out = $('#search-results');
    this.title = $('<h2>' + _('Searching') + '</h2>').appendTo(this.out);
    this.dots = $('<span></span>').appendTo(this.title);
    this.status = $('<p style="display: none"></p>').appendTo(this.out);
    this.output = $('<ul class="search"/>').appendTo(this.out);

    $('#search-progress').text(_('Preparing search...'));
    this.startPulse();

    // index already loaded, the browser was quick!
    if (this.hasIndex())
      this.query(query);
    else
      this.deferQuery(query);
  },

  /**
   * execute search (requires search index to be loaded)
   */
  query : function(query) {
    var i;
    var stopwords = ["alle","at","av","bare","begge","ble","blei","bli","blir","blitt","b\u00e5de","b\u00e5e","da","de","deg","dei","deim","deira","deires","dem","den","denne","der","dere","deres","det","dette","di","din","disse","ditt","du","dykk","dykkar","d\u00e5","eg","ein","eit","eitt","eller","elles","en","enn","er","et","ett","etter","for","fordi","fra","f\u00f8r","ha","hadde","han","hans","har","hennar","henne","hennes","her","hj\u00e5","ho","hoe","honom","hoss","hossen","hun","hva","hvem","hver","hvilke","hvilken","hvis","hvor","hvordan","hvorfor","i","ikke","ikkje","ingen","ingi","inkje","inn","inni","ja","jeg","kan","kom","korleis","korso","kun","kunne","kva","kvar","kvarhelst","kven","kvi","kvifor","man","mange","me","med","medan","meg","meget","mellom","men","mi","min","mine","mitt","mot","mykje","ned","no","noe","noen","noka","noko","nokon","nokor","nokre","n\u00e5","n\u00e5r","og","ogs\u00e5","om","opp","oss","over","p\u00e5","samme","seg","selv","si","sia","sidan","siden","sin","sine","sitt","sj\u00f8l","skal","skulle","slik","so","som","somme","somt","s\u00e5","s\u00e5nn","til","um","upp","ut","uten","var","vart","varte","ved","vere","verte","vi","vil","ville","vore","vors","vort","v\u00e5r","v\u00e6re","v\u00e6rt","\u00e5"];

    // stem the searchterms and add them to the correct list
    var stemmer = new Stemmer();
    var searchterms = [];
    var excluded = [];
    var hlterms = [];
    var tmp = query.split(/\s+/);
    var objectterms = [];
    for (i = 0; i < tmp.length; i++) {
      if (tmp[i] !== "") {
          objectterms.push(tmp[i].toLowerCase());
      }

      if ($u.indexOf(stopwords, tmp[i].toLowerCase()) != -1 || tmp[i].match(/^\d+$/) ||
          tmp[i] === "") {
        // skip this "word"
        continue;
      }
      // stem the word
      var word = stemmer.stemWord(tmp[i].toLowerCase());
      var toAppend;
      // select the correct list
      if (word[0] == '-') {
        toAppend = excluded;
        word = word.substr(1);
      }
      else {
        toAppend = searchterms;
        hlterms.push(tmp[i].toLowerCase());
      }
      // only add if not already in the list
      if (!$u.contains(toAppend, word))
        toAppend.push(word);
    }
    var highlightstring = '?highlight=' + $.urlencode(hlterms.join(" "));

    // console.debug('SEARCH: searching for:');
    // console.info('required: ', searchterms);
    // console.info('excluded: ', excluded);

    // prepare search
    var terms = this._index.terms;
    var titleterms = this._index.titleterms;

    // array of [filename, title, anchor, descr, score]
    var results = [];
    $('#search-progress').empty();

    // lookup as object
    for (i = 0; i < objectterms.length; i++) {
      var others = [].concat(objectterms.slice(0, i),
                             objectterms.slice(i+1, objectterms.length));
      results = results.concat(this.performObjectSearch(objectterms[i], others));
    }

    // lookup as search terms in fulltext
    results = results.concat(this.performTermsSearch(searchterms, excluded, terms, Scorer.term))
                     .concat(this.performTermsSearch(searchterms, excluded, titleterms, Scorer.title));

    // let the scorer override scores with a custom scoring function
    if (Scorer.score) {
      for (i = 0; i < results.length; i++)
        results[i][4] = Scorer.score(results[i]);
    }

    // now sort the results by score (in opposite order of appearance, since the
    // display function below uses pop() to retrieve items) and then
    // alphabetically
    results.sort(function(a, b) {
      var left = a[4];
      var right = b[4];
      if (left > right) {
        return 1;
      } else if (left < right) {
        return -1;
      } else {
        // same score: sort alphabetically
        left = a[1].toLowerCase();
        right = b[1].toLowerCase();
        return (left > right) ? -1 : ((left < right) ? 1 : 0);
      }
    });

    // for debugging
    //Search.lastresults = results.slice();  // a copy
    //console.info('search results:', Search.lastresults);

    // print the results
    var resultCount = results.length;
    function displayNextItem() {
      // results left, load the summary and display it
      if (results.length) {
        var item = results.pop();
        var listItem = $('<li style="display:none"></li>');
        if (DOCUMENTATION_OPTIONS.FILE_SUFFIX === '') {
          // dirhtml builder
          var dirname = item[0] + '/';
          if (dirname.match(/\/index\/$/)) {
            dirname = dirname.substring(0, dirname.length-6);
          } else if (dirname == 'index/') {
            dirname = '';
          }
          listItem.append($('<a/>').attr('href',
            DOCUMENTATION_OPTIONS.URL_ROOT + dirname +
            highlightstring + item[2]).html(item[1]));
        } else {
          // normal html builders
          listItem.append($('<a/>').attr('href',
            item[0] + DOCUMENTATION_OPTIONS.FILE_SUFFIX +
            highlightstring + item[2]).html(item[1]));
        }
        if (item[3]) {
          listItem.append($('<span> (' + item[3] + ')</span>'));
          Search.output.append(listItem);
          listItem.slideDown(5, function() {
            displayNextItem();
          });
        } else if (DOCUMENTATION_OPTIONS.HAS_SOURCE) {
          $.ajax({url: DOCUMENTATION_OPTIONS.URL_ROOT + '_sources/' + item[0] + '.txt',
                  dataType: "text",
                  complete: function(jqxhr, textstatus) {
                    var data = jqxhr.responseText;
                    if (data !== '' && data !== undefined) {
                      listItem.append(Search.makeSearchSummary(data, searchterms, hlterms));
                    }
                    Search.output.append(listItem);
                    listItem.slideDown(5, function() {
                      displayNextItem();
                    });
                  }});
        } else {
          // no source available, just display title
          Search.output.append(listItem);
          listItem.slideDown(5, function() {
            displayNextItem();
          });
        }
      }
      // search finished, update title and status message
      else {
        Search.stopPulse();
        Search.title.text(_('Search Results'));
        if (!resultCount)
          Search.status.text(_('Your search did not match any documents. Please make sure that all words are spelled correctly and that you\'ve selected enough categories.'));
        else
            Search.status.text(_('Search finished, found %s page(s) matching the search query.').replace('%s', resultCount));
        Search.status.fadeIn(500);
      }
    }
    displayNextItem();
  },

  /**
   * search for object names
   */
  performObjectSearch : function(object, otherterms) {
    var filenames = this._index.filenames;
    var objects = this._index.objects;
    var objnames = this._index.objnames;
    var titles = this._index.titles;

    var i;
    var results = [];

    for (var prefix in objects) {
      for (var name in objects[prefix]) {
        var fullname = (prefix ? prefix + '.' : '') + name;
        if (fullname.toLowerCase().indexOf(object) > -1) {
          var score = 0;
          var parts = fullname.split('.');
          // check for different match types: exact matches of full name or
          // "last name" (i.e. last dotted part)
          if (fullname == object || parts[parts.length - 1] == object) {
            score += Scorer.objNameMatch;
          // matches in last name
          } else if (parts[parts.length - 1].indexOf(object) > -1) {
            score += Scorer.objPartialMatch;
          }
          var match = objects[prefix][name];
          var objname = objnames[match[1]][2];
          var title = titles[match[0]];
          // If more than one term searched for, we require other words to be
          // found in the name/title/description
          if (otherterms.length > 0) {
            var haystack = (prefix + ' ' + name + ' ' +
                            objname + ' ' + title).toLowerCase();
            var allfound = true;
            for (i = 0; i < otherterms.length; i++) {
              if (haystack.indexOf(otherterms[i]) == -1) {
                allfound = false;
                break;
              }
            }
            if (!allfound) {
              continue;
            }
          }
          var descr = objname + _(', in ') + title;

          var anchor = match[3];
          if (anchor === '')
            anchor = fullname;
          else if (anchor == '-')
            anchor = objnames[match[1]][1] + '-' + fullname;
          // add custom score for some objects according to scorer
          if (Scorer.objPrio.hasOwnProperty(match[2])) {
            score += Scorer.objPrio[match[2]];
          } else {
            score += Scorer.objPrioDefault;
          }
          results.push([filenames[match[0]], fullname, '#'+anchor, descr, score]);
        }
      }
    }

    return results;
  },

  /**
   * search for full-text terms in the index
   */
  performTermsSearch : function(searchterms, excluded, terms, score) {
    var filenames = this._index.filenames;
    var titles = this._index.titles;

    var i, j, file, files;
    var fileMap = {};
    var results = [];

    // perform the search on the required terms
    for (i = 0; i < searchterms.length; i++) {
      var word = searchterms[i];
      // no match but word was a required one
      if ((files = terms[word]) === undefined)
        break;
      if (files.length === undefined) {
        files = [files];
      }
      // create the mapping
      for (j = 0; j < files.length; j++) {
        file = files[j];
        if (file in fileMap)
          fileMap[file].push(word);
        else
          fileMap[file] = [word];
      }
    }

    // now check if the files don't contain excluded terms
    for (file in fileMap) {
      var valid = true;

      // check if all requirements are matched
      if (fileMap[file].length != searchterms.length)
          continue;

      // ensure that none of the excluded terms is in the search result
      for (i = 0; i < excluded.length; i++) {
        if (terms[excluded[i]] == file ||
          $u.contains(terms[excluded[i]] || [], file)) {
          valid = false;
          break;
        }
      }

      // if we have still a valid result we can add it to the result list
      if (valid) {
        results.push([filenames[file], titles[file], '', null, score]);
      }
    }
    return results;
  },

  /**
   * helper function to return a node containing the
   * search summary for a given text. keywords is a list
   * of stemmed words, hlwords is the list of normal, unstemmed
   * words. the first one is used to find the occurrence, the
   * latter for highlighting it.
   */
  makeSearchSummary : function(text, keywords, hlwords) {
    var textLower = text.toLowerCase();
    var start = 0;
    $.each(keywords, function() {
      var i = textLower.indexOf(this.toLowerCase());
      if (i > -1)
        start = i;
    });
    start = Math.max(start - 120, 0);
    var excerpt = ((start > 0) ? '...' : '') +
      $.trim(text.substr(start, 240)) +
      ((start + 240 - text.length) ? '...' : '');
    var rv = $('<div class="context"></div>').text(excerpt);
    $.each(hlwords, function() {
      rv = rv.highlightText(this, 'highlighted');
    });
    return rv;
  }
};

$(document).ready(function() {
  Search.init();
});