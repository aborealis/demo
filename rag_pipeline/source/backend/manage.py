#!/usr/bin/env python3

"""
Alembic CLI for managing database migrations.
Usage:
  manage.py makemigrations <message>
  manage.py migrate
"""
import os
import re
import typer
from pathlib import Path
from alembic import command
from alembic.config import Config

DATABASE_URL = os.environ["DATABASE_URL"]

app = typer.Typer()
cfg = Config("alembic.ini")
cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

ALEMBIC_VERSIONS_PATH = os.path.join("db", "alembic", "versions")


def get_next_migration_number() -> str:
    """
    Get next migration number.
    """
    versions_dir = Path(ALEMBIC_VERSIONS_PATH)

    if not versions_dir.exists():
        return "0001"

    migration_numbers = []
    pattern = re.compile(r'^(\d{4})_')

    for migration_file in versions_dir.glob("*.py"):
        match = pattern.match(migration_file.name)
        if match:
            try:
                number = int(match.group(1))
                migration_numbers.append(number)
            except ValueError:
                continue

    if not migration_numbers:
        return "0001"

    max_number = max(migration_numbers)
    next_number = max_number + 1

    return f"{next_number:04d}"


@app.command()
def makemigrations(message: str):
    """
    Execute makemigrations.
    """
    migration_number = get_next_migration_number()

    typer.echo(f"Creating migration {migration_number}: {message}")

    try:
        command.revision(
            cfg,
            autogenerate=True,
            message=message,
            rev_id=migration_number
        )
        typer.echo(f"✅ Migration {migration_number} created successfully!")
    except Exception as e:
        typer.echo(f"❌ Operation failed: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def migrate():
    """Apply Alembic migrations to the database."""
    typer.echo("Applying migrations...")

    try:
        command.upgrade(cfg, "head")
        typer.echo("✅ Migrations applied successfully!")
    except Exception as e:
        typer.echo(f"❌ Operation failed: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def downgrade(revision: str = "base"):
    """
    Execute downgrade.
    """
    typer.echo(f"Downgrading to revision: {revision}")

    try:
        command.downgrade(cfg, revision)
        typer.echo(f"✅ Downgraded to {revision}!")
    except Exception as e:
        typer.echo(f"❌ Operation failed: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def status():
    """Show the current Alembic revision."""
    typer.echo("Current migration:")

    try:
        command.current(cfg)
    except Exception as e:
        typer.echo(f"❌ Operation failed: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def history():
    """Show Alembic migration history."""
    typer.echo("Migration history:")

    try:
        command.history(cfg)
    except Exception as e:
        typer.echo(f"❌ Operation failed: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def list_migrations():
    """List migration scripts available in the repository."""
    versions_dir = Path(ALEMBIC_VERSIONS_PATH)

    if not versions_dir.exists():
        typer.echo("No migration directory found.")
        return

    migration_files = sorted(versions_dir.glob("*.py"))

    if not migration_files:
        typer.echo("No migrations found.")
        return

    typer.echo("Available migrations:")
    for i, migration_file in enumerate(migration_files, 1):
        name_parts = migration_file.name.split('_', 1)
        if len(name_parts) > 1:
            description = name_parts[1].replace('.py', '').replace('_', ' ')
        else:
            description = migration_file.name.replace('.py', '')

        typer.echo(f"  {i:3d}. {migration_file.name}")
        typer.echo(f"       description: {description}")


if __name__ == "__main__":
    app()
