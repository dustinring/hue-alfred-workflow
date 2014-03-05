# -*- coding: utf-8 -*-
import json
import os

import alp

from base_filter import HueFilterBase


ITEMS = '''
set_color:
  title: Set color to…
  subtitle: Accepts 6-digit hex colors or CSS literal color names (e.g. "blue")
  valid: false

color_picker:
  title: Use color picker…
  valid: true

set_effect:
  title: Set effect…
  valid: false

effect_none:
  title: None
  subtitle: 'Cancel any ongoing effects, such as a color loop.'

color_loop:
  title: Color loop

set_brightness:
  title: Set brightness…
  subtitle: 'Set on a scale from 0 to 255, where 0 is off.'
  valid: false

set_reminder:
  title: Set reminder…
  valid: false

light_rename:
  title: Set light name to…
  valid: false
'''


class HueLightFilter(HueFilterBase):

    items_yaml = ITEMS

    def get_results(self, lid, light_name, query, is_on=None):
        control = query.split(':')

        if lid != 'all':
            icon = ('icons/%s.png' % lid) if is_on else 'icons/off.png'
        else:
            icon = 'icon.png'

        if len(control) is 1:
            self.partial_query = control[0]

            if is_on or lid == 'all':
                self._add_item('light_off',
                    title='Turn %s off' % light_name,
                    autocomplete='lights:%s:off' % lid,
                    icon=icon,
                    arg=json.dumps({
                        'lid': lid,
                        'data': {'on': False},
                    }))

            if not is_on or lid == 'all':
                self._add_item(
                    title='Turn %s on' % light_name,
                    autocomplete='lights:%s:on' % lid,
                    icon=icon,
                    arg=json.dumps({
                        'lid': lid,
                        'data': {'on': True},
                    }))

            if is_on or lid == 'all':
                self._add_item('set_color',
                    subtitle='',
                    icon=icon,
                    autocomplete='lights:%s:color:' % lid)

                self._add_item('set_effect',
                    subtitle='',
                    icon=icon,
                    autocomplete='lights:%s:effect:' % lid)

                self._add_item('set_brightness',
                    subtitle='',
                    icon=icon,
                    autocomplete='lights:%s:bri:' % lid)

                self._add_item('set_reminder',
                    icon=icon,
                    autocomplete='lights:%s:reminder:' % lid)

            if lid != 'all':
                self._add_item('light_rename',
                    icon=icon,
                    autocomplete='lights:%s:rename:' % lid)

        elif len(control) >= 2:
            function = control[0]
            value = control[1]

            if function == 'color':

                self._add_item('set_color',
                    valid=True,
                    icon=icon,
                    arg=json.dumps({
                        'action': 'set_color',
                        'lid': lid,
                        'color': value,
                    }))

                self._add_item('color_picker',
                    icon=icon,
                    arg='colorpicker:%s' % lid)

            elif function == 'bri':
                self._add_item('set_brightness',
                    title='Set brightness to %s' % (value or u'…'),
                    icon=icon,
                    valid=True if value else False,
                    arg=json.dumps({
                        'lid': lid,
                        'data': { 'bri': int(value) if value else 1 },
                    }))

            elif function == 'effect':
                self._add_item('effect_none',
                    icon=icon,
                    arg=json.dumps({
                        'lid': lid,
                        'data': {'effect': 'none'},
                    }))

                self._add_item('color_loop',
                    icon=icon,
                    arg=json.dumps({
                        'lid': lid,
                        'data': {'effect': 'colorloop'},
                    }))

            elif function == 'reminder':
                try:
                    int_value = int(value)
                except ValueError:
                    int_value = False

                def reminder_title(suffix):
                    return u'Blink {light_name} in {time} {suffix}'.format(
                        light_name=light_name,
                        time=(int_value or u'…'),
                        suffix=suffix,
                    )

                self._add_item(
                    title=reminder_title('seconds'),
                    subtitle='',
                    icon=icon,
                    valid=True if int_value else False,
                    arg=json.dumps({
                        'lid': lid,
                        'action': 'reminder',
                        'time_delta': int_value,
                    }))

                self._add_item(
                    title=reminder_title('minutes'),
                    subtitle='',
                    icon=icon,
                    valid=True if int_value else False,
                    arg=json.dumps({
                        'lid': lid,
                        'action': 'reminder',
                        'time_delta': (int_value * 60) if int_value else 0,
                    }))

                self._add_item(
                    title=reminder_title('hours'),
                    subtitle='',
                    icon=icon,
                    valid=True if int_value else False,
                    arg=json.dumps({
                        'lid': lid,
                        'action': 'reminder',
                        'time_delta': (int_value * 60 * 60) if int_value else 0,
                    }))

            elif function == 'rename':
                self._add_item('light_rename',
                    icon=icon,
                    valid=True,
                    arg=json.dumps({
                        'action': 'rename',
                        'lid': lid,
                        'data': {'name': value},
                    }))

        self._filter_results()
        return self.results


if __name__ == '__main__':
    light_filter = HueLightFilter()
    results = light_filter.get_results(alp.args()[0])
    alp.feedback(results)