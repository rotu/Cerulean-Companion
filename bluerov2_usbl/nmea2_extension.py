import pynmea2


# by making this a subclass of TalkerSentence, pynmea2 will automatically recognize
# this sentence type
class RTH(pynmea2.TalkerSentence):
    """
    RTH
    """
    fields = (
        ("Apparent Bearing to Target in Degrees", "ab", float),
        ("Apparent Bearing to Target in Compass Degrees", "ac", float),
        ("Apparent Elevation to Target in Degrees", "ae", float),
        ("Slant Range in Meters", "sr", float),
        ("True Bearing to Target in Degrees", "tb", float),
        ("True Bearing to Target in Compass Degrees", "cb", float),
        ("True Elevation to Target in Degrees", "te", float),
        ("Euler Roll", "er", float),
        ("Euler Pitch", "ep", float),
        ("Euler Yaw", "ey", float),
        ("Compass Heading", "ch", float),
        ("AGC Gain in db", "db", float)
    )

    def __init__(self, talker, sentence_type, data):
        expected_len_data = len(type(self).fields)
        len_data = len(data)
        if len_data != expected_len_data:
            raise pynmea2.ParseError(
                f'Wrong number of fields. Expected {expected_len_data} but got {len_data}', self.data)

        super().__init__(talker, sentence_type, data)


def register_nmea_extensions():
    assert 'RTH' in pynmea2.TalkerSentence.sentence_types
