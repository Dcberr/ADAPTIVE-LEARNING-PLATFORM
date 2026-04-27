# SubmissionRelation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**previous_submission_id** | **str** |  | 
**next_submission_id** | **str** |  | 
**student_id** | **str** |  | [optional] [default to '']
**linked_at** | **str** |  | [optional] [default to '']
**same_exercise** | **bool** |  | [optional] [default to True]
**improvement_ratio** | **float** |  | [optional] [default to 0.0]
**regression_ratio** | **float** |  | [optional] [default to 0.0]

## Example

```python
from code_review_ai_client.models.submission_relation import SubmissionRelation

# TODO update the JSON string below
json = "{}"
# create an instance of SubmissionRelation from a JSON string
submission_relation_instance = SubmissionRelation.from_json(json)
# print the JSON string representation of the object
print(SubmissionRelation.to_json())

# convert the object into a dict
submission_relation_dict = submission_relation_instance.to_dict()
# create an instance of SubmissionRelation from a dict
submission_relation_from_dict = SubmissionRelation.from_dict(submission_relation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


