# ReviewItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**line** | [**LineContext**](LineContext.md) |  | [optional] 
**column** | [**ColumnContext**](ColumnContext.md) |  | [optional] 
**code_snippet** | **str** |  | 
**type** | **str** |  | 
**issue** | **str** | For a &#39;Warning&#39;, this should explain a clean-code, readability, or refactoring improvement in simple terms. | 
**fix_suggestion** | **str** |  | 
**review_link** | [**ReviewLink**](ReviewLink.md) |  | [optional] 

## Example

```python
from code_review_ai_client.models.review_item import ReviewItem

# TODO update the JSON string below
json = "{}"
# create an instance of ReviewItem from a JSON string
review_item_instance = ReviewItem.from_json(json)
# print the JSON string representation of the object
print(ReviewItem.to_json())

# convert the object into a dict
review_item_dict = review_item_instance.to_dict()
# create an instance of ReviewItem from a dict
review_item_from_dict = ReviewItem.from_dict(review_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


