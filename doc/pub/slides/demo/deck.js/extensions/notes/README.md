deck.js-notes extension
=======================
This simple extension allows you to view notes in your slides.
The notes can be accessed by hitting the 'n' key.

# Installation: #

Move all this into a folder called 'notes' in your deck.js/extensions/ folder.

# Setup: #

Include the stylesheet:

    <link rel="stylesheet" href="../extensions/notes/deck.notes.css">

Include the JS source:

    <script src="../extensions/notes/deck.notes.js"></script>

# Use: #

    <section class="slide">
      <h2>Important stuff:</h2>
      <ul>
        <li>This stuff is important
      </ul>
      <div class="notes">
        <ul>
          <li>Tell people: it is important because it is</li>
        </ul>  
      <div>
    <section/>
