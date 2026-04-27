# TestcaseRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**input** | **str** |  | [optional] 
**expected_output** | **str** |  | [optional] 
**explanation** | **str** |  | [optional] 
**sample** | **bool** |  | [optional] 

## Example

```python
from code_review_api_client.models.testcase_request import TestcaseRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestcaseRequest from a JSON string
testcase_request_instance = TestcaseRequest.from_json(json)
# print the JSON string representation of the object
print(TestcaseRequest.to_json())

# convert the object into a dict
testcase_request_dict = testcase_request_instance.to_dict()
# create an instance of TestcaseRequest from a dict
testcase_request_from_dict = TestcaseRequest.from_dict(testcase_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


