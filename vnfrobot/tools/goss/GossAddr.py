from tools.goss.GossEntity import GossEntity


class GossAddr(GossEntity):
    """
    Goss test: `address`

    """
    name = 'addresses'
    template = \
        """addr:
            {% for addr in addresses %}
              {{ addr.protocol or 'tcp' }}://{{ addr.address }}:{{ addr.port }}:
                reachable: {{ addr.reachable }}
                timeout: 1000
            {% endfor %}
        """
    key_mappings = {
        'state': 'reachable'
    }
    type_mappings = {}
    value_mappings = {
        'reachable': {
            'reachable': True,
            'is not reachable': False,
        }
    }
    matcher_mappings = {
        'reachable': {
            'is': True,
            'is not': False
        }
    }

    def __init__(self, data):
        GossEntity.__init__(self, data)