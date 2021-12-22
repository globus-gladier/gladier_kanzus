import json
import os
import datetime
import globus_sdk
import click
import pprint
from pilot.client import PilotClient
pilot_client = PilotClient()
search_client = pilot_client.get_search_client()


@click.group()
def cli():
    pass


@cli.command(help='Create a local backup of an index')
def backup():
    """List all entries for a project, save them to the local directory"""
    entries = pilot_client.list_entries()
    date = datetime.datetime.now().isoformat()
    backup_name = f'{pilot_client.get_index()}-{pilot_client.project.current}-backup-{date}.json'
    with open(backup_name, 'w+') as f:
        f.write(json.dumps(entries, indent=2))


@cli.command(help='Create a migration using a backup')
@click.argument('backup_doc', type=click.File('r'))
@click.argument('migration_doc', type=click.File('w+'), default='migration.json')
def make_migration(backup_doc, migration_doc):
    content_map = {}
    click.secho(f'Creating migration from {backup_doc.name}...')
    for record in json.loads(backup_doc.read()):
        content = record['content'][0]
        for file_record in content['files']:
            file_record['url'] = pilot_client.get_short_path(file_record['url'])
        content_map[pilot_client.get_short_path(record['subject'])] = content
    migration_doc.write(json.dumps(content_map, indent=2))
    click.secho(f'Saved {migration_doc.name}')


@cli.command(help='Ingest a migration document to an index')
@click.argument('migration_doc', type=click.File('r'))
@click.option('--force', is_flag=True, help='Make a mistake even though we warned you not to')
def migrate(migration_doc, force):
    content_map = json.loads(migration_doc.read())
    index_info = search_client.get_index(pilot_client.get_index())
    name = index_info["display_name"]
    click.secho(f'Preparing to ingest {len(content_map)} records into index '
                f'{name} ({index_info["id"]})')

    for record in content_map.values():
        for file_record in record['files']:
            file_record['url'] = pilot_client.get_globus_http_url(file_record['url'])

    if index_info['num_subjects'] > 1 and not force:
        click.secho(f'WARNING: index {name} contains {index_info["num_subjects"]} subjects, '
                    f'suggest you wipe the index before proceeding', fg='red')
        return

    answer = input(f'Ingest {len(content_map)} into {name}? (y/N)> ')
    if answer in ['y', 'Y', 'yes', 'YES', 'YEEEEESSS!', 'AHHHH!']:  # Anxiety is normal
        pilot_client.ingest_many(content_map)
        click.secho('Success', fg='green')
    else:
        click.secho('Aborted', fg='red')







if __name__ == '__main__':
    cli()