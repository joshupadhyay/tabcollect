# TabSweep

To beat my own procrastination, and having 100 tabs open. I simply export all the links after I use `tab session`, then I write `done`, then that's all stored for Obsidian. It's for the hoarder who can't *stand* to have an important link lost. 

Throwaway code, this one. I'll have to make it better but served the purpose. 

A CLI tool to categorize and organize browser tabs into Obsidian notes using rule-based classification and AI.

## Features

- 📚 Interactive URL collection from stdin
- 🎯 AI-powered classification using Anthropic Claude (Haiku - super cheap!)
- 🔄 Batch processing for efficiency (10 URLs per API call)
- 📝 Clean Markdown output to Obsidian vault
- 🎨 Beautiful terminal UI with progress indicators
- 💾 Duplicate detection and tracking
- 🌐 Web scraping for accurate titles

## Installation

```bash
# Using uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

## Quick Start

### 1. Initialize Configuration

```bash
tabsweep init
```

This will prompt you for your Obsidian vault path and create `~/.tabsweep/config.json`.

### 2. Set API Key

**Option A: Create `.env` file (recommended)**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your key
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Option B: Environment variable**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Option C: Add to shell profile**
```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key-here' >> ~/.zshrc
```

### 3. Start a Session

```bash
tabsweep session
```

Then paste URLs (one per line, or space-separated), and type `done` or press Ctrl+D when finished.

## Usage

### Interactive Session

```bash
$ tabsweep session
Paste URLs (one per line). Type 'done' or Ctrl+D when finished.

https://greenhouse.io/company/role
https://leetcode.com/problems/two-sum
https://example.com/article
done
```

### Debug Mode

Include confidence scores and reasons in the markdown output:

```bash
tabsweep session --debug
```

## Configuration

Configuration is stored in `~/.tabsweep/config.json`:

```json
{
  "vault_path": "~/Documents/Obsidian",
  "model": "claude-3-5-haiku-latest",
  "categories": [...],
  "rules": [...]
}
```

**Note:** Using Haiku keeps costs extremely low. You can change to `claude-3-5-sonnet-latest` if you want better accuracy, but Haiku works great for URL classification.

You can manually edit this file to:
- Add custom categories
- Define domain-based rules
- Change the AI model

## Output Format

TabSweep creates files in `{vault_path}/Sessions/YYYY-MM-DD Tab Sweep.md`:

```markdown
# Tab Sweep - 2026-01-02

## Job Applications
[[Senior Engineer at Acme Corp]](https://greenhouse.io/acme/senior-engineer) - Backend position focusing on distributed systems and scalability
[[Backend Developer]](https://lever.co/company/backend) - Full-stack role with emphasis on API development

## Interview Prep
[[Two Sum - LeetCode]](https://leetcode.com/problems/two-sum) - Classic hash table problem for coding interviews
```

The format uses Obsidian-style `[[links]]` with AI-generated summaries for each URL.

## Default Categories

- Job Applications
- Interview Prep
- Learning & Tutorials
- Tools & Resources
- Articles & Blogs
- Reference
- Shopping & Products
- Social & Entertainment
- Maybe (low confidence)
- Uncategorized (fallback)

## Development

```bash
# Install dependencies
uv pip install -e .

# Run from source
python -m tabsweep init
python -m tabsweep session
```

## License

MIT
