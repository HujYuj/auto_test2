import os
import sys

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(root_path, ".."))
try:
    from nokia_5G_hwiv_configuration.libraries.common_lib.LoggingCommon import LoggingCommon
except ImportError:
    sys.path.insert(0, os.getcwd())
    from nokia_5G_hwiv_configuration.libraries.common_lib.LoggingCommon import LoggingCommon
from stopit import threading_timeoutable as timeoutable
# from nokia_5G_hwiv_configuration.resources.test_environment.json_keyword_mapper import JsonKeywordMapper


@timeoutable('TIME OUT')
def main(l1_xml=None, L1Connection_file='L1Connection'):
    # Environment variable to select configuration/test to run
    tc_name = os.environ.get('SCRIPTS')
    if tc_name is None:
        tc_name = L1Connection_file  # Use "FDDL1Conn" for FDD testing
        print("Using default test case: {}".format(tc_name))

    # Environment variable to select L1 parameters xml for test
    tc_l1_xml = os.environ.get('L1_XML')
    if tc_l1_xml is None:
        if l1_xml:
            tc_l1_xml = l1_xml
        else:
            tc_l1_xml = "LibraryParametersExample_TM1.1_A1-5_LB_AEQB_100MHz"

    # Environment variable to select environment xml for test
    tc_env_xml = os.environ.get('ENV_XML')
    if tc_env_xml is None:
        tc_env_xml = "env_parameters_example"

    logging_common = LoggingCommon(tc_l1_xml=tc_l1_xml, env_xml=tc_env_xml)
    logger = logging_common.common_logging_init()

    logger.info(f"Test case: {tc_name}")
    logger.info(f"L1_parameter file: {tc_l1_xml}")
    logger.info(f"Environment file: {tc_env_xml}")
    root_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, root_path + os.sep + os.sep + 'JESD')
    sys.path.insert(0, root_path + os.sep + os.sep + 'Dpdin')
    try:
        logger.error_flag = False
        print(sys.path)
        test_case = getattr(__import__(tc_name), tc_name)(logger)
        test_case.run_test()
    except Exception as e:
        logger.exception("Test crashed with {}".format(e))
        logger.error_flag = True

    try:
        # build_json_case_result(test_case, tc_l1_xml, tc_name)
        pass
    except Exception as e:
        logger.exception("Creation of the result json failed with {}".format(e))

    status = logging_common.common_logging_end()
    if status == "FAIL":
        print("\n{h}\nTest case FAILED.\n{h}\n".format(h="#" * 200))
        # exit(-1)
    return status


if __name__ == "__main__":
    # l1_xml = "LibraryParametersExample_TM1.1_A1-5_100MHz_AEQB"
    l1_xml = "LibraryParametersExample_4X4_MIMO_LB_AEQB_L1_Call"
    main(l1_xml)
