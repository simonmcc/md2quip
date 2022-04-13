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
            # print(f"options from file = {options}")
    except KeyError:
        options = {}
    ctx.default_map = options


# set auto_envvar_prefix so that we can load options from environment variables
# and still use poetry's tool.poetry.scripts
CONTEXT_SETTINGS = dict(auto_envvar_prefix='MD2QUIP')


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.version_option()
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
@click.option('--quip-thread-id', required=True)
@click.option('--quip-api-base-url', default='https://platform.quip.com')
@click.option('--quip-api-access-token', required=True)
@click.pass_context
# def cli(ctx, debug, quip_thread_id, quip_api_base_url, quip_api_access_token):
def cli(ctx, **kwargs):
    click.echo("md2quip")
    click.echo("=" * len("md2quip"))
    click.echo("Mark Down to Quip - publish your docs to Quip")

    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if __name__ == '__main__':` block below.
    ctx.ensure_object(dict)

    # shove all of the global options into the ctx so that sub-commands
    # have easy access to them
    for k, v in kwargs.items():
        ctx.obj[k] = v


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def find_folders(ctx):
    # TODO: Should we just create a single md2quip object for the group in cli()?
    foo = md2quip.md2quip(ctx.obj.get('quip_api_base_url'), ctx.obj.get('quip_api_access_token'))
    foo.show_folders(thread_id=ctx.obj.get('quip_thread_id'), depth=1)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def find_folders_and_docs(ctx):
    # TODO: Should we just create a single md2quip object for the group in cli()?
    foo = md2quip.md2quip(ctx.obj.get('quip_api_base_url'), ctx.obj.get('quip_api_access_token'))
    foo.show_folders_and_docs(thread_id=ctx.obj.get('quip_thread_id'), depth=1)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def find_local_files(ctx, path='.'):
    # TODO: Should we just create a single md2quip object for the group in cli()?
    foo = md2quip.md2quip(ctx.obj.get('quip_api_base_url'), ctx.obj.get('quip_api_access_token'))
    files = foo.find_files()
    click.echo(f"find_files() = {files}")


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--path', default='.', type=click.Path(exists=True))
@click.option('--publish-at-root', default=False)
@click.pass_context
def publish(ctx, path, publish_at_root):
    click.echo(f"Debug mode is {'on' if ctx.obj['debug'] else 'off'}")
    click.echo(f"path is {path}")

    click.echo("TODO")


if __name__ == '__main__':
    cli(obj={})
