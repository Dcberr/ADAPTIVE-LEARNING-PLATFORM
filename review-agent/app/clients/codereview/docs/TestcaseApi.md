# openapi_client.TestcaseApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_testcase**](TestcaseApi.md#create_testcase) | **POST** /testcases | Create a testcase for a problem
[**get_testcases**](TestcaseApi.md#get_testcases) | **GET** /testcases/problem/{problemId} | Get testcases by problem ID


# **create_testcase**
> ApiResponseTestcaseResponse create_testcase(create_testcase_request)

Create a testcase for a problem

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_testcase_response import ApiResponseTestcaseResponse
from openapi_client.models.create_testcase_request import CreateTestcaseRequest
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
    api_instance = openapi_client.TestcaseApi(api_client)
    create_testcase_request = openapi_client.CreateTestcaseRequest() # CreateTestcaseRequest | 

    try:
        # Create a testcase for a problem
        api_response = api_instance.create_testcase(create_testcase_request)
        print("The response of TestcaseApi->create_testcase:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestcaseApi->create_testcase: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_testcase_request** | [**CreateTestcaseRequest**](CreateTestcaseRequest.md)|  | 

### Return type

[**ApiResponseTestcaseResponse**](ApiResponseTestcaseResponse.md)

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

# **get_testcases**
> ApiResponseListTestcaseResponse get_testcases(problem_id)

Get testcases by problem ID

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import openapi_client
from openapi_client.models.api_response_list_testcase_response import ApiResponseListTestcaseResponse
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
    api_instance = openapi_client.TestcaseApi(api_client)
    problem_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | Problem ID

    try:
        # Get testcases by problem ID
        api_response = api_instance.get_testcases(problem_id)
        print("The response of TestcaseApi->get_testcases:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestcaseApi->get_testcases: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **problem_id** | **UUID**| Problem ID | 

### Return type

[**ApiResponseListTestcaseResponse**](ApiResponseListTestcaseResponse.md)

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

