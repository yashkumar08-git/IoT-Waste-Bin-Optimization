import unittest

from optimizer import haversine_km, optimize_route


class RouteOptimizerTests(unittest.TestCase):

    def setUp(self):
        self.bins = [
            {
                "bin_id": "BIN001",
                "latitude": 27.493,
                "longitude": 77.674,
                "fill_percent": 95,
            },
            {
                "bin_id": "BIN002",
                "latitude": 27.495,
                "longitude": 77.676,
                "fill_percent": 70,
            },
            {
                "bin_id": "BIN003",
                "latitude": 27.490,
                "longitude": 77.670,
                "fill_percent": 25,
            },
        ]

    def test_distance_is_zero_for_same_location(self):
        distance = haversine_km(27.49, 77.67, 27.49, 77.67)
        self.assertAlmostEqual(distance, 0.0, places=5)

    def test_only_eligible_bins_are_selected(self):
        result = optimize_route(
            self.bins, 27.492, 77.673, threshold=60
        )
        ids = [item["bin_id"] for item in result["route"]]

        self.assertEqual(len(ids), 2)
        self.assertNotIn("BIN003", ids)

    def test_route_distance_is_non_negative(self):
        result = optimize_route(
            self.bins, 27.492, 77.673, threshold=60
        )
        self.assertGreaterEqual(result["total_distance_km"], 0)

    def test_no_bins_meet_threshold(self):
        result = optimize_route(
            self.bins, 27.492, 77.673, threshold=100
        )
        self.assertEqual(result["route"], [])
        self.assertEqual(result["bins_to_collect"], 0)


if __name__ == "__main__":
    unittest.main()