LINKS_SCHEMA = {
    'type': 'object',
    'properties': {
        'links': {
            'type': 'array',
            'items': {
                'type': 'string',
                'pattern': "^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
            }
        }
    },
    'additionalProperties': False
}
