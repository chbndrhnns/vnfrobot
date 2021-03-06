import unittest

import os

import pytest
from robot.running import TestSuiteBuilder
from tests import path


@pytest.mark.kw_address
@pytest.mark.keyword
def test__address_kw__pass():

    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/robot/address.robot'))
    result = suite.run(output=None, variablefile=os.path.join(path, 'fixtures/robot/common.py'))

    assert result.return_code == 0
