#deck.js extension presenterview

Presenterview is an extension for deck.js that brings a presentation view for the presentator. You can add comments into your presentation that will be shown
in the presenter view and the next slide is also included.

## Dependencies (not included in this repository)

- [deck.js](https://github.com/imakewebthings/deck.js)

## Instruction

1. Copy the presenterview extension to your deck.js extensions directory
2. Include the extensions javascript at the bottom of your presentations index.html: `<script type="text/javascript" src="../extensions/presenterview/deck.presenterview.js"></script>`
3. Also include the hash extension at the bottom of your presentations index.html: `<script type="text/javascript" src="../extensions/hash/deck.hash.js"></script>`
4. Add notes as HTML commentaries to the sections of your presentation (<!-- commentary -->) - you may use HTML-Markup inside the commentaries if you like to
5. (Optional) Style your presentation view
6. Open up your presentation - if the popup gets blocked, allow it and reload
7. Click on you Presentation Window again and do your stuff.

## License

Copyright (c) 2011 [Steven Wirges](https://github.com/stvnwrgs) & [Marc Dix](https://github.com/mdix)

Dual licensed under the [MIT license](https://github.com/imakewebthings/deck.js/blob/master/MIT-license.txt) and [GPL license](https://github.com/imakewebthings/deck.js/blob/master/GPL-license.txt).