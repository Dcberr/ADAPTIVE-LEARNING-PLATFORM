# RunCodeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**language** | **str** |  | [optional] 
**code** | **str** |  | [optional] 
**input** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.run_code_request import RunCodeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RunCodeRequest from a JSON string
run_code_request_instance = RunCodeRequest.from_json(json)
# print the JSON string representation of the object
print(RunCodeRequest.to_json())

# convert the object into a dict
run_code_request_dict = run_code_request_instance.to_dict()
# create an instance of RunCodeRequest from a dict
run_code_request_from_dict = RunCodeRequest.from_dict(run_code_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


