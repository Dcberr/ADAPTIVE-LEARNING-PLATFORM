# ExerciseRelation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercise_id** | **str** |  | 
**related_exercise_id** | **str** |  | 
**weight** | **float** |  | [optional] [default to 1.0]
**relation_type** | **str** |  | [optional] [default to '']
**target_concept_id** | **str** |  | [optional] [default to '']
**shared_concept_ids** | **List[str]** |  | [optional] 
**difficulty_gap** | **float** |  | [optional] [default to 0.0]
**progression_score** | **float** |  | [optional] [default to 0.0]
**similarity_score** | **float** |  | [optional] [default to 0.0]

## Example

```python
from reviewagent_client.models.exercise_relation import ExerciseRelation

# TODO update the JSON string below
json = "{}"
# create an instance of ExerciseRelation from a JSON string
exercise_relation_instance = ExerciseRelation.from_json(json)
# print the JSON string representation of the object
print(ExerciseRelation.to_json())

# convert the object into a dict
exercise_relation_dict = exercise_relation_instance.to_dict()
# create an instance of ExerciseRelation from a dict
exercise_relation_from_dict = ExerciseRelation.from_dict(exercise_relation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


