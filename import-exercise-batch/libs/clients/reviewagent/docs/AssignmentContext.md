# AssignmentContext


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **str** |  | 
**language** | **str** | E.g., C, C++, Python | 

## Example

```python
from reviewagent_client.models.assignment_context import AssignmentContext

# TODO update the JSON string below
json = "{}"
# create an instance of AssignmentContext from a JSON string
assignment_context_instance = AssignmentContext.from_json(json)
# print the JSON string representation of the object
print(AssignmentContext.to_json())

# convert the object into a dict
assignment_context_dict = assignment_context_instance.to_dict()
# create an instance of AssignmentContext from a dict
assignment_context_from_dict = AssignmentContext.from_dict(assignment_context_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


