# code_review_api_client.UserApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_user**](UserApi.md#get_user) | **GET** /users/{id} | Get user by ID
[**me**](UserApi.md#me) | **GET** /users/me | Get current user profile
[**update_profile**](UserApi.md#update_profile) | **PUT** /users/me | Update current user profile


# **get_user**
> ApiResponseUserResponse get_user(id)

Get user by ID

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_user_response import ApiResponseUserResponse
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
    api_instance = code_review_api_client.UserApi(api_client)
    id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | User ID

    try:
        # Get user by ID
        api_response = api_instance.get_user(id)
        print("The response of UserApi->get_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->get_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **UUID**| User ID | 

### Return type

[**ApiResponseUserResponse**](ApiResponseUserResponse.md)

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

# **me**
> ApiResponseUserResponse me()

Get current user profile

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_user_response import ApiResponseUserResponse
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
    api_instance = code_review_api_client.UserApi(api_client)

    try:
        # Get current user profile
        api_response = api_instance.me()
        print("The response of UserApi->me:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->me: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ApiResponseUserResponse**](ApiResponseUserResponse.md)

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

# **update_profile**
> ApiResponseUserResponse update_profile(update_user_request)

Update current user profile

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_user_response import ApiResponseUserResponse
from code_review_api_client.models.update_user_request import UpdateUserRequest
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
    api_instance = code_review_api_client.UserApi(api_client)
    update_user_request = code_review_api_client.UpdateUserRequest() # UpdateUserRequest | 

    try:
        # Update current user profile
        api_response = api_instance.update_profile(update_user_request)
        print("The response of UserApi->update_profile:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->update_profile: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **update_user_request** | [**UpdateUserRequest**](UpdateUserRequest.md)|  | 

### Return type

[**ApiResponseUserResponse**](ApiResponseUserResponse.md)

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

