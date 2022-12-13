"""!
The command line interface for the fos package
See `fos --help` for more information.
"""

import atexit
import cProfile
import sys

import click

from fos.util import console, create_wrf_df, get_coords


@click.group()
@click.option("--profile", is_flag=True, help="Profile the program.")
@click.option(
    "--profile-output",
    default="profile.out",
    help="Output file when profiling, else it's ignored.",
)
def cli(profile: bool, profile_output: str) -> None:
    """!
    This function provides the command line interface for the fos package.
    See subcommand options with `fos --help` or `fos <subcommand> --help`.
    See click.group() for more information on the arguments.
    @param profile [bool]: Whether to profile the program or not.
    @param profile_output [str]: The output file when profiling, else it's ignored.
    @return None
    """
    # Profiling snippet modified from
    # https://stackoverflow.com/questions/55880601/how-to-use-profiler-with-click-cli-in-python
    if profile:
        console.log("Profiling...", style="bold yellow")
        pr = cProfile.Profile()
        pr.enable()

        def exit():
            pr.disable()
            pr.dump_stats(profile_output)
            console.log(
                "Profiling Complete. See profile.prof using snakeviz. `snakeviz profile.prof`",
                style="bold yellow",
            )

        atexit.register(exit)
    console.log("Beginning analysis...", style="bold yellow")


@click.command()
def dev():
    """
    Command for development purposes.
    """
    res = get_coords()
    create_wrf_df(res["snotel_gdf"])


cli.add_command(dev)


# TODO
# Add the subcommands


if __name__ == "__main__":
    console.log("Use command line binary `fos`, see `fos --help`")
    sys.exit(1)
