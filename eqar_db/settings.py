from split_settings.tools import optional, include

include(
    'settings_base.py',
    optional('settings_local.py')
)

