package com.example.demo.execution.model;

public class JudgeUtil {

    public static boolean compareOutput(String expected, String actual) {

        if (expected == null || actual == null) {
            return false;
        }

        return expected.trim().equals(actual.trim());
    }
}
