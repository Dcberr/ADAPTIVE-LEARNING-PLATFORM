# code_review_api_client.ExecutionApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**judge**](ExecutionApi.md#judge) | **POST** /execution/judge | Run and judge code against testcases
[**run**](ExecutionApi.md#run) | **POST** /execution/run | Run code without judging


# **judge**
> ApiResponseRunCodeResponse judge(run_testcase_request)

Run and judge code against testcases

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_run_code_response import ApiResponseRunCodeResponse
from code_review_api_client.models.run_testcase_request import RunTestcaseRequest
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
    api_instance = code_review_api_client.ExecutionApi(api_client)
    run_testcase_request = code_review_api_client.RunTestcaseRequest() # RunTestcaseRequest | 

    try:
        # Run and judge code against testcases
        api_response = api_instance.judge(run_testcase_request)
        print("The response of ExecutionApi->judge:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionApi->judge: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_testcase_request** | [**RunTestcaseRequest**](RunTestcaseRequest.md)|  | 

### Return type

[**ApiResponseRunCodeResponse**](ApiResponseRunCodeResponse.md)

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

# **run**
> ApiResponseRunCodeResponse run(run_code_request)

Run code without judging

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import code_review_api_client
from code_review_api_client.models.api_response_run_code_response import ApiResponseRunCodeResponse
from code_review_api_client.models.run_code_request import RunCodeRequest
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
    api_instance = code_review_api_client.ExecutionApi(api_client)
    run_code_request = code_review_api_client.RunCodeRequest() # RunCodeRequest | 

    try:
        # Run code without judging
        api_response = api_instance.run(run_code_request)
        print("The response of ExecutionApi->run:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionApi->run: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_code_request** | [**RunCodeRequest**](RunCodeRequest.md)|  | 

### Return type

[**ApiResponseRunCodeResponse**](ApiResponseRunCodeResponse.md)

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

