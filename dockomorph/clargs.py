import argparse


def parse_args(description, args):
    p = argparse.ArgumentParser(description=description)
    return p.parse_args(args)
