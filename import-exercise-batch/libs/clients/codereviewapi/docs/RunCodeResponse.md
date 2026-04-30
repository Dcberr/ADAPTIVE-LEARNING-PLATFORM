# RunCodeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] 
**testcases** | [**List[TestcaseResult]**](TestcaseResult.md) |  | [optional] 
**passed_testcases** | **int** |  | [optional] 
**total_testcases** | **int** |  | [optional] 

## Example

```python
from code_review_api_client.models.run_code_response import RunCodeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RunCodeResponse from a JSON string
run_code_response_instance = RunCodeResponse.from_json(json)
# print the JSON string representation of the object
print(RunCodeResponse.to_json())

# convert the object into a dict
run_code_response_dict = run_code_response_instance.to_dict()
# create an instance of RunCodeResponse from a dict
run_code_response_from_dict = RunCodeResponse.from_dict(run_code_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


