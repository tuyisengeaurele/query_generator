-- Read-only role the API connects through for query execution. The pipeline
-- guardrails reject non-SELECT statements before they ever reach the
-- database, but this role is a second, independent line of defense: even a
-- guardrail bug cannot result in a write against this connection.
CREATE ROLE query_generator_readonly LOGIN PASSWORD 'query_generator_readonly';
GRANT CONNECT ON DATABASE query_generator TO query_generator_readonly;
GRANT USAGE ON SCHEMA public TO query_generator_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO query_generator_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO query_generator_readonly;
