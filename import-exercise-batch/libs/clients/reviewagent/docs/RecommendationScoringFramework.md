# RecommendationScoringFramework


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**risk_level** | **str** |  | 
**readiness_level** | **str** |  | 
**explanation** | **str** |  | 

## Example

```python
from reviewagent_client.models.recommendation_scoring_framework import RecommendationScoringFramework

# TODO update the JSON string below
json = "{}"
# create an instance of RecommendationScoringFramework from a JSON string
recommendation_scoring_framework_instance = RecommendationScoringFramework.from_json(json)
# print the JSON string representation of the object
print(RecommendationScoringFramework.to_json())

# convert the object into a dict
recommendation_scoring_framework_dict = recommendation_scoring_framework_instance.to_dict()
# create an instance of RecommendationScoringFramework from a dict
recommendation_scoring_framework_from_dict = RecommendationScoringFramework.from_dict(recommendation_scoring_framework_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


