"""Console script for md2quip."""

import logging

import click
import click_log
import yaml

from md2quip import md2quip

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    click_log.basic_config(logger)


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
@click.option('--quip-root', required=True)
@click.option('--quip-api-base-url', default='https://platform.quip.com')
@click.option('--quip-api-access-token', required=True)
@click_log.simple_verbosity_option(logger)
@click.pass_context
# def cli(ctx, quip_root, quip_api_base_url, quip_api_access_token):
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
        logger.debug(f"{k}={v}")
        ctx.obj[k] = v

    ctx.obj['md2quip'] = md2quip.md2quip(
        quip_root=ctx.obj.get('quip_root'),
        quip_api_base_url=ctx.obj.get('quip_api_base_url'),
        quip_api_access_token=ctx.obj.get('quip_api_access_token'),
    )


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def find_folders(ctx):
    ctx.obj['md2quip'].show_folders()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def find_folders_and_docs(ctx):
    ctx.obj['md2quip'].show_folders_and_docs()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def find_local_files(ctx, path='.'):
    files = ctx.obj['md2quip'].find_files()
    click.echo(f"find_files() = {files}")


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--path', default='.', type=click.Path(exists=True))
@click.option('--publish-at-root', default=False)
@click.pass_context
def publish(ctx, path, publish_at_root):
    click.echo(f"Debug mode is {'on' if ctx.obj['debug'] else 'off'}")
    click.echo(f"path is {path}")

    files = ctx.obj['md2quip'].find_files()
    ctx.obj['md2quip'].publish(files, root_folder_id=ctx.obj.get('quip_thread_id'))


if __name__ == '__main__':
    cli(obj={})
