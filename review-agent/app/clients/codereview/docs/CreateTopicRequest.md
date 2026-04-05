# CreateTopicRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**class_id** | **UUID** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.create_topic_request import CreateTopicRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTopicRequest from a JSON string
create_topic_request_instance = CreateTopicRequest.from_json(json)
# print the JSON string representation of the object
print(CreateTopicRequest.to_json())

# convert the object into a dict
create_topic_request_dict = create_topic_request_instance.to_dict()
# create an instance of CreateTopicRequest from a dict
create_topic_request_from_dict = CreateTopicRequest.from_dict(create_topic_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


