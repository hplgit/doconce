/*
  This module adds support for notes in your deck. 
  To enable it on your elements add the classname:
  .notes to a section. To toggle notes press 'n'

  Example:
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
*/
(function($, deck, undefined) {

  var notesDisplayed = false;

  function showNotes(slide) {
    var notes = slide.find(".notes");
    notes.each(function(i, note) { $(note).show(); });
  }

  function toggleNotes(slide) {
    if (!notesDisplayed) {
      showNotes(slide);
      notesDisplayed = true;
    } else {
      var notes = slide.find(".notes");
      notes.each(function(i, note) { $(note).hide(); });
      notesDisplayed = false;
    }
  }

  $(document).bind("deck.change", function(event, from, to) {
    $(".notes").hide(); //hide all notes
    if (notesDisplayed) {
      var slide = $.deck('getSlide', to);
      showNotes(slide);
    }
  });

  $(document).bind("keypress", function(event) {
    if (event.which == "110") { //'n'
      toggleNotes($(".deck-current"));
    }
  });
})(jQuery, 'deck', this);

