# openapi_client.AssignmentApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_assignment**](AssignmentApi.md#create_assignment) | **POST** /assignments | Create new assignment
[**get_assignments**](AssignmentApi.md#get_assignments) | **GET** /assignments/topic/{topicId} | Get assignments by topicId


# **create_assignment**
> ApiResponseAssignmentResponse create_assignment(create_assignment_request)

Create new assignment

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_assignment_response import ApiResponseAssignmentResponse
from openapi_client.models.create_assignment_request import CreateAssignmentRequest
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
    api_instance = openapi_client.AssignmentApi(api_client)
    create_assignment_request = openapi_client.CreateAssignmentRequest() # CreateAssignmentRequest | 

    try:
        # Create new assignment
        api_response = api_instance.create_assignment(create_assignment_request)
        print("The response of AssignmentApi->create_assignment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssignmentApi->create_assignment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_assignment_request** | [**CreateAssignmentRequest**](CreateAssignmentRequest.md)|  | 

### Return type

[**ApiResponseAssignmentResponse**](ApiResponseAssignmentResponse.md)

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

# **get_assignments**
> ApiResponseListAssignmentResponse get_assignments(topic_id)

Get assignments by topicId

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_list_assignment_response import ApiResponseListAssignmentResponse
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
    api_instance = openapi_client.AssignmentApi(api_client)
    topic_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | 

    try:
        # Get assignments by topicId
        api_response = api_instance.get_assignments(topic_id)
        print("The response of AssignmentApi->get_assignments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssignmentApi->get_assignments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **topic_id** | **UUID**|  | 

### Return type

[**ApiResponseListAssignmentResponse**](ApiResponseListAssignmentResponse.md)

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

