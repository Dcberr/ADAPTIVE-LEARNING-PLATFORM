# ProblemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**testcases** | [**List[TestcaseRequest]**](TestcaseRequest.md) |  | [optional] 

## Example

```python
from code_review_api_client.models.problem_request import ProblemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProblemRequest from a JSON string
problem_request_instance = ProblemRequest.from_json(json)
# print the JSON string representation of the object
print(ProblemRequest.to_json())

# convert the object into a dict
problem_request_dict = problem_request_instance.to_dict()
# create an instance of ProblemRequest from a dict
problem_request_from_dict = ProblemRequest.from_dict(problem_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


