# RunTestcaseRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**problem_id** | **UUID** |  | [optional] 
**language** | **str** |  | [optional] 
**code** | **str** |  | [optional] 

## Example

```python
from code_review_api_client.models.run_testcase_request import RunTestcaseRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RunTestcaseRequest from a JSON string
run_testcase_request_instance = RunTestcaseRequest.from_json(json)
# print the JSON string representation of the object
print(RunTestcaseRequest.to_json())

# convert the object into a dict
run_testcase_request_dict = run_testcase_request_instance.to_dict()
# create an instance of RunTestcaseRequest from a dict
run_testcase_request_from_dict = RunTestcaseRequest.from_dict(run_testcase_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


