# SubmissionHistoryItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**submission_id** | **UUID** |  | 
**code** | **str** |  | 
**failed_test_case_ids** | **List[UUID]** | UUIDs of the failed testcases for that submission attempt | [optional] 
**passed_test_case_ids** | **List[UUID]** | UUIDs of the passed testcases for that submission attempt | [optional] 

## Example

```python
from code_review_ai_client.models.submission_history_item import SubmissionHistoryItem

# TODO update the JSON string below
json = "{}"
# create an instance of SubmissionHistoryItem from a JSON string
submission_history_item_instance = SubmissionHistoryItem.from_json(json)
# print the JSON string representation of the object
print(SubmissionHistoryItem.to_json())

# convert the object into a dict
submission_history_item_dict = submission_history_item_instance.to_dict()
# create an instance of SubmissionHistoryItem from a dict
submission_history_item_from_dict = SubmissionHistoryItem.from_dict(submission_history_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


