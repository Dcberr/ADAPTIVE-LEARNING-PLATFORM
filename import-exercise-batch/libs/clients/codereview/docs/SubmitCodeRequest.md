# SubmitCodeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**problem_id** | **UUID** |  | [optional] 
**language** | **str** |  | [optional] 
**code** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.submit_code_request import SubmitCodeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SubmitCodeRequest from a JSON string
submit_code_request_instance = SubmitCodeRequest.from_json(json)
# print the JSON string representation of the object
print(SubmitCodeRequest.to_json())

# convert the object into a dict
submit_code_request_dict = submit_code_request_instance.to_dict()
# create an instance of SubmitCodeRequest from a dict
submit_code_request_from_dict = SubmitCodeRequest.from_dict(submit_code_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


