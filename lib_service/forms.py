from wtforms import StringField, FloatField, IntegerField, validators, BooleanField
from wtforms.validators import InputRequired, optional, Length, DataRequired
from flask_wtf import FlaskForm


class ExecutingForm(FlaskForm):
    # runner_type = StringField(validators=[InputRequired(message='Please select Runner Type')])
    dl_tm = StringField(validators=[InputRequired(message='Please select DL TM')])
    ul_tm = StringField(validators=[InputRequired(message='Please select UL TM')])
    tdd_switch = StringField(validators=[InputRequired(message='Please select TDD SWITCH')])
    abil_slot = StringField(validators=[InputRequired(message='Please select ABIL SLOT')])
    rru = StringField(validators=[InputRequired(message='Please select RRU')])
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

    cycle_times = IntegerField(validators=[InputRequired(message="Please input test cycle times")])
    jesd_flag = BooleanField(validators=[DataRequired(), ])
    cpri_flag = BooleanField(validators=[DataRequired(),])
    dpdin_flag = BooleanField(validators=[DataRequired(),])
    cpri_repeat_times = IntegerField(validators=[optional()])
    jesd_repeat_times = IntegerField(validators=[optional()])
    dpdin_repeat_times = IntegerField(validators=[optional()])
    pause_on_cpri_fail = BooleanField(validators=[DataRequired(),])
    pause_on_jesd_fail = BooleanField(validators=[DataRequired(),])
    pause_on_power_fail = BooleanField(validators=[DataRequired(),])

    power_supply_model = StringField(validators=[InputRequired(message="Please select power supply model")])
    power_supply_address = StringField(validators=[InputRequired(message="Please input power supply address")])
    serial_port = IntegerField(validators=[InputRequired(message="Please select serial port number")])
    l1_version = StringField(validators=[InputRequired(message="Please select L1 initial version")])
