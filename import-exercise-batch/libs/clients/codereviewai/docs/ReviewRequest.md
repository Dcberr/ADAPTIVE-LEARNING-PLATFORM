# ReviewRequest

The complete input payload for the code review endpoint.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignment** | [**AssignmentContext**](AssignmentContext.md) |  | 
**code** | **str** |  | 
**test_results** | [**List[TestResult]**](TestResult.md) |  | 
**history** | [**List[SubmissionHistoryItem]**](SubmissionHistoryItem.md) |  | [optional] 

## Example

```python
from code_review_ai_client.models.review_request import ReviewRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ReviewRequest from a JSON string
review_request_instance = ReviewRequest.from_json(json)
# print the JSON string representation of the object
print(ReviewRequest.to_json())

# convert the object into a dict
review_request_dict = review_request_instance.to_dict()
# create an instance of ReviewRequest from a dict
review_request_from_dict = ReviewRequest.from_dict(review_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


