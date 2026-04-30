# ApiResponseListReviewResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | [**List[ReviewResponse]**](ReviewResponse.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from code_review_api_client.models.api_response_list_review_response import ApiResponseListReviewResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseListReviewResponse from a JSON string
api_response_list_review_response_instance = ApiResponseListReviewResponse.from_json(json)
# print the JSON string representation of the object
print(ApiResponseListReviewResponse.to_json())

# convert the object into a dict
api_response_list_review_response_dict = api_response_list_review_response_instance.to_dict()
# create an instance of ApiResponseListReviewResponse from a dict
api_response_list_review_response_from_dict = ApiResponseListReviewResponse.from_dict(api_response_list_review_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


