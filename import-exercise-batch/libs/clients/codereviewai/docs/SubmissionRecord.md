# SubmissionRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**submission_id** | **str** |  | 
**student_id** | **str** |  | 
**exercise_id** | **str** |  | [optional] [default to '']
**code** | **str** |  | 
**testcase_outputs** | [**List[SubmissionTestCaseOutput]**](SubmissionTestCaseOutput.md) |  | [optional] 
**created_at** | **str** |  | [optional] [default to '']

## Example

```python
from code_review_ai_client.models.submission_record import SubmissionRecord

# TODO update the JSON string below
json = "{}"
# create an instance of SubmissionRecord from a JSON string
submission_record_instance = SubmissionRecord.from_json(json)
# print the JSON string representation of the object
print(SubmissionRecord.to_json())

# convert the object into a dict
submission_record_dict = submission_record_instance.to_dict()
# create an instance of SubmissionRecord from a dict
submission_record_from_dict = SubmissionRecord.from_dict(submission_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


