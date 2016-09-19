import unittest

test_loader = unittest.defaultTestLoader.discover( 'tests' )
test_runner = unittest.TextTestRunner()
test_runner.run( test_loader )