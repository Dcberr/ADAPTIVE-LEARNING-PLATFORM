# ApiResponseClassDetailResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | [**ClassDetailResponse**](ClassDetailResponse.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from openapi_client.models.api_response_class_detail_response import ApiResponseClassDetailResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseClassDetailResponse from a JSON string
api_response_class_detail_response_instance = ApiResponseClassDetailResponse.from_json(json)
# print the JSON string representation of the object
print(ApiResponseClassDetailResponse.to_json())

# convert the object into a dict
api_response_class_detail_response_dict = api_response_class_detail_response_instance.to_dict()
# create an instance of ApiResponseClassDetailResponse from a dict
api_response_class_detail_response_from_dict = ApiResponseClassDetailResponse.from_dict(api_response_class_detail_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


