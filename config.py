import yaml


def load_config():
    with open('config.yml', 'r') as file:
        return yaml.safe_load(file)


config = load_config()
config_faker_locales = config.get("faker", {}).get("locale", ["en_US"])
config_maternity = config.get("maternity", 0.0)
# config_male = config.get("gender", {}).get("male", 0.5)
# config_female = config.get("gender", {}).get("female", 0.5)
config_result_format = config.get("result_format", 'json')
config_filter_icd_groups = set(config.get("filter_icd_prefix", []))
