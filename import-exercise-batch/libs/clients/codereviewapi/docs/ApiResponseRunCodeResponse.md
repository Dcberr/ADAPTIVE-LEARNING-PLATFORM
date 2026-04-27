# ApiResponseRunCodeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | [**RunCodeResponse**](RunCodeResponse.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from code_review_api_client.models.api_response_run_code_response import ApiResponseRunCodeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseRunCodeResponse from a JSON string
api_response_run_code_response_instance = ApiResponseRunCodeResponse.from_json(json)
# print the JSON string representation of the object
print(ApiResponseRunCodeResponse.to_json())

# convert the object into a dict
api_response_run_code_response_dict = api_response_run_code_response_instance.to_dict()
# create an instance of ApiResponseRunCodeResponse from a dict
api_response_run_code_response_from_dict = ApiResponseRunCodeResponse.from_dict(api_response_run_code_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


