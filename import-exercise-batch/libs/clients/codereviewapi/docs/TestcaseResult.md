# TestcaseResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **int** |  | [optional] 
**input** | **str** |  | [optional] 
**expected_output** | **str** |  | [optional] 
**output** | **str** |  | [optional] 
**error** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**runtime** | **int** |  | [optional] 

## Example

```python
from code_review_api_client.models.testcase_result import TestcaseResult

# TODO update the JSON string below
json = "{}"
# create an instance of TestcaseResult from a JSON string
testcase_result_instance = TestcaseResult.from_json(json)
# print the JSON string representation of the object
print(TestcaseResult.to_json())

# convert the object into a dict
testcase_result_dict = testcase_result_instance.to_dict()
# create an instance of TestcaseResult from a dict
testcase_result_from_dict = TestcaseResult.from_dict(testcase_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


