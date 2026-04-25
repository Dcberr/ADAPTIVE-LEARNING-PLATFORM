# SubmissionTestCaseOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**expect** | **str** |  | [optional] [default to '']
**output** | **str** |  | [optional] [default to '']

## Example

```python
from reviewagent_client.models.submission_test_case_output import SubmissionTestCaseOutput

# TODO update the JSON string below
json = "{}"
# create an instance of SubmissionTestCaseOutput from a JSON string
submission_test_case_output_instance = SubmissionTestCaseOutput.from_json(json)
# print the JSON string representation of the object
print(SubmissionTestCaseOutput.to_json())

# convert the object into a dict
submission_test_case_output_dict = submission_test_case_output_instance.to_dict()
# create an instance of SubmissionTestCaseOutput from a dict
submission_test_case_output_from_dict = SubmissionTestCaseOutput.from_dict(submission_test_case_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


