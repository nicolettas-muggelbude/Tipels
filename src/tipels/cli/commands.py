"""
Tipels - CLI Commands

Kommandozeilen-Interface für Tipels
"""

import click
from tipels import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """Tipels - Drucker & Scanner Setup-Tool für Linux"""
    pass


@cli.command()
def scan():
    """Scanne nach Druckern und Scannern"""
    click.echo("Scanne nach Geräten...")
    # TODO: Implementierung
    click.echo("TODO: Hardware-Scan implementieren")


@cli.command()
@click.option("--model", required=True, help="Drucker/Scanner-Modell")
@click.option("--connection", type=click.Choice(["usb", "network"]), required=True)
@click.option("--ip", help="IP-Adresse (nur bei Netzwerk)")
def install(model, connection, ip):
    """Installiere Drucker/Scanner"""
    click.echo(f"Installiere {model} via {connection}...")
    if connection == "network" and not ip:
        click.echo("Fehler: --ip ist erforderlich für Netzwerk-Verbindungen", err=True)
        return
    # TODO: Implementierung
    click.echo("TODO: Installation implementieren")


@cli.command()
@click.argument("device_name")
def remove(device_name):
    """Entferne Drucker/Scanner"""
    click.echo(f"Entferne {device_name}...")
    # TODO: Implementierung
    click.echo("TODO: Deinstallation implementieren")


@cli.command()
def list():
    """Liste installierte Geräte"""
    click.echo("Installierte Geräte:")
    # TODO: Implementierung
    click.echo("TODO: Geräte-Liste implementieren")


@cli.command()
@click.argument("output_path", type=click.Path())
def backup(output_path):
    """Erstelle Backup der Konfiguration"""
    click.echo(f"Erstelle Backup nach {output_path}...")
    # TODO: Implementierung
    click.echo("TODO: Backup implementieren")


@cli.command()
@click.argument("backup_path", type=click.Path(exists=True))
def restore(backup_path):
    """Stelle Backup wieder her"""
    click.echo(f"Stelle Backup von {backup_path} wieder her...")
    # TODO: Implementierung
    click.echo("TODO: Restore implementieren")


if __name__ == "__main__":
    cli()
