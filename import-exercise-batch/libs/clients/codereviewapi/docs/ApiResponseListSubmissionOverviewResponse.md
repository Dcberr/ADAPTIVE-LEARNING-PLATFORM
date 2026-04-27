# ApiResponseListSubmissionOverviewResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | [**List[SubmissionOverviewResponse]**](SubmissionOverviewResponse.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from code_review_api_client.models.api_response_list_submission_overview_response import ApiResponseListSubmissionOverviewResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseListSubmissionOverviewResponse from a JSON string
api_response_list_submission_overview_response_instance = ApiResponseListSubmissionOverviewResponse.from_json(json)
# print the JSON string representation of the object
print(ApiResponseListSubmissionOverviewResponse.to_json())

# convert the object into a dict
api_response_list_submission_overview_response_dict = api_response_list_submission_overview_response_instance.to_dict()
# create an instance of ApiResponseListSubmissionOverviewResponse from a dict
api_response_list_submission_overview_response_from_dict = ApiResponseListSubmissionOverviewResponse.from_dict(api_response_list_submission_overview_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


