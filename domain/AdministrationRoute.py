from enum import Enum


class AdministrationRoute(Enum):
    OINTMENT = ("Ointment", "A semi-solid preparation applied to the skin")
    INHAL_POWDER = ("Inhalation Powder", "Dry powder inhaled through the lungs")
    INHAL_AEROSOL = ("Inhalation Aerosol", "Medication delivered as a mist for inhalation")
    TD = ("Transdermal", "Medication absorbed through the skin, typically via patches")
    IMPLANT = ("Implant", "Medication delivered through an implanted device under the skin")
    P = ("Parenteral", "Medication administered by injection or infusion")
    INHAL_SOLUTION = ("Inhalation Solution", "Liquid medication inhaled through the lungs")
    URETHRAL = ("Urethral", "Medication administered through the urethra")
    INSTILL_SOLUTION = ("Instillation Solution", "Liquid medication instilled into a body cavity")
    SC_IMPLANT = ("Subcutaneous Implant", "Medication administered through an implant under the skin")
    INTRAVESICAL = ("Intravesical", "Medication administered directly into the bladder")
    O = ("Oral", "Medication taken through the mouth")
    SL = ("Sublingual", "Medication placed under the tongue for absorption")
    R = ("Rectal", "Medication administered through the rectum")
    V = ("Vaginal", "Medication administered through the vagina")
    N = ("Nasal", "Medication administered through the nose")

    def __new__(cls, name, description):
        obj = object.__new__(cls)
        obj._value_ = name
        obj.description = description
        return obj

    @classmethod
    def get_name(cls, route_name):
        try:
            return cls[route_name].value
        except KeyError:
            return "Name not available"

    @classmethod
    def get_description(cls, route_name):
        try:
            return cls[route_name].description
        except KeyError:
            return "Description not available"

    @classmethod
    def get_snomed_code(cls):
        return {
            "Ointment": "129595002",
            "Inhalation Powder": "127013003",
            "Inhalation Aerosol": "404681000000109",
            "Transdermal": "26643006",
            "Implant": "324121000000109",
            "Parenteral": "2604137",
            "Inhalation Solution": "404681000000109",
            "Urethral": "241451000000109",
            "Instillation Solution": "424961000000109",
            "Subcutaneous Implant": "39579001",
            "Intravesical": "258256000",
            "Oral": "26643006",
            "Sublingual": "13003003",
            "Rectal": "304825000",
            "Vaginal": "306931000000109",
            "Nasal": "13329001",
        }
