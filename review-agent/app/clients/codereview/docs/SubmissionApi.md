# openapi_client.SubmissionApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**detail**](SubmissionApi.md#detail) | **GET** /submissions/{submissionId} | Get submission detail
[**get_problem_submissions**](SubmissionApi.md#get_problem_submissions) | **GET** /submissions/problem/{problemId} | Get submissions of a problem
[**overview**](SubmissionApi.md#overview) | **GET** /submissions/me | Get current user&#39;s submissions overview
[**submit**](SubmissionApi.md#submit) | **POST** /submissions | Submit code for a problem


# **detail**
> ApiResponseSubmissionDetailResponse detail(submission_id)

Get submission detail

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_submission_detail_response import ApiResponseSubmissionDetailResponse
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
    api_instance = openapi_client.SubmissionApi(api_client)
    submission_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | Submission ID

    try:
        # Get submission detail
        api_response = api_instance.detail(submission_id)
        print("The response of SubmissionApi->detail:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SubmissionApi->detail: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submission_id** | **UUID**| Submission ID | 

### Return type

[**ApiResponseSubmissionDetailResponse**](ApiResponseSubmissionDetailResponse.md)

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

# **get_problem_submissions**
> ApiResponseListSubmissionOverviewResponse get_problem_submissions(problem_id)

Get submissions of a problem

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_list_submission_overview_response import ApiResponseListSubmissionOverviewResponse
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
    api_instance = openapi_client.SubmissionApi(api_client)
    problem_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | Problem ID

    try:
        # Get submissions of a problem
        api_response = api_instance.get_problem_submissions(problem_id)
        print("The response of SubmissionApi->get_problem_submissions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SubmissionApi->get_problem_submissions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **problem_id** | **UUID**| Problem ID | 

### Return type

[**ApiResponseListSubmissionOverviewResponse**](ApiResponseListSubmissionOverviewResponse.md)

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

# **overview**
> ApiResponseListSubmissionOverviewResponse overview()

Get current user's submissions overview

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_list_submission_overview_response import ApiResponseListSubmissionOverviewResponse
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
    api_instance = openapi_client.SubmissionApi(api_client)

    try:
        # Get current user's submissions overview
        api_response = api_instance.overview()
        print("The response of SubmissionApi->overview:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SubmissionApi->overview: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ApiResponseListSubmissionOverviewResponse**](ApiResponseListSubmissionOverviewResponse.md)

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

# **submit**
> ApiResponseSubmissionResponse submit(submit_code_request)

Submit code for a problem

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_submission_response import ApiResponseSubmissionResponse
from openapi_client.models.submit_code_request import SubmitCodeRequest
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
    api_instance = openapi_client.SubmissionApi(api_client)
    submit_code_request = openapi_client.SubmitCodeRequest() # SubmitCodeRequest | 

    try:
        # Submit code for a problem
        api_response = api_instance.submit(submit_code_request)
        print("The response of SubmissionApi->submit:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SubmissionApi->submit: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submit_code_request** | [**SubmitCodeRequest**](SubmitCodeRequest.md)|  | 

### Return type

[**ApiResponseSubmissionResponse**](ApiResponseSubmissionResponse.md)

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

