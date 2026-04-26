# UpsertStudentProfileRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**student_profile** | [**StudentProfileScoring**](StudentProfileScoring.md) |  | 

## Example

```python
from reviewagent_client.models.upsert_student_profile_request import UpsertStudentProfileRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertStudentProfileRequest from a JSON string
upsert_student_profile_request_instance = UpsertStudentProfileRequest.from_json(json)
# print the JSON string representation of the object
print(UpsertStudentProfileRequest.to_json())

# convert the object into a dict
upsert_student_profile_request_dict = upsert_student_profile_request_instance.to_dict()
# create an instance of UpsertStudentProfileRequest from a dict
upsert_student_profile_request_from_dict = UpsertStudentProfileRequest.from_dict(upsert_student_profile_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


