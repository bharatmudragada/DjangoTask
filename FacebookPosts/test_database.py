import pytest
from PostData.models import *


@pytest.mark.django_db
class TestUsers:

    def test_my_user(self):

        me = User.objects.get(pk=1)
        User.objects.create(username='bharath', is_superuser=True)

        assert me.is_superuser
        assert User.objects.count() == 2

    def test_my_user_2(self):

        assert User.objects.count() == 1


@pytest.fixture(params=['Bharat', 'Karthik', 'Krishna'])
def get_params_fixture(request):
    return request.param


def test_param_fixtures(get_params_fixture):
    assert get_params_fixture in ['Bharat', 'Karthik', 'Krishna']