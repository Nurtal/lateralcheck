import pandas as pd
import re


def extract_text(text:str) -> str:
    """Extract & clean test to analyze from CR"""
    

def spot_laterality(text:str) -> list:
    """Spot sentences that contains a reference to laterality"""

    # init
    spoted_sentences = []

    # preprocess & split into sentences
    text = text.lower()
    sentence_list = text.split('. ')

    # catch laterality
    for sentence in sentence_list:
        match_droite = re.search('droit', sentence)
        match_gauche = re.search('gauche', sentence)
        if match_droite or match_gauche and sentence not in spoted_sentences:
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
    df = pd.read_csv('data/short.csv', sep="\t")

    # loop over text
    for text in list(df['TEXTE']):
        machin = simple_and_stupid(text)
        print(machin)



if __name__ == "__main__":


    run()
