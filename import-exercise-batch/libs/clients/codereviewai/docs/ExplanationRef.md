# ExplanationRef


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ref_id** | **str** |  | 
**content** | **str** |  | 
**ref_category** | **str** |  | 

## Example

```python
from code_review_ai_client.models.explanation_ref import ExplanationRef

# TODO update the JSON string below
json = "{}"
# create an instance of ExplanationRef from a JSON string
explanation_ref_instance = ExplanationRef.from_json(json)
# print the JSON string representation of the object
print(ExplanationRef.to_json())

# convert the object into a dict
explanation_ref_dict = explanation_ref_instance.to_dict()
# create an instance of ExplanationRef from a dict
explanation_ref_from_dict = ExplanationRef.from_dict(explanation_ref_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


