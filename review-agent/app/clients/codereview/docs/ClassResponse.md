# ClassResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**instructor_id** | **UUID** |  | [optional] 
**image_url** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.class_response import ClassResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ClassResponse from a JSON string
class_response_instance = ClassResponse.from_json(json)
# print the JSON string representation of the object
print(ClassResponse.to_json())

# convert the object into a dict
class_response_dict = class_response_instance.to_dict()
# create an instance of ClassResponse from a dict
class_response_from_dict = ClassResponse.from_dict(class_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


