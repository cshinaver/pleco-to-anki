#!/usr/bin/env python

# Read XML file exported from Pleco and convert to Anki deck
# Usage: read_pleco_to_anki.py <input_file> <output_file>

input_file = 'flash.xml'

import xml.etree.ElementTree as ET


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
        try:
            entry = card[0]
            simplified = entry[0].text
            traditional = entry[1].text
            pron = entry[2].text
            defn = entry[3].text
        except Exception as e:
            print('failed to parse card')
            for child in card:
                print(child.tag, child.attrib, child.text)
            print(e)
            continue
        card = Card(simplified, traditional, pron, defn)
        cards.append(card)
    return cards

if __name__ == '__main__':
    cards = parse_cards_from_pleco_xml(input_file)
    print(len(cards))
