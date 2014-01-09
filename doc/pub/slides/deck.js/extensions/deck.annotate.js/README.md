deck.annotate.js
================

Allows you to annotate deck.js presentation slides

## Requirements

[deck.js](https://github.com/imakewebthings/deck.js)

## Example:

![Sample Image](https://raw.github.com/nemec/deck.annotate.js/master/example.png)

## Features:

* Separate canvases for each slide.
* Multiple shapes (line, circle, rectangle).
* Multiple thicknesses.
* Multiple colors.
* All colors, shapes, and thicknesses are modifiable as options.
* Allows simple undo/redo per-slide.
* Allows clearing of single slide or all slides.
* Annotations show up when printing (although they
  can be disabled by turning off annotations).
* UI toolbox to make picking shape, size, and color easy.

## Default Keybindings:

* Enable/disable annotations: `P`
* Undo shape: `Ctrl + Z`
* Redo shape: `Ctrl + Shift + Z`
* Clear slide: `C`
* Clear all slides: `Ctrl + C`

## Todo:

* Add localstorage support so that annotations persist across refreshes.
* Better UI for the toolbox and less gaudy default colors.
