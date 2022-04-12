"""Console script for md2quip."""

import click
import yaml

from md2quip import md2quip

# extend click so that we can load options from a yaml file
# https://jwodder.github.io/kbits/posts/click-config/
DEFAULT_CFG = 'md2quip.yml'


def configure(ctx, param, filename):
    try:
        with open(filename, 'r') as f:
            options = yaml.safe_load(f)
            print(f"options from file = {options}")
    except KeyError:
        options = {}
    ctx.default_map = options


# set auto_envvar_prefix so that we can load options from environment variables
# and still use poetry's tool.poetry.scripts
CONTEXT_SETTINGS = dict(auto_envvar_prefix='MD2QUIP')


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '-c',
    '--config',
    type=click.Path(dir_okay=False),
    default=DEFAULT_CFG,
    callback=configure,
    is_eager=True,
    expose_value=False,
    help='Read option defaults from the specified YAML file',
    show_default=True,
)
@click.option('--debug/--no-debug')
@click.option('--path', default='.', type=click.Path(exists=True))
@click.option('--quip-thread-id', required=True)
@click.option('--quip-api-base-url', default='https://platform.quip.com')
@click.option('--quip-api-access-token', required=True)
@click.option('--publish-at-root', default=False)
def main(debug, path, quip_thread_id, quip_api_base_url, quip_api_access_token, publish_at_root):
    """Main entrypoint."""
    click.echo("md2quip")
    click.echo("=" * len("md2quip"))
    click.echo("Mark Down to Quip - publish your docs to Quip")
    click.echo("TODO")
    click.echo(f"Debug mode is {'on' if debug else 'off'}")
    click.echo(f"path is {path}")
    click.echo(f"quip_thread_id is {quip_thread_id}")
    click.echo(f"quip_api_base_url is {quip_api_base_url}")

    foo = md2quip.md2quip(
        path, quip_thread_id, quip_api_base_url, quip_api_access_token, publish_at_root=publish_at_root
    )
    foo._descend_into_folder(thread_id=quip_thread_id, depth=1)
    # files = foo.find_files()
    # click.echo(f"find_files() = {files}")
    # foo.publish(files)
