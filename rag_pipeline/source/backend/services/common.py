from typing import Optional
from types import FrameType
import inspect


def get_caller_name(depth: int = 0) -> str:
    """
    Get caller name.
    """

    skip_names = {
        'run_until_complete', 'call_and_report',
        'pytest_pyfunc_call', 'pytest_runtest_call',
        '_execute', '_run_module_code', 'runtestprotocol',
        'inner', 'run', '__call__', 'run_forever',
        'pytest_runtest_protocol', 'pytest_runtestloop',
        'wrap_session', 'async_wrapper',
        'run_path', '<lambda>', '_run_once', 'main',
        'from_call', '_run', '<module>',
        '_hookexec', '_main',
        '_run_code', 'runtest', '_run_module_as_main',
        '_multicall', 'pytest_cmdline_main', 'run_file'
    }

    frame: Optional[FrameType] = inspect.currentframe()
    filtered_depth = 0

    while frame:
        function_name = frame.f_code.co_name
        filename = frame.f_code.co_filename

        if (
            function_name not in skip_names
            and "tenacity" not in filename
        ):
            if filtered_depth == depth:
                module = frame.f_globals.get("__name__", "")
                return f"{module}.{function_name}"
            filtered_depth += 1

        frame = frame.f_back

    return "<unknown>"
