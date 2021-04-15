import requests
import logging
import time


logger = logging.getLogger(__name__)


class LibraryCaller:

    def __init__(self):
        pass

    @staticmethod
    def activate_carriers():
        try:
            # print('start')
            response = requests.post(url='http://127.0.0.1:8099/api/dutCtrl5g/v0/testModel', json=Model().post_request_body, timeout=(3600, 3600))
            message = f'{response.request.method} {response.request.url}--\
                status code {response.status_code} -- {response.json()}'
            logger.info(message)
            print(message)
            # print('end')
        except Exception as e:
            # logger.info(msg=e)
            print('error ',e)

    def deactivate_carriers(self):
        pass
        # TODO

    @staticmethod
    def get_dut_status() -> int:
        try:
            response = requests.get(url='http://127.0.0.1:8099/api/dutCtrl5g/v0/dutStatus')
            message = (f'{response.request.method} {response.request.url}--'
                       f'status code {response.status_code} -- {response.json()}')
            print(message)
            #logger.info(message)
            print(response.status_code)
            return response.status_code
        except Exception as e:
            print(e)
            # logger.info(msg=e)

    @staticmethod
    def get_bler():
        try:
            response = requests.post(
                url='http://127.0.0.1:8099/api/dutCtrl5g/v0/measurement',
                json=Model().bler_request_body,
                timeout=(3600, 3600))
            message = f'{response.request.method} {response.request.url}--' \
                      f'status code {response.status_code} -- {response.json()}'
            # logger.info(message)
        except Exception as e:
            # logger.info(msg=e)
            pass

    @staticmethod
    def check_dut_status_ready():
        while LibraryCaller.get_dut_status() == 202:
            message = 'Wait for DUT configuration to finish'
            # logger.info(message)
            time.sleep(5)


class Model:

    def __init__(self):
        self.post_request_body = {
            "testModels": [{
                "commonCellParameters": {
                "operatingBand": "77",
                "physicalCellId": "1",
                "cellId": "1",
                "tddFrameConfiguration": "dl_special_ul_7_1_2",
                "tddSpecialSlotConfiguration": "dlsymbl_gp_ulsymbl_6_4_4",
                "virtualAntenna": "All",
                "polarization": "0",
                "standard": "5GNR",
                "specificationVersion": "3gpp_38141_v15_1"
                },
                "downlinkParameters": {
                    "downlinkFrequencyMhz": 3950.01,
                    "downlinkTestmodel": "nr-tm1-1_scs30khz_rank1_ant0",
                    "downlinkBandwidth": "100",
                    "downlinkPower": 36.00,
                    "powerScale": 0.0,
                    "peakToAverageRatio": "0"
                },
                "uplinkParameters": {
                    "uplinkFrequencyMhz": 3950.01,
                    "uplinkTestmodel": "g-fr1-a1-5",
                    "uplinkBandwidth": "100",
                    "userOfInterest": "0",
                    "rbOffset": 0
                }
            }],
            "releaseVersion": "5G19B",
            "cellConfigurationType": "",
            "dutRfOn": True,
            "radioModuleType": "AEQV"
        }

        self.bler_request_body = {
            "measurementType": "ulBler",
            "virtualAntenna": "1",
            "cellId": 1,
            "measurementTimeMs": 1000.00000000000
        }


if __name__ == '__main__':
    remote_url = "http://127.0.0.1:8099/"
    LibraryCaller.get_dut_status()
