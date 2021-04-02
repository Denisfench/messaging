from unittest import TestCase

from APIServer.Heroku.pull import get_heroku_deployments


class HerokuTests(TestCase):
    """
    Tests for all Heroku interaction code.
    """
    def test_get_heroku_deployments(self):
        self.assertTrue(isinstance
                        (get_heroku_deployments("Need server here!"),
                         dict))
