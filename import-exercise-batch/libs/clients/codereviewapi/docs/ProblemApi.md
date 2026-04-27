# code_review_api_client.ProblemApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_problem**](ProblemApi.md#create_problem) | **POST** /problems | Create a new problem
[**get_problem**](ProblemApi.md#get_problem) | **GET** /problems/{problemId} | Get problem detail
[**import_leet_code_problems**](ProblemApi.md#import_leet_code_problems) | **POST** /problems/leetcode/batch | Batch import LeetCode problems


# **create_problem**
> ApiResponseProblemResponse create_problem(create_problem_request)

Create a new problem

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_problem_response import ApiResponseProblemResponse
from code_review_api_client.models.create_problem_request import CreateProblemRequest
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
    api_instance = code_review_api_client.ProblemApi(api_client)
    create_problem_request = code_review_api_client.CreateProblemRequest() # CreateProblemRequest | 

    try:
        # Create a new problem
        api_response = api_instance.create_problem(create_problem_request)
        print("The response of ProblemApi->create_problem:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProblemApi->create_problem: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_problem_request** | [**CreateProblemRequest**](CreateProblemRequest.md)|  | 

### Return type

[**ApiResponseProblemResponse**](ApiResponseProblemResponse.md)

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

# **get_problem**
> ApiResponseProblemResponse get_problem(problem_id)

Get problem detail

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_problem_response import ApiResponseProblemResponse
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
    api_instance = code_review_api_client.ProblemApi(api_client)
    problem_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | Problem ID

    try:
        # Get problem detail
        api_response = api_instance.get_problem(problem_id)
        print("The response of ProblemApi->get_problem:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProblemApi->get_problem: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **problem_id** | **UUID**| Problem ID | 

### Return type

[**ApiResponseProblemResponse**](ApiResponseProblemResponse.md)

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

# **import_leet_code_problems**
> ApiResponseString import_leet_code_problems(leet_code_import_request)

Batch import LeetCode problems

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_string import ApiResponseString
from code_review_api_client.models.leet_code_import_request import LeetCodeImportRequest
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
    api_instance = code_review_api_client.ProblemApi(api_client)
    leet_code_import_request = [code_review_api_client.LeetCodeImportRequest()] # List[LeetCodeImportRequest] | 

    try:
        # Batch import LeetCode problems
        api_response = api_instance.import_leet_code_problems(leet_code_import_request)
        print("The response of ProblemApi->import_leet_code_problems:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProblemApi->import_leet_code_problems: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **leet_code_import_request** | [**List[LeetCodeImportRequest]**](LeetCodeImportRequest.md)|  | 

### Return type

[**ApiResponseString**](ApiResponseString.md)

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

