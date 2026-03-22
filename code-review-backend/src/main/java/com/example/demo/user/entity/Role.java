package com.example.demo.user.entity;

public enum Role {

    STUDENT("STU"),
    INSTRUCTOR("INS"),
    ADMIN("ADM");

    private final String prefix;

    Role(String prefix) {
        this.prefix = prefix;
    }

    public String getPrefix() {
        return prefix;
    }
}
