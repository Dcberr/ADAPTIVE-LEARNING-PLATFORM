# ExercisePathLink


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercise_id** | **str** |  | 
**concept_id** | **str** |  | 
**path** | **str** |  | 
**weight** | **float** |  | [optional] [default to 1.0]

## Example

```python
from reviewagent_client.models.exercise_path_link import ExercisePathLink

# TODO update the JSON string below
json = "{}"
# create an instance of ExercisePathLink from a JSON string
exercise_path_link_instance = ExercisePathLink.from_json(json)
# print the JSON string representation of the object
print(ExercisePathLink.to_json())

# convert the object into a dict
exercise_path_link_dict = exercise_path_link_instance.to_dict()
# create an instance of ExercisePathLink from a dict
exercise_path_link_from_dict = ExercisePathLink.from_dict(exercise_path_link_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


