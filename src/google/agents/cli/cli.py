import click
from google.agents.cli._click import LazyGroup

class AgentsCLI(LazyGroup):
    """
    The main entry point for the agents-cli.
    This group uses LazyGroup to defer loading of subcommands until they are needed.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Register existing commands using add_lazy_command
        self.add_lazy_command(
            "data-ingestion",
            "google.agents.cli.data.cmd_data_ingestion:cmd_data_ingestion",
            "Ingest data for agents."
        )
        self.add_lazy_command(
            "infra-datastore",
            "google.agents.cli.infra.cmd_datastore:cmd_infra_datastore",
            "Manage infrastructure datastores."
        )
        self.add_lazy_command(
            "create",
            "google.agents.cli.scaffold.commands.create:create",
            "Create a new agent project."
        )
        # Add the new 'agy' subcommand, now pointing to the main subdirectory
        self.add_lazy_command(
            "agy",
            "google.agents.cli.cmd_agy:agy", # Updated path
            "Commands for interacting with the AGY SDK."
        )

@click.command(
    cls=AgentsCLI,
    context_settings={"help_option_names": ["-h", "--help"]},
)
def main():
    """
    agents-cli: A command-line interface for managing agents.

    This tool provides various commands to create, manage, deploy, and interact
    with agents and their associated infrastructure.
    """
    pass

if __name__ == "__main__":
    # This block allows the CLI to be run directly as a Python module
    # e.g., `python -m google.agents.cli.cli --help`
    main()

