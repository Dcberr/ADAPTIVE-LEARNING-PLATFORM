# SubmissionDetailResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**submission_id** | **UUID** |  | [optional] 
**problem_title** | **str** |  | [optional] 
**problem_description** | **str** |  | [optional] 
**score** | **str** |  | [optional] 
**difficulty** | **str** |  | [optional] 
**code** | **str** |  | [optional] 
**language** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**testcases** | [**List[TestcaseResponse]**](TestcaseResponse.md) |  | [optional] 

## Example

```python
from code_review_api_client.models.submission_detail_response import SubmissionDetailResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SubmissionDetailResponse from a JSON string
submission_detail_response_instance = SubmissionDetailResponse.from_json(json)
# print the JSON string representation of the object
print(SubmissionDetailResponse.to_json())

# convert the object into a dict
submission_detail_response_dict = submission_detail_response_instance.to_dict()
# create an instance of SubmissionDetailResponse from a dict
submission_detail_response_from_dict = SubmissionDetailResponse.from_dict(submission_detail_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


