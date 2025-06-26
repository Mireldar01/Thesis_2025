import ontoaligner
import json
import os

from ontoaligner import ontology, encoder
from ontoaligner.aligner import SimpleFuzzySMLightweight
from ontoaligner.utils import metrics, xmlify
from abc import ABC
from typing import Any, Dict
from ontoaligner.base.ontology import BaseAlignmentsParser

class OMDataset(ABC):
    track: str = "dataset-track"
    ontology_name: str = "Clariah-ToolsAndCode-Lib"

    source_ontology: Any = "clariah-tools.ttl"
    target_ontology: Any = "code-lib.ttl"

    alignments: Any = BaseAlignmentsParser()

    def collect(self, source_ontology_path: str, target_ontology_path: str) -> Dict:
        data = {
            "dataset-info": {"track": self.track, "ontology-name": self.ontology_name},
            "source": self.source_ontology.parse(input_file_path=source_ontology_path),
            "target": self.target_ontology.parse(input_file_path=target_ontology_path),
        }
        return data
    # def load_from_json(self, json_file_path: str) -> Dict:
        
    #     with open(json_file_path, encoding="utf-8") as f:
    #         json_data = json.load(f)
    #     return json_data

    def __dir__(self):
        
        return os.path.join(self.track, self.ontology_name)

    def __str__(self):
        
        return f"{self.ontology_name}"


from ontoaligner.ontology import GenericOMDataset
task = GenericOMDataset()
task.track = "Test-track"
task.ontology_name = "clariah(tools)-code(lib)"
dataset = task.parse(source_onotology_path = "clariah-tools.ttl", target_ontology_path = "code-lib.ttl")

# task = ontology.MaterialInformationMatOntoOMDataset()
# print("Test Task:", task)

# dataset = task.collect(
#     source_ontology_path="D:/uni/Thesis/ontology_and_schema_alignment_experiments/clariah-tools.ttl",
#     target_ontology_path="D:/uni/Thesis/ontology_and_schema_alignment_experiments/code-lib.rdf",
#     ##reference_matching_path="../assets/MI-MatOnto/matchings.xml"
# )

encoder_model = encoder.ConceptParentLightweightEncoder()
encoder_output = encoder_model(
        source=dataset['source'],
        target=dataset['target']
)

model = SimpleFuzzySMLightweight(fuzzy_sm_threshold=0.2)
matchings = model.generate(input_data=encoder_output)

evaluation = metrics.evaluation_report(
    predicts=matchings,
    references=dataset['reference']
)
print("Evaluation Report:", json.dumps(evaluation, indent=4))

xml_str = xmlify.xml_alignment_generator(matchings=matchings)
with open("matchings.xml", "w", encoding="utf-8") as xml_file:
    xml_file.write(xml_str)

