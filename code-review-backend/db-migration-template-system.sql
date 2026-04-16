-- Migration: Add starter code templates support with generic template system
-- This migration adds support for generic starter code templates with placeholders

-- Create table for starter_codes containing full templates (ElementCollection mapping)
-- The existing problem_starter_codes table is repurposed to store templates with placeholders
CREATE TABLE IF NOT EXISTS problem_starter_codes (
    problem_id UUID NOT NULL,
    language VARCHAR(50) NOT NULL,
    starter_code TEXT,
    PRIMARY KEY (problem_id, language),
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_problem_starter_codes_language 
    ON problem_starter_codes(language);
