from app import app
import os
import click

@app.cli.group()
def translate():
    """Translation and localization commands."""
    pass

@translate.command()
def update():
    """Update all language."""
    if os.system('pybabel extract -F babel.cfg -k -l messages.pot .') != 0:
        raise RuntimeError('Failed to extract messages.')
    if os.system('pybabel update -i messages.pot -d app/translations') != 0:
        raise RuntimeError('Update command failed.')
    os.remove('messages.pot')

@translate.command()
def compile():
    """Compile all language."""
    if os.system('pybabel compile -d app/translations') != 0:
        raise RuntimeError('Compile command failed.')
    
@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .') != 0:
        raise RuntimeError('Extract command failed.')
    if os.system(
        'pybabel init -i messages.pot -d app/translations -l ' + lang) != 0:
        raise RuntimeError('Init command failed.')
    os.remove('messages.pot')
    