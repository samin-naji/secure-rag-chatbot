SELECT current_user, current_database();
ALTER TABLE document_chunks
ADD COLUMN embedding vector(384);
SELECT
    column_name,
    data_type,
    udt_name,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'document_chunks'
ORDER BY ordinal_position;
SELECT
    COUNT(*) AS total_chunks,
    COUNT(embedding) AS chunks_with_embedding,
    COUNT(*) FILTER (
        WHERE embedding IS NULL
    ) AS chunks_without_embedding
FROM document_chunks;
SELECT
    id,
    document_id,
    chunk_index,
    LEFT(content, 100) AS content_preview
FROM document_chunks
WHERE embedding IS NULL
ORDER BY id;
SELECT
    COUNT(*) AS total_chunks,
    COUNT(embedding) AS chunks_with_embedding,
    COUNT(*) FILTER (
        WHERE embedding IS NULL
    ) AS chunks_without_embedding
FROM document_chunks;
SELECT
    u.id AS user_id,
    u.username,
    u.role,
    d.id AS document_id,
    d.filename,
    dp.permission
FROM users u
LEFT JOIN document_permissions dp
    ON dp.user_id = u.id
LEFT JOIN documents d
    ON d.id = dp.document_id
ORDER BY u.id, d.id;
SELECT
    document_id,
    permission
FROM document_permissions
WHERE user_id = (
    SELECT id
    FROM users
    WHERE username = 'sara'
)
AND permission = 'read';
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'audit_logs'
ORDER BY ordinal_position;
SELECT
    id,
    user_id,
    username,
    event_type,
    status,
    resource_type,
    resource_id,
    created_at
FROM audit_logs
WHERE event_type = 'audit_test'
ORDER BY id DESC
LIMIT 5;
SELECT
    id,
    user_id,
    username,
    event_type,
    status,
    resource_type,
    resource_id,
    created_at
FROM audit_logs
WHERE event_type = 'chat'
ORDER BY id DESC
LIMIT 5;
SELECT
    id,
    user_id,
    username,
    event_type,
    status,
    resource_type,
    resource_id,
    created_at
FROM audit_logs
WHERE event_type IN ('login', 'register')
ORDER BY id DESC
LIMIT 20;
SELECT
    id,
    user_id,
    username,
    event_type,
    status,
    resource_type,
    resource_id,
    created_at
FROM audit_logs
WHERE event_type = 'document_view'
ORDER BY id DESC
LIMIT 10;
SELECT
    id,
    user_id,
    username,
    event_type,
    status,
    resource_type,
    resource_id,
    created_at
FROM audit_logs
WHERE event_type = 'document_upload'
ORDER BY id DESC
LIMIT 10;
SELECT
    d.id AS document_id,
    d.filename,
    a.id AS audit_id,
    a.event_type,
    a.status,
    a.username
FROM documents AS d
JOIN audit_logs AS a
    ON a.resource_id = d.id
WHERE a.event_type = 'document_upload'
  AND a.status = 'success'
ORDER BY a.id DESC
LIMIT 5;
SELECT
    id,
    user_id,
    username,
    event_type,
    status,
    resource_type,
    resource_id,
    created_at
FROM audit_logs
WHERE event_type = 'access_denied'
ORDER BY id DESC
LIMIT 10;
SELECT
    u.username,
    dp.document_id,
    dp.permission
FROM document_permissions AS dp
JOIN users AS u ON u.id = dp.user_id
WHERE u.username = 'sara'
  AND dp.document_id = 10;
SELECT
    event_type,
    status,
    COUNT(*) AS total_events
FROM audit_logs
GROUP BY event_type, status
ORDER BY event_type, status;
SELECT
    id,
    user_id,
    username,
    event_type,
    status,
    resource_type,
    created_at
FROM audit_logs
WHERE event_type = 'chat'
ORDER BY id DESC
LIMIT 5;