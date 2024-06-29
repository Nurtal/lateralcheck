import pandas as pd
import re


def extract_text(text:str) -> list:
    """Extract & clean text to analyze from CR"""

    cleaned_text = []
    text_array = text.split("\n\n")
    for bloc in text_array:
        bloc = bloc.replace("\n", ". ").replace('.. ', '. ')

    return cleaned_text
    

def spot_laterality(text:str) -> list:
    """Spot sentences that contains a reference to laterality"""

    # parameters
    spoted_sentences = []
    target_list = ['droit', 'gauche', 'latéralité', 'homolatéral', 'controlatéral']

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


def appariement(sentence_list:list):
    """Associate laterality to an object in each of the sentence in sentence_list"""




def analyze():
    """ """



def run():
    """ """

    # load data
    with open('data/cr1.txt') as f: s = f.read()

    # process
    text_list = extract_text(s)
    for text in text_list:
        sentence_list = spot_laterality(text)




if __name__ == "__main__":


    # run()



    

    extract_text(s)
