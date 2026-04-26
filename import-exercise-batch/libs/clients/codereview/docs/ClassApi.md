# openapi_client.ClassApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_student**](ClassApi.md#add_student) | **POST** /classes/{classId}/students | Add student to class
[**class_detail**](ClassApi.md#class_detail) | **GET** /classes/{classId} | Get class detail
[**create_class**](ClassApi.md#create_class) | **POST** /classes | Create a new class
[**my_classes**](ClassApi.md#my_classes) | **GET** /classes/me | Get classes of current user
[**remove_student**](ClassApi.md#remove_student) | **DELETE** /classes/{classId}/students/{studentId} | Remove student from class


# **add_student**
> ApiResponseObject add_student(class_id, add_student_request)

Add student to class

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.add_student_request import AddStudentRequest
from openapi_client.models.api_response_object import ApiResponseObject
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
    api_instance = openapi_client.ClassApi(api_client)
    class_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | Class ID
    add_student_request = openapi_client.AddStudentRequest() # AddStudentRequest | 

    try:
        # Add student to class
        api_response = api_instance.add_student(class_id, add_student_request)
        print("The response of ClassApi->add_student:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClassApi->add_student: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **class_id** | **UUID**| Class ID | 
 **add_student_request** | [**AddStudentRequest**](AddStudentRequest.md)|  | 

### Return type

[**ApiResponseObject**](ApiResponseObject.md)

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

# **class_detail**
> ApiResponseClassDetailResponse class_detail(class_id)

Get class detail

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_class_detail_response import ApiResponseClassDetailResponse
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
    api_instance = openapi_client.ClassApi(api_client)
    class_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | 

    try:
        # Get class detail
        api_response = api_instance.class_detail(class_id)
        print("The response of ClassApi->class_detail:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClassApi->class_detail: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **class_id** | **UUID**|  | 

### Return type

[**ApiResponseClassDetailResponse**](ApiResponseClassDetailResponse.md)

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

# **create_class**
> ApiResponseClassResponse create_class(request)

Create a new class

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_class_response import ApiResponseClassResponse
from openapi_client.models.create_class_request import CreateClassRequest
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
    api_instance = openapi_client.ClassApi(api_client)
    request = openapi_client.CreateClassRequest() # CreateClassRequest | 

    try:
        # Create a new class
        api_response = api_instance.create_class(request)
        print("The response of ClassApi->create_class:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClassApi->create_class: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**CreateClassRequest**](.md)|  | 

### Return type

[**ApiResponseClassResponse**](ApiResponseClassResponse.md)

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

# **my_classes**
> ApiResponseListClassOverviewResponse my_classes()

Get classes of current user

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_list_class_overview_response import ApiResponseListClassOverviewResponse
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
    api_instance = openapi_client.ClassApi(api_client)

    try:
        # Get classes of current user
        api_response = api_instance.my_classes()
        print("The response of ClassApi->my_classes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClassApi->my_classes: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ApiResponseListClassOverviewResponse**](ApiResponseListClassOverviewResponse.md)

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

# **remove_student**
> ApiResponseObject remove_student(class_id, student_id)

Remove student from class

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_object import ApiResponseObject
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
    api_instance = openapi_client.ClassApi(api_client)
    class_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | 
    student_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | 

    try:
        # Remove student from class
        api_response = api_instance.remove_student(class_id, student_id)
        print("The response of ClassApi->remove_student:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClassApi->remove_student: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **class_id** | **UUID**|  | 
 **student_id** | **UUID**|  | 

### Return type

[**ApiResponseObject**](ApiResponseObject.md)

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

