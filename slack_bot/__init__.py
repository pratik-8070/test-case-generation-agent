"""Slack front end for the Test Case Generation Agent.

/test-case opens a modal (modal.py) -> the submission is turned into an input
file and run through the existing /generate-test-cases skill with the Claude
Agent SDK (runner.py) -> results are posted back to the channel (summary.py).
app.py wires these to Slack Bolt. Only app.py imports slack_bolt and only
runner._run_agent imports claude_agent_sdk, so the rest is unit-testable
without either installed.
"""
