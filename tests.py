import unittest
import requests

from ddt import ddt, file_data


@ddt
class TestMethods(unittest.TestCase):
    @file_data("data_straight_wholequery_city_plain.json")
    def test_straight_wholequery_city(self, query):
        """Correct response on a valid query"""
        self.assertTrue(straight_wholequery_city(query),
                        msg=f"Expected {query['result']}, not found instead")

    @file_data("data_straight_param_country_valid.json")
    def test_straight_param_country_valid(self, query):
        """Correct response on a query with 'country' parameter"""
        self.assertTrue(straight_param_country_valid(query),
                        msg=f"Expected {query['result']}, not found instead")

    @file_data("data_straight_address_to_coords.json")
    def test_straight_query_to_coords(self, query):
        """Correct conversion search query to coordinates"""
        self.assertTrue(straight_query_to_coords(query),
                        msg=f"Expected {query['lat']} and {query['lon']}, got different object(s) instead")

    @file_data("data_straight_wholequery_wrong.json")
    def test_straight_wholequery_wrong(self, query):
        """Empty response on a wrong query"""
        response = straight_wholequery_wrong(query)
        self.assertEqual(response, None,
                         msg=f"Expected empty response, got {response} instead")

    @file_data("data_reverse_coords_right.json")
    def test_reverse_coords_right(self, query):
        """Correct single response on a valid query"""
        response = reverse_coords_right(query)
        self.assertEqual(response, True,
                         msg=f"Expected {query['result']} in display_name, got {response} instead")

    @file_data("data_reverse_coords_unable_to_geocode.json")
    def test_reverse_coords_unable_to_geocode(self, query):
        """'Error: Unable to geocode' on non valid query"""
        response = reverse_coords_unable_to_geocode(query)
        self.assertEqual(response, True,
                         msg=f"Expected error response, got {response} instead")

    @file_data("data_reverse_coords_wrong_input.json")
    def test_reverse_coords_wrong_input(self, query):
        """'Error 400: Floating-point number expected for parameter' on non valid query"""
        response = reverse_coords_wrong_input(query)
        self.assertEqual(response, True,
                         msg=f"Expected error response, got {response} instead")


# There below are the methods for each test case

def get_response_straight_wholequery(query):
    openstreetmap_url = "https://nominatim.openstreetmap.org/search"
    payload = {
        "q": query["name"],
        "format": "json"
    }
    return requests.get(openstreetmap_url, params=payload).json()


def get_response_straight_country(query):
    """There could be street, city etc. query parameters but they are omitted for simplicity"""
    openstreetmap_url = "https://nominatim.openstreetmap.org/search"
    payload = {
        "country": query["name"],
        "format": "json"
    }
    return requests.get(openstreetmap_url, params=payload).json()


def get_response_reverse_coords(query):
    openstreetmap_url = "https://nominatim.openstreetmap.org/reverse"
    payload = {
        "lat": query["lat"],
        "lon": query["lon"],
        "format": "json"
    }
    return requests.get(openstreetmap_url, params=payload).json()


def straight_wholequery_city(query):
    response = get_response_straight_wholequery(query)
    for line in response:
        if query["result"] in line.get("display_name", False):
            return True
    return False


def straight_query_to_coords(query):
    """There could be street, city etc. query parameters but they are omitted for simplicity"""
    response = get_response_straight_wholequery(query)
    eps = 0.001
    for line in response:
        diff = abs(query["lat"] - float(line.get("lat", False)))
        diff += abs(query["lon"] - float(line.get("lon", False)))
        if diff < eps:
            return True
    return response

def straight_param_country_valid(query):
    response = get_response_straight_country(query)
    for line in response:
        if query["result"] in line.get("display_name", False):
            return True
    return False


def straight_wholequery_wrong(query):
    response = get_response_straight_wholequery(query)
    if not response:
        return None
    return response


def reverse_coords_right(query):
    response = get_response_reverse_coords(query)
    if query["result"] in response.get("display_name", False):
        return True
    return response


def reverse_coords_unable_to_geocode(query):
    response = get_response_reverse_coords(query)
    if response.get("error", False) == query["result"]:
        return True
    return response


def reverse_coords_wrong_input(query):
    response = get_response_reverse_coords(query)
    if response.get("error", False).get("code", False) == query["result"]:
        return True
    return response


if __name__ == '__main__':
    unittest.main()
