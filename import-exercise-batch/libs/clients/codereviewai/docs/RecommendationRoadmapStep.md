# RecommendationRoadmapStep


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**step** | **int** |  | 
**exercise** | [**RecommendationExercise**](RecommendationExercise.md) |  | 

## Example

```python
from code_review_ai_client.models.recommendation_roadmap_step import RecommendationRoadmapStep

# TODO update the JSON string below
json = "{}"
# create an instance of RecommendationRoadmapStep from a JSON string
recommendation_roadmap_step_instance = RecommendationRoadmapStep.from_json(json)
# print the JSON string representation of the object
print(RecommendationRoadmapStep.to_json())

# convert the object into a dict
recommendation_roadmap_step_dict = recommendation_roadmap_step_instance.to_dict()
# create an instance of RecommendationRoadmapStep from a dict
recommendation_roadmap_step_from_dict = RecommendationRoadmapStep.from_dict(recommendation_roadmap_step_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


