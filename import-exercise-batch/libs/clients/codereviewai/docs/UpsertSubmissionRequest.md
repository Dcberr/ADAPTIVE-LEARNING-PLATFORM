# UpsertSubmissionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**student_id** | **str** |  | 
**exercise_id** | **str** |  | 
**code** | **str** |  | 
**testcase_outputs** | [**List[SubmissionTestCaseOutput]**](SubmissionTestCaseOutput.md) |  | [optional] 

## Example

```python
from code_review_ai_client.models.upsert_submission_request import UpsertSubmissionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertSubmissionRequest from a JSON string
upsert_submission_request_instance = UpsertSubmissionRequest.from_json(json)
# print the JSON string representation of the object
print(UpsertSubmissionRequest.to_json())

# convert the object into a dict
upsert_submission_request_dict = upsert_submission_request_instance.to_dict()
# create an instance of UpsertSubmissionRequest from a dict
upsert_submission_request_from_dict = UpsertSubmissionRequest.from_dict(upsert_submission_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


