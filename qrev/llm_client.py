"""Multi-backend LLM client for QReviewer."""

import json
import logging
import subprocess
import asyncio
import re
import yaml
from typing import List, Optional, Dict, Any
from .models import Hunk, Finding
from .prompts import get_system_prompt, build_review_prompt
from .config import config

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """LLM client error."""
    pass


class BaseLLMClient:
    """Base class for LLM clients."""
    
    def __init__(self):
        self.config = config
    
    async def review_hunk(self, hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
        """Review a code hunk using the configured LLM backend."""
        raise NotImplementedError("Subclasses must implement review_hunk")
    
    def _parse_findings_response(self, response_text: str, hunk: Hunk) -> List[Finding]:
        """Parse LLM response into Finding objects."""
        try:
            # Q CLI returns formatted text with ANSI color codes, clean it up
            import re
            
            # Strip ANSI color codes
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            clean_text = ansi_escape.sub('', response_text).strip()
            
            # Remove Q CLI prompt prefix ("> ")
            if clean_text.startswith('> '):
                clean_text = clean_text[2:].strip()
            
            # Remove any remaining control characters that could break YAML parsing
            clean_text = ''.join(char for char in clean_text if ord(char) >= 32 or char in '\n\r\t')
            
            # Debug: log the cleaned response
            logger.debug(f"Cleaned Q CLI response: {repr(clean_text[:200])}")
            
            # Look for YAML content in the response
            # Try to find YAML block between ```yaml and ``` markers
            yaml_match = re.search(r'```yaml\s*\n(.*?)\n```', clean_text, re.DOTALL)
            if yaml_match:
                yaml_text = yaml_match.group(1)
            else:
                # Look for findings: section
                findings_match = re.search(r'findings:\s*\n(.*)', clean_text, re.DOTALL)
                if findings_match:
                    yaml_text = f"findings:\n{findings_match.group(1)}"
                else:
                    # Use the entire cleaned text
                    yaml_text = clean_text
                
            logger.debug(f"Extracted YAML: {repr(yaml_text[:200])}")
            
            # Try to parse as YAML
            findings_data = yaml.safe_load(yaml_text)
            
            # Handle different response formats
            if isinstance(findings_data, dict) and "findings" in findings_data:
                findings_list = findings_data["findings"]
            elif isinstance(findings_data, list):
                findings_list = findings_data
            else:
                logger.warning(f"Unexpected response format: {type(findings_data)}")
                return self._create_dummy_finding(hunk, "Unexpected response format")
            
            findings = []
            for finding_data in findings_list:
                if isinstance(finding_data, dict):
                    finding = Finding(
                        file=hunk.file_path,
                        hunk_header=hunk.hunk_header,
                        severity=finding_data.get("severity", "info"),
                        category=finding_data.get("category", "general"),
                        message=finding_data.get("message", "No message provided"),
                        confidence=finding_data.get("confidence", 0.5),
                        suggested_patch=finding_data.get("suggested_patch"),
                        line_hint=hunk.end_line
                    )
                    findings.append(finding)
            
            return findings if findings else self._create_dummy_finding(hunk, "No findings generated")
            
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML response: {e}")
            return self._create_dummy_finding(hunk, f"Failed to parse response: {e}")
        except Exception as e:
            logger.error(f"Error parsing findings: {e}")
            return self._create_dummy_finding(hunk, f"Error parsing findings: {e}")
    
    def _create_dummy_finding(self, hunk: Hunk, message: str) -> List[Finding]:
        """Create a dummy finding when parsing fails."""
        return [Finding(
            file=hunk.file_path,
            hunk_header=hunk.hunk_header,
            severity="info",
            category="system",
            message=f"LLM response parsing failed: {message}",
            confidence=0.1,
            suggested_patch=None,
            line_hint=hunk.end_line
        )]


class AmazonQCLIClient(BaseLLMClient):
    """Amazon Q CLI client using local execution or SSH to remote machine."""
    
    def __init__(self):
        super().__init__()
        self.q_config = self.config.llm_config
    
    async def review_hunk(self, hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
        """Review a code hunk using Amazon Q CLI."""
        try:
            logger.info(f"Starting Q CLI review for {hunk.file_path} ({hunk.hunk_header})")
            
            # Build the prompt
            system_prompt = get_system_prompt()
            user_prompt = build_review_prompt(hunk, guidelines)
            
            # Create the Q CLI command
            q_command = self._build_q_command(system_prompt, user_prompt)
            logger.debug(f"Q CLI command built for {hunk.file_path}")
            
            # Execute Q CLI command
            if self.q_config.get("local", True):
                logger.debug(f"Executing Q CLI locally for {hunk.file_path}")
                response = await self._execute_local_command(q_command)
            else:
                logger.debug(f"Executing Q CLI via SSH for {hunk.file_path}")
                response = await self._execute_ssh_command(q_command)
            
            logger.info(f"Q CLI response received for {hunk.file_path}")
            
            # Parse the response
            findings = self._parse_findings_response(response, hunk)
            logger.info(f"Parsed {len(findings)} findings for {hunk.file_path}")
            return findings
            
        except Exception as e:
            logger.error(f"Amazon Q CLI error: {e}")
            return self._create_dummy_finding(hunk, f"Amazon Q CLI error: {e}")
    
    def _build_q_command(self, system_prompt: str, user_prompt: str) -> str:
        """Build the Q CLI command for code review."""
        # Create a focused code review prompt that requests only YAML
        # Use string concatenation to avoid f-string formatting issues
        review_prompt = "Review this code and respond with ONLY a YAML document of findings. No other text, explanations, or formatting.\n\n"
        review_prompt += user_prompt
        review_prompt += "\n\nReturn YAML document with this exact format:\n\n"
        review_prompt += "```yaml\n"
        review_prompt += "findings:\n"
        review_prompt += "  - severity: minor\n"
        review_prompt += "    category: style\n"
        review_prompt += "    message: Consider adding documentation\n"
        review_prompt += "    confidence: 0.8\n"
        review_prompt += "  - severity: major\n"
        review_prompt += "    category: security\n"
        review_prompt += "    message: Potential SQL injection vulnerability\n"
        review_prompt += "    confidence: 0.9\n"
        review_prompt += "    suggested_patch: |\n"
        review_prompt += "      Use parameterized queries instead\n"
        review_prompt += "```\n\n"
        review_prompt += "RESPOND WITH ONLY THE YAML DOCUMENT:"
        
        # Write prompt to a temporary file to avoid shell escaping issues
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(review_prompt)
            temp_file = f.name
        
        # Use q chat with file input and trust all tools for non-interactive mode
        return f'q chat --no-interactive --trust-all-tools "$(cat {temp_file})" && rm {temp_file}'
    
    async def _execute_local_command(self, command: str) -> str:
        """Execute Q CLI command locally."""
        logger.debug(f"Executing local Q CLI command: {command}")
        
        try:
            # Execute the command locally
            process = await asyncio.create_subprocess_exec(
                "bash", "-c", command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.review_timeout_sec
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown Q CLI error"
                raise LLMClientError(f"Q CLI command failed: {error_msg}")
            
            response = stdout.decode().strip()
            if not response:
                raise LLMClientError("Empty response from Q CLI")
            
            # Strip ANSI color codes and control characters
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            response = ansi_escape.sub('', response)
            
            # Remove Q CLI prompt prefix ("> ")
            if response.startswith('> '):
                response = response[2:]
            
            # Clean up any remaining formatting
            response = response.strip()
            
            return response
            
        except asyncio.TimeoutError:
            raise LLMClientError(f"Q CLI command timed out after {self.config.review_timeout_sec} seconds")
        except Exception as e:
            raise LLMClientError(f"Local Q CLI execution error: {e}")
    
    async def _execute_ssh_command(self, command: str) -> str:
        """Execute a command on the remote Q machine via SSH."""
        ssh_config = self.q_config
        
        # Build SSH command
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=30",
            "-p", str(ssh_config["port"]),
        ]
        
        # Add SSH key if specified
        if ssh_config.get("key_path"):
            ssh_cmd.extend(["-i", ssh_config["key_path"]])
        
        # Add user@host
        ssh_cmd.append(f"{ssh_config['user']}@{ssh_config['host']}")
        
        # Add the Q command
        ssh_cmd.append(command)
        
        logger.debug(f"Executing SSH command: {' '.join(ssh_cmd)}")
        
        try:
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.review_timeout_sec
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown SSH error"
                raise LLMClientError(f"SSH command failed: {error_msg}")
            
            response = stdout.decode().strip()
            if not response:
                raise LLMClientError("Empty response from Q CLI")
            
            # Strip ANSI color codes and control characters
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            response = ansi_escape.sub('', response)
            
            # Remove Q CLI prompt prefix ("> ")
            if response.startswith('> '):
                response = response[2:]
            
            # Clean up any remaining formatting
            response = response.strip()
            
            return response
            
        except asyncio.TimeoutError:
            raise LLMClientError(f"SSH command timed out after {self.config.review_timeout_sec} seconds")
        except Exception as e:
            raise LLMClientError(f"SSH execution error: {e}")


class BedrockClient(BaseLLMClient):
    """AWS Bedrock client for fallback LLM access."""
    
    def __init__(self):
        super().__init__()
        self.bedrock_config = self.config.llm_config
    
    async def review_hunk(self, hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
        """Review a code hunk using AWS Bedrock."""
        try:
            logger.info(f"Starting Bedrock review for {hunk.file_path} ({hunk.hunk_header})")
            
            # Import boto3 here to avoid dependency issues
            import boto3
            from botocore.exceptions import ClientError
            
            # Create Bedrock client
            logger.debug(f"Creating Bedrock client for {hunk.file_path}")
            bedrock = boto3.client(
                'bedrock-runtime',
                region_name=self.bedrock_config["region"],
                aws_access_key_id=self.bedrock_config["access_key_id"],
                aws_secret_access_key=self.bedrock_config["secret_access_key"]
            )
            
            # Build the prompt
            system_prompt = get_system_prompt()
            user_prompt = build_review_prompt(hunk, guidelines)
            logger.debug(f"Prompt built for {hunk.file_path}")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Call Bedrock
            logger.debug(f"Calling Bedrock API for {hunk.file_path}")
            response = bedrock.invoke_model(
                modelId=self.bedrock_config["model_id"],
                body=json.dumps({
                    "messages": messages,
                    "max_tokens": 2048,
                    "temperature": 0.1
                })
            )
            
            logger.info(f"Bedrock response received for {hunk.file_path}")
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            findings = self._parse_findings_response(content, hunk)
            logger.info(f"Parsed {len(findings)} findings for {hunk.file_path}")
            return findings
            
        except ImportError:
            logger.error("boto3 not installed for Bedrock support")
            return self._create_dummy_finding(hunk, "boto3 not installed for Bedrock support")
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            return self._create_dummy_finding(hunk, f"Bedrock API error: {e}")
        except Exception as e:
            logger.error(f"Bedrock error: {e}")
            return self._create_dummy_finding(hunk, f"Bedrock error: {e}")


class OpenAIClient(BaseLLMClient):
    """OpenAI client for fallback LLM access."""
    
    def __init__(self):
        super().__init__()
        self.openai_config = self.config.llm_config
    
    async def review_hunk(self, hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
        """Review a code hunk using OpenAI."""
        try:
            logger.info(f"Starting OpenAI review for {hunk.file_path} ({hunk.hunk_header})")
            
            # Import openai here to avoid dependency issues
            import openai
            
            # Configure OpenAI
            openai.api_key = self.openai_config["api_key"]
            logger.debug(f"OpenAI client configured for {hunk.file_path}")
            
            # Build the prompt
            system_prompt = get_system_prompt()
            user_prompt = build_review_prompt(hunk, guidelines)
            logger.debug(f"Prompt built for {hunk.file_path}")
            
            # Call OpenAI
            logger.debug(f"Calling OpenAI API for {hunk.file_path}")
            response = await openai.ChatCompletion.acreate(
                model=self.openai_config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2048,
                temperature=0.1
            )
            
            logger.info(f"OpenAI response received for {hunk.file_path}")
            content = response.choices[0].message.content
            findings = self._parse_findings_response(content, hunk)
            logger.info(f"Parsed {len(findings)} findings for {hunk.file_path}")
            return findings
            
        except ImportError:
            logger.error("openai not installed for OpenAI support")
            return self._create_dummy_finding(hunk, "openai not installed for OpenAI support")
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return self._create_dummy_finding(hunk, f"OpenAI error: {e}")


class KiroClient(BaseLLMClient):
    """Kiro AI client for code review."""
    
    def __init__(self):
        super().__init__()
        self.kiro_config = self.config.llm_config
    
    async def review_hunk(self, hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
        """Review a code hunk using Kiro AI."""
        try:
            logger.info(f"Starting Kiro review for {hunk.file_path} ({hunk.hunk_header})")
            
            # Import aiohttp for async HTTP requests
            import aiohttp
            import json as json_lib
            
            # Build the prompt
            system_prompt = get_system_prompt()
            user_prompt = build_review_prompt(hunk, guidelines)
            logger.debug(f"Prompt built for {hunk.file_path}")
            
            # Prepare the request payload
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "model": self.kiro_config["model"],
                "max_tokens": 2048,
                "temperature": 0.1
            }
            
            # Add workspace if specified
            if self.kiro_config.get("workspace"):
                payload["workspace"] = self.kiro_config["workspace"]
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "QReviewer/1.0"
            }
            
            # Add API key if provided
            if self.kiro_config.get("api_key"):
                headers["Authorization"] = f"Bearer {self.kiro_config['api_key']}"
            
            # Make the API call
            api_url = f"{self.kiro_config['api_url'].rstrip('/')}/api/chat"
            logger.debug(f"Calling Kiro API at {api_url} for {hunk.file_path}")
            
            timeout = aiohttp.ClientTimeout(total=self.config.review_timeout_sec)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise LLMClientError(f"Kiro API error {response.status}: {error_text}")
                    
                    response_data = await response.json()
                    logger.info(f"Kiro response received for {hunk.file_path}")
            
            # Extract content from response
            # Kiro might return different response formats, handle common ones
            content = None
            if "choices" in response_data and response_data["choices"]:
                # OpenAI-compatible format
                content = response_data["choices"][0]["message"]["content"]
            elif "content" in response_data:
                # Direct content format
                content = response_data["content"]
            elif "response" in response_data:
                # Alternative response format
                content = response_data["response"]
            else:
                # Fallback - use the entire response as string
                content = str(response_data)
            
            if not content:
                raise LLMClientError("Empty response from Kiro API")
            
            findings = self._parse_findings_response(content, hunk)
            logger.info(f"Parsed {len(findings)} findings for {hunk.file_path}")
            return findings
            
        except ImportError:
            logger.error("aiohttp not installed for Kiro support")
            return self._create_dummy_finding(hunk, "aiohttp not installed for Kiro support")
        except asyncio.TimeoutError:
            logger.error(f"Kiro API timeout after {self.config.review_timeout_sec} seconds")
            return self._create_dummy_finding(hunk, f"Kiro API timeout after {self.config.review_timeout_sec} seconds")
        except Exception as e:
            logger.error(f"Kiro error: {e}")
            return self._create_dummy_finding(hunk, f"Kiro error: {e}")


def get_llm_client() -> BaseLLMClient:
    """Get the configured LLM client."""
    backend = config.llm_backend
    
    if backend == "amazon_q":
        return AmazonQCLIClient()
    elif backend == "bedrock":
        return BedrockClient()
    elif backend == "openai":
        return OpenAIClient()
    elif backend == "kiro":
        return KiroClient()
    else:
        raise ValueError(f"Unsupported LLM backend: {backend}")


# Backward compatibility
def review_hunk(hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
    """Backward compatibility function for existing code."""
    client = get_llm_client()
    
    # Run in event loop if not already running
    try:
        loop = asyncio.get_running_loop()
        # If we're already in an event loop, we need to handle this differently
        # For now, just return a dummy finding
        logger.warning("Cannot run async review_hunk in existing event loop")
        return client._create_dummy_finding(hunk, "Async execution not supported in this context")
    except RuntimeError:
        # No event loop running, we can create one
        return asyncio.run(client.review_hunk(hunk, guidelines))


def apply_security_heuristics(findings: List[Finding]) -> List[Finding]:
    """Apply security heuristics to flag potential security issues."""
    security_keywords = [
        "password", "secret", "key", "token", "auth", "login", "admin",
        "sql", "injection", "xss", "csrf", "eval", "exec", "shell",
        "file", "upload", "download", "path", "traversal", "overflow"
    ]
    
    enhanced_findings = findings.copy()
    
    for finding in enhanced_findings:
        # Check if finding contains security-related keywords
        content_lower = finding.message.lower()
        if any(keyword in content_lower for keyword in security_keywords):
            # If it's not already marked as security, consider upgrading severity
            if finding.category != "security":
                finding.category = "security"
                # Upgrade severity if it's currently low
                if finding.severity in ["nit", "minor"]:
                    finding.severity = "major"
                    finding.confidence = min(finding.confidence + 0.2, 1.0)
    
    return enhanced_findings
