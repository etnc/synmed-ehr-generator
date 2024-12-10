import argparse
import time
from concurrent.futures import ProcessPoolExecutor

from config import ConfigManager
from service.fhir_service import save_fhir
from service.generate_ehr_service import create_ehr_record, format_and_save_record
from service.logger_service import setup_logger


def print_usage(logger):
    logger.info("""
Usage:
  --records <number_of_records>   Number of records to generate
  --result_format <format>        Output format (JSON, XML, Turtle)
  --generate_fhir                 Get records in additional fhir format

Config file settings:
  - maternity: <value>            Probability of generating maternity records
  - faker.locale: <list>          Available locales for Faker
  - filter_icd_prefix: <list>     ICD codes to filter
  - result_format: <format>       Format for saving the output (JSON, XML, Turtle,json-ld, rdf/xml)
""")


def parse_arguments():
    parser = argparse.ArgumentParser(description="EHR Record Generator")
    parser.add_argument("--config", type=str, default="config.yml", help="Path to the YAML configuration file")
    parser.add_argument("--result_format", type=str,
                        choices=["json", "xml", "turtle", "rdf/xml", "json-ld", "JSON", "XML", "TURTLE", "RDF/XML",
                                 "JSON-LD"],
                        help="Override result format (e.g., 'JSON')")
    parser.add_argument("--generate_fhir", type=int, help="Set to 1 to generate FHIR data, 0 otherwise")
    parser.add_argument("--records", type=int, help="Number of records to generate (overrides YAML)")
    return parser.parse_args()


def config_updated(args):
    config = ConfigManager.load_config()
    if args.records:
        config['records'] = args.records
    if args.result_format:
        config['result_format'] = args.result_format.upper()
    ConfigManager.load_config(config)
    return config


def generate_and_save_records(number):
    start_time = time.time()
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(create_ehr_record, range(number)))
    file_format = format_and_save_record(results, 'generated_data')
    if ConfigManager.config_fhir():
        save_fhir(records=results)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return file_format, elapsed_time


def main():
    logger = setup_logger()
    print_usage(logger)
    arguments = parse_arguments()
    config_updated(arguments)
    number = ConfigManager.config_record()

    logger.info("-Final Configuration:")
    logger.info(ConfigManager.get_config())
    logger.info(f"Generating {number} records....")

    file_format, elapsed_time = generate_and_save_records(number)
    logger.info(f"Records have been written to results/generated_data.{file_format}...")
    logger.info(f"Time taken: {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    #     # profiler = cProfile.Profile()
    #     # profiler.enable()
    main()
    # profiler.disable()
    # profiler.print_stats()
