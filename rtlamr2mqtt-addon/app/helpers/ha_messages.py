"""
Helper functions for writing MQTT payloads
"""

import helpers.info as i

def meter_discover_payload(base_topic, meter_config):
    """
    Returns the discovery payload for Home Assistant.
    """

    if 'id' in meter_config:
        meter_id = meter_config['id']
        meter_name = meter_config.get('name', 'Unknown Meter')
        meter_config['name']

    # Build value templates with optional multiplier
    multiplier = meter_config.get('multiplier')
    if multiplier is not None and multiplier != 1:
        reading_template = f"{{{{ value_json.reading|float * {multiplier} }}}}"
        generation_template = f"{{{{ value_json.generation|float * {multiplier} }}}}"
    else:
        reading_template = "{{ value_json.reading|float }}"
        generation_template = "{{ value_json.generation|float }}"

    template_payload = {
        "device": {
            "identifiers": f"meter_{meter_id}",
            "name": meter_name,
            "manufacturer": "RTLAMR2MQTT",
            "model": "Smart Meter",
            "sw_version": "1.0",
            "serial_number": meter_id,
            "hw_version": "1.0"
        },
        "origin": {
            "name":"2mqtt",
            "sw_version": i.version(),
            "support_url": i.origin_url()
        },
        "components": {
            f"{meter_id}_reading": {
                "platform": "sensor",
                "name": "Reading",
                "value_template": reading_template,
                "json_attributes_topic": f"{base_topic}/{meter_id}/attributes",
                "unique_id": f"{meter_id}_reading"
            },
            f"{meter_id}_lastseen": {
                "platform": "sensor",
                "name": "Last Seen",
                "device_class": "timestamp",
                "value_template":"{{ value_json.lastseen }}",
                "unique_id": f"{meter_id}_lastseen"
            }
        },
        "state_topic": f"{base_topic}/{meter_id}/state",
        "availability_topic": f"{base_topic}/status",
        "qos": 1
    }

    template_payload['components'][f'{meter_id}_reading'].update(meter_config)
    # Restore the value_template after update() since meter_config doesn't include it
    template_payload['components'][f'{meter_id}_reading']['value_template'] = reading_template

    # Add generation sensor for meters with NetIDM support
    if 'netidm' in meter_config.get('protocol', ''):
        template_payload['components'][f'{meter_id}_generation'] = {
            "platform": "sensor",
            "name": "Generation",
            "value_template": generation_template,
            "json_attributes_topic": f"{base_topic}/{meter_id}/attributes",
            "unique_id": f"{meter_id}_generation",
            "unit_of_measurement": meter_config.get('unit_of_measurement', 'Wh'),
            "device_class": "energy",
            "state_class": "total_increasing",
            "icon": "mdi:solar-power"
        }

    return template_payload
