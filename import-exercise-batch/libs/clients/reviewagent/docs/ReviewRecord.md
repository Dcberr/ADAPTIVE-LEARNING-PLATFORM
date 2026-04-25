# ReviewRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**review_id** | **str** |  | 
**student_id** | **str** |  | 
**exercise_id** | **str** |  | [optional] [default to '']
**submission_id** | **str** |  | [optional] [default to '']
**current_concept** | **str** |  | [optional] [default to '']
**created_at** | **str** |  | [optional] [default to '']
**summary** | **str** |  | 
**detail** | **str** |  | 

## Example

```python
from reviewagent_client.models.review_record import ReviewRecord

# TODO update the JSON string below
json = "{}"
# create an instance of ReviewRecord from a JSON string
review_record_instance = ReviewRecord.from_json(json)
# print the JSON string representation of the object
print(ReviewRecord.to_json())

# convert the object into a dict
review_record_dict = review_record_instance.to_dict()
# create an instance of ReviewRecord from a dict
review_record_from_dict = ReviewRecord.from_dict(review_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


