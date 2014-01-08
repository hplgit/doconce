Warning:
New versions of reveal.js may have changes in style files that
may lead to strange behavior of old talks.

As of Jan 9, 2014, this directory contained a complete set of styles and
associated reveal.js.zip file that can be used if a future version
of reveal.js causes trouble.

How to create a custom style:

 * Unzip lib/doconce/reveal.js.zip.
   (Check the code in `_update.py` if a new version `reveal.js`
   is desired.)
 * Go to reveal.js/css/theme/source.
 * Start a new theme, say new.scss, as a copy of another theme.
 * Variables in new.scss can be set (font, font size, etc.).
 * Go to the reveal.js directory.
 * Run `grunt themes` to translate `*.scss` in `css/theme/source`
   to real CSS files `*.css` in `css/theme`. The `grunt` program
   must be installed.
 * Copy `new.css` over to the "fixed style files tree":
   `bundled/doconce_modifications/reveal/css/theme/`. Copy `new.scss`
   to `bundled/doconce_modifications/reveal/css/theme/source`.
 * Pack new reveal tree: `zip -r reveal.js.zip reveal.js`, and
   move to `../lib/doconce` (the official place the where
   bundled reveal.js software reside in the Doconce package).

