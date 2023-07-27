# Pleco to Anki Import


There's no good way to sync Pleco flashcards and Anki flashcards, so I created
this script to convert a Pleco XML file to an Anki deck.


# Installation
Install the requirements from `requirements.txt` with pip 

`pip install -r requirements.txt` 

and then run

`python read_pleco_to_anki.py flash.xml ~/Desktop/`

This will create an anki deck called `pleco_to_anki.apkg` that you can open with your Desktop Anki application.

# Export from Pleco
For this to work, you must have the following checked from "Include Data":
* Card Defnintions
* Dictionary Definitions

# Loading into anki.
This can only be done with Desktop Anki. Double clicking on the deck will load
it into your desktop anki app. The deck id is constant, so if you rename it in
the app, new cards will be added to the correct deck. The script also creates
cards with ids hashed on their contents, so you can do reimports without
breaking your studying scores.

## Front of card
![Screenshot 2023-07-27 at 1 50 42 PM](https://github.com/cshinaver/pleco-to-anki/assets/7769334/334d9d4b-8627-4ab6-98a1-f599c5d18638)

## Back of card
![Screenshot 2023-07-27 at 1 50 46 PM](https://github.com/cshinaver/pleco-to-anki/assets/7769334/b6d97bb5-f7bd-4504-b7c3-6cf6040b10ee)
