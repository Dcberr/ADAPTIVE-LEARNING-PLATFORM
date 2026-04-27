# ScoreCard


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**problem_solving_creativity** | [**ScoreCardItem**](ScoreCardItem.md) |  | 
**logic_traceability** | [**ScoreCardItem**](ScoreCardItem.md) |  | 
**generalization_score** | [**ScoreCardItem**](ScoreCardItem.md) |  | 
**construct_appropriateness** | [**ScoreCardItem**](ScoreCardItem.md) |  | 
**self_correction_path** | [**ScoreCardItem**](ScoreCardItem.md) |  | 
**variable_understanding** | [**ScoreCardItem**](ScoreCardItem.md) |  | 
**control_flow_understanding** | [**ScoreCardItem**](ScoreCardItem.md) |  | 
**input_output_awareness** | [**ScoreCardItem**](ScoreCardItem.md) |  | 
**edge_case_awareness** | [**ScoreCardItem**](ScoreCardItem.md) |  | 
**debugging_readiness** | [**ScoreCardItem**](ScoreCardItem.md) |  | 

## Example

```python
from code_review_ai_client.models.score_card import ScoreCard

# TODO update the JSON string below
json = "{}"
# create an instance of ScoreCard from a JSON string
score_card_instance = ScoreCard.from_json(json)
# print the JSON string representation of the object
print(ScoreCard.to_json())

# convert the object into a dict
score_card_dict = score_card_instance.to_dict()
# create an instance of ScoreCard from a dict
score_card_from_dict = ScoreCard.from_dict(score_card_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


