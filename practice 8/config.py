from configparser import ConfigParser


def load_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)

    if parser.has_section(section):
        config = {}
        for key, value in parser.items(section):
            config[key] = value
        return config
    else:
        raise Exception(f"Section {section} not found in {filename}")