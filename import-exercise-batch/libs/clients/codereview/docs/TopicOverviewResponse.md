# TopicOverviewResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ids** | **List[UUID]** |  | [optional] 

## Example

```python
from openapi_client.models.topic_overview_response import TopicOverviewResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TopicOverviewResponse from a JSON string
topic_overview_response_instance = TopicOverviewResponse.from_json(json)
# print the JSON string representation of the object
print(TopicOverviewResponse.to_json())

# convert the object into a dict
topic_overview_response_dict = topic_overview_response_instance.to_dict()
# create an instance of TopicOverviewResponse from a dict
topic_overview_response_from_dict = TopicOverviewResponse.from_dict(topic_overview_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


