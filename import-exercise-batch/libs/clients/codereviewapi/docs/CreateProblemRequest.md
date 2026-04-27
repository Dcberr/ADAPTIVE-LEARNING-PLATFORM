# CreateProblemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**assignment_id** | **UUID** |  | [optional] 
**problem_constraint** | **str** |  | [optional] 
**testcases** | [**List[TestcaseRequest]**](TestcaseRequest.md) |  | [optional] 

## Example

```python
from code_review_api_client.models.create_problem_request import CreateProblemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateProblemRequest from a JSON string
create_problem_request_instance = CreateProblemRequest.from_json(json)
# print the JSON string representation of the object
print(CreateProblemRequest.to_json())

# convert the object into a dict
create_problem_request_dict = create_problem_request_instance.to_dict()
# create an instance of CreateProblemRequest from a dict
create_problem_request_from_dict = CreateProblemRequest.from_dict(create_problem_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


