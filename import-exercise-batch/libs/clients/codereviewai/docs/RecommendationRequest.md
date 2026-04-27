# RecommendationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**student_id** | **str** |  | 
**exercise_id** | **str** |  | 

## Example

```python
from code_review_ai_client.models.recommendation_request import RecommendationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RecommendationRequest from a JSON string
recommendation_request_instance = RecommendationRequest.from_json(json)
# print the JSON string representation of the object
print(RecommendationRequest.to_json())

# convert the object into a dict
recommendation_request_dict = recommendation_request_instance.to_dict()
# create an instance of RecommendationRequest from a dict
recommendation_request_from_dict = RecommendationRequest.from_dict(recommendation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


