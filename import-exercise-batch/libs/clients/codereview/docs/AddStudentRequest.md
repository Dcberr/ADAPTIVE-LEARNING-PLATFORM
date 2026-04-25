# AddStudentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**student_id** | **UUID** |  | [optional] 

## Example

```python
from openapi_client.models.add_student_request import AddStudentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AddStudentRequest from a JSON string
add_student_request_instance = AddStudentRequest.from_json(json)
# print the JSON string representation of the object
print(AddStudentRequest.to_json())

# convert the object into a dict
add_student_request_dict = add_student_request_instance.to_dict()
# create an instance of AddStudentRequest from a dict
add_student_request_from_dict = AddStudentRequest.from_dict(add_student_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


