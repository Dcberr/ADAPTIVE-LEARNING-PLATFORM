# openapi_client.DocumentApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](DocumentApi.md#create) | **POST** /documents | Upload document (PDF, video, etc.)
[**download**](DocumentApi.md#download) | **GET** /documents/download/{id} | Download document (inline preview)
[**get_by_topic**](DocumentApi.md#get_by_topic) | **GET** /documents/topic/{topicId} | Get documents by topic
[**stream**](DocumentApi.md#stream) | **GET** /documents/stream/{id} | Stream video document (supports Range header)


# **create**
> ApiResponseDocumentResponse create(topic_id, title, description, file)

Upload document (PDF, video, etc.)

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_document_response import ApiResponseDocumentResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8080"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DocumentApi(api_client)
    topic_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | Topic ID
    title = 'title_example' # str | 
    description = 'description_example' # str | 
    file = None # bytes | File to upload

    try:
        # Upload document (PDF, video, etc.)
        api_response = api_instance.create(topic_id, title, description, file)
        print("The response of DocumentApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **topic_id** | **UUID**| Topic ID | 
 **title** | **str**|  | 
 **description** | **str**|  | 
 **file** | **bytes**| File to upload | 

### Return type

[**ApiResponseDocumentResponse**](ApiResponseDocumentResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download**
> bytes download(id)

Download document (inline preview)

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8080"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DocumentApi(api_client)
    id = 'id_example' # str | Document ID

    try:
        # Download document (inline preview)
        api_response = api_instance.download(id)
        print("The response of DocumentApi->download:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentApi->download: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Document ID | 

### Return type

**bytes**

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

# **get_by_topic**
> ApiResponseListDocumentResponse get_by_topic(topic_id)

Get documents by topic

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_list_document_response import ApiResponseListDocumentResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8080"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DocumentApi(api_client)
    topic_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | Topic ID

    try:
        # Get documents by topic
        api_response = api_instance.get_by_topic(topic_id)
        print("The response of DocumentApi->get_by_topic:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentApi->get_by_topic: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **topic_id** | **UUID**| Topic ID | 

### Return type

[**ApiResponseListDocumentResponse**](ApiResponseListDocumentResponse.md)

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

# **stream**
> bytes stream(id, range=range)

Stream video document (supports Range header)

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:8080"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DocumentApi(api_client)
    id = 'id_example' # str | Document ID
    range = 'range_example' # str | Range header for streaming (optional)

    try:
        # Stream video document (supports Range header)
        api_response = api_instance.stream(id, range=range)
        print("The response of DocumentApi->stream:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentApi->stream: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Document ID | 
 **range** | **str**| Range header for streaming | [optional] 

### Return type

**bytes**

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

