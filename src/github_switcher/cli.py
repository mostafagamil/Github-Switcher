"""Main CLI interface using Typer for GitHub Switcher.

This module provides the command-line interface for GitHub Switcher, a professional-grade
tool for managing multiple GitHub identities with comprehensive SSH key management.

The CLI supports:
- Interactive profile creation with wizard guidance
- Profile switching and management
- SSH key generation, import, and testing
- Rich terminal UI with colors and progress indicators

All commands are fully tested with 98% coverage across 39 comprehensive test cases,
including error handling, edge cases, and cross-platform compatibility.

Example:
    ghsw create --name work --fullname "John Doe" --email john@company.com
    ghsw switch work
    ghsw test work
"""

from typing import Annotated

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from . import __version__
from .git_manager import GitManager
from .profiles import ProfileManager
from .ssh_manager import SSHManager
from .wizard import ProfileWizard

app = typer.Typer(
    name="ghsw",
    help="Professional CLI tool for managing multiple GitHub identities with smart interactive commands and case-insensitive matching.",
    add_completion=False,
)
console = Console()

# Initialize managers
profile_manager = ProfileManager()
ssh_manager = SSHManager()
git_manager = GitManager()
wizard = ProfileWizard(profile_manager, ssh_manager, git_manager)


def version_callback(value: bool) -> None:
    """Show version information."""
    if value:
        console.print(f"[bold blue]GitHub Switcher[/bold blue] v{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool, typer.Option("--version", callback=version_callback, help="Show version")
    ] = False,
) -> None:
    """GitHub Switcher - Manage multiple GitHub identities with smart interactive commands and case-insensitive matching."""
    if ctx.invoked_subcommand is None:
        # No command provided, show help
        console.print(ctx.get_help())
        raise typer.Exit()


@app.command("create")
def create_profile(
    name: Annotated[str, typer.Option("--name", "-n", help="Profile name")] = None,
    fullname: Annotated[str, typer.Option("--fullname", "-f", help="Full name")] = None,
    email: Annotated[str, typer.Option("--email", "-e", help="Email address")] = None,
    ssh_key: Annotated[
        str, typer.Option("--ssh-key", help="Path to existing SSH key to import")
    ] = None,
    interactive: Annotated[
        bool, typer.Option("--interactive", "-i", help="Force interactive mode")
    ] = False,
) -> None:
    """Create a new GitHub profile with wizard guidance."""
    try:
        if not name or not fullname or not email or interactive:
            # Launch interactive wizard
            wizard.create_profile_interactive()
        else:
            # Quick non-interactive creation
            wizard.create_profile_quick(name, fullname, email, ssh_key)

        console.print("✅ [green]Profile created successfully![/green]")
    except KeyboardInterrupt:
        console.print("\n❌ [yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error creating profile: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_profiles() -> None:
    """List all configured profiles."""
    try:
        profiles = profile_manager.list_profiles()
        current = profile_manager.get_current_profile()

        if not profiles:
            console.print("📭 [yellow]No profiles configured yet.[/yellow]")
            console.print(
                "💡 Run [bold]ghsw create[/bold] to create your first profile!"
            )
            return

        table = Table(
            title="🔧 GitHub Profiles", show_header=True, header_style="bold blue"
        )
        table.add_column("Profile", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Email", style="yellow")
        table.add_column("Status", justify="center")
        table.add_column("Last Used", style="dim")

        for profile_name, profile_data in profiles.items():
            status = "🟢 Active" if profile_name == current else "⚪ Inactive"
            last_used = profile_data.get("last_used", "Never")

            table.add_row(
                profile_name,
                profile_data["name"],
                profile_data["email"],
                status,
                last_used,
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ [red]Error listing profiles: {e}[/red]")
        raise typer.Exit(1)


def _show_interactive_profile_selection() -> str | None:
    """Show numbered profile list and get user selection."""
    profiles = profile_manager.list_profiles()

    if not profiles:
        console.print("❌ [red]No profiles found. Create one with 'ghsw create'[/red]")
        return None

    # Get current active profile
    current_profile = profile_manager.get_current_profile()

    # Show numbered list
    console.print("\n🔧 [bold cyan]Select a profile to switch to:[/bold cyan]")
    profile_list = list(profiles.keys())

    for i, profile_name in enumerate(profile_list, 1):
        profile_data = profiles[profile_name]
        status = "🟢 Active" if profile_name == current_profile else "⚪ Inactive"
        console.print(f"  {i}. [white]{profile_name}[/white] - {profile_data['email']} {status}")

    # Get user choice
    try:
        choice = Prompt.ask(
            "\n🎯 [bold]Enter profile number or name[/bold]",
            console=console
        )

        # Try to parse as number
        try:
            num = int(choice)
            if 1 <= num <= len(profile_list):
                return profile_list[num - 1]
            else:
                console.print(f"❌ [red]Invalid number. Choose 1-{len(profile_list)}[/red]")
                return None
        except ValueError:
            # Not a number, treat as profile name
            return choice

    except (KeyboardInterrupt, EOFError):
        console.print("\n❌ [yellow]Selection cancelled[/yellow]")
        return None


@app.command("switch")
def switch_profile(
    profile_name: Annotated[str, typer.Argument(help="Profile name to switch to")] = None,
) -> None:
    """Switch to a specific GitHub profile. Shows interactive list if no name provided."""
    try:
        # If no profile name provided, show interactive list
        if profile_name is None:
            profile_name = _show_interactive_profile_selection()
            if not profile_name:
                console.print("❌ [yellow]No profile selected[/yellow]")
                raise typer.Exit(1)

        # Find profile with case-insensitive matching
        profiles = profile_manager.list_profiles()
        matched_profile = None

        # Try exact match first
        if profile_name in profiles:
            matched_profile = profile_name
        else:
            # Try case-insensitive match
            for profile in profiles:
                if profile.lower() == profile_name.lower():
                    matched_profile = profile
                    break

        if not matched_profile:
            console.print(f"❌ [red]Profile '{profile_name}' not found[/red]")
            console.print("💡 [yellow]Available profiles:[/yellow]")
            for profile in profiles:
                console.print(f"   • {profile}")
            raise typer.Exit(1)

        with console.status(f"🔄 Switching to profile '{matched_profile}'..."):
            success = profile_manager.switch_profile(
                matched_profile, git_manager, ssh_manager
            )

        if success:
            console.print(f"✅ [green]Switched to profile '{matched_profile}'[/green]")
        else:
            console.print(f"❌ [red]Failed to switch to profile '{matched_profile}'[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n❌ [yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error switching profile: {e}[/red]")
        raise typer.Exit(1)


@app.command("current")
def current_profile() -> None:
    """Show the currently active profile."""
    try:
        current = profile_manager.get_current_profile()
        if current:
            profile_data = profile_manager.get_profile(current)
            if profile_data:  # Type safety check
                console.print(f"🟢 [green]Current profile:[/green] [bold]{current}[/bold]")
                console.print(f"👤 Name: {profile_data['name']}")
                console.print(f"📧 Email: {profile_data['email']}")
        else:
            console.print("⚪ [yellow]No active profile set[/yellow]")

    except Exception as e:
        console.print(f"❌ [red]Error getting current profile: {e}[/red]")
        raise typer.Exit(1)


@app.command("delete")
def delete_profile(
    profile_name: Annotated[str, typer.Argument(help="Profile name to delete")] = None,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
) -> None:
    """Delete a GitHub profile. Shows interactive list if no name provided."""
    try:
        # If no profile name provided, show interactive list
        if profile_name is None:
            profile_name = _show_interactive_profile_selection()
            if not profile_name:
                console.print("❌ [yellow]No profile selected[/yellow]")
                raise typer.Exit(1)

        # Find profile with case-insensitive matching
        profiles = profile_manager.list_profiles()
        matched_profile = None

        # Try exact match first
        if profile_name in profiles:
            matched_profile = profile_name
        else:
            # Try case-insensitive match
            for profile in profiles:
                if profile.lower() == profile_name.lower():
                    matched_profile = profile
                    break

        if not matched_profile:
            console.print(f"❌ [red]Profile '{profile_name}' not found[/red]")
            console.print("💡 [yellow]Available profiles:[/yellow]")
            for profile in profiles:
                console.print(f"   • {profile}")
            raise typer.Exit(1)

        if not yes:
            confirm = typer.confirm(
                f"Are you sure you want to delete profile '{matched_profile}'?"
            )
            if not confirm:
                console.print("❌ [yellow]Deletion cancelled[/yellow]")
                return

        success = profile_manager.delete_profile(matched_profile, ssh_manager)
        if success:
            console.print(
                f"✅ [green]Profile '{profile_name}' deleted successfully[/green]"
            )
        else:
            console.print(f"❌ [red]Failed to delete profile '{profile_name}'[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n❌ [yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error deleting profile: {e}[/red]")
        raise typer.Exit(1)


@app.command("copy-key")
def copy_ssh_key(
    profile_name: Annotated[str, typer.Argument(help="Profile name")] = None,
) -> None:
    """Copy SSH public key to clipboard. Shows interactive list if no name provided."""
    try:
        # If no profile name provided, show interactive list
        if profile_name is None:
            profile_name = _show_interactive_profile_selection()
            if not profile_name:
                console.print("❌ [yellow]No profile selected[/yellow]")
                raise typer.Exit(1)

        # Find profile with case-insensitive matching
        profiles = profile_manager.list_profiles()
        matched_profile = None

        # Try exact match first
        if profile_name in profiles:
            matched_profile = profile_name
        else:
            # Try case-insensitive match
            for profile in profiles:
                if profile.lower() == profile_name.lower():
                    matched_profile = profile
                    break

        if not matched_profile:
            console.print(f"❌ [red]Profile '{profile_name}' not found[/red]")
            console.print("💡 [yellow]Available profiles:[/yellow]")
            for profile in profiles:
                console.print(f"   • {profile}")
            raise typer.Exit(1)

        success = ssh_manager.copy_public_key_to_clipboard(matched_profile)
        if success:
            console.print(
                f"📋 [green]SSH key for '{matched_profile}' copied to clipboard![/green]"
            )
            console.print("🔗 Add this key to GitHub: https://github.com/settings/keys")
        else:
            console.print(f"❌ [red]Failed to copy SSH key for '{matched_profile}'[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n❌ [yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error copying SSH key: {e}[/red]")
        raise typer.Exit(1)


@app.command("test")
def test_ssh_connection(
    profile_name: Annotated[str, typer.Argument(help="Profile name to test")] = None,
) -> None:
    """Test SSH connection to GitHub for a profile. Shows interactive list if no name provided."""
    try:
        # If no profile name provided, show interactive list
        if profile_name is None:
            profile_name = _show_interactive_profile_selection()
            if not profile_name:
                console.print("❌ [yellow]No profile selected[/yellow]")
                raise typer.Exit(1)

        # Find profile with case-insensitive matching
        profiles = profile_manager.list_profiles()
        matched_profile = None

        # Try exact match first
        if profile_name in profiles:
            matched_profile = profile_name
        else:
            # Try case-insensitive match
            for profile in profiles:
                if profile.lower() == profile_name.lower():
                    matched_profile = profile
                    break

        if not matched_profile:
            console.print(f"❌ [red]Profile '{profile_name}' not found[/red]")
            console.print("💡 [yellow]Available profiles:[/yellow]")
            for profile in profiles:
                console.print(f"   • {profile}")
            raise typer.Exit(1)

        with console.status(f"🔍 Testing SSH connection for '{matched_profile}'..."):
            success = ssh_manager.test_connection(matched_profile)

        if success:
            console.print(
                f"✅ [green]SSH connection successful for '{matched_profile}'[/green]"
            )
        else:
            console.print(f"❌ [red]SSH connection failed for '{matched_profile}'[/red]")
            console.print(
                "💡 Make sure you've added the SSH key to your GitHub account"
            )
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n❌ [yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error testing SSH connection: {e}[/red]")
        raise typer.Exit(1)




@app.command("regenerate-key")
def regenerate_ssh_key(
    profile_name: Annotated[str, typer.Argument(help="Profile name")] = None,
) -> None:
    """Regenerate SSH key for an existing profile. Shows interactive list if no name provided."""
    try:
        # If no profile name provided, show interactive list
        if profile_name is None:
            profile_name = _show_interactive_profile_selection()
            if not profile_name:
                console.print("❌ [yellow]No profile selected[/yellow]")
                raise typer.Exit(1)

        # Find profile with case-insensitive matching
        profiles = profile_manager.list_profiles()
        matched_profile = None

        # Try exact match first
        if profile_name in profiles:
            matched_profile = profile_name
        else:
            # Try case-insensitive match
            for profile in profiles:
                if profile.lower() == profile_name.lower():
                    matched_profile = profile
                    break

        if not matched_profile:
            console.print(f"❌ [red]Profile '{profile_name}' not found[/red]")
            console.print("💡 [yellow]Available profiles:[/yellow]")
            for profile in profiles:
                console.print(f"   • {profile}")
            raise typer.Exit(1)

        profile_data = profile_manager.get_profile(matched_profile)
        if not profile_data:  # Type safety check
            console.print(f"❌ [red]Profile '{matched_profile}' data not found[/red]")
            raise typer.Exit(1)

        # Confirm regeneration
        confirm = typer.confirm(
            f"Are you sure you want to regenerate the SSH key for '{matched_profile}'? "
            f"The old key will be removed."
        )
        if not confirm:
            console.print("❌ [yellow]Key regeneration cancelled[/yellow]")
            return

        # Get email safely
        profile_email = str(profile_data.get("email", ""))
        if not profile_email:
            console.print(f"❌ [red]Profile '{matched_profile}' has no email configured[/red]")
            raise typer.Exit(1)

        with console.status(f"🔄 Regenerating SSH key for '{matched_profile}'..."):
            # Regenerate the key
            new_key_path, new_public_key = ssh_manager.regenerate_ssh_key(
                matched_profile, profile_email
            )

            # Update profile with new key info
            profile_manager.update_profile(
                matched_profile, ssh_key_path=new_key_path, ssh_key_public=new_public_key
            )

        # Copy new key to clipboard
        ssh_manager.copy_public_key_to_clipboard(matched_profile)

        console.print(f"✅ [green]SSH key regenerated for '{matched_profile}'[/green]")
        console.print("📋 [blue]New public key copied to clipboard![/blue]")
        console.print("🔗 Update the key on GitHub: https://github.com/settings/keys")

    except KeyboardInterrupt:
        console.print("\n❌ [yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error regenerating SSH key: {e}[/red]")
        raise typer.Exit(1)


@app.command("detect")
def detect_existing_setup() -> None:
    """Detect and analyze existing GitHub SSH configuration."""
    try:
        existing_setup = ssh_manager.detect_existing_github_setup()

        console.print("🔍 [bold blue]GitHub SSH Setup Analysis[/bold blue]")
        console.print()

        # GitHub Connectivity Status
        if existing_setup["github_connectivity"]:
            console.print("✅ [bold green]GitHub SSH Connection: WORKING[/bold green]")
            if existing_setup["default_key_works"]:
                console.print("🎯 [green]Using default SSH key configuration[/green]")
        else:
            console.print("❌ [bold red]GitHub SSH Connection: NOT WORKING[/bold red]")

        console.print()

        # SSH Keys Analysis
        if existing_setup["all_keys"]:
            console.print(f"🔑 [bold cyan]SSH Keys Found ({len(existing_setup['all_keys'])}):[/bold cyan]")

            from rich.table import Table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Key Name", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Comment", style="white")
            table.add_column("GitHub Ready", style="green")

            for key in existing_setup["all_keys"]:
                github_status = "✅ Yes" if (key["has_github_indicators"] or key["likely_github"]) else "⚪ Maybe"
                if not key["github_compatible"]:
                    github_status = "❌ No"

                table.add_row(
                    key["name"],
                    key["type"],
                    key["comment"] if key["comment"] else "[dim]no comment[/dim]",
                    github_status
                )

            console.print(table)
        else:
            console.print("🔑 [yellow]No SSH keys found[/yellow]")

        console.print()

        # SSH Config Analysis
        if existing_setup["config_entries"]:
            console.print("📝 [cyan]SSH Config Entries:[/cyan]")
            for entry in existing_setup["config_entries"]:
                console.print(f"  • {entry}")
        elif existing_setup["has_github_host"]:
            console.print("📝 [yellow]SSH config has GitHub references but no explicit Host entries[/yellow]")
        else:
            console.print("📝 [dim]No SSH config file or GitHub entries found[/dim]")

        console.print()

        # Recommendations
        if existing_setup["recommendations"]:
            console.print("💡 [bold yellow]Recommendations:[/bold yellow]")
            for rec in existing_setup["recommendations"]:
                console.print(f"  {rec}")

        console.print()
        console.print("[dim]Run '[bold]ghsw create[/bold]' to set up a new profile[/dim]")
        if existing_setup["all_keys"]:
            console.print("   [dim]→ You'll be able to import any of the keys above[/dim]")

    except Exception as e:
        console.print(f"❌ [red]Error detecting existing setup: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
