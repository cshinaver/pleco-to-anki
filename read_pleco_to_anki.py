#!/usr/bin/env python

# Read XML file exported from Pleco and convert to Anki deck
# Usage: read_pleco_to_anki.py <input_file> <output_file>

import xml.etree.ElementTree as ET
import genanki
import argparse, os, sys, re

OUTPUT_FILENAME = 'pleco_to_anki_deck.apkg'
DECK_ID = 2059400110 # generate random model ID import random; random.randrange(1 << 30, 1 << 31)
CARD_TEMPLATE_ID = 1607392319 # generate random model ID import random; random.randrange(1 << 30, 1 << 31)

# Implement argument parsing with argparse.
# Expect one input xml file and one output anki file
def parse_args():
  parser = argparse.ArgumentParser(description='Read XML file exported from Pleco and convert to Anki deck')
  parser.add_argument('input_file', type=str, help='Flashcards XML file from Pleco')
  parser.add_argument('output_path', type=str, help='output path for Anki deck')
  args = parser.parse_args()

  # Verify input file exists and is xml file
  if not os.path.isfile(args.input_file):
    print('Input file {} does not exist'.format(args.input_file))
    sys.exit(1)
  if not args.input_file.endswith('.xml'):
    print('Input file {} is not an xml file'.format(args.input_file))
    sys.exit(1)

  # verify output path is valid path
  if not os.path.isdir(os.path.dirname(args.output_path)):
    print('Output path {} is not a valid path'.format(args.output_path))
    sys.exit(1)

  return args



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


def is_chinese_char(char):
  return char >= u'\u4e00' and char <= u'\u9fff'

def clean_defn(raw_defn):
  defn = raw_defn

  ls = []

  # Raw definition looks like this
  # adjective 1 difficult; hard; troublesome (opp. 易) 很难想象 Hěn nán xiǎngxiàng (it’s) hard to imagine 山路难走。 Shānlù nán zǒu. Mountain paths are hard to travel. 说起来容易做起来难。 Shuō qǐ
  # lai róngyì zuò qǐlai nán. Easier said than done. 这道题很难解。 zhè dào tí hěn nán jiě. This problem is hard to solve. 2 hardly possible; unavoidable See 27188992难免nan2mian3难免 3 bad;
  # unpleasant 这种啤酒真难喝。 zhèzhǒng píjiǔ zhēn nán hē. This beer tastes really bad.
  # verb put sb. into a difficult position 这问题一下子把我难住了。 Zhè wèntí yīxiàzi bǎ wǒ nán zhù le. The question put me on the spot.

  # Convert to look like this
  # adjective 1 difficult; hard; troublesome (opp. 易)
  # | 很难想象 Hěn nán xiǎngxiàng (it’s) hard to imagine
  # | 山路难走。 Shānlù nán zǒu. Mountain paths are hard to travel.
  # | 说起来容易做起来难。 Shuō qǐ lai róngyì zuò qǐlai nán. Easier said than done.
  # | 这道题很难解。 zhè dào tí hěn nán jiě. This problem is hard to solve.

  # 2 hardly possible; unavoidable
  # See 27188992难免nan2mian3难免

  in_chinese_sentence = False
  for i, c in enumerate(raw_defn):
    # if current and next chars are chinese, add new line before current char
    if i < len(raw_defn) - 1 and not in_chinese_sentence and is_chinese_char(c) and is_chinese_char(raw_defn[i+1]):
      ls.append('\n')
      in_chinese_sentence = True
    elif in_chinese_sentence and not is_chinese_char(c):
      in_chinese_sentence = False
    # if next section is a number followed by words followed by semicolon, add a newline
    elif re.match(r'^\d+ [a-zA-Z ]+;', raw_defn[i:i+40]):
      ls.append('\n\n')

    # if word is 'noun', 'verb', or 'adjective', add a new line
    current_word = re.match(r'^[a-zA-Z]+', raw_defn[i:i+40])
    if current_word and current_word.group(0) in ['noun', 'verb', 'adjective']:
      ls.append('\n')

    ls.append(c)
  defn = ''.join(ls)
  return defn


# Print all the cards
def parse_cards_from_pleco_xml(input_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    cards = []
    for i, card in enumerate(root.iter('card')):
      entry = card[0]
      if entry == None or entry.tag != 'entry':
        print('skipping card with no <entry>')

      columns = len(entry)
      if columns != 4:
        print('skipping card {} with entry missing expected information. <entry> tag should have simplified, traditional, pron, and defn'.format(i))
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
      defn = clean_defn(entry[3].text)
      card = Card(simplified, traditional, pron, defn)
      cards.append(card)
    return cards


def create_anki_deck(cards, output_path):
  my_model = genanki.Model(
    CARD_TEMPLATE_ID,
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

  deck_name = 'Pleco to Anki Imported Cards'

  pleco_to_anki_deck = genanki.Deck(
    DECK_ID,
    deck_name)

  for note in notes:
    pleco_to_anki_deck.add_note(note)


  genanki.Package(pleco_to_anki_deck).write_to_file(os.path.join(output_path, 'pleco_to_anki.apkg'))


if __name__ == '__main__':
  args = parse_args()
  print('Importing Pleco XML file')
  cards = parse_cards_from_pleco_xml(args.input_file)
  print('found {} cards'.format(len(cards)))
  print('creating anki deck')
  create_anki_deck(cards, args.output_path)
  print('done')
