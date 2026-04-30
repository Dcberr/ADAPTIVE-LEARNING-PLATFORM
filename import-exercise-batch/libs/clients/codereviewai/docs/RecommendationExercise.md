# RecommendationExercise


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercise_id** | **str** |  | 
**slug** | **str** |  | [optional] [default to '']
**title** | **str** |  | 
**description** | **str** |  | 
**content** | **str** |  | 
**difficulty** | **str** |  | 
**tags** | **List[str]** |  | [optional] 
**concept_ids** | **List[str]** |  | 
**directive** | **str** |  | 

## Example

```python
from code_review_ai_client.models.recommendation_exercise import RecommendationExercise

# TODO update the JSON string below
json = "{}"
# create an instance of RecommendationExercise from a JSON string
recommendation_exercise_instance = RecommendationExercise.from_json(json)
# print the JSON string representation of the object
print(RecommendationExercise.to_json())

# convert the object into a dict
recommendation_exercise_dict = recommendation_exercise_instance.to_dict()
# create an instance of RecommendationExercise from a dict
recommendation_exercise_from_dict = RecommendationExercise.from_dict(recommendation_exercise_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


