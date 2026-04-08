"""Command-line interface for OpenClaw."""

import asyncio
import sys
import logging
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from .config import Config
from .gateway import GatewayServer
from .channels import ChannelManager
from .channels.console import ConsoleChannel
from .sessions import SessionManager
from .llm import LLMManager
from .plugins import PluginManager
from .tools import ToolExecutor

console = Console()


@click.group()
@click.version_option(version="2026.4.1", prog_name="openclaw")
@click.option("--config", "-c", default=None, help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, config, verbose):
    """OpenClaw - Your own personal AI assistant. Any OS. Any Platform."""
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load configuration
    ctx.ensure_object(dict)
    try:
        ctx.obj["config"] = Config(config_path=config)
    except Exception as e:
        console.print(f"[red]Error loading config:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.option("--host", "-h", default=None, help="Gateway host address")
@click.option("--port", "-p", default=None, type=int, help="Gateway port number")
@click.pass_context
def start(ctx, host, port):
    """Start the OpenClaw gateway server."""
    config = ctx.obj["config"]

    # Override host/port if provided
    if host:
        config.gateway.host = host
    if port:
        config.gateway.port = port

    async def run():
        # Initialize components
        from openclaw.config.models import ChannelConfig
        
        gateway = GatewayServer(config)
        channel_manager = ChannelManager(config)
        session_manager = SessionManager(config)
        llm_manager = LLMManager(config)
        plugin_manager = PluginManager(config)
        tool_executor = ToolExecutor(config)

        # Register console channel
        console_channel = ConsoleChannel()
        channel_manager.register_channel_type("console", ConsoleChannel)
        config.channels["console"] = ChannelConfig(enabled=True, config={})

        # Initialize components
        console.print("[green]Initializing OpenClaw...[/green]")

        await llm_manager.initialize_providers()
        await plugin_manager.load_plugins()
        await channel_manager.initialize_channels()

        # Set up message handling
        async def handle_message(message):
            """Handle incoming messages from channels."""
            console.print(f"[blue]Received:[/blue] {message.content}")

            # Get or create session
            session = session_manager.get_or_create_session(
                message.channel, message.chat_id
            )

            # Add user message
            session_manager.add_message(
                message.channel,
                message.chat_id,
                "user",
                message.content,
            )

            # Get recent messages for context
            messages = session.to_llm_messages()

            # Get LLM response
            llm_response = await llm_manager.chat(messages)

            if llm_response:
                # Add assistant response to session
                session_manager.add_message(
                    message.channel,
                    message.chat_id,
                    "assistant",
                    llm_response.content,
                )

                # Send response back through channel
                channel = channel_manager.get_channel(message.channel)
                if channel:
                    await channel.send_message(
                        message.chat_id,
                        llm_response.content,
                    )

        # Register message callbacks
        for channel_name in channel_manager.list_channels():
            channel_manager.set_message_callback(channel_name, handle_message)

        # Register RPC methods
        gateway.register_rpc_method("list_sessions", lambda: {
            "count": session_manager.get_active_session_count()
        })
        gateway.register_rpc_method("list_providers", lambda: {
            "providers": llm_manager.list_providers()
        })
        gateway.register_rpc_method("list_tools", lambda: {
            "tools": tool_executor.list_tools()
        })

        # Start channels
        await channel_manager.start_all()

        console.print(f"[green]OpenClaw Gateway running on ws://{config.gateway.host}:{config.gateway.port}[/green]")
        console.print("[yellow]Press Ctrl+C to stop[/yellow]")

        # Start gateway
        await gateway.start()

        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down...[/yellow]")

            # Cleanup
            await gateway.stop()
            await channel_manager.stop_all()
            await plugin_manager.shutdown_all()

            console.print("[green]Goodbye![/green]")

    try:
        asyncio.run(run())
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show OpenClaw status and configuration."""
    config = ctx.obj["config"]

    table = Table(title="OpenClaw Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Gateway Host", config.gateway.host)
    table.add_row("Gateway Port", str(config.gateway.port))
    table.add_row("Max Connections", str(config.gateway.max_connections))
    table.add_row("Channels", str(len(config.channels)))
    table.add_row("LLM Providers", str(len(config.llms)))
    table.add_row("Plugins", str(len(config.plugins)))
    table.add_row("Session Max History", str(config.session.max_history))
    table.add_row("Sandbox Enabled", str(config.sandbox.enabled))

    console.print(table)


@cli.command()
@click.option("--output", "-o", default="openclaw-config.yaml", help="Output file path")
@click.pass_context
def init(ctx, output):
    """Generate a sample configuration file."""
    from openclaw.config.models import ChannelConfig
    
    config = Config()

    # Add some example configurations
    config.channels["console"] = ChannelConfig(enabled=True, config={})

    config.save_to_file(output)
    console.print(f"[green]Configuration saved to:[/green] {output}")


@cli.command()
@click.pass_context
def plugins(ctx):
    """List available and loaded plugins."""
    config = ctx.obj["config"]

    table = Table(title="Configured Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Enabled", style="green")
    table.add_column("Config Keys", style="yellow")

    for name, plugin_config in config.plugins.items():
        table.add_row(
            name,
            str(plugin_config.enabled),
            ", ".join(plugin_config.config.keys()) if plugin_config.config else "-",
        )

    console.print(table)


@cli.command()
@click.pass_context
def channels(ctx):
    """List configured channels."""
    config = ctx.obj["config"]

    table = Table(title="Configured Channels")
    table.add_column("Name", style="cyan")
    table.add_column("Enabled", style="green")
    table.add_column("Config Keys", style="yellow")

    for name, channel_config in config.channels.items():
        table.add_row(
            name,
            str(channel_config.enabled),
            ", ".join(channel_config.config.keys()) if channel_config.config else "-",
        )

    console.print(table)


@cli.command()
@click.pass_context
def llms(ctx):
    """List configured LLM providers."""
    config = ctx.obj["config"]

    table = Table(title="Configured LLM Providers")
    table.add_column("Name", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Model", style="yellow")
    table.add_column("API Key Set", style="red")

    for name, llm_config in config.llms.items():
        table.add_row(
            name,
            llm_config.provider,
            llm_config.model,
            "Yes" if llm_config.api_key else "No",
        )

    console.print(table)


def main():
    """Main entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
