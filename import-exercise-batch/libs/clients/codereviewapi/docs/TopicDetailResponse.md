# TopicDetailResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**assignments** | [**List[AssignmentResponse]**](AssignmentResponse.md) |  | [optional] 
**documents** | [**List[DocumentResponse]**](DocumentResponse.md) |  | [optional] 

## Example

```python
from code_review_api_client.models.topic_detail_response import TopicDetailResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TopicDetailResponse from a JSON string
topic_detail_response_instance = TopicDetailResponse.from_json(json)
# print the JSON string representation of the object
print(TopicDetailResponse.to_json())

# convert the object into a dict
topic_detail_response_dict = topic_detail_response_instance.to_dict()
# create an instance of TopicDetailResponse from a dict
topic_detail_response_from_dict = TopicDetailResponse.from_dict(topic_detail_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


