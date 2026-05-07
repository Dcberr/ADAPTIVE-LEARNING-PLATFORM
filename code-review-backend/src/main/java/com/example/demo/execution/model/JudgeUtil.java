package com.example.demo.execution.model;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class JudgeUtil {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    public static boolean compareOutput(String expected, String actual, boolean ignoreOrder) {

        if (expected == null || actual == null) {
            return false;
        }

        if (ignoreOrder) {
            Boolean unorderedMatch = compareTopLevelJsonArrayIgnoringOrder(expected, actual);
            if (unorderedMatch != null) {
                return unorderedMatch;
            }
        }

        return expected.trim().equals(actual.trim());
    }

    private static Boolean compareTopLevelJsonArrayIgnoringOrder(String expected, String actual) {
        try {
            JsonNode expectedNode = OBJECT_MAPPER.readTree(expected.trim());
            JsonNode actualNode = OBJECT_MAPPER.readTree(actual.trim());

            if (!expectedNode.isArray() || !actualNode.isArray()) {
                return null;
            }

            List<String> expectedItems = canonicalizeArrayItems(expectedNode);
            List<String> actualItems = canonicalizeArrayItems(actualNode);
            return expectedItems.equals(actualItems);
        } catch (Exception ex) {
            return null;
        }
    }

    private static List<String> canonicalizeArrayItems(JsonNode arrayNode) throws Exception {
        List<String> items = new ArrayList<>();
        for (JsonNode item : arrayNode) {
            items.add(OBJECT_MAPPER.writeValueAsString(item));
        }
        items.sort(Comparator.naturalOrder());
        return items;
    }
}
