# Changelog

## [0.1.0] - 2026-01-02

### Changed
- **All URLs now classified with AI** - No more lazy rule-based-only classification!
- Switched default model to `claude-3-5-haiku-latest` for super cheap classification
- Simplified pipeline: Scrape all URLs → Classify all URLs with AI
- Removed separate rule-based classification path

### Features
- Interactive URL collection (paste URLs, type 'done' or Ctrl+D)
- Batch AI classification (10 URLs per API call)
- Web scraping for page titles and descriptions
- Beautiful terminal UI with Rich library
- Duplicate detection and tracking
- Clean Markdown output to Obsidian vault
- Debug mode for confidence scores

### Pricing
With Haiku, classifying URLs is incredibly cheap:
- ~$0.25 per million input tokens
- ~$1.25 per million output tokens
- Classifying 100 URLs with titles ≈ $0.01-0.02

### Usage
```bash
# Initialize
tabsweep init

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run session
tabsweep session
```
