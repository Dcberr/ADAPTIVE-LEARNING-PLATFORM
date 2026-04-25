# ApiResponseSubmissionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | [**SubmissionResponse**](SubmissionResponse.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from openapi_client.models.api_response_submission_response import ApiResponseSubmissionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseSubmissionResponse from a JSON string
api_response_submission_response_instance = ApiResponseSubmissionResponse.from_json(json)
# print the JSON string representation of the object
print(ApiResponseSubmissionResponse.to_json())

# convert the object into a dict
api_response_submission_response_dict = api_response_submission_response_instance.to_dict()
# create an instance of ApiResponseSubmissionResponse from a dict
api_response_submission_response_from_dict = ApiResponseSubmissionResponse.from_dict(api_response_submission_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


