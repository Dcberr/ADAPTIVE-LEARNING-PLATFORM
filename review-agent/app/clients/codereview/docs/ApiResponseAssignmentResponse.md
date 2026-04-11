# ApiResponseAssignmentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | [**AssignmentResponse**](AssignmentResponse.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from openapi_client.models.api_response_assignment_response import ApiResponseAssignmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseAssignmentResponse from a JSON string
api_response_assignment_response_instance = ApiResponseAssignmentResponse.from_json(json)
# print the JSON string representation of the object
print(ApiResponseAssignmentResponse.to_json())

# convert the object into a dict
api_response_assignment_response_dict = api_response_assignment_response_instance.to_dict()
# create an instance of ApiResponseAssignmentResponse from a dict
api_response_assignment_response_from_dict = ApiResponseAssignmentResponse.from_dict(api_response_assignment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


