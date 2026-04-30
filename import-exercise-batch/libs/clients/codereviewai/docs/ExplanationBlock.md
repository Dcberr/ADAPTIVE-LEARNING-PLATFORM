# ExplanationBlock


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **str** |  | 
**refs** | [**List[ExplanationRef]**](ExplanationRef.md) |  | 

## Example

```python
from code_review_ai_client.models.explanation_block import ExplanationBlock

# TODO update the JSON string below
json = "{}"
# create an instance of ExplanationBlock from a JSON string
explanation_block_instance = ExplanationBlock.from_json(json)
# print the JSON string representation of the object
print(ExplanationBlock.to_json())

# convert the object into a dict
explanation_block_dict = explanation_block_instance.to_dict()
# create an instance of ExplanationBlock from a dict
explanation_block_from_dict = ExplanationBlock.from_dict(explanation_block_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


