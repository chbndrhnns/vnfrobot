import pytest
from ruamel import yaml

from fixtures.test_data_Port import ports_test_data
from tools.goss.GossPort import GossPort


@pytest.mark.kw_port
@pytest.mark.parametrize('inp, data, mapped, out', ports_test_data)
def test__GossPort__transform__pass(inp, data, mapped, out):
    g = GossPort(data.get('data'))

    g.transform_to_goss(g)

    expected = yaml.safe_load(out.get('expected_yaml'))
    actual = yaml.safe_load(g.out)

    assert actual == expected


@pytest.mark.kw_port
@pytest.mark.parametrize('inp, data, expected, yaml', ports_test_data)
def test__GossPort__apply_mappings__pass(inp, data, expected, yaml):
    g = GossPort(data.get('data'))

    g.apply_mappings(g)

    expected = expected.get('with_mappings')
    actual = g.mapped

    assert actual == expected