# UpsertReviewRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**submission_id** | **str** |  | 
**summary** | **str** |  | 
**detail** | **str** |  | 
**review_items** | [**List[ReviewItem]**](ReviewItem.md) |  | [optional] 
**scorecard** | [**ScoreCard**](ScoreCard.md) |  | 
**current_concept** | **str** |  | [optional] [default to '']

## Example

```python
from reviewagent_client.models.upsert_review_request import UpsertReviewRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertReviewRequest from a JSON string
upsert_review_request_instance = UpsertReviewRequest.from_json(json)
# print the JSON string representation of the object
print(UpsertReviewRequest.to_json())

# convert the object into a dict
upsert_review_request_dict = upsert_review_request_instance.to_dict()
# create an instance of UpsertReviewRequest from a dict
upsert_review_request_from_dict = UpsertReviewRequest.from_dict(upsert_review_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


