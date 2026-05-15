"""APIFlow CLI -- multi-agent API testing and documentation pipeline."""

import sys
import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.utils.api import APIFlowConfig, DeepSeekClient
from src.agents.analyzer import analyze
from src.agents.tester import generate_tests
from src.agents.documenter import generate_docs
from src.agents.validator import validate

console = Console()

PIPELINE_NAME = "APIFlow"


def _print_banner():
    """Print startup banner."""
    console.print(Panel.fit(
        "[bold]APIFlow[/] -- Multi-Agent API Testing & Documentation Pipeline\n"
        "Pipeline: Analyzer >> Tester >> Documenter >> Validator\n"
        "Powered by DeepSeek API",
        border_style="blue"
    ))


def _print_agent_header(name: str):
    """Print agent stage header."""
    console.print(f"\n>> Running [bold cyan]{name}[/bold cyan] agent...", style="bold")


def _print_result_summary(label: str, data: dict):
    """Print a brief summary of agent output."""
    if "error" in data:
        console.print(f"   [red][FAIL][/]{label}: {data['error']}")
    else:
        console.print(f"   [green][OK][/]{label}")


def _save_json(data: dict, filepath: str):
    """Save dict as formatted JSON."""
    path = Path(filepath)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"   Saved to {path}")


@click.group()
@click.version_option(version="0.1.0", prog_name="apiflow")
def cli():
    """APIFlow -- AI-powered multi-agent API testing & documentation pipeline.

    Four agents collaborate in sequence:
    Analyzer >> Tester >> Documenter >> Validator
    """


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.option("--base-url", default="http://localhost:5000", help="API base URL for test requests")
@click.option("--output", "-o", default="apiflow_report.json", help="Save full report to JSON file")
@click.option("--model", envvar="APIFLOW_MODEL", default=None, help="Model name override")
@click.option("--temperature", default=0.3, help="LLM temperature (0.0-1.0)")
def run(source, base_url, output, model, temperature):
    """Run the full pipeline on a SOURCE file containing API code."""
    _print_banner()

    config = APIFlowConfig.from_env()
    if model:
        config.model = model
    config.temperature = temperature

    console.print(f"Source: {source}")
    console.print(f"Base URL: {base_url}")
    console.print(f"Model: {config.model}")

    try:
        client = DeepSeekClient(config)
    except ValueError as e:
        console.print(f"[red]Configuration Error:[/] {e}")
        console.print("[dim]Make sure DEEPSEEK_API_KEY is set in your .env file[/]")
        sys.exit(1)

    # Read source code
    source_code = Path(source).read_text(encoding="utf-8")

    # Stage 1: Analyzer
    _print_agent_header("Analyzer")
    analysis = analyze(source_code, client)
    _print_result_summary("Endpoint analysis complete", analysis)

    ep_count = analysis.get("total_endpoints", len(analysis.get("endpoints", [])))
    console.print(f"   Found {ep_count} endpoint(s)")

    if ep_count == 0:
        console.print("[yellow]No endpoints found. Stopping pipeline.[/]")
        sys.exit(0)

    # Stage 2: Tester
    _print_agent_header("Tester")
    tests = generate_tests(analysis, client)
    _print_result_summary("Test generation complete", tests)

    test_count = tests.get("total_tests", 0)
    console.print(f"   Generated {test_count} test case(s)")

    # Stage 3: Documenter
    _print_agent_header("Documenter")
    docs = generate_docs(analysis, client)
    _print_result_summary("OpenAPI documentation generated", docs)

    # Stage 4: Validator
    _print_agent_header("Validator")
    validation = validate(analysis, tests, docs, client)
    _print_result_summary("Validation complete", validation)

    # Print validation summary
    score = validation.get("score", "N/A")
    passed = validation.get("validation_passed", False)
    status = "[green]PASSED[/]" if passed else "[red]FAILED[/]"
    console.print(f"\n   Validation: {status}  Score: {score}/100")

    # Print issues
    issues = validation.get("issues", [])
    if issues:
        console.print("\n[bold]Issues:[/]")
        for issue in issues:
            sev = issue.get("severity", "info")
            console.print(f"   [{sev}] {issue.get('description', '')}")

    # Print recommendations
    recs = validation.get("recommendations", [])
    if recs:
        console.print("\n[bold]Recommendations:[/]")
        for rec in recs:
            console.print(f"   - {rec}")

    # Save report
    report = {
        "source": source,
        "base_url": base_url,
        "model": config.model,
        "analysis": analysis,
        "tests": tests,
        "documentation": docs,
        "validation": validation,
    }

    if output:
        _save_json(report, output)

    console.print(Panel.fit(
        f"[bold]Pipeline Complete[/]\n"
        f"Endpoints: {ep_count}  |  Tests: {test_count}  |  Score: {score}/100",
        border_style="green" if passed else "red"
    ))


@cli.command()
@click.argument("source", type=click.Path(exists=True))
def analyze_only(source):
    """Run only the Analyzer agent on a SOURCE file."""
    _print_banner()
    config = APIFlowConfig.from_env()
    try:
        client = DeepSeekClient(config)
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)

    source_code = Path(source).read_text(encoding="utf-8")

    _print_agent_header("Analyzer")
    result = analyze(source_code, client)
    _print_result_summary("Endpoint analysis", result)

    _save_json(result, "apiflow_analysis.json")
    console.print("[green][OK] Analysis complete.[/]")


@cli.command()
def config():
    """Show current configuration."""
    cfg = APIFlowConfig.from_env()
    console.print(f"API Base:  {cfg.base_url}")
    console.print(f"Model:     {cfg.model}")
    key_display = "***" + cfg.api_key[-4:] if cfg.api_key and len(cfg.api_key) >= 4 else "NOT SET"
    console.print(f"API Key:   {key_display}")
    console.print(f"Temp:      {cfg.temperature}")
    console.print(f"Timeout:   {cfg.timeout}s")


if __name__ == "__main__":
    cli()
