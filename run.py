import pandas as pd
import re
import spacy
import glob


def extract_text(text:str) -> list:
    """Extract & clean text to analyze from CR"""

    cleaned_text = []
    text_array = text.split("\n\n")
    for bloc in text_array:
        bloc = bloc.replace("\n", ". ").replace('.. ', '. ')
        cleaned_text.append(bloc)

    return cleaned_text
    

def spot_laterality(text:str, target_list:list) -> list:
    """Spot sentences that contains a reference to laterality"""

    # parameters
    spoted_sentences = []

    # preprocess & split into sentences
    text = text.lower()
    sentence_list = text.split('. ')

    # catch laterality
    for sentence in sentence_list:
        for target in target_list:
            match_target = re.search(target, sentence)
            if match_target and sentence not in spoted_sentences:
                spoted_sentences.append(sentence)

    # return interesting sentences
    return spoted_sentences


def appariement(sentence:str, nlp, target_list:list):
    """Associate adjective to a noun in sentence
    Args:
        sentence (str) : the sentence to parse
        target_list (list) : list of adjective to spot

    Returns:
        list of tuples [(adjective, noun)]
    """

    # process sentence
    doc = nlp(sentence)

    # Iterate through the parsed tokens
    adjectives_and_nouns = []
    for token in doc:
        if token.pos_ == "ADJ" and token.text in target_list:
            for child in token.children:
                if child.dep_ in ["amod", "acomp", "attr"]:
                    adjectives_and_nouns.append((token.text, child.text))
            if token.head.pos_ == "NOUN":
                adjectives_and_nouns.append((token.text, token.head.text))

    # return apparied data
    return adjectives_and_nouns




def extract_changes(apparied_data:list):
    """ """

    element_to_position = {}
    for elt in apparied_data:
        adj = elt[0]
        noun = elt[1]
        if noun not in element_to_position:
            element_to_position[noun] = [adj]
        elif adj not in element_to_position[noun]:
            element_to_position[noun].append(adj)
    elt_to_changes = {}
    for elt in element_to_position:
        if len(element_to_position[elt]) > 1:
            elt_to_changes[elt] = element_to_position[elt]

    return elt_to_changes
        

    




def run(doc_list):
    """ """

    # init
    nlp = spacy.load("fr_core_news_sm")
    sentence_list = []
    apparied_data = []
    target_list = [
        'droit',
        'droite',
        'gauche',
        'latéralité',
        'homolatéral',
        'controlatéral',
        'dorsal',
        'dorsale',
        'dorsaux',            
        'ventral',
        'ventrale',
        'ventraux'
    ]

    # Extract informations
    for doc in doc_list:
        with open(doc) as f: s = f.read()
        text_list = extract_text(s)
        for text in text_list:
            sentence_list += spot_laterality(text, target_list)
        for sentence in sentence_list:
            apparied_data += appariement(sentence, nlp, target_list)

    # Analyse information
    element_to_changes = extract_changes(apparied_data)
    print(element_to_changes)





if __name__ == "__main__":

    text_list = glob.glob('data/scenar1/*.txt')
    run(text_list)

