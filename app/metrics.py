from prometheus_client import Counter, Histogram

secrets_created = Counter(
    "vanishd_secrets_created_total",
    "Secrets created successfully",
)
secrets_read = Counter(
    "vanishd_secrets_read_total",
    "Secrets read (consumed)",
)
secrets_expired = Counter(
    "vanishd_secrets_expired_total",
    "Secrets removed by the cleanup job",
)
secrets_not_found = Counter(
    "vanishd_secrets_not_found_total",
    "Read attempts with no result (expired or already read)",
)
request_duration = Histogram(
    "vanishd_request_duration_seconds",
    "Request latency by route and method",
    ["route", "method"],
)
