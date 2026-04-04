# CreateAssignmentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**topic_id** | **UUID** |  | [optional] 
**title** | **str** |  | [optional] 
**deadline** | **datetime** |  | [optional] 
**difficulty** | **str** |  | [optional] 
**problem** | [**ProblemRequest**](ProblemRequest.md) |  | [optional] 

## Example

```python
from openapi_client.models.create_assignment_request import CreateAssignmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAssignmentRequest from a JSON string
create_assignment_request_instance = CreateAssignmentRequest.from_json(json)
# print the JSON string representation of the object
print(CreateAssignmentRequest.to_json())

# convert the object into a dict
create_assignment_request_dict = create_assignment_request_instance.to_dict()
# create an instance of CreateAssignmentRequest from a dict
create_assignment_request_from_dict = CreateAssignmentRequest.from_dict(create_assignment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


