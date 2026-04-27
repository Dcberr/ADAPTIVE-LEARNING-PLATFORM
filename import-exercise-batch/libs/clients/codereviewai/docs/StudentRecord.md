# StudentRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**student_id** | **str** |  | 
**current_concept** | **str** |  | [optional] [default to '']
**notes** | **str** |  | [optional] [default to '']

## Example

```python
from code_review_ai_client.models.student_record import StudentRecord

# TODO update the JSON string below
json = "{}"
# create an instance of StudentRecord from a JSON string
student_record_instance = StudentRecord.from_json(json)
# print the JSON string representation of the object
print(StudentRecord.to_json())

# convert the object into a dict
student_record_dict = student_record_instance.to_dict()
# create an instance of StudentRecord from a dict
student_record_from_dict = StudentRecord.from_dict(student_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


