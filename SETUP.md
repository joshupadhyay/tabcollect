# TabSweep Setup Guide

## Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
cd tabcollect
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 2. Add Your API Key

**Option A: Create .env file (easiest)**
```bash
cp .env.example .env
# Edit .env and paste your Anthropic API key
```

Your `.env` file should look like:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

**Option B: Export in terminal**
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### 3. Initialize Config
```bash
tabsweep init
```

Enter your Obsidian vault path when prompted (e.g., `~/Documents/Obsidian`)

### 4. Run Your First Session!
```bash
tabsweep session
```

Then paste some URLs:
```
https://github.com/anthropics/anthropic-sdk-python
https://leetcode.com/problems/two-sum
https://news.ycombinator.com
done
```

## Output Format

Your URLs will be saved to `{vault}/Sessions/YYYY-MM-DD Tab Sweep.md` as:

```markdown
## Learning & Tutorials
[[Anthropic Python SDK]](https://github.com/anthropics/anthropic-sdk-python) - Official Python library for Anthropic's Claude API with examples and documentation

## Interview Prep
[[Two Sum - LeetCode]](https://leetcode.com/problems/two-sum) - Classic hash table coding problem commonly asked in technical interviews

## Articles & Blogs
[[Hacker News]](https://news.ycombinator.com) - Technology news aggregator and discussion forum for programmers and entrepreneurs
```

## Configuration

Edit `~/.tabsweep/config.json` to:
- Change categories
- Add domain rules
- Switch AI model (default: `claude-3-5-haiku-latest`)

## Cost

Using Haiku, each session costs ~$0.0001-0.0002 per URL.

**Example:**
- 50 URLs = ~$0.01
- 500 URLs/month = ~$0.10/month

Super cheap! 🎉

## Troubleshooting

**"Error: ANTHROPIC_API_KEY not set"**
- Make sure you created `.env` file or exported the variable
- Check: `echo $ANTHROPIC_API_KEY`

**"Error: Vault path does not exist"**
- Run `tabsweep init` again
- Or manually edit `~/.tabsweep/config.json`

**No summaries appearing**
- Make sure you're using the latest code
- Try reinstalling: `uv pip install -e . --force-reinstall`
