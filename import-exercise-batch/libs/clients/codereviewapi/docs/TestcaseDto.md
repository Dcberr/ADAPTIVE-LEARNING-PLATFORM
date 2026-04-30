# TestcaseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**input** | **str** |  | [optional] 
**expected_output** | **str** |  | [optional] 
**is_hidden** | **bool** |  | [optional] 
**explanation** | **str** |  | [optional] 

## Example

```python
from code_review_api_client.models.testcase_dto import TestcaseDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestcaseDto from a JSON string
testcase_dto_instance = TestcaseDto.from_json(json)
# print the JSON string representation of the object
print(TestcaseDto.to_json())

# convert the object into a dict
testcase_dto_dict = testcase_dto_instance.to_dict()
# create an instance of TestcaseDto from a dict
testcase_dto_from_dict = TestcaseDto.from_dict(testcase_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


