# TestcaseResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**problem_id** | **UUID** |  | [optional] 
**input** | **str** |  | [optional] 
**expected_output** | **str** |  | [optional] 
**is_hidden** | **bool** |  | [optional] 
**explanation** | **str** |  | [optional] 

## Example

```python
from code_review_api_client.models.testcase_response import TestcaseResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TestcaseResponse from a JSON string
testcase_response_instance = TestcaseResponse.from_json(json)
# print the JSON string representation of the object
print(TestcaseResponse.to_json())

# convert the object into a dict
testcase_response_dict = testcase_response_instance.to_dict()
# create an instance of TestcaseResponse from a dict
testcase_response_from_dict = TestcaseResponse.from_dict(testcase_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


