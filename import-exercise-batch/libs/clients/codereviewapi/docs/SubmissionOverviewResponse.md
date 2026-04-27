# SubmissionOverviewResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**submission_id** | **UUID** |  | [optional] 
**assignment_title** | **str** |  | [optional] 
**problem_title** | **str** |  | [optional] 
**score** | **str** |  | [optional] 
**difficulty** | **str** |  | [optional] 
**deadline** | **datetime** |  | [optional] 
**status** | **str** |  | [optional] 
**submitted_at** | **datetime** |  | [optional] 
**student_name** | **str** |  | [optional] 

## Example

```python
from code_review_api_client.models.submission_overview_response import SubmissionOverviewResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SubmissionOverviewResponse from a JSON string
submission_overview_response_instance = SubmissionOverviewResponse.from_json(json)
# print the JSON string representation of the object
print(SubmissionOverviewResponse.to_json())

# convert the object into a dict
submission_overview_response_dict = submission_overview_response_instance.to_dict()
# create an instance of SubmissionOverviewResponse from a dict
submission_overview_response_from_dict = SubmissionOverviewResponse.from_dict(submission_overview_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


