#!/usr/bin/env python

# Read XML file exported from Pleco and convert to Anki deck
# Usage: read_pleco_to_anki.py <input_file> <output_file>

input_file = 'flash.xml'

import xml.etree.ElementTree as ET
import genanki


class Card:
    def __init__(self,
                 simplified,
                 traditional,
                 pinyin,
                 definition
                 ):
        self.simplified = simplified
        self.traditional = traditional
        self.pinyin = pinyin
        self.definition = definition

    def __str__(self):
        return 'Card(simplified={}, traditional={}, pinyin={}, definition={})'.format(self.simplified,
                                       self.traditional,
                                       self.pinyin,
                                       self.definition)

# the structure is
#    <card language="chinese" created="1686178463" modified="1689690343">
#      <entry>
#        <headword charset="sc">难</headword>
#        <headword charset="tc">難</headword>
#        <pron type="hypy" tones="numbers">nan2</pron>
#        <defn>adjective 1 difficult; hard; troublesome (opp. 易) 很难想象 Hěn nán xiǎngxiàng (it’s) hard to imagine 山路难走。 Shānlù nán zǒu. Mountain paths are hard to travel. 说起来容易做起来难。 Shuō qǐlai róngyì zuò qǐlai nán. Easier said than done. 这道题很难解。 zhè dào tí hěn nán jiě. This problem is hard to solve. 2 hardly possible; unavoidable See 27188992难免nan2mian3难免 3 bad; unpleasant 这种啤酒真难喝。 zhèzhǒng píjiǔ zhēn nán hē. This beer tastes really bad.
#verb put sb. into a difficult position 这问题一下子把我难住了。 Zhè wèntí yīxiàzi bǎ wǒ nán zhù le. The question put me on the spot.</defn>
#      </entry>
#      <dictref dictid="PACE" entryid="27183104"/>
#      <catassign category="HSK 3.0/Level 1"/>
#      <catassign category="HSK 2012-2021/Level 3"/>
#      <catassign category="Custom"/>
#      <scoreinfo scorefile="Default" score="400" difficulty="84" history="5154" correct="3" incorrect="1" reviewed="4" sincelast="0" firstreviewedtime="1689690614" lastreviewedtime="1690296433"/>
#    </card>


# Print all the cards
def parse_cards_from_pleco_xml(input_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    cards = []
    for card in root.iter('card'):
      entry = card[0]
      if entry == None or entry.tag != 'entry':
        print('skipping card with no <entry>')

      columns = len(entry)
      if columns != 4:
        print('skipping card with entry missing expected information. <entry> tag should have simplified, traditional, pron, and defn')
        continue

      simplified_tag = entry[0]
      if simplified_tag == None or simplified_tag.tag != 'headword' or simplified_tag.attrib['charset'] != 'sc':
        continue
      simplified = entry[0].text

      traditional_tag = entry[1]
      traditional = None
      if traditional_tag != None and traditional_tag.tag == 'headword' and traditional_tag.attrib['charset'] == 'tc':
        traditional = entry[1].text

      pron_tag = entry[2]
      if pron_tag == None or pron_tag.tag != 'pron' or pron_tag.attrib['type'] != 'hypy':
        print('skipping card with no pronunciation')
        continue
      pron = entry[2].text

      defn_tag = entry[3]
      if defn_tag == None or defn_tag.tag != 'defn':
        print('skipping card with no definition')
        continue
      defn = entry[3].text
      card = Card(simplified, traditional, pron, defn)
      cards.append(card)
    return cards


def create_anki_deck(cards):
  my_model = genanki.Model(
    1607392319, # generate random model ID import random; random.randrange(1 << 30, 1 << 31)
    'Pleco to Anki Import model',
    fields=[
      {'name': 'SimplifiedChar'},
      {'name': 'TraditionalChar'},
      {'name': 'Pinyin'},
      {'name': 'DictDefinition'},
    ],
    templates=[
      {
        'name': 'Card 1',
        'qfmt': '{{SimplifiedChar}}: {{Pinyin}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{DictDefinition}}',
      },
    ])
  notes = []

  for card in cards:
    my_note = genanki.Note(
      model=my_model,
      fields=[card.simplified, card.traditional, card.pinyin, card.definition])
    notes.append(my_note)

  pleco_to_anki_deck = genanki.Deck(
    2059400110, # generate random model ID import random; random.randrange(1 << 30, 1 << 31)
    'Pleco to Anki Imported Cards')

  for note in notes:
    pleco_to_anki_deck.add_note(note)

  genanki.Package(pleco_to_anki_deck).write_to_file('/Users/cshinaver/Desktop/output.apkg')


if __name__ == '__main__':
  print('Importing Pleco XML file')
  cards = parse_cards_from_pleco_xml(input_file)
  print('found {} cards'.format(len(cards)))
  print('creating anki deck')
  create_anki_deck(cards)
  print('done')
