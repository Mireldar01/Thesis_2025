import rdflib
from rdflib.namespace import RDF, OWL, RDFS
from rdflib import URIRef, Literal
from rapidfuzz import fuzz, process


def extract_entities(graph):
    """Extract classes (rdf:type owl:Class) from graph."""
    entities = set()
    for s, p, o in graph.triples((None, RDF.type, None)):
        entities.add(str(s))
    return entities

def clean_uri(uri):
    """Safely extract the last part after / or # from a URI or Literal."""
    if isinstance(uri, URIRef):
        return str(uri).split("/")[-1].split("#")[-1]
    elif isinstance(uri, Literal):
        return str(uri)
    else:
        return str(uri)

def match_labels(labels1, labels2, threshold=50):
    """Match labels with fuzzy matching above threshold."""
    matches = []
    for label in labels1:
        result = process.extractOne(label, labels2, scorer=fuzz.token_sort_ratio)
        if result is not None:
            match, score, _ = result
            if score >= threshold:
                matches.append((label, match, score))
    return matches

def get_labels(graph, entity):
    """Get all rdfs:labels for an entity. Fallback to URI if no labels."""
    labels = []
    for _, _, label in graph.triples((entity, RDFS.label, None)):
        labels.append(str(label))
    if not labels:
        labels.append(str(entity).split("/")[-1].split("#")[-1])  # fallback to URI part
    return labels

ontology1 = rdflib.Graph()
ontology1.parse("clariah-tools.ttl", format="turtle")

ontology2 = rdflib.Graph()
ontology2.parse("code-lib.ttl", format="turtle")

classes1 = extract_entities(ontology1)
classes2 = extract_entities(ontology2)

labels1 = [clean_uri(c) for c in classes1]
labels2 = [clean_uri(c) for c in classes2]

matches = match_labels(labels1, labels2)

for l1, l2, score in matches:
    print(f"Matched\n" f"{l1} ↔ {l2}\n" f"with score {score}\n")
