import yaml


class ConfigManager:
    _config = None

    @classmethod
    def load_config(cls, final_config_file=None):
        if final_config_file is not None:
            cls._config = final_config_file
            return cls._config
        else:
            with open('config.yml', 'r') as file:
                cls._config = yaml.safe_load(file)
                return cls._config

    @classmethod
    def get_config(cls):
        if cls._config is None:
            raise ValueError("Config not loaded yet")
        return cls._config

    @classmethod
    def config_faker_locales(cls):
        return cls.get_config().get("faker", {}).get("locale", ["en_US"])

    @classmethod
    def config_maternity(cls):
        return cls.get_config().get("maternity", 0.0)

    @classmethod
    def config_result_format(cls):
        return cls.get_config().get("result_format", 'json')

    @classmethod
    def config_filter_icd_groups(cls):
        return set(cls.get_config().get("filter_icd_prefix", []))

    @classmethod
    def config_record(cls):
        return cls.get_config().get("records", 1)

    @classmethod
    def config_fhir(cls):
        return cls.get_config().get("generate_fhir", 0)


ConfigManager.load_config()
