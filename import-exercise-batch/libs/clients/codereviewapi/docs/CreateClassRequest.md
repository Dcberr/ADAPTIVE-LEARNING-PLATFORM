# CreateClassRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**image** | **bytes** |  | [optional] 
**schedule** | **str** |  | [optional] 

## Example

```python
from code_review_api_client.models.create_class_request import CreateClassRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateClassRequest from a JSON string
create_class_request_instance = CreateClassRequest.from_json(json)
# print the JSON string representation of the object
print(CreateClassRequest.to_json())

# convert the object into a dict
create_class_request_dict = create_class_request_instance.to_dict()
# create an instance of CreateClassRequest from a dict
create_class_request_from_dict = CreateClassRequest.from_dict(create_class_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


