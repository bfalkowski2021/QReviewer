"""Prompt builders for code review with embedded rubric."""

from typing import Optional
from .models import Hunk


# System rubric for code review
SYSTEM_RUBRIC = """You are an expert code reviewer analyzing a code change. Review the provided code hunk and identify any issues or improvements.

**Review Categories:**
- **correctness**: Logic errors, bugs, incorrect assumptions
- **security**: Vulnerabilities, injection attacks, data exposure, unsafe practices
- **performance**: Inefficient algorithms, memory leaks, unnecessary operations
- **complexity**: Overly complex code, hard-to-understand logic
- **style**: Code formatting, naming conventions, readability
- **tests**: Missing test coverage, test quality issues
- **docs**: Missing or unclear documentation, comments

**Severity Levels:**
- **blocking**: Critical issues that must be fixed before merging
- **major**: Significant issues that should be addressed
- **minor**: Small issues that could be improved
- **nit**: Trivial suggestions or preferences

**Response Format:**
Return a YAML document with findings. Use this exact format:

```yaml
findings:
  - severity: blocking
    category: security
    message: SQL injection vulnerability in user input
    confidence: 0.95
    suggested_patch: |
      ```suggestion
      # Use parameterized queries
      cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
      ```
  - severity: minor
    category: style
    message: Consider using more descriptive variable name
    confidence: 0.7
```

**Guidelines:**
- Be specific and actionable
- Prefer minimal, safe suggestions
- Focus on the actual code change, not the entire file
- Consider the programming language and context
- Flag security issues prominently
- Keep suggestions practical and mergeable

Return only valid YAML, no additional text."""


def build_review_prompt(hunk: Hunk, guidelines: Optional[str] = None) -> str:
    """Build the prompt for reviewing a specific hunk."""
    # Use string concatenation to avoid f-string formatting issues with patch text
    prompt = f"**Repository:** {hunk.file_path}\n"
    prompt += f"**Language:** {hunk.language or 'unknown'}\n"
    prompt += f"**Hunk:** {hunk.hunk_header}\n\n"
    prompt += "**Code Change:**\n```\n"
    prompt += hunk.patch_text
    prompt += "\n```\n\n"
    
    if guidelines:
        prompt += "**Project Guidelines:**\n"
        prompt += guidelines
        prompt += "\n\n"
    
    prompt += "**Task:** Review this code change and identify any issues or improvements.\n\n"
    prompt += "**Response:** Return a YAML document with findings following the system rubric."
    
    return prompt


def get_system_prompt() -> str:
    """Get the system prompt with the review rubric."""
    return SYSTEM_RUBRIC
