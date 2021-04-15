from flask import Flask, render_template, flash, redirect, request, current_app, jsonify
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf.file import FileField
from wtforms import StringField, TextField, HiddenField, ValidationError, RadioField, \
    BooleanField, SubmitField, IntegerField, FormField, validators, SelectField, \
    SelectMultipleField, FloatField
from wtforms.validators import InputRequired, optional
from flask_wtf import FlaskForm
from utils.common import get_specific_config_data, get_default_config, get_root_folder
from flask_socketio import SocketIO, emit

# straight from the wtforms docs:
import sys
import logging

root_folder = get_root_folder()
sys.path.insert(0, root_folder)
from auto_test_20b.tools_dev.start import start_stability_test
from auto_test_20b.web_tool.sample_application.log_handler.socketio_handler import SocketIOHandler
from auto_test_20b.tools_dev.testings.activate_carriers_setting import ActivateCarriersSetting


class BaseForm(FlaskForm):
    '''
    errors 中的键值对长这样
    ('password', ['Please enter right format password'])
    [1][0] 表示取'Please enter right format password'
    '''

    def get_error(self):
        return self.errors.popitem()[1][0]

    def validate(self):
        return super(BaseForm, self).validate()


class ExecutingForm(BaseForm):
    # runner_type = StringField(validators=[InputRequired(message='Please select Runner Type')])
    dl_tm = StringField(validators=[InputRequired(message='Please select DL TM')])
    ul_tm = StringField(validators=[InputRequired(message='Please select UL TM')])
    tdd_switch = StringField(validators=[InputRequired(message='Please select TDD SWITCH')])
    abil_slot = StringField(validators=[InputRequired(message='Please select ABIL SLOT')])
    rru = StringField(validators=[InputRequired(message='Please select RRU')])
    # rru = StringField(u'RRU', [validators.optional()])
    case_type = StringField(validators=[InputRequired(message='Please select CARRIER TYPE')])

    c1_bw = StringField(validators=[InputRequired(message='Please enter BW@Sample freq(MHz) for C1')])
    c1_freq = FloatField(u'FREQ (MHz) for c1', [validators.optional()])
    c1_power = FloatField(u'POWER (dBm) for c1', [validators.optional()])
    c1_cell_id = IntegerField(u'Cell ID for c1', [validators.optional()])
    c1_rnti = IntegerField(u'Rnti for c1', [validators.optional()])
    c1_rboffset = IntegerField(u'RB Offset for c1', [validators.optional()])
    c1_power_backoff = FloatField(u'Power Backoff (dBm) for c1', [validators.optional()])

    c2_bw = StringField(u'Please enter BW@Sample freq(MHz) for C2', [validators.optional()])
    c2_freq = FloatField(u'FREQ (MHz) for C2', [validators.optional()])
    c2_power = FloatField(u'POWER (dBm) for C2', [validators.optional()])
    c2_cell_id = IntegerField(u'Cell ID for C2', [validators.optional()])
    c2_rnti = IntegerField(u'Rnti for C2', [validators.optional()])
    c2_rboffset = IntegerField(u'RB Offset for C2', [validators.optional()])
    c2_power_backoff = FloatField(u'Power Backoff (dBm) for C2', [validators.optional()])

    auto_generate = StringField(validators=[InputRequired(message='Please select Auto-Generate XML')])
    beamer_log_capture = StringField(u'Capture Beamer Log', [validators.optional()])

    l1_call_list = StringField(u'Please select L1Call xml file', [validators.optional()])
    bf_cal_list = StringField(u'Please select BFCal xml file', [validators.optional()])

    cycle_times = IntegerField(validators=[InputRequired(message="Please input test cycle times")])
    jesd_flag = BooleanField(validators=[optional()])
    cpri_flag = BooleanField(validators=[optional()])
    dpdin_flag = BooleanField(validators=[optional()])
    cpri_repeat_times = IntegerField(validators=[optional()])
    jesd_repeat_times = IntegerField(validators=[optional()])
    dpdin_repeat_times = IntegerField(validators=[optional()])

    # empty_field_list = []
    #
    # def validate(self):
    #     if not super().validate():
    #         print('stop')
    #         return False
    #     result = True
    #
    #     self.empty_field_list.clear()
    #     if self.runner_type.data == "tm" and self.auto_generate.data == "auto":
    #         if len(self.rru.data) == 0:
    #             # self.rru.errors.append("Please select RRU")
    #             self.empty_field_list.append("RRU")
    #             result = False
    #         if self.c1_freq.data is None:
    #             # self.c1_freq.errors.append("Please input FREQ (MHz) for C1")
    #             self.empty_field_list.append("FREQ (MHz) for c1")
    #             result = False
    #         if self.c1_power.data is None:
    #             # self.c1_power.errors.append("Please input POWER (dBm) for C1")
    #             self.empty_field_list.append("POWER (dBm) for c1")
    #             result = False
    #         if self.case_type.data != "1CC":
    #             if self.c2_freq.data is None:
    #                 # self.c2_freq.errors.append("Please input FREQ (MHz) for C2")
    #                 self.empty_field_list.append("FREQ (MHz) for c2")
    #                 result = False
    #             if self.c2_power.data is None:
    #                 # self.c2_power.errors.append("Please input POWER (dBm) for C2")
    #                 self.empty_field_list.append("POWER (dBm) for c2")
    #                 result = False
    #     elif self.runner_type.data == "l1call" and self.l1_call_list.data == "":
    #         self.empty_field_list.append("Please select L1Call xml file.")
    #         result = False
    #     elif self.runner_type.data == "bfcal" and self.bf_cal_list.data == "":
    #         self.empty_field_list.append("Please select BFCal xml file.")
    #         result = False
    #
    #     return result
    #
    # def get_errors(self):
    #     return f"Please input fields: [{', '.join(self.empty_field_list)}]"


def dummy_function(activate_carriers_setting, test_options):
    # Added by L1 INT3 for Web log presentation
    import json
    # socket_io_server_url = os.environ.get("socket_io_server_url", None)
    # print(f"socket_io_server_url:{socket_io_server_url}")
    # if socket_io_server_url is not None:
    #     socket_io_server_url: object = json.loads(socket_io_server_url)
    #     socket_io_handler = SocketIOHandler(socket_io_server_url["url"], socket_io_server_url["event"])
    #     socket_io_handler.setFormatter(formatter)
    #     socket_io_handler.setLevel(logging.getLevelName(self.log_level))
    #     self.logger.addHandler(socket_io_handler)
    server_url = "http://localhost:5000/"
    event = "runner_message_event"
    socket_io_handler = SocketIOHandler(server_url, event)
    socket_io_handler.setLevel(logging.DEBUG)
    logger = logging.getLogger("main")
    logger.addHandler(socket_io_handler)
    logger.setLevel(logging.DEBUG)
    timer = 1
    while timer < 1000:
        logger.info(f"timer: {timer}")
        timer += 1


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
    # highly recommend =)
    # https://github.com/mbr/flask-appconfig
    # Bootstrap(app)

    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'
    app.config['RECAPTCHA_PUBLIC_KEY'] = \
        '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'
    socketio = SocketIO(app)

    @app.route('/', methods=('GET', 'POST'))
    def index():
        form = get_default_config()
        rru_list = get_specific_config_data('rru_list')
        bandwidth_list = get_specific_config_data('bandwidth_list')
        # form.validate_on_submit()  # to get error messages to the browser
        # if request.method == 'POST':
        #     print('do something')
        # add function

        # return redirect('/')
        # flash('critical message', 'critical')
        # flash('error message', 'error')
        # flash('warning message', 'warning')
        # flash('info message', 'info')
        # flash('debug message', 'debug')
        # flash('different message', 'different')
        # flash('uncategorized message')
        return render_template('index.html', form=form, rru_list=rru_list, bandwidth_list=bandwidth_list, tm_list=[])

    @app.route('/executing', methods=['POST'])
    def execute():
        form = ExecutingForm(request.form)
        # print(form)
        # if form.validate():
        #     try:
        activate_carriers_setting = ActivateCarriersSetting(ABIL_SLOT_NUMBER=form.abil_slot,
                                                            RRU=form.rru,
                                                            TDD_SWITCH=form.tdd_switch,
                                                            CASE_TYPE=form.case_type,
                                                            DL_TM=form.dl_tm,
                                                            BANDWIDTH=form.c1_bw,
                                                            FREQUENCY=form.c1_freq,
                                                            POWER=form.c1_power)
        test_options = {
            'CycleTimes': form.cycle_times,
            'CpriFlag': form.cpri_flag,
            'CpriRepeatTimes': form.cpri_repeat_times,
            'JesdFlag': form.jesd_flag,
            'JesdRepeatTimes': form.jesd_repeat_times,
            'UdpcpFlag': False,
            'SoapFlag': False,
            'DpdinFlag': form.dpdin_flag,
            'DpdinRepeatTimes': form.dpdin_repeat_times}
        # start_stability_test(activate_carriers_setting, test_options)
        dummy_function(activate_carriers_setting, test_options)
        # return jsonify({'type': 'success', 'message': 'Started successfully.'})
        #     except RuntimeError as exp:
        #         current_app.logger.error(exp)
        #         return jsonify({'type': 'error', 'message': str(exp)})
        # else:
        #     print("values not valid!")
        #     errors = form.get_errors()
        #     current_app.logger.error(errors)
        #     print(errors)
        #     return jsonify({'type': 'error', 'message': errors})

    @socketio.on('connect')
    def connect():
        print(f"{request.sid} connected!!")
        current_app.logger.info("websocket connected.")

    @socketio.on('disconnect')
    def disconnect():
        print(f"{request.sid} disconnected!!")
        current_app.logger.info("websocket disconnected.")

    @socketio.on('runner_message_event')
    def runner_handleMessage(message):
        emit('runner_message', message, broadcast=True, include_self=False)

    @socketio.on('ping_message_event')
    def ping_handleMessage(message):
        emit('ping_message', message, broadcast=True, include_self=False)

    @socketio.on('carrier_activation_message_event')
    def carrier_activation_handleMessage(message):
        emit('carrier_activation_message', message, broadcast=True, include_self=False)

    @socketio.on('iq_capture_message_event')
    def iq_capture_handleMessage(message):
        emit('iq_capture_message', message, broadcast=True, include_self=False)

    @socketio.on('bler_check_message_event')
    def bler_check_handleMessage(message):
        emit('bler_check_message', message, broadcast=True, include_self=False)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
