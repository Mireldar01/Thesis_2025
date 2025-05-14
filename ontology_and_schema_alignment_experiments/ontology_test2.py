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
    """Get all non-empty rdfs:labels for an entity. Fallback to URI if no labels."""
    labels = []
    for _, _, label in graph.triples((entity, RDFS.label, None)):
        label_str = str(label).strip()
        if label_str:
            labels.append(label_str)
    if not labels:
        uri_part = str(entity).split("/")[-1].split("#")[-1]
        if uri_part:
            labels.append(uri_part)
    return labels

def match_entities_multiple_labels_with_score(entities_labels1, entities_labels2, threshold=50):
    """Match entities using multiple labels and calculate overall matching score."""
    matches = []
    for entity1, labels1 in entities_labels1:
        for entity2, labels2 in entities_labels2:
            strong_label_matches = []
            total_comparisons = len(labels1) * len(labels2)
            matched_count = 0
            for label1 in labels1:
                for label2 in labels2:
                    score = fuzz.token_sort_ratio(label1, label2)
                    if score >= threshold:
                        strong_label_matches.append((label1, label2, score))
                        matched_count += 1
            if strong_label_matches:
                match_quality = matched_count / total_comparisons if total_comparisons > 0 else 0
                matches.append((entity1, entity2, strong_label_matches, match_quality))
    return matches

ontology1 = rdflib.Graph()
ontology1.parse("clariah-tools.ttl", format="turtle")

ontology2 = rdflib.Graph()
ontology2.parse("code-lib.ttl", format="turtle")

entities1 = extract_entities(ontology1)
entities2 = extract_entities(ontology2)

entities_labels1 = [(e, get_labels(ontology1, e)) for e in entities1]
entities_labels2 = [(e, get_labels(ontology2, e)) for e in entities2]

entities_labels1 = [(e, labels) for e, labels in entities_labels1 if labels]
entities_labels2 = [(e, labels) for e, labels in entities_labels2 if labels]

matches = match_entities_multiple_labels_with_score(entities_labels1, entities_labels2)

# print("Classes from Ontology 1:")
# for c in classes1:
#     print(clean_uri(c))

# print("\nClasses from Ontology 2:")
# for c in classes2:
#     print(clean_uri(c))
# Output results
for e1, e2, label_matches, quality in matches:
    print(f"\nMatched Entities:")
    print(f"  Entity1: {e1}")
    print(f"  Entity2: {e2}")
    print(f"  Matching Quality Score: {quality:.2%}")
    print(f"  Matched Labels:")
    for label1, label2, score in label_matches:
        print(f"    {label1} ↔ {label2} (Score: {score})")
