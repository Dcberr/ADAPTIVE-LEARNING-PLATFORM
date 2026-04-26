# ReviewLink


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**previous_submission_id** | **str** |  | 
**previous_code_snippets** | **List[str]** |  | [optional] 
**comparison_mode** | **str** |  | [optional] 
**what_improved** | **str** |  | 
**what_still_needs_work** | **str** |  | 
**relation_summary** | **str** |  | 

## Example

```python
from reviewagent_client.models.review_link import ReviewLink

# TODO update the JSON string below
json = "{}"
# create an instance of ReviewLink from a JSON string
review_link_instance = ReviewLink.from_json(json)
# print the JSON string representation of the object
print(ReviewLink.to_json())

# convert the object into a dict
review_link_dict = review_link_instance.to_dict()
# create an instance of ReviewLink from a dict
review_link_from_dict = ReviewLink.from_dict(review_link_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


