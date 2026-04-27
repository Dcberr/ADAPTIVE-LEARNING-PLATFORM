# ApiResponseUserResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | [**UserResponse**](UserResponse.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from code_review_api_client.models.api_response_user_response import ApiResponseUserResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseUserResponse from a JSON string
api_response_user_response_instance = ApiResponseUserResponse.from_json(json)
# print the JSON string representation of the object
print(ApiResponseUserResponse.to_json())

# convert the object into a dict
api_response_user_response_dict = api_response_user_response_instance.to_dict()
# create an instance of ApiResponseUserResponse from a dict
api_response_user_response_from_dict = ApiResponseUserResponse.from_dict(api_response_user_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


