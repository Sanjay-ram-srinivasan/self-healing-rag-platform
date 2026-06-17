import json
import logging
import os
from datetime import datetime, timedelta
from statistics import mean


logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_FILE = os.path.join(BASE_DIR, "data", "rag_stats.json")


def _default_stats():
    return {
        "queries": []
    }


def load_stats():
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    if not os.path.exists(STATS_FILE):
        return _default_stats()

    try:
        with open(STATS_FILE, "r", encoding="utf-8") as file:
            stats = json.load(file)
    except Exception:
        logger.warning("Could not load rag stats file", exc_info=True)
        return _default_stats()

    if isinstance(stats, dict) and isinstance(stats.get("queries"), list):
        return stats

    # Migrate the previous aggregate-only shape into the new query-log format.
    return _default_stats()


def save_stats(stats):
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, "w", encoding="utf-8") as file:
        json.dump(stats, file, indent=2)


def append_query_log(entry):
    stats = load_stats()
    stats.setdefault("queries", []).append(entry)
    save_stats(stats)
    return stats


def _safe_mean(items, key):
    values = [float(item.get(key, 0) or 0) for item in items]
    return round(mean(values), 2) if values else 0.0


def build_history(queries, days=7):
    now = datetime.now()
    history = []

    for offset in range(days - 1, -1, -1):
        day = (now - timedelta(days=offset)).date()
        day_queries = []
        for item in queries:
            timestamp = item.get("timestamp")
            if not timestamp:
                continue
            try:
                item_day = datetime.fromisoformat(timestamp).date()
            except ValueError:
                continue
            if item_day == day:
                day_queries.append(item)

        history.append({
            "date": day.isoformat(),
            "questions": len(day_queries),
            "retries": sum(1 for item in day_queries if int(item.get("attempts", 1) or 1) > 1),
            "average_confidence": _safe_mean(day_queries, "confidence"),
            "average_faithfulness": _safe_mean(day_queries, "faithfulness"),
            "average_relevance": _safe_mean(day_queries, "relevance"),
            "average_precision": _safe_mean(day_queries, "precision"),
            "average_recall": _safe_mean(day_queries, "recall"),
        })

    return history


def summarize_analytics(stats, total_documents=0, vector_store_mb=0.0):
    queries = stats.get("queries", [])
    total_queries = len(queries)
    retried_queries = [item for item in queries if int(item.get("attempts", 1) or 1) > 1]
    hallucinated_queries = [
        item for item in queries
        if not bool(item.get("grounded", False)) or float(item.get("faithfulness", 0) or 0) < 70
    ]

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

    return {
        "documents_indexed": total_documents,
        "vector_store_mb": vector_store_mb,
        "total_queries": total_queries,
        "questions_asked": total_queries,
        "verified_answers": total_queries - len(hallucinated_queries),
        "failed_answers": len(hallucinated_queries),
        **averages,
        "hallucination_rate": round((len(hallucinated_queries) / total_queries) * 100, 2) if total_queries else 0.0,
        "hallucination_prevention_rate": round(((total_queries - len(hallucinated_queries)) / total_queries) * 100, 2) if total_queries else 0.0,
        "retry_rate": round((len(retried_queries) / total_queries) * 100, 2) if total_queries else 0.0,
        "history": build_history(queries, days=7),
        "retry_history": [
            {
                "date": item["date"],
                "retries": item["retries"],
                "questions": item["questions"],
            }
            for item in build_history(queries, days=7)
        ],
        "recent_queries": list(reversed(queries[-20:])),
        "failed_queries": failed_queries,
        "status": "healthy",
    }
