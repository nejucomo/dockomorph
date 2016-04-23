import argparse


def parse_args(description, args):
    p = argparse.ArgumentParser(description=description)

    p.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Webserver listen port.')

    return p.parse_args(args)
