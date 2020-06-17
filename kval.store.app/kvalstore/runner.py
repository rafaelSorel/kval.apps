__author__ = 'kval team'

__all__ = ['run']

import copy
from impl.kvalstore_runner import KvalStoreRunner as Runner
from impl.kvalstore_context import KvalStoreContext as Context

__RUNNER__ = Runner()


def run(provider, context=None):
    if not context:
        context = Context(plugin_id='kval.store.app', plugin_name=u'Kval Store')

    context.log_debug('Starting kval store app...')
    python_version = 'Unknown version of Python'
    try:
        import platform

        python_version = str(platform.python_version())
        python_version = 'Python %s' % python_version
    except:
        # do nothing
        pass

    version = context.get_system_version()
    name = context.get_name()
    addon_version = context.get_version()
    context_params = copy.deepcopy(context.get_params())

    context.log_notice('Running: %s (%s) on %s with %s\n\tPath: %s\n\tParams: %s' %
                       (name, addon_version, version, python_version,
                        context.get_path(), str(context_params)))

    __RUNNER__.run(provider, context)

    context.log_info('Shutdown of Kval Store App')
