# RecommendationGraphSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**current_concept_weight** | **float** |  | 
**best_path_weight** | **float** |  | 
**best_related_exercise_weight** | **float** |  | 
**latest_review_improvement_signal** | **float** |  | 
**latest_review_severity_change** | **float** |  | 
**latest_submission_improvement_ratio** | **float** |  | 
**latest_submission_regression_ratio** | **float** |  | 

## Example

```python
from code_review_ai_client.models.recommendation_graph_summary import RecommendationGraphSummary

# TODO update the JSON string below
json = "{}"
# create an instance of RecommendationGraphSummary from a JSON string
recommendation_graph_summary_instance = RecommendationGraphSummary.from_json(json)
# print the JSON string representation of the object
print(RecommendationGraphSummary.to_json())

# convert the object into a dict
recommendation_graph_summary_dict = recommendation_graph_summary_instance.to_dict()
# create an instance of RecommendationGraphSummary from a dict
recommendation_graph_summary_from_dict = RecommendationGraphSummary.from_dict(recommendation_graph_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


