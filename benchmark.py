"""
QueryGenie AI — Accuracy Benchmark
Run from repo root: python benchmark.py

Tests the full pipeline on 20 questions with known correct answers.
Reports accuracy, pass/fail per question, and saves results to benchmark_results.json
"""

import json
import time
from backend.agents.pipeline import run_pipeline

# ─── Golden Test Set ──────────────────────────────────────────────────────────
# Each test: question + what the correct answer MUST contain (keywords/values)
GOLDEN_SET = [
    {
        "id": 1,
        "question": "How many customers are there?",
        "must_contain": ["10"],
        "category": "count"
    },
    {
        "id": 2,
        "question": "Which customers are from Mumbai?",
        "must_contain": ["Rohan Mehta"],
        "category": "filter"
    },
    {
        "id": 3,
        "question": "Which customers are from Delhi?",
        "must_contain": ["Arjun Verma", "Karan Singh"],
        "category": "filter"
    },
    {
        "id": 4,
        "question": "How many orders were delivered?",
        "must_contain": ["10"],
        "category": "count"
    },
    {
        "id": 5,
        "question": "How many orders were cancelled?",
        "must_contain": ["1"],
        "category": "count"
    },
    {
        "id": 6,
        "question": "What is the total revenue from successful payments?",
        "must_contain": ["29525"],
        "category": "aggregation"
    },
    {
        "id": 7,
        "question": "How many products are in the Electronics category?",
        "must_contain": ["3"],
        "category": "count"
    },
    {
        "id": 8,
        "question": "What is the most expensive product?",
        "must_contain": ["Smartwatch", "2999"],
        "category": "filter"
    },
    {
        "id": 9,
        "question": "How many customers are from Bangalore?",
        "must_contain": ["2"],
        "category": "count"
    },
    {
        "id": 10,
        "question": "How many orders have status placed?",
        "must_contain": ["2"],
        "category": "count"
    },
    {
        "id": 11,
        "question": "Which payment methods are used?",
        "must_contain": ["upi", "card"],
        "category": "filter"
    },
    {
        "id": 12,
        "question": "How many payments failed?",
        "must_contain": ["1"],
        "category": "count"
    },
    {
        "id": 13,
        "question": "What is the cheapest product?",
        "must_contain": ["Notebook Set", "199"],
        "category": "filter"
    },
    {
        "id": 14,
        "question": "How many products are there in total?",
        "must_contain": ["12"],
        "category": "count"
    },
    {
        "id": 15,
        "question": "Which customers signed up in 2025?",
        "must_contain": ["2025"],
        "category": "filter"
    },
    {
        "id": 16,
        "question": "How many orders were shipped?",
        "must_contain": ["2"],
        "category": "count"
    },
    {
        "id": 17,
        "question": "What is the total number of orders?",
        "must_contain": ["15"],
        "category": "count"
    },
    {
        "id": 18,
        "question": "Which customer is from Chennai?",
        "must_contain": ["Meera Iyer"],
        "category": "filter"
    },
    {
        "id": 19,
        "question": "How many payments were successful?",
        "must_contain": ["13"],
        "category": "count"
    },
    {
        "id": 20,
        "question": "What are the product categories?",
        "must_contain": ["Electronics", "Clothing"],
        "category": "filter"
    },
]


def check_answer(answer: str, results: list, must_contain: list) -> bool:
    """
    Checks if the answer OR the raw results contain all required keywords/values.
    Case-insensitive.
    """
    combined = answer.lower() + " " + json.dumps(results).lower()
    return all(str(kw).lower() in combined for kw in must_contain)


def run_benchmark():
    print("=" * 65)
    print("  QueryGenie AI — Accuracy Benchmark")
    print("=" * 65)
    print(f"  Running {len(GOLDEN_SET)} test questions...\n")

    results_log = []
    passed = 0
    failed = 0
    errors = 0

    for test in GOLDEN_SET:
        try:
            start = time.time()
            output = run_pipeline(test["question"])
            elapsed = round(time.time() - start, 2)

            is_correct = check_answer(
                output["answer"],
                output["results"],
                test["must_contain"]
            )

            status = "✅ PASS" if is_correct else "❌ FAIL"
            if is_correct:
                passed += 1
            else:
                failed += 1

            print(f"[{test['id']:02d}] {status} | {test['question']}")
            if not is_correct:
                print(f"       Expected: {test['must_contain']}")
                print(f"       Got: {output['answer'][:100]}...")
            print(f"       SQL: {output['sql']}")
            print(f"       Time: {elapsed}s")
            print()

            results_log.append({
                "id": test["id"],
                "question": test["question"],
                "category": test["category"],
                "status": "pass" if is_correct else "fail",
                "sql": output["sql"],
                "answer": output["answer"],
                "time_seconds": elapsed,
            })

        except Exception as e:
            errors += 1
            print(f"[{test['id']:02d}] 💥 ERROR | {test['question']}")
            print(f"       Error: {str(e)[:100]}")
            print()
            results_log.append({
                "id": test["id"],
                "question": test["question"],
                "category": test["category"],
                "status": "error",
                "error": str(e),
            })

    # ─── Summary ──────────────────────────────────────────────────────────────
    total = len(GOLDEN_SET)
    accuracy = round((passed / total) * 100, 1)

    print("=" * 65)
    print(f"  RESULTS: {passed}/{total} passed | Accuracy: {accuracy}%")
    print(f"  ✅ Passed: {passed} | ❌ Failed: {failed} | 💥 Errors: {errors}")
    print("=" * 65)

    # Category breakdown
    categories = {}
    for r in results_log:
        cat = r.get("category", "other")
        if cat not in categories:
            categories[cat] = {"pass": 0, "total": 0}
        categories[cat]["total"] += 1
        if r.get("status") == "pass":
            categories[cat]["pass"] += 1

    print("\n  Category Breakdown:")
    for cat, stats in categories.items():
        cat_acc = round((stats["pass"] / stats["total"]) * 100)
        print(f"  {cat:15s} {stats['pass']}/{stats['total']} ({cat_acc}%)")

    # Save results
    summary = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "accuracy_percent": accuracy,
        "category_breakdown": categories,
        "results": results_log,
    }
    with open("benchmark_results.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Results saved to benchmark_results.json")
    print(f"\n  Resume bullet: 'Achieved {accuracy}% accuracy on a 20-question golden benchmark'")


if __name__ == "__main__":
    run_benchmark()
