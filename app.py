from flask import Flask, request, jsonify
import spacy
from spacy.matcher import PhraseMatcher
from spacy.language import Language
import re
from fuzzywuzzy import fuzz
from flowchart_mapping import FLOWCHART_MAPPING, MINI_FLOWCHART_MAPPING
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)

# Load the spaCy model
nlp = spacy.load('es_core_news_md')

# Use the same model for embeddings
embedding_model = spacy.load('es_core_news_md')

# Define the phrases you want to match as a whole
PHRASES = ["blindaje total", "llamada directa", "alguien real","75 caracteres","excede"]

# Initialize the PhraseMatcher with the shared vocabulary
phrase_matcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(text) for text in PHRASES]
phrase_matcher.add("PHRASE_MATCHER", patterns)

# Define custom component
@Language.component("phrase_matcher_component")
def phrase_matcher_component(doc):
    matches = phrase_matcher(doc)
    spans = [doc[start:end] for _, start, end in matches]
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)
    return doc

# Add the custom component to the pipeline
nlp.add_pipe("phrase_matcher_component", last=True)

CANCEL_KEYWORDS = [
    "retroceder", "volver", "cancelar", "reiniciar", "retroceder"
]

HUMAN_KEYWORDS = [
    "llamada directa", "hablar con alguien", "hablar con un humano", "ayuda humana",
    "quiero hablar con alguien", "asistencia humana",
    "necesito hablar con una persona", "atención humana", "soporte humano", "persona real", "humano real", "persona de verdad", "humano de verdad"
]


LAST_STEPS = ["VR", "IF", "VM", "BT", "OP", "PF", "EPZ", "EPF", "SBSPy", "CS", "GMS", "HP"]

EXCEPTION_WORDS = ["persona", "humano"]

# Depth weight factor (can be adjusted)
DEPTH_WEIGHT = 1

def get_embedding(text):
    return embedding_model(text).vector

def detect_cancel_intent(message):
    doc = nlp(message)
    extracted_keywords = [ent.text.lower() for ent in doc.ents]
    extracted_keywords += [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
    
    message_embedding = get_embedding(message)
    cancel_embeddings = [get_embedding(keyword) for keyword in CANCEL_KEYWORDS]
    
    for cancel_embedding in cancel_embeddings:
        if cosine_similarity([message_embedding], [cancel_embedding])[0][0] > 0.85:
            return True

    for keyword in CANCEL_KEYWORDS:
        if any(fuzz.partial_ratio(keyword.lower(), ek) >= 90 for ek in extracted_keywords):
            return True

    return False

def detect_human_intent(message):
    doc = nlp(message)
    message_lower = message.lower()
    
    # Check for exact phrase matches
    for phrase in HUMAN_KEYWORDS:
        if phrase in message_lower:
            return "human"

    # Extract keywords and embeddings
    extracted_keywords = [ent.text.lower() for ent in doc.ents]
    extracted_keywords += [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]

    # Check exception words
    for word in EXCEPTION_WORDS:
        if word in extracted_keywords:
            return "not human"
    
    message_embedding = get_embedding(message)
    human_embeddings = [get_embedding(keyword) for keyword in HUMAN_KEYWORDS]

    for human_embedding in human_embeddings:
        if cosine_similarity([message_embedding], [human_embedding])[0][0] > 0.9:
            return "human"

    for keyword in HUMAN_KEYWORDS:
        if any(fuzz.partial_ratio(keyword.lower(), ek) >= 90 for ek in extracted_keywords):
            return "human"

    return "not human"


def match_intents(message, flowchart, base_code=""):
    matches = {}
    doc = nlp(message)
    extracted_keywords = [ent.text.lower() for ent in doc.ents]
    extracted_keywords += [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]

    def recurse(node, code_prefix, depth):
        for key, details in node.items():
            new_code = f"{code_prefix}.{key}" if code_prefix else key
            match_count = 0
            for keyword in details.get('keywords', []):
                match_count += sum(fuzz.partial_ratio(keyword.lower(), ek) >= 88 for ek in extracted_keywords)
            if match_count > 0:
                weighted_score = match_count + (depth * DEPTH_WEIGHT) 
                matches[new_code] = max(matches.get(new_code, 0), weighted_score)
            if 'children' in details:
                recurse(details['children'], new_code, depth + 1)
    
    recurse(flowchart, base_code, 0)

    # Find the highest score
    if matches:
        max_score = max(matches.values())
        best_matches = [code for code, score in matches.items() if score == max_score]
        return best_matches
    return []

@app.route('/process', methods=['POST'])
def process_message():
    data = request.get_json()
    message = data.get('message')
    current_code = data.get('code')

    # Determine if the current step is a last step
    codes = current_code.split('.')
    current_branch = FLOWCHART_MAPPING
    
    # Traverse the current path to the correct branch
    try:
        for code in codes:
            if code in current_branch:
                if 'children' in current_branch[code]:
                    current_branch = current_branch[code]['children']
                else:
                    current_branch = {}
                    break
            else:
                return jsonify({"error": "Invalid path"})
    except KeyError:
        return jsonify({"error": "Invalid path"})

    # If the path is deep, switch to MINI_FLOWCHART_MAPPING
    if current_code.startswith("NA") and len(codes) > 3:
        current_branch = MINI_FLOWCHART_MAPPING
        for code in codes[4:]:  # Start from the 4th level in the mini mapping
            if code in current_branch:
                if 'children' in current_branch[code]:
                    current_branch = current_branch[code]['children']
                else:
                    current_branch = {}
                    break
            else:
                return jsonify({"error": "Invalid path"})

    matches = match_intents(message, current_branch, current_code)
    
    if matches:
        # Prepare response with the best matches
        response_data = {
            'flowSteps': matches
        }
        return jsonify(response_data)

    # Check for cancel intent
    cancel_intent = detect_cancel_intent(message)
    if cancel_intent == "cancel" and "no" not in message.lower():
        return jsonify({"flowSteps": ["NA"]})

    # Check for human intent
    human_intent = detect_human_intent(message)
    if human_intent == "human" and "no" not in message.lower():
        return jsonify({"flowSteps": ["Humano"]})

    return jsonify({"error": "Intent not recognized"})


def detect_cancel_intent(message):
    doc = nlp(message)
    extracted_keywords = [ent.text.lower() for ent in doc.ents]
    extracted_keywords += [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]

    message_embedding = get_embedding(message)
    cancel_embeddings = [get_embedding(keyword) for keyword in CANCEL_KEYWORDS]

    for cancel_embedding in cancel_embeddings:
        if cosine_similarity([message_embedding], [cancel_embedding])[0][0] > 0.85:
            return "cancel"

    for keyword in CANCEL_KEYWORDS:
        if any(fuzz.partial_ratio(keyword.lower(), ek) >= 90 for ek in extracted_keywords):
            return "cancel"

    return "not cancel"


@app.route('/extract_ids', methods=['POST'])
def extract_ids():
    data = request.get_json()
    message = data.get('message')

    user_id_pattern = re.compile(r'\b(?:n|x)\d{6}\b', re.IGNORECASE)
    workplace_id_pattern = re.compile(r'\b(?:GSM_|CC)\d{4}\b', re.IGNORECASE)

    user_id_matches = user_id_pattern.findall(message)
    workplace_id_matches = workplace_id_pattern.findall(message)

    response_data = {
        'user_ids': user_id_matches,
        'workplace_ids': workplace_id_matches
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=3692)
