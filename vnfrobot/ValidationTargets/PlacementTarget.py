from ValidationTargets.ValidationTarget import ValidationTarget
from testtools.DockerTool import DockerTool
from tools import validators
from tools.testutils import call_validator


class Placement(ValidationTarget):
    """
    Set service context

    """
    properties = {
        # 'node.id': {
        #     'matchers': ['is', 'is not'],
        #     'value': '\S+'
        # },
        'node.role': {
            'matchers': ['is', 'is not'],
            'values': '\S+'
        },
        # 'node.hostname': {
        #     'matchers': ['contains', 'contains not', 'is', 'is not'],
        #     'value': '\S+'
        # },
        # 'node.labels': {
        #     'matchers': ['contains', 'contains not', 'is', 'is not'],
        #     'value': '\S+'
        # }
    }
    options = {
        'test_tool': DockerTool,
        'command': 'placement'
    }
    allowed_contexts = ['service']
    tool = DockerTool

    def __init__(self, instance=None):
        super(Placement, self).__init__(instance)

    def validate(self):
        self._find_robot_instance()
        self._check_test_data()

        call_validator(self.instance.sut.target_type, validators.Context, Placement.allowed_contexts)
        call_validator(self.property, validators.Property, Placement.properties)
        call_validator(self.matcher, validators.InList, Placement.properties.get(self.property, {}).get('matchers', []))
        call_validator(self.value, validators.Regex, Placement.properties.get(self.property, {}).get('values', ''))

    def _prepare_transform(self):
        pass

    def _prepare_run(self, tool_instance):
        pass

    def get_as_dict(self):
        return {
            'context': getattr(self, 'context', None),
            'property': getattr(self, 'property', None),
            'matcher': getattr(self, 'matcher', None),
            'value': getattr(self, 'value', None)
        }
