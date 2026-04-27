# LeetCodeImportRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**external_id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**difficulty** | **str** |  | [optional] 
**constraints** | **str** |  | [optional] 
**starter_codes** | **Dict[str, str]** |  | [optional] 
**testcases** | [**List[TestcaseDto]**](TestcaseDto.md) |  | [optional] 
**similar_question_ids** | **List[str]** |  | [optional] 

## Example

```python
from code_review_api_client.models.leet_code_import_request import LeetCodeImportRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LeetCodeImportRequest from a JSON string
leet_code_import_request_instance = LeetCodeImportRequest.from_json(json)
# print the JSON string representation of the object
print(LeetCodeImportRequest.to_json())

# convert the object into a dict
leet_code_import_request_dict = leet_code_import_request_instance.to_dict()
# create an instance of LeetCodeImportRequest from a dict
leet_code_import_request_from_dict = LeetCodeImportRequest.from_dict(leet_code_import_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


