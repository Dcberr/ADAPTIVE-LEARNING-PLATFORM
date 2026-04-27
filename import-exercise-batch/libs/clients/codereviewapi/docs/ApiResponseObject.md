# ApiResponseObject


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | **object** |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from code_review_api_client.models.api_response_object import ApiResponseObject

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseObject from a JSON string
api_response_object_instance = ApiResponseObject.from_json(json)
# print the JSON string representation of the object
print(ApiResponseObject.to_json())

# convert the object into a dict
api_response_object_dict = api_response_object_instance.to_dict()
# create an instance of ApiResponseObject from a dict
api_response_object_from_dict = ApiResponseObject.from_dict(api_response_object_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


