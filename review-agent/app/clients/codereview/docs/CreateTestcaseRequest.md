# CreateTestcaseRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**problem_id** | **UUID** |  | [optional] 
**input** | **str** |  | [optional] 
**expected_output** | **str** |  | [optional] 
**explanation** | **str** |  | [optional] 
**sample** | **bool** |  | [optional] 

## Example

```python
from openapi_client.models.create_testcase_request import CreateTestcaseRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTestcaseRequest from a JSON string
create_testcase_request_instance = CreateTestcaseRequest.from_json(json)
# print the JSON string representation of the object
print(CreateTestcaseRequest.to_json())

# convert the object into a dict
create_testcase_request_dict = create_testcase_request_instance.to_dict()
# create an instance of CreateTestcaseRequest from a dict
create_testcase_request_from_dict = CreateTestcaseRequest.from_dict(create_testcase_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


