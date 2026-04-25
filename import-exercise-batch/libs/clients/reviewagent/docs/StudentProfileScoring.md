# StudentProfileScoring


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**concept_mastery** | **float** |  | 
**implementation_consistency** | **float** |  | 
**debugging_independence** | **float** |  | 
**efficiency_awareness** | **float** |  | 
**concept_transfer** | **float** |  | 
**learning_velocity** | **float** |  | 
**notes** | **str** |  | [optional] [default to '']

## Example

```python
from reviewagent_client.models.student_profile_scoring import StudentProfileScoring

# TODO update the JSON string below
json = "{}"
# create an instance of StudentProfileScoring from a JSON string
student_profile_scoring_instance = StudentProfileScoring.from_json(json)
# print the JSON string representation of the object
print(StudentProfileScoring.to_json())

# convert the object into a dict
student_profile_scoring_dict = student_profile_scoring_instance.to_dict()
# create an instance of StudentProfileScoring from a dict
student_profile_scoring_from_dict = StudentProfileScoring.from_dict(student_profile_scoring_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


