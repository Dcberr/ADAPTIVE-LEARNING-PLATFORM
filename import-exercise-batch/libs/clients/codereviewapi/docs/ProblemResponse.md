# ProblemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**external_id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**difficulty** | **str** |  | [optional] 
**problem_constraint** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**function_skeletons** | **Dict[str, str]** |  | [optional] 
**testcases** | [**List[TestcaseResponse]**](TestcaseResponse.md) |  | [optional] 
**similar_question_ids** | **List[str]** |  | [optional] 

## Example

```python
from code_review_api_client.models.problem_response import ProblemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProblemResponse from a JSON string
problem_response_instance = ProblemResponse.from_json(json)
# print the JSON string representation of the object
print(ProblemResponse.to_json())

# convert the object into a dict
problem_response_dict = problem_response_instance.to_dict()
# create an instance of ProblemResponse from a dict
problem_response_from_dict = ProblemResponse.from_dict(problem_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


