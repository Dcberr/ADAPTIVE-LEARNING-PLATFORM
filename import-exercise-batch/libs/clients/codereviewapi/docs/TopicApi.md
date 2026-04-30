# code_review_api_client.TopicApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_topic**](TopicApi.md#create_topic) | **POST** /topics | Create a new topic
[**get_topic_detail**](TopicApi.md#get_topic_detail) | **GET** /topics/{topicId} | Get topic detail (assignments + documents)
[**get_topics_by_class**](TopicApi.md#get_topics_by_class) | **GET** /topics/class/{classId} | Get topics overview by classId


# **create_topic**
> ApiResponseTopicResponse create_topic(create_topic_request)

Create a new topic

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_topic_response import ApiResponseTopicResponse
from code_review_api_client.models.create_topic_request import CreateTopicRequest
from code_review_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_api_client.Configuration(
    host = "http://localhost:8080"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = code_review_api_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with code_review_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_api_client.TopicApi(api_client)
    create_topic_request = code_review_api_client.CreateTopicRequest() # CreateTopicRequest | 

    try:
        # Create a new topic
        api_response = api_instance.create_topic(create_topic_request)
        print("The response of TopicApi->create_topic:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TopicApi->create_topic: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_topic_request** | [**CreateTopicRequest**](CreateTopicRequest.md)|  | 

### Return type

[**ApiResponseTopicResponse**](ApiResponseTopicResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_topic_detail**
> ApiResponseTopicDetailResponse get_topic_detail(topic_id)

Get topic detail (assignments + documents)

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_topic_detail_response import ApiResponseTopicDetailResponse
from code_review_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_api_client.Configuration(
    host = "http://localhost:8080"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = code_review_api_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with code_review_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_api_client.TopicApi(api_client)
    topic_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | Topic ID

    try:
        # Get topic detail (assignments + documents)
        api_response = api_instance.get_topic_detail(topic_id)
        print("The response of TopicApi->get_topic_detail:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TopicApi->get_topic_detail: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **topic_id** | **UUID**| Topic ID | 

### Return type

[**ApiResponseTopicDetailResponse**](ApiResponseTopicDetailResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_topics_by_class**
> ApiResponseTopicOverviewResponse get_topics_by_class(class_id)

Get topics overview by classId

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_topic_overview_response import ApiResponseTopicOverviewResponse
from code_review_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_api_client.Configuration(
    host = "http://localhost:8080"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = code_review_api_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with code_review_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_api_client.TopicApi(api_client)
    class_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | Class ID

    try:
        # Get topics overview by classId
        api_response = api_instance.get_topics_by_class(class_id)
        print("The response of TopicApi->get_topics_by_class:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TopicApi->get_topics_by_class: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **class_id** | **UUID**| Class ID | 

### Return type

[**ApiResponseTopicOverviewResponse**](ApiResponseTopicOverviewResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

