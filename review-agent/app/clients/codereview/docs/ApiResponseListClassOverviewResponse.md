# ApiResponseListClassOverviewResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | [**List[ClassOverviewResponse]**](ClassOverviewResponse.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from openapi_client.models.api_response_list_class_overview_response import ApiResponseListClassOverviewResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseListClassOverviewResponse from a JSON string
api_response_list_class_overview_response_instance = ApiResponseListClassOverviewResponse.from_json(json)
# print the JSON string representation of the object
print(ApiResponseListClassOverviewResponse.to_json())

# convert the object into a dict
api_response_list_class_overview_response_dict = api_response_list_class_overview_response_instance.to_dict()
# create an instance of ApiResponseListClassOverviewResponse from a dict
api_response_list_class_overview_response_from_dict = ApiResponseListClassOverviewResponse.from_dict(api_response_list_class_overview_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


