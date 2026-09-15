"""Virtual-On reconstruction harness.

The `vonctl` command line replaces the bespoke bash entrypoints under
`scripts/`. Modules here own orchestration; the recovered analysis and
extraction logic stays in `von/tools/`.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
