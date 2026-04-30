# code_review_ai_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch_patch_exercise_relations_api_v1_knowledgegraph_exercises_relations_batch_patch**](DefaultApi.md#batch_patch_exercise_relations_api_v1_knowledgegraph_exercises_relations_batch_patch) | **PATCH** /api/v1/knowledgegraph/exercises/relations/batch | Batch Patch Exercise Relations
[**batch_upsert_exercises_api_v1_knowledgegraph_exercises_batch_put**](DefaultApi.md#batch_upsert_exercises_api_v1_knowledgegraph_exercises_batch_put) | **PUT** /api/v1/knowledgegraph/exercises/batch | Batch Upsert Exercises
[**generate_recommendation_api_v1_recommendation_post**](DefaultApi.md#generate_recommendation_api_v1_recommendation_post) | **POST** /api/v1/recommendation | Generate Recommendation
[**get_knowledge_graph_snapshot_api_v1_knowledgegraph_get**](DefaultApi.md#get_knowledge_graph_snapshot_api_v1_knowledgegraph_get) | **GET** /api/v1/knowledgegraph | Get Knowledge Graph Snapshot
[**patch_concept_relations_api_v1_knowledgegraph_concepts_concept_slug_relations_patch**](DefaultApi.md#patch_concept_relations_api_v1_knowledgegraph_concepts_concept_slug_relations_patch) | **PATCH** /api/v1/knowledgegraph/concepts/{concept_slug}/relations | Patch Concept Relations
[**patch_exercise_relations_api_v1_knowledgegraph_exercises_exercise_id_relations_patch**](DefaultApi.md#patch_exercise_relations_api_v1_knowledgegraph_exercises_exercise_id_relations_patch) | **PATCH** /api/v1/knowledgegraph/exercises/{exercise_id}/relations | Patch Exercise Relations
[**review_code_api_v1_review_code_post**](DefaultApi.md#review_code_api_v1_review_code_post) | **POST** /api/v1/review_code | Review Code
[**upsert_concept_api_v1_knowledgegraph_concepts_concept_slug_put**](DefaultApi.md#upsert_concept_api_v1_knowledgegraph_concepts_concept_slug_put) | **PUT** /api/v1/knowledgegraph/concepts/{concept_slug} | Upsert Concept
[**upsert_exercise_api_v1_knowledgegraph_exercises_exercise_id_put**](DefaultApi.md#upsert_exercise_api_v1_knowledgegraph_exercises_exercise_id_put) | **PUT** /api/v1/knowledgegraph/exercises/{exercise_id} | Upsert Exercise
[**upsert_review_api_v1_knowledgegraph_reviews_review_id_put**](DefaultApi.md#upsert_review_api_v1_knowledgegraph_reviews_review_id_put) | **PUT** /api/v1/knowledgegraph/reviews/{review_id} | Upsert Review
[**upsert_student_api_v1_knowledgegraph_students_student_id_put**](DefaultApi.md#upsert_student_api_v1_knowledgegraph_students_student_id_put) | **PUT** /api/v1/knowledgegraph/students/{student_id} | Upsert Student
[**upsert_submission_api_v1_knowledgegraph_submissions_submission_id_put**](DefaultApi.md#upsert_submission_api_v1_knowledgegraph_submissions_submission_id_put) | **PUT** /api/v1/knowledgegraph/submissions/{submission_id} | Upsert Submission


# **batch_patch_exercise_relations_api_v1_knowledgegraph_exercises_relations_batch_patch**
> KnowledgeGraphExercisesBatchResponse batch_patch_exercise_relations_api_v1_knowledgegraph_exercises_relations_batch_patch(batch_patch_exercise_relations_request)

Batch Patch Exercise Relations

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.batch_patch_exercise_relations_request import BatchPatchExerciseRelationsRequest
from code_review_ai_client.models.knowledge_graph_exercises_batch_response import KnowledgeGraphExercisesBatchResponse
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    batch_patch_exercise_relations_request = code_review_ai_client.BatchPatchExerciseRelationsRequest() # BatchPatchExerciseRelationsRequest | 

    try:
        # Batch Patch Exercise Relations
        api_response = api_instance.batch_patch_exercise_relations_api_v1_knowledgegraph_exercises_relations_batch_patch(batch_patch_exercise_relations_request)
        print("The response of DefaultApi->batch_patch_exercise_relations_api_v1_knowledgegraph_exercises_relations_batch_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->batch_patch_exercise_relations_api_v1_knowledgegraph_exercises_relations_batch_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_patch_exercise_relations_request** | [**BatchPatchExerciseRelationsRequest**](BatchPatchExerciseRelationsRequest.md)|  | 

### Return type

[**KnowledgeGraphExercisesBatchResponse**](KnowledgeGraphExercisesBatchResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **batch_upsert_exercises_api_v1_knowledgegraph_exercises_batch_put**
> KnowledgeGraphExercisesBatchResponse batch_upsert_exercises_api_v1_knowledgegraph_exercises_batch_put(batch_upsert_exercises_request)

Batch Upsert Exercises

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.batch_upsert_exercises_request import BatchUpsertExercisesRequest
from code_review_ai_client.models.knowledge_graph_exercises_batch_response import KnowledgeGraphExercisesBatchResponse
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    batch_upsert_exercises_request = code_review_ai_client.BatchUpsertExercisesRequest() # BatchUpsertExercisesRequest | 

    try:
        # Batch Upsert Exercises
        api_response = api_instance.batch_upsert_exercises_api_v1_knowledgegraph_exercises_batch_put(batch_upsert_exercises_request)
        print("The response of DefaultApi->batch_upsert_exercises_api_v1_knowledgegraph_exercises_batch_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->batch_upsert_exercises_api_v1_knowledgegraph_exercises_batch_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_upsert_exercises_request** | [**BatchUpsertExercisesRequest**](BatchUpsertExercisesRequest.md)|  | 

### Return type

[**KnowledgeGraphExercisesBatchResponse**](KnowledgeGraphExercisesBatchResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generate_recommendation_api_v1_recommendation_post**
> RecommendationResponse generate_recommendation_api_v1_recommendation_post(recommendation_request)

Generate Recommendation

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.recommendation_request import RecommendationRequest
from code_review_ai_client.models.recommendation_response import RecommendationResponse
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    recommendation_request = code_review_ai_client.RecommendationRequest() # RecommendationRequest | 

    try:
        # Generate Recommendation
        api_response = api_instance.generate_recommendation_api_v1_recommendation_post(recommendation_request)
        print("The response of DefaultApi->generate_recommendation_api_v1_recommendation_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->generate_recommendation_api_v1_recommendation_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **recommendation_request** | [**RecommendationRequest**](RecommendationRequest.md)|  | 

### Return type

[**RecommendationResponse**](RecommendationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_knowledge_graph_snapshot_api_v1_knowledgegraph_get**
> KnowledgeGraphSnapshotResponse get_knowledge_graph_snapshot_api_v1_knowledgegraph_get()

Get Knowledge Graph Snapshot

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.knowledge_graph_snapshot_response import KnowledgeGraphSnapshotResponse
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)

    try:
        # Get Knowledge Graph Snapshot
        api_response = api_instance.get_knowledge_graph_snapshot_api_v1_knowledgegraph_get()
        print("The response of DefaultApi->get_knowledge_graph_snapshot_api_v1_knowledgegraph_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_knowledge_graph_snapshot_api_v1_knowledgegraph_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**KnowledgeGraphSnapshotResponse**](KnowledgeGraphSnapshotResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_concept_relations_api_v1_knowledgegraph_concepts_concept_slug_relations_patch**
> KnowledgeGraphConceptResponse patch_concept_relations_api_v1_knowledgegraph_concepts_concept_slug_relations_patch(concept_slug, patch_concept_relations_request)

Patch Concept Relations

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.knowledge_graph_concept_response import KnowledgeGraphConceptResponse
from code_review_ai_client.models.patch_concept_relations_request import PatchConceptRelationsRequest
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    concept_slug = 'concept_slug_example' # str | 
    patch_concept_relations_request = code_review_ai_client.PatchConceptRelationsRequest() # PatchConceptRelationsRequest | 

    try:
        # Patch Concept Relations
        api_response = api_instance.patch_concept_relations_api_v1_knowledgegraph_concepts_concept_slug_relations_patch(concept_slug, patch_concept_relations_request)
        print("The response of DefaultApi->patch_concept_relations_api_v1_knowledgegraph_concepts_concept_slug_relations_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->patch_concept_relations_api_v1_knowledgegraph_concepts_concept_slug_relations_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **concept_slug** | **str**|  | 
 **patch_concept_relations_request** | [**PatchConceptRelationsRequest**](PatchConceptRelationsRequest.md)|  | 

### Return type

[**KnowledgeGraphConceptResponse**](KnowledgeGraphConceptResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_exercise_relations_api_v1_knowledgegraph_exercises_exercise_id_relations_patch**
> KnowledgeGraphExerciseResponse patch_exercise_relations_api_v1_knowledgegraph_exercises_exercise_id_relations_patch(exercise_id, patch_exercise_relations_request)

Patch Exercise Relations

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.knowledge_graph_exercise_response import KnowledgeGraphExerciseResponse
from code_review_ai_client.models.patch_exercise_relations_request import PatchExerciseRelationsRequest
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    exercise_id = 'exercise_id_example' # str | 
    patch_exercise_relations_request = code_review_ai_client.PatchExerciseRelationsRequest() # PatchExerciseRelationsRequest | 

    try:
        # Patch Exercise Relations
        api_response = api_instance.patch_exercise_relations_api_v1_knowledgegraph_exercises_exercise_id_relations_patch(exercise_id, patch_exercise_relations_request)
        print("The response of DefaultApi->patch_exercise_relations_api_v1_knowledgegraph_exercises_exercise_id_relations_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->patch_exercise_relations_api_v1_knowledgegraph_exercises_exercise_id_relations_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **exercise_id** | **str**|  | 
 **patch_exercise_relations_request** | [**PatchExerciseRelationsRequest**](PatchExerciseRelationsRequest.md)|  | 

### Return type

[**KnowledgeGraphExerciseResponse**](KnowledgeGraphExerciseResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **review_code_api_v1_review_code_post**
> ReviewResponse review_code_api_v1_review_code_post(review_request)

Review Code

Endpoint that uses the LangGraph workflow with Gemini for code review.

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.review_request import ReviewRequest
from code_review_ai_client.models.review_response import ReviewResponse
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    review_request = code_review_ai_client.ReviewRequest() # ReviewRequest | 

    try:
        # Review Code
        api_response = api_instance.review_code_api_v1_review_code_post(review_request)
        print("The response of DefaultApi->review_code_api_v1_review_code_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->review_code_api_v1_review_code_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **review_request** | [**ReviewRequest**](ReviewRequest.md)|  | 

### Return type

[**ReviewResponse**](ReviewResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_concept_api_v1_knowledgegraph_concepts_concept_slug_put**
> KnowledgeGraphConceptResponse upsert_concept_api_v1_knowledgegraph_concepts_concept_slug_put(concept_slug, upsert_concept_request)

Upsert Concept

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.knowledge_graph_concept_response import KnowledgeGraphConceptResponse
from code_review_ai_client.models.upsert_concept_request import UpsertConceptRequest
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    concept_slug = 'concept_slug_example' # str | 
    upsert_concept_request = code_review_ai_client.UpsertConceptRequest() # UpsertConceptRequest | 

    try:
        # Upsert Concept
        api_response = api_instance.upsert_concept_api_v1_knowledgegraph_concepts_concept_slug_put(concept_slug, upsert_concept_request)
        print("The response of DefaultApi->upsert_concept_api_v1_knowledgegraph_concepts_concept_slug_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->upsert_concept_api_v1_knowledgegraph_concepts_concept_slug_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **concept_slug** | **str**|  | 
 **upsert_concept_request** | [**UpsertConceptRequest**](UpsertConceptRequest.md)|  | 

### Return type

[**KnowledgeGraphConceptResponse**](KnowledgeGraphConceptResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_exercise_api_v1_knowledgegraph_exercises_exercise_id_put**
> KnowledgeGraphExerciseResponse upsert_exercise_api_v1_knowledgegraph_exercises_exercise_id_put(exercise_id, upsert_exercise_request)

Upsert Exercise

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.knowledge_graph_exercise_response import KnowledgeGraphExerciseResponse
from code_review_ai_client.models.upsert_exercise_request import UpsertExerciseRequest
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    exercise_id = 'exercise_id_example' # str | 
    upsert_exercise_request = code_review_ai_client.UpsertExerciseRequest() # UpsertExerciseRequest | 

    try:
        # Upsert Exercise
        api_response = api_instance.upsert_exercise_api_v1_knowledgegraph_exercises_exercise_id_put(exercise_id, upsert_exercise_request)
        print("The response of DefaultApi->upsert_exercise_api_v1_knowledgegraph_exercises_exercise_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->upsert_exercise_api_v1_knowledgegraph_exercises_exercise_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **exercise_id** | **str**|  | 
 **upsert_exercise_request** | [**UpsertExerciseRequest**](UpsertExerciseRequest.md)|  | 

### Return type

[**KnowledgeGraphExerciseResponse**](KnowledgeGraphExerciseResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_review_api_v1_knowledgegraph_reviews_review_id_put**
> KnowledgeGraphReviewResponse upsert_review_api_v1_knowledgegraph_reviews_review_id_put(review_id, upsert_review_request)

Upsert Review

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.knowledge_graph_review_response import KnowledgeGraphReviewResponse
from code_review_ai_client.models.upsert_review_request import UpsertReviewRequest
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    review_id = 'review_id_example' # str | 
    upsert_review_request = code_review_ai_client.UpsertReviewRequest() # UpsertReviewRequest | 

    try:
        # Upsert Review
        api_response = api_instance.upsert_review_api_v1_knowledgegraph_reviews_review_id_put(review_id, upsert_review_request)
        print("The response of DefaultApi->upsert_review_api_v1_knowledgegraph_reviews_review_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->upsert_review_api_v1_knowledgegraph_reviews_review_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **review_id** | **str**|  | 
 **upsert_review_request** | [**UpsertReviewRequest**](UpsertReviewRequest.md)|  | 

### Return type

[**KnowledgeGraphReviewResponse**](KnowledgeGraphReviewResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_student_api_v1_knowledgegraph_students_student_id_put**
> KnowledgeGraphStudentResponse upsert_student_api_v1_knowledgegraph_students_student_id_put(student_id, upsert_student_profile_request)

Upsert Student

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.knowledge_graph_student_response import KnowledgeGraphStudentResponse
from code_review_ai_client.models.upsert_student_profile_request import UpsertStudentProfileRequest
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    student_id = 'student_id_example' # str | 
    upsert_student_profile_request = code_review_ai_client.UpsertStudentProfileRequest() # UpsertStudentProfileRequest | 

    try:
        # Upsert Student
        api_response = api_instance.upsert_student_api_v1_knowledgegraph_students_student_id_put(student_id, upsert_student_profile_request)
        print("The response of DefaultApi->upsert_student_api_v1_knowledgegraph_students_student_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->upsert_student_api_v1_knowledgegraph_students_student_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **student_id** | **str**|  | 
 **upsert_student_profile_request** | [**UpsertStudentProfileRequest**](UpsertStudentProfileRequest.md)|  | 

### Return type

[**KnowledgeGraphStudentResponse**](KnowledgeGraphStudentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_submission_api_v1_knowledgegraph_submissions_submission_id_put**
> KnowledgeGraphSubmissionResponse upsert_submission_api_v1_knowledgegraph_submissions_submission_id_put(submission_id, upsert_submission_request)

Upsert Submission

### Example


```python
import code_review_ai_client
from code_review_ai_client.models.knowledge_graph_submission_response import KnowledgeGraphSubmissionResponse
from code_review_ai_client.models.upsert_submission_request import UpsertSubmissionRequest
from code_review_ai_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = code_review_ai_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with code_review_ai_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = code_review_ai_client.DefaultApi(api_client)
    submission_id = 'submission_id_example' # str | 
    upsert_submission_request = code_review_ai_client.UpsertSubmissionRequest() # UpsertSubmissionRequest | 

    try:
        # Upsert Submission
        api_response = api_instance.upsert_submission_api_v1_knowledgegraph_submissions_submission_id_put(submission_id, upsert_submission_request)
        print("The response of DefaultApi->upsert_submission_api_v1_knowledgegraph_submissions_submission_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->upsert_submission_api_v1_knowledgegraph_submissions_submission_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **submission_id** | **str**|  | 
 **upsert_submission_request** | [**UpsertSubmissionRequest**](UpsertSubmissionRequest.md)|  | 

### Return type

[**KnowledgeGraphSubmissionResponse**](KnowledgeGraphSubmissionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

