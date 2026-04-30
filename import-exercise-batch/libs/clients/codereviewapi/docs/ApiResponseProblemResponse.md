# ApiResponseProblemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] 
**message** | **str** |  | [optional] 
**data** | [**ProblemResponse**](ProblemResponse.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 

## Example

```python
from code_review_api_client.models.api_response_problem_response import ApiResponseProblemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiResponseProblemResponse from a JSON string
api_response_problem_response_instance = ApiResponseProblemResponse.from_json(json)
# print the JSON string representation of the object
print(ApiResponseProblemResponse.to_json())

# convert the object into a dict
api_response_problem_response_dict = api_response_problem_response_instance.to_dict()
# create an instance of ApiResponseProblemResponse from a dict
api_response_problem_response_from_dict = ApiResponseProblemResponse.from_dict(api_response_problem_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


