# Pleco to Anki Import


There's no good way to sync Pleco flashcards and Anki flashcards, so I created
this script to convert a Pleco XML file to an Anki deck.


# Installation
Install the requirements from `requirements.txt` and then run

`python read_pleco_to_anki.py flash.xml ~/Desktop/`

# Loading into anki.
This can only be done with Desktop Anki. Double clicking on the deck will load
it into your desktop anki app. The deck id is constant, so if you rename it in
the app, new cards will be added to the correct deck. The script also creates
cards with ids hashed on their contents, so you can do reimports without
breaking your studying scores.
