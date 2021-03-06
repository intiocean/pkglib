import os
import pytest

from pkglib.testing.mongo_server import MongoTestServer

# Cleanup any old mongo sessions for this workspace when run in Jenkins
# We do this here rather than doing:
#    request.cached_setup(MongoTestServer.kill_all, scope='session')
# as with pytest-xidst, the per-session setups appear to be run for each worker

# We don't do this for users (who don't have the WORKSPACE env variable set)
# as they may legitimately be running a test suite more than once.

# TODO: check that with the latest py.test this is still the case, work has
#       been done to improve fixtures with xdist
if 'WORKSPACE' in os.environ:
    MongoTestServer.kill_all()


def _mongo_server(request):
    """ This does the actual work - there are several versions of this used
        with different scopes.
    """
    test_server = MongoTestServer()
    request.addfinalizer(lambda p=test_server: p.teardown())
    return test_server


@pytest.fixture(scope='function')
def mongo_server(request):
    """ Boot up MongoDB in a local thread.
        This also provides a temp workspace, under
            - $WORKSPACE/mongo
            - $SCRATCH/mongo
        We start a mongo per function under test.
        We tear down, and cleanup mongos at the end of the test.

        For completeness, we tidy up any outstanding mongo temp directories
        at the start and end of each test session
    """
    return _mongo_server(request)
