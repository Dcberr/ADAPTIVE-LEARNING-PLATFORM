# SubmissionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**status** | **str** |  | [optional] 
**runtime** | **int** |  | [optional] 
**passed_testcases** | **int** |  | [optional] 
**total_testcases** | **int** |  | [optional] 

## Example

```python
from code_review_api_client.models.submission_response import SubmissionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SubmissionResponse from a JSON string
submission_response_instance = SubmissionResponse.from_json(json)
# print the JSON string representation of the object
print(SubmissionResponse.to_json())

# convert the object into a dict
submission_response_dict = submission_response_instance.to_dict()
# create an instance of SubmissionResponse from a dict
submission_response_from_dict = SubmissionResponse.from_dict(submission_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


