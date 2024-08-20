from numpy.core.function_base import logspace
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


def extract_changes(apparied_data:list) -> dict:
    """Extract changes of orientation from apparied data, return organ with changed orientation
    and the list of associated orientation as dict """

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
        

    
def display_changes(changes:dict, data:dict) -> pd.DataFrame:
    """Generate a pandas dataframe where each row correspond to:
        ORGAN / ORIENTATION / DOC / SENTENCE 
    """

    # craft data
    vector_list = []
    for o in changes:
        laterallity_list = changes[o]
        for doc in data:
            for sentence in data[doc]:
                infos = data[doc][sentence]
                for elt in infos:
                    if o == elt[1] and elt[0] in laterallity_list:
                        vector = {"ORGAN":o, "ORIENTATION":elt[0], "DOC":doc, "SENTENCE":sentence}
                        if vector not in vector_list:
                            vector_list.append(vector)
    # export in dataframe
    return pd.DataFrame(vector_list)



def parse_result(result_file, element_to_changes, log_file):
    """ """

    # loop over element to scan
    logs = []
    for organ in element_to_changes:

        # load laterality to doc
        laterality_to_doc = {}
        df = pd.read_csv(result_file)
        df = df[df['ORGAN'] == organ]
        for index, row in df.iterrows():
            doc = row['DOC']
            orientation = row['ORIENTATION']
            if orientation not in laterality_to_doc:
                laterality_to_doc[orientation] = [doc]
            else:
                if doc not in laterality_to_doc[orientation]:
                    laterality_to_doc[orientation].append(doc)

        # craft logs
        sentence = f"[*] Attention ! Changement d'orientation détécté pour l'élément {organ} :\n"
        for orientation in laterality_to_doc:
            sentence += f"[+]{orientation} dans les documents :\n"
            for doc in laterality_to_doc[orientation]:
                sentence+= f"\t- {doc}\n"
        logs.append(sentence)

    # save logs
    output_data = open(log_file, 'w')
    for sentence in logs:
        output_data.write(sentence)
        output_data.write("-"*45)
    output_data.close()



def run(doc_list:list, result:str, logs:str):
    """ Main function, scan documents in doc list, write results in result file """

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
    doc_to_sentence_to_infos = {}
    for doc in doc_list:
        doc_to_sentence_to_infos[doc] = {}
        with open(doc) as f: s = f.read()
        text_list = extract_text(s)
        for text in text_list:
            sentence_list += spot_laterality(text, target_list)
        for sentence in sentence_list:
            infos = appariement(sentence, nlp, target_list)
            doc_to_sentence_to_infos[doc][sentence] = infos
            apparied_data += infos

    # Analyse information
    element_to_changes = extract_changes(apparied_data)
    analysis = display_changes(element_to_changes, doc_to_sentence_to_infos)

    # save
    analysis.to_csv(result, index=False)

    # generate logs
    parse_result(result, element_to_changes, logs)



if __name__ == "__main__":

    text_list = glob.glob('data/scenar1/*.txt')
    run(text_list, "changements.csv", "changements.log")

