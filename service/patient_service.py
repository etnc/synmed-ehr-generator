import random
import re
import pycountry

from config import ConfigManager
from data.distributions import age_ranges, age_distribution, gender_distribution
from domain.Gender import Gender


def assign_gender():
    rand_num = random.random()
    male = gender_distribution['Male']
    if rand_num < male:
        return Gender.MALE.value
    else:
        return Gender.FEMALE.value


def categorize_age_group(age):
    for group, age_range in age_ranges.items():
        if age_range[0] <= age <= age_range[1]:
            return group
    return None


def assign_age():
    total = sum(age_distribution.values())
    normalized_distribution = {k: v / total for k, v in age_distribution.items()}

    cumulative_distribution = []
    cumulative_prob = 0
    for range_str, prob in normalized_distribution.items():
        cumulative_prob += prob
        cumulative_distribution.append((range_str, cumulative_prob))

    rand = random.random()

    chosen_range = None
    for range_str, cum_prob in cumulative_distribution:
        if rand <= cum_prob:
            chosen_range = range_str
            break

    if chosen_range:
        start, end = map(int, chosen_range.strip('()[]').split(','))
        age = random.randint(start, end)
        return age, categorize_age_group(age)


def get_phone_number(phone_number):
    digits = re.sub(r'\D', '', phone_number)
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:10]}"


def determine_maternity(gender, age_group):
    if gender == Gender.FEMALE.value and (age_group == "adults"):
        weight = ConfigManager.config_maternity()
        rand_num = random.random()
        if rand_num < weight:
            return True
    return False


def get_country_from_locale(locale):
    if '_' in locale:
        _, country_code = locale.split('_')
    else:
        country_code = locale
    country = pycountry.countries.get(alpha_2=country_code)
    return country.name if country else None
