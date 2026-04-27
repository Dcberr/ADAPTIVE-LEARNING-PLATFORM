# RecommendationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**student_id** | **str** |  | 
**current_exercise_id** | **str** |  | 
**anchor_concept** | **str** |  | 
**assigned_path** | **str** |  | 
**focus_concept_id** | **str** |  | 
**critical_errors** | **int** |  | 
**framework** | [**RecommendationScoringFramework**](RecommendationScoringFramework.md) |  | 
**graph_summary** | [**RecommendationGraphSummary**](RecommendationGraphSummary.md) |  | 
**reasoning** | [**ExplanationBlock**](ExplanationBlock.md) |  | 
**roadmap_summary** | [**ExplanationBlock**](ExplanationBlock.md) |  | 
**roadmap** | [**List[RecommendationRoadmapStep]**](RecommendationRoadmapStep.md) |  | 

## Example

```python
from code_review_ai_client.models.recommendation_response import RecommendationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RecommendationResponse from a JSON string
recommendation_response_instance = RecommendationResponse.from_json(json)
# print the JSON string representation of the object
print(RecommendationResponse.to_json())

# convert the object into a dict
recommendation_response_dict = recommendation_response_instance.to_dict()
# create an instance of RecommendationResponse from a dict
recommendation_response_from_dict = RecommendationResponse.from_dict(recommendation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


