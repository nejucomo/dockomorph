import ConfigParser


def parse_config(path):
    # Use RawConfigParser for its parser, but undo its terrible interface:
    rcp = ConfigParser.RawConfigParser()
    rcp.read(path)

    config = {}
    for section in rcp.sections():
        config[section] = rcp.items(section)

    return config
