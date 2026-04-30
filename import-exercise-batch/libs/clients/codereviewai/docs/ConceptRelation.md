# ConceptRelation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prerequisite_id** | **str** |  | 
**concept_id** | **str** |  | 
**strength** | **float** |  | [optional] [default to 1.0]

## Example

```python
from code_review_ai_client.models.concept_relation import ConceptRelation

# TODO update the JSON string below
json = "{}"
# create an instance of ConceptRelation from a JSON string
concept_relation_instance = ConceptRelation.from_json(json)
# print the JSON string representation of the object
print(ConceptRelation.to_json())

# convert the object into a dict
concept_relation_dict = concept_relation_instance.to_dict()
# create an instance of ConceptRelation from a dict
concept_relation_from_dict = ConceptRelation.from_dict(concept_relation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


