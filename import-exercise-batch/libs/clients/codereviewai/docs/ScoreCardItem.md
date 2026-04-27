# ScoreCardItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**score** | **int** |  | 
**label** | **str** |  | 
**explanation** | **str** |  | 

## Example

```python
from code_review_ai_client.models.score_card_item import ScoreCardItem

# TODO update the JSON string below
json = "{}"
# create an instance of ScoreCardItem from a JSON string
score_card_item_instance = ScoreCardItem.from_json(json)
# print the JSON string representation of the object
print(ScoreCardItem.to_json())

# convert the object into a dict
score_card_item_dict = score_card_item_instance.to_dict()
# create an instance of ScoreCardItem from a dict
score_card_item_from_dict = ScoreCardItem.from_dict(score_card_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


