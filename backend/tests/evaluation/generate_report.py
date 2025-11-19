#!/usr/bin/env python3
"""
Generate HTML report from Ragas evaluation results.

This script takes JSON evaluation results and generates a comprehensive
HTML report with visualizations and metric explanations.

Usage:
    # Generate report from latest result
    python generate_report.py

    # Generate report from specific result file
    python generate_report.py --input results/ragas_comprehensive_20250119_143022.json

    # Specify output file
    python generate_report.py --output custom_report.html
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ragas Evaluation Report - NC-ASK</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}

        h2 {{
            color: #2c3e50;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}

        h3 {{
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 15px;
        }}

        .meta-info {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}

        .meta-info p {{
            margin: 5px 0;
        }}

        .meta-info strong {{
            color: #2c3e50;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .metric-card {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 20px;
            border-radius: 5px;
            transition: transform 0.2s;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}

        .metric-name {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .metric-score {{
            font-size: 36px;
            font-weight: 700;
            margin: 15px 0;
        }}

        .score-excellent {{ color: #27ae60; }}
        .score-good {{ color: #f39c12; }}
        .score-poor {{ color: #e74c3c; }}

        .metric-description {{
            font-size: 14px;
            color: #7f8c8d;
            line-height: 1.5;
        }}

        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }}

        .progress-excellent {{ background: linear-gradient(90deg, #27ae60, #2ecc71); }}
        .progress-good {{ background: linear-gradient(90deg, #f39c12, #f1c40f); }}
        .progress-poor {{ background: linear-gradient(90deg, #e74c3c, #c0392b); }}

        .interpretation {{
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 3px;
        }}

        .interpretation h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .recommendations {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 3px;
        }}

        .recommendations h4 {{
            color: #856404;
            margin-bottom: 10px;
        }}

        .recommendations ul {{
            margin-left: 20px;
            margin-top: 10px;
        }}

        .recommendations li {{
            margin: 5px 0;
            color: #856404;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}

        th {{
            background: #34495e;
            color: white;
            font-weight: 600;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Ragas Evaluation Report - NC-ASK RAG Pipeline</h1>

        <div class="meta-info">
            <p><strong>Evaluation Run:</strong> {run_name}</p>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <p><strong>Metrics Evaluated:</strong> {metrics_list}</p>
        </div>

        <h2>📊 Evaluation Results</h2>

        <div class="metrics-grid">
            {metric_cards}
        </div>

        <h2>📈 Detailed Metrics</h2>
        {detailed_metrics}

        <h2>💡 Interpretation</h2>
        <div class="interpretation">
            <h4>Overall Assessment</h4>
            {interpretation}
        </div>

        {recommendations_section}

        <div class="footer">
            <p>Generated by NC-ASK Ragas Evaluation System</p>
            <p>{generation_time}</p>
        </div>
    </div>
</body>
</html>
"""


METRIC_DESCRIPTIONS = {
    "faithfulness": "Measures whether the generated answer is grounded in the retrieved contexts. Higher scores indicate better factual consistency with the source material.",
    "answer_relevancy": "Measures how relevant the generated answer is to the question. Higher scores indicate that the answer directly addresses what was asked.",
    "context_recall": "Measures whether the retrieved contexts contain all relevant information from the ground truth. Higher scores indicate better retrieval coverage.",
    "context_precision": "Measures whether the top-ranked contexts are the most relevant ones. Higher scores indicate better ranking quality in the retrieval system.",
    "answer_correctness": "Measures the overall quality of the generated answer compared to ground truth. Considers both factual and semantic correctness.",
    "context_relevancy": "Measures whether the retrieved contexts are relevant to the question. Higher scores indicate better retrieval relevance.",
}


def get_score_class(score: float) -> str:
    """Get CSS class based on score value."""
    if score >= 0.7:
        return "excellent"
    elif score >= 0.5:
        return "good"
    else:
        return "poor"


def generate_metric_card(metric_name: str, score: float) -> str:
    """Generate HTML for a single metric card."""
    score_class = get_score_class(score)
    description = METRIC_DESCRIPTIONS.get(metric_name, "No description available")
    percentage = score * 100

    return f"""
    <div class="metric-card">
        <div class="metric-name">{metric_name.replace('_', ' ').title()}</div>
        <div class="metric-score score-{score_class}">{score:.4f}</div>
        <div class="progress-bar">
            <div class="progress-fill progress-{score_class}" style="width: {percentage}%"></div>
        </div>
        <div class="metric-description">{description}</div>
    </div>
    """


def generate_detailed_metrics_table(summary: dict[str, float]) -> str:
    """Generate detailed metrics table."""
    rows = []
    for metric, score in summary.items():
        if score is not None:
            score_class = get_score_class(score)
            status = "✓ Excellent" if score >= 0.7 else "⚠ Good" if score >= 0.5 else "✗ Needs Improvement"
            rows.append(f"""
                <tr>
                    <td><strong>{metric.replace('_', ' ').title()}</strong></td>
                    <td>{score:.4f}</td>
                    <td><span class="score-{score_class}">{status}</span></td>
                </tr>
            """)

    return f"""
    <table>
        <thead>
            <tr>
                <th>Metric</th>
                <th>Score</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """


def generate_interpretation(summary: dict[str, float]) -> str:
    """Generate interpretation of results."""
    avg_score = sum(s for s in summary.values() if s is not None) / len([s for s in summary.values() if s is not None])

    if avg_score >= 0.7:
        overall = "The RAG pipeline is performing excellently across all evaluated metrics."
    elif avg_score >= 0.5:
        overall = "The RAG pipeline is performing adequately, with room for improvement in some areas."
    else:
        overall = "The RAG pipeline needs significant improvement across multiple metrics."

    specific_notes = []

    if "faithfulness" in summary:
        if summary["faithfulness"] < 0.6:
            specific_notes.append("Faithfulness is below optimal levels, indicating that answers may not be fully grounded in retrieved contexts.")

    if "answer_relevancy" in summary:
        if summary["answer_relevancy"] < 0.6:
            specific_notes.append("Answer relevancy could be improved to better address user questions.")

    if "context_recall" in summary:
        if summary["context_recall"] < 0.6:
            specific_notes.append("Context recall is low, suggesting that retrieval may be missing relevant information.")

    if "context_precision" in summary:
        if summary["context_precision"] < 0.6:
            specific_notes.append("Context precision needs improvement to better rank the most relevant documents.")

    interpretation_html = f"<p>{overall}</p>"
    if specific_notes:
        interpretation_html += "<ul>"
        for note in specific_notes:
            interpretation_html += f"<li>{note}</li>"
        interpretation_html += "</ul>"

    return interpretation_html


def generate_recommendations(summary: dict[str, float]) -> str:
    """Generate recommendations based on results."""
    recommendations = []

    if "faithfulness" in summary and summary["faithfulness"] < 0.7:
        recommendations.append("Improve faithfulness by refining prompts to emphasize staying grounded in provided context")
        recommendations.append("Review and improve the quality of source documents")

    if "answer_relevancy" in summary and summary["answer_relevancy"] < 0.7:
        recommendations.append("Enhance answer relevancy by improving prompt engineering")
        recommendations.append("Consider adding query expansion or reformulation")

    if "context_recall" in summary and summary["context_recall"] < 0.7:
        recommendations.append("Improve retrieval by tuning the TOP_K_RETRIEVAL parameter")
        recommendations.append("Consider using a different embedding model or adjusting chunk size")

    if "context_precision" in summary and summary["context_precision"] < 0.7:
        recommendations.append("Improve ranking by adjusting similarity thresholds")
        recommendations.append("Consider implementing re-ranking strategies")

    if not recommendations:
        recommendations.append("Maintain current performance levels with regular monitoring")
        recommendations.append("Consider A/B testing for further optimization")

    if recommendations:
        recs_html = '<div class="recommendations"><h4>🎯 Recommendations</h4><ul>'
        for rec in recommendations:
            recs_html += f"<li>{rec}</li>"
        recs_html += "</ul></div>"
        return recs_html
    return ""


def generate_html_report(results_data: dict[str, Any]) -> str:
    """Generate complete HTML report from results data."""
    summary = results_data.get("summary", {})
    run_name = results_data.get("run_name", "Unknown")
    timestamp = results_data.get("timestamp", "Unknown")
    metrics_list = ", ".join(results_data.get("metrics", []))

    # Generate metric cards
    metric_cards = "".join([
        generate_metric_card(metric, score)
        for metric, score in summary.items()
        if score is not None
    ])

    # Generate detailed metrics table
    detailed_metrics = generate_detailed_metrics_table(summary)

    # Generate interpretation
    interpretation = generate_interpretation(summary)

    # Generate recommendations
    recommendations_section = generate_recommendations(summary)

    # Generate timestamp
    generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fill template
    html = HTML_TEMPLATE.format(
        run_name=run_name,
        timestamp=timestamp,
        metrics_list=metrics_list,
        metric_cards=metric_cards,
        detailed_metrics=detailed_metrics,
        interpretation=interpretation,
        recommendations_section=recommendations_section,
        generation_time=generation_time,
    )

    return html


def main():
    parser = argparse.ArgumentParser(description="Generate HTML report from Ragas evaluation results")
    parser.add_argument(
        "--input",
        type=Path,
        help="Input JSON results file (default: latest file in results/)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output HTML file (default: results/report_<timestamp>.html)"
    )

    args = parser.parse_args()

    # Determine input file
    results_dir = Path(__file__).parent / "results"

    if args.input:
        input_file = args.input
    else:
        # Find latest results file
        json_files = list(results_dir.glob("ragas_*.json"))
        if not json_files:
            print("Error: No results files found in results/")
            print("Run an evaluation first using run_evaluation.py")
            sys.exit(1)

        input_file = max(json_files, key=lambda p: p.stat().st_mtime)
        print(f"Using latest results file: {input_file.name}")

    # Load results
    try:
        with open(input_file) as f:
            results_data = json.load(f)
    except Exception as e:
        print(f"Error loading results file: {e}")
        sys.exit(1)

    # Generate HTML
    html = generate_html_report(results_data)

    # Determine output file
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = results_dir / f"report_{timestamp}.html"

    # Write HTML
    try:
        with open(output_file, "w") as f:
            f.write(html)
        print(f"\n✓ Report generated successfully!")
        print(f"  Output: {output_file}")
        print(f"\nOpen in browser:")
        print(f"  open {output_file}")
    except Exception as e:
        print(f"Error writing report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()
