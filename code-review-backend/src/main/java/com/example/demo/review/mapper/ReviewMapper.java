// package com.example.demo.review.mapper;

// import java.util.List;

// import com.example.demo.execution.dto.RunCodeResponse;
// import com.example.demo.problem.entity.Testcase;
// import com.example.demo.review.dto.RunResponse;
// import com.example.demo.review.dto.TestcaseResult;

// public class ReviewMapper {

//     public static RunResponse mapExecutionResult(
//             List<Testcase> testcases,
//             RunCodeResponse executionResult
//     ) {

//         List<TestcaseResult> results =
//                 testcases.stream()
//                         .map(tc -> TestcaseResult.builder()
//                                 .input(tc.getInput())
//                                 .expectedOutput(tc.getExpectedOutput())
//                                 .actualOutput(executionResult.getOutput())
//                                 .passed(
//                                         tc.getExpectedOutput()
//                                                 .trim()
//                                                 .equals(executionResult.getOutput().trim())
//                                 )
//                                 .build())
//                         .toList();

//         return RunResponse.builder()
//                 .testcaseResults(results)
//                 .build();
//     }
// }