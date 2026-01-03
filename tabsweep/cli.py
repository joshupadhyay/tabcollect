"""CLI interface for TabSweep."""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from tabsweep import classifier, config, database, output, scraper

# Load .env file if it exists
load_dotenv()

app = typer.Typer(help="Organize browser tabs into categorized Obsidian notes")
console = Console()


@app.command()
def init():
    """Initialize TabSweep configuration."""
    console.print("\n[bold cyan]TabSweep Configuration[/bold cyan]\n")

    # Prompt for vault path
    vault_path = Prompt.ask(
        "[yellow]Enter path to your Obsidian vault[/yellow]",
        default=str(Path.home() / "Documents" / "Obsidian")
    )

    # Expand and validate path
    vault_expanded = Path(vault_path).expanduser()
    if not vault_expanded.exists():
        console.print(f"\n[yellow]Warning: Path does not exist: {vault_expanded}[/yellow]")
        create = Prompt.ask("Create this directory?", choices=["y", "n"], default="y")
        if create == "y":
            vault_expanded.mkdir(parents=True, exist_ok=True)
        else:
            console.print("[red]Configuration cancelled.[/red]")
            raise typer.Exit(1)

    # Initialize config
    config.init_config(str(vault_expanded))

    console.print(f"\n[green]✓[/green] Config saved to [cyan]{config.get_config_path()}[/cyan]")
    console.print(f"[green]✓[/green] Vault path: [cyan]{vault_expanded}[/cyan]\n")


@app.command()
def session(debug: bool = typer.Option(False, "--debug", help="Include debug info in markdown output")):
    """Start a new tab collection session."""

    # Check config exists
    if not config.config_exists():
        console.print("[red]Error: Configuration not found. Run 'tabsweep init' first.[/red]")
        raise typer.Exit(1)

    cfg = config.load_config()

    # Check API key
    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[yellow]Warning: ANTHROPIC_API_KEY not set. LLM classification will be skipped.[/yellow]\n")

    # Validate vault path
    vault_path = Path(cfg["vault_path"])
    if not vault_path.exists():
        console.print(f"[red]Error: Vault path does not exist: {vault_path}[/red]")
        raise typer.Exit(1)

    # Show welcome animation
    console.print()
    console.print(Panel.fit(
        "[bold cyan]📚 Tab Sweep Session[/bold cyan]\n"
        "[dim]Organizing your browser tabs...[/dim]",
        border_style="cyan"
    ))
    console.print()

    # Collect URLs
    console.print("[yellow]Paste URLs (one per line). Type 'done' or press Ctrl+D when finished.[/yellow]\n")

    urls = []
    try:
        while True:
            line = input().strip()
            if line.lower() == "done":
                break
            if line:
                urls.append(line)
    except EOFError:
        pass  # Ctrl+D pressed

    console.print()

    # Extract and deduplicate URLs
    url_pattern = re.compile(r'https?://[^\s]+')
    extracted_urls = []
    for line in urls:
        extracted_urls.extend(url_pattern.findall(line))

    # Deduplicate
    unique_urls = list(dict.fromkeys(extracted_urls))

    if not unique_urls:
        console.print("[yellow]No URLs found. Exiting.[/yellow]")
        raise typer.Exit(0)

    console.print(f"[cyan]Found {len(unique_urls)} unique URLs[/cyan]\n")

    # Check for duplicates in database
    duplicates = []
    for url in unique_urls:
        is_dup, orig_date = database.check_duplicate(url)
        if is_dup:
            duplicates.append((url, orig_date))

    if duplicates:
        console.print(f"[yellow]⚠  {len(duplicates)} duplicate(s) found (will still process):[/yellow]")
        for url, orig_date in duplicates[:3]:  # Show first 3
            console.print(f"   [dim]{url[:60]}... (from {orig_date})[/dim]")
        if len(duplicates) > 3:
            console.print(f"   [dim]... and {len(duplicates) - 3} more[/dim]")
        console.print()

    # Classification pipeline
    classified = []
    session_date = datetime.now().strftime("%Y-%m-%d")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Step 1: Scrape metadata for ALL URLs
        task1 = progress.add_task(f"[cyan]Scraping {len(unique_urls)} URLs...", total=len(unique_urls))

        scraped_data = []
        for url in unique_urls:
            title, description = scraper.scrape_metadata(url)
            scraped_data.append({
                "url": url,
                "title": title,
                "description": description
            })
            progress.update(task1, advance=1)

        progress.update(task1, completed=True)
        console.print(f"[green]✓[/green] Metadata scraped")

        # Step 2: Classify ALL URLs with AI in batches
        batch_size = 10
        batches = [scraped_data[i:i+batch_size] for i in range(0, len(scraped_data), batch_size)]

        task2 = progress.add_task(f"[cyan]Classifying with AI ({len(batches)} batches)...", total=len(batches))

        for batch in batches:
            results = classifier.classify_batch_with_llm(batch, cfg["categories"], cfg["model"])

            for i, result in enumerate(results):
                classified.append({
                    "url": batch[i]["url"],
                    "category": result["category"],
                    "title": result.get("title") or batch[i].get("title") or batch[i]["url"],
                    "confidence": result.get("confidence", 0),
                    "reason": result.get("reason", ""),
                    "summary": result.get("summary", "")
                })

            progress.update(task2, advance=1)

        progress.update(task2, completed=True)
        console.print(f"[green]✓[/green] AI classification complete")

    # Show results
    console.print()
    for item in classified:
        emoji = "✓" if item["category"] != "Uncategorized" else "?"
        conf_str = f"confidence: {item['confidence']:.2f}" if item.get("confidence") else "rule-based"

        # Truncate URL for display
        display_url = item["url"][:60] + "..." if len(item["url"]) > 60 else item["url"]

        console.print(f"[green]{emoji}[/green] {display_url} → [cyan]{item['category']}[/cyan] [dim]({conf_str})[/dim]")

    # Generate markdown
    markdown_content = output.generate_markdown(classified, debug=debug)

    # Write to vault
    output_file = output.write_session_file(cfg["vault_path"], markdown_content)

    # Update database
    database.add_urls_batch([(item["url"], item["category"]) for item in classified], session_date)

    # Final summary
    console.print()
    console.print(Panel.fit(
        f"[bold green]✅ Session Complete[/bold green]\n\n"
        f"[cyan]{len(classified)}[/cyan] URLs categorized\n"
        f"Saved to [cyan]{output_file}[/cyan]",
        border_style="green"
    ))
    console.print()


if __name__ == "__main__":
    app()
