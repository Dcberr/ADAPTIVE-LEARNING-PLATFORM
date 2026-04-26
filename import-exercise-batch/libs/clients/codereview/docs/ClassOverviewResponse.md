# ClassOverviewResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**name** | **str** |  | [optional] 
**instructor_name** | **str** |  | [optional] 
**enrolled_students_count** | **int** |  | [optional] 
**status** | **str** |  | [optional] 
**image_url** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.class_overview_response import ClassOverviewResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ClassOverviewResponse from a JSON string
class_overview_response_instance = ClassOverviewResponse.from_json(json)
# print the JSON string representation of the object
print(ClassOverviewResponse.to_json())

# convert the object into a dict
class_overview_response_dict = class_overview_response_instance.to_dict()
# create an instance of ClassOverviewResponse from a dict
class_overview_response_from_dict = ClassOverviewResponse.from_dict(class_overview_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


