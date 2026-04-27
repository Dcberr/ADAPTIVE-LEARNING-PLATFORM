# ClassDetailResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**instructor_name** | **str** |  | [optional] 
**enrolled_students_count** | **int** |  | [optional] 
**created_at** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**schedule** | **str** |  | [optional] 
**image_url** | **str** |  | [optional] 

## Example

```python
from code_review_api_client.models.class_detail_response import ClassDetailResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ClassDetailResponse from a JSON string
class_detail_response_instance = ClassDetailResponse.from_json(json)
# print the JSON string representation of the object
print(ClassDetailResponse.to_json())

# convert the object into a dict
class_detail_response_dict = class_detail_response_instance.to_dict()
# create an instance of ClassDetailResponse from a dict
class_detail_response_from_dict = ClassDetailResponse.from_dict(class_detail_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


