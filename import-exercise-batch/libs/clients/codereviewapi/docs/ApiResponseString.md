# ApiResponseString


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | **str** |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from code_review_api_client.models.api_response_string import ApiResponseString

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseString from a JSON string
api_response_string_instance = ApiResponseString.from_json(json)
# print the JSON string representation of the object
print(ApiResponseString.to_json())

# convert the object into a dict
api_response_string_dict = api_response_string_instance.to_dict()
# create an instance of ApiResponseString from a dict
api_response_string_from_dict = ApiResponseString.from_dict(api_response_string_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


