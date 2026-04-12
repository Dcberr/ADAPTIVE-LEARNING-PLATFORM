# Docs Index

This folder is organized for coding agents and teammates who need a fast path to the right context.

## Start Here

- [architecture.md](/Users/thaibao/projects/review-code-app/review-agent/docs/architecture.md): system-level overview of the app, main flows, and major components

## API Docs

- [api/README.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/README.md): index of all API contracts
- [api/review-code-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/review-code-api.md): code review endpoint
- [api/concept-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/concept-api.md): concept upsert endpoint
- [api/exercise-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/exercise-api.md): exercise upsert endpoint
- [api/student-profile-import-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/student-profile-import-api.md): student profile upsert endpoint
- [api/review-import-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/review-import-api.md): submission and review upsert endpoints
- [api/knowledge-graph-snapshot-api.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/knowledge-graph-snapshot-api.md): graph snapshot endpoint

## Domain Docs

- [domain/README.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/README.md): domain model index
- [domain/knowledge-graph.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/knowledge-graph.md): Neo4j entity and relationship design
- [domain/student-profile-scoring.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/student-profile-scoring.md): meaning of normalized student profile scores

## Workflow Docs

- [workflows/README.md](/Users/thaibao/projects/review-code-app/review-agent/docs/workflows/README.md): workflow index
- [workflows/review-agent.md](/Users/thaibao/projects/review-code-app/review-agent/docs/workflows/review-agent.md): review-agent pipeline details
- [workflows/recommendation-flow.md](/Users/thaibao/projects/review-code-app/review-agent/docs/workflows/recommendation-flow.md): recommendation pipeline walkthrough
- [workflows/knowledge-graph-flow.md](/Users/thaibao/projects/review-code-app/review-agent/docs/workflows/knowledge-graph-flow.md): graph-write and graph-read flow

## Suggested Reading Order

1. Read [architecture.md](/Users/thaibao/projects/review-code-app/review-agent/docs/architecture.md)
2. Open the relevant endpoint in [api/README.md](/Users/thaibao/projects/review-code-app/review-agent/docs/api/README.md)
3. Read the matching workflow doc in [workflows/README.md](/Users/thaibao/projects/review-code-app/review-agent/docs/workflows/README.md)
4. Use [domain/knowledge-graph.md](/Users/thaibao/projects/review-code-app/review-agent/docs/domain/knowledge-graph.md) for graph-level reasoning
