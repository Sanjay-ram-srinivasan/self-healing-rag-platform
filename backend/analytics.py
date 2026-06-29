import json
import logging
import os
from collections import Counter
from datetime import date, datetime, time, timedelta
from statistics import mean

from backend.persistence import get_firestore_client
from backend.storage import load_json, save_json


logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_FILE = os.path.join(BASE_DIR, "data", "rag_stats.json")
ANALYTICS_COLLECTION = "analytics"


def _default_stats():
    return {
        "queries": []
    }


def _local_stats():
    return load_json(STATS_FILE, _default_stats())


def _remote_doc_ref(user_id):
    client = get_firestore_client()
    if not client:
        return None
    return client.collection(ANALYTICS_COLLECTION).document(user_id)


def _utc_now():
    return datetime.utcnow().isoformat()


def load_stats():
    stats = _local_stats()
    client = get_firestore_client()
    if not client:
        return stats

    try:
        # Merge all user analytics into a single list (for backward compat)
        all_queries = []
        for doc in client.collection(ANALYTICS_COLLECTION).stream():
            user_data = doc.to_dict()
            all_queries.extend(user_data.get("queries", []))
        if all_queries:
            stats["queries"] = all_queries
            save_json(STATS_FILE, stats)
    except Exception:
        logger.warning("Could not sync analytics from Firestore", exc_info=True)

    return stats


def save_stats(stats):
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, "w", encoding="utf-8") as file:
        json.dump(stats, file, indent=2)


def append_query_log(entry, user_id=None):
    stats = load_stats()
    next_entry = dict(entry)
    next_entry.setdefault("timestamp", datetime.now().isoformat())
    if user_id:
        next_entry["user_id"] = user_id
    stats.setdefault("queries", []).append(next_entry)
    save_stats(stats)

    # Persist to Firestore per user
    if user_id:
        doc_ref = _remote_doc_ref(user_id)
        if doc_ref:
            try:
                snapshot = doc_ref.get()
                if snapshot.exists:
                    existing_queries = snapshot.to_dict().get("queries", [])
                else:
                    existing_queries = []
                existing_queries.append(next_entry)
                doc_ref.set({
                    "user_id": user_id,
                    "queries": existing_queries,
                    "updated_at": _utc_now(),
                })
            except Exception:
                logger.warning("Could not persist analytics to Firestore for user %s", user_id, exc_info=True)

    return stats


def load_user_stats(user_id):
    """Load analytics stats for a specific user, falling back to local file."""
    client = get_firestore_client()
    if client and user_id:
        try:
            doc_ref = client.collection(ANALYTICS_COLLECTION).document(user_id)
            snapshot = doc_ref.get()
            if snapshot.exists:
                queries = snapshot.to_dict().get("queries", [])
                return {"queries": queries}
        except Exception:
            logger.warning("Could not load analytics from Firestore for user %s", user_id, exc_info=True)

    # Fallback: filter local stats by user_id
    stats = _local_stats()
    queries = stats.get("queries", [])
    if user_id:
        queries = [q for q in queries if q.get("user_id") == user_id or q.get("user", {}).get("uid") == user_id]
    return {"queries": queries}


def parse_query_timestamp(timestamp_value):
    if not timestamp_value:
        return None

    if isinstance(timestamp_value, datetime):
        parsed = timestamp_value
        return parsed.astimezone().replace(tzinfo=None) if parsed.tzinfo else parsed

    if isinstance(timestamp_value, date):
        return datetime.combine(timestamp_value, time.min)

    if isinstance(timestamp_value, (int, float)):
        return datetime.fromtimestamp(timestamp_value)

    if isinstance(timestamp_value, str):
        try:
            parsed = datetime.fromisoformat(timestamp_value.replace("Z", "+00:00"))
            return parsed.astimezone().replace(tzinfo=None) if parsed.tzinfo else parsed
        except ValueError:
            return None

    return None


def resolve_analytics_period(selected_range, start_date=None, end_date=None, now=None):
    # Use local time so "today" midnight matches how timestamps are stored
    now = now or datetime.now()
    selected_range = (selected_range or "7d").strip().lower()

    if selected_range == "today":
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif selected_range == "7d":
        start_dt = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif selected_range == "30d":
        start_dt = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif selected_range in ("all", "*"):
        # No date filtering — return everything
        start_dt = datetime.min.replace(tzinfo=None)
        end_dt = now
    elif selected_range == "custom":
        if not start_date or not end_date:
            raise ValueError("Custom range requires start_date and end_date.")

        try:
            start_dt = parse_query_timestamp(start_date)
            end_dt = parse_query_timestamp(end_date)
        except ValueError as exc:
            raise ValueError("Invalid custom date format. Use ISO format.") from exc

        if start_dt is None or end_dt is None:
            raise ValueError("Invalid custom date format. Use ISO format.")

        if isinstance(start_date, str) and "T" not in start_date:
            start_dt = datetime.combine(start_dt.date(), time.min)
        if isinstance(end_date, str) and "T" not in end_date:
            end_dt = datetime.combine(end_dt.date(), time.max)
    else:
        # Unknown range — default to 7 days
        logger.warning("Unknown analytics range '%s', defaulting to 7d.", selected_range)
        start_dt = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now

    return start_dt, end_dt


def filter_queries_by_timestamp(queries, start_dt, end_dt):
    filtered_queries = []

    for query in queries:
        query_dt = parse_query_timestamp(query.get("timestamp"))
        if query_dt is None:
            continue
        if start_dt <= query_dt <= end_dt:
            filtered_queries.append(query)

    return filtered_queries


def log_analytics_summary(selected_range, total_loaded, total_filtered, data):
    logger.info("Analytics selected range: %s", selected_range)
    logger.info("Analytics total records loaded: %s", total_loaded)
    logger.info("Analytics records after filtering: %s", total_filtered)
    logger.info(
        "Analytics returned metrics: total_queries=%s avg_confidence=%s avg_faithfulness=%s hallucination_rate=%s retry_rate=%s",
        data.get("total_queries", 0),
        data.get("average_confidence", 0),
        data.get("average_faithfulness", 0),
        data.get("hallucination_rate", 0),
        data.get("retry_rate", 0),
    )


def _score_value(item, key):
    try:
        value = float(item.get(key))
    except (TypeError, ValueError):
        return None
    return max(0.0, min(100.0, value))


def _safe_mean(items, key):
    values = [
        value
        for item in items
        for value in [_score_value(item, key)]
        if value is not None
    ]
    return round(mean(values), 2) if values else 0.0


def _attempts(item):
    try:
        return max(1, int(item.get("attempts", 1) or 1))
    except (TypeError, ValueError):
        return 1


def is_hallucinated(item):
    grounded = item.get("grounded")
    if grounded is False:
        return True
    if grounded is True:
        return False

    faithfulness = _score_value(item, "faithfulness")
    return faithfulness is not None and faithfulness < 70


def _source_name(source):
    if isinstance(source, str):
        raw_name = source
    elif isinstance(source, dict):
        raw_name = (
            source.get("filename")
            or source.get("name")
            or source.get("source")
            or source.get("document")
        )
    else:
        raw_name = None

    if not raw_name:
        return None
    return os.path.basename(str(raw_name).replace("\\", os.sep))


def most_queried_documents(queries, limit=10):
    document_counts = Counter()
    for item in queries:
        seen_for_query = set()
        for source in item.get("sources") or item.get("source_documents") or []:
            name = _source_name(source)
            if name:
                seen_for_query.add(name)
        document_counts.update(seen_for_query)

    return [
        {"document": document, "queries": count}
        for document, count in document_counts.most_common(limit)
    ]


def build_history(queries, start_dt=None, end_dt=None):
    end_dt = end_dt or datetime.utcnow()
    if start_dt is None:
        start_dt = (end_dt - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

    start_day = start_dt.date()
    end_day = end_dt.date()
    total_days = max(1, (end_day - start_day).days + 1)
    history = []

    for day_offset in range(total_days):
        day = start_day + timedelta(days=day_offset)
        day_queries = []
        for item in queries:
            item_dt = parse_query_timestamp(item.get("timestamp"))
            if item_dt is None:
                continue
            if item_dt.date() == day:
                day_queries.append(item)

        history.append({
            "date": day.isoformat(),
            "questions": len(day_queries),
            "retries": sum(1 for item in day_queries if _attempts(item) > 1),
            "hallucinations": sum(1 for item in day_queries if is_hallucinated(item)),
            "average_confidence": _safe_mean(day_queries, "confidence"),
            "average_faithfulness": _safe_mean(day_queries, "faithfulness"),
            "average_relevance": _safe_mean(day_queries, "relevance"),
            "average_precision": _safe_mean(day_queries, "precision"),
            "average_recall": _safe_mean(day_queries, "recall"),
        })

    return history


def summarize_analytics(
    stats,
    total_documents=0,
    vector_store_mb=0.0,
    start_dt=None,
    end_dt=None,
    selected_range="7d",
):
    queries = stats.get("queries", [])
    total_queries = len(queries)
    retried_queries = [item for item in queries if _attempts(item) > 1]
    hallucinated_queries = [item for item in queries if is_hallucinated(item)]
    verified_answers = total_queries - len(hallucinated_queries)

    averages = {
        "average_confidence": _safe_mean(queries, "confidence"),
        "average_faithfulness": _safe_mean(queries, "faithfulness"),
        "average_relevance": _safe_mean(queries, "relevance"),
        "average_precision": _safe_mean(queries, "precision"),
        "average_recall": _safe_mean(queries, "recall"),
    }

    failed_queries = [
        {
            "query": item.get("question", ""),
            "reason": item.get("reason", ""),
            "confidence": item.get("confidence", 0),
            "faithfulness": item.get("faithfulness", 0),
            "relevance": item.get("relevance", 0),
            "precision": item.get("precision", 0),
            "recall": item.get("recall", 0),
            "timestamp": item.get("timestamp", ""),
        }
        for item in reversed(hallucinated_queries[-10:])
    ]

    history = build_history(queries, start_dt=start_dt, end_dt=end_dt)

    return {
        "documents_indexed": total_documents,
        "vector_store_mb": vector_store_mb,
        "range": selected_range,
        "start_date": start_dt.isoformat() if start_dt else None,
        "end_date": end_dt.isoformat() if end_dt else None,
        "total_queries": total_queries,
        "questions_asked": total_queries,
        "verified_answers": verified_answers,
        "failed_answers": len(hallucinated_queries),
        "retry_count": len(retried_queries),
        "hallucination_count": len(hallucinated_queries),
        "reliable_count": verified_answers,
        **averages,
        "hallucination_rate": round((len(hallucinated_queries) / total_queries) * 100, 2) if total_queries else 0.0,
        "hallucination_prevention_rate": round((verified_answers / total_queries) * 100, 2) if total_queries else 0.0,
        "retry_rate": round((len(retried_queries) / total_queries) * 100, 2) if total_queries else 0.0,
        "history": history,
        "retry_history": [
            {
                "date": item["date"],
                "retries": item["retries"],
                "questions": item["questions"],
            }
            for item in history
        ],
        "recent_queries": list(reversed(queries[-20:])),
        "failed_queries": failed_queries,
        "most_queried_documents": most_queried_documents(queries),
        "status": "healthy",
    }
