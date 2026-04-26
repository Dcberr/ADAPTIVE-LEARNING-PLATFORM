# ReviewRelation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**previous_review_id** | **str** |  | 
**next_review_id** | **str** |  | 
**student_id** | **str** |  | [optional] [default to '']
**linked_at** | **str** |  | [optional] [default to '']
**same_concept** | **bool** |  | [optional] [default to False]
**improvement_signal** | **float** |  | [optional] [default to 0.0]
**severity_change** | **float** |  | [optional] [default to 0.0]

## Example

```python
from reviewagent_client.models.review_relation import ReviewRelation

# TODO update the JSON string below
json = "{}"
# create an instance of ReviewRelation from a JSON string
review_relation_instance = ReviewRelation.from_json(json)
# print the JSON string representation of the object
print(ReviewRelation.to_json())

# convert the object into a dict
review_relation_dict = review_relation_instance.to_dict()
# create an instance of ReviewRelation from a dict
review_relation_from_dict = ReviewRelation.from_dict(review_relation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


