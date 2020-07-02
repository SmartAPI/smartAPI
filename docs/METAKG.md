##### What is Meta-KG?

The SmartAPI Meta Knowledge Graph (Meta-KG) represents how biomedical concepts can be connected through APIs. Each node in the meta-KG represents a biolink entity type, e.g. Gene, SequenceVariant, ChemicalSubstance. Each edge in the meta-KG represents a unique combination of a biolink predicate, e.g. targets, treats, and an API which delivers the association.

The Meta-KG is constructed using the collection of SmartAPI specifications currently registered in SmartAPI. All APIs registered with x-smartapi field will be integrated into the meta-KG. In addition, all ReasonerStdAPIs registered in SmartAPI and implemented the **/predicate** endpoint will also be integrated.


