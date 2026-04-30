# ExerciseConceptLink


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercise_id** | **str** |  | 
**concept_id** | **str** |  | 
**weight** | **float** |  | [optional] [default to 1.0]

## Example

```python
from code_review_ai_client.models.exercise_concept_link import ExerciseConceptLink

# TODO update the JSON string below
json = "{}"
# create an instance of ExerciseConceptLink from a JSON string
exercise_concept_link_instance = ExerciseConceptLink.from_json(json)
# print the JSON string representation of the object
print(ExerciseConceptLink.to_json())

# convert the object into a dict
exercise_concept_link_dict = exercise_concept_link_instance.to_dict()
# create an instance of ExerciseConceptLink from a dict
exercise_concept_link_from_dict = ExerciseConceptLink.from_dict(exercise_concept_link_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


