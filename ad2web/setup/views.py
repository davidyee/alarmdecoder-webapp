# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response, redirect, url_for
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..decoder import decoder
from ..extensions import db
from ..decorators import admin_required
from ..settings.models import Setting
from .forms import (DeviceTypeForm, NetworkDeviceForm, SerialDeviceForm,
                   DeviceLocationForm, SSLForm, SSLHostForm, DeviceForm)
from .constants import (STAGES, SETUP_TYPE, SETUP_LOCATION, SETUP_NETWORK,
                    SETUP_LOCAL, SETUP_DEVICE, SETUP_COMPLETE)

setup = Blueprint('setup', __name__, url_prefix='/setup')

def set_stage(stage):
    setup_stage = Setting.get_by_name('setup_stage')
    setup_stage.value = stage
    db.session.add(setup_stage)

@setup.context_processor
def setup_context_processor():
    return { }

@setup.route('/')
def index():
    return render_template('setup/index.html')

@setup.route('/type', methods=['GET', 'POST'])
def type():
    form = DeviceTypeForm()
    if form.validate_on_submit():
        # do stuff
        #

        device_type = Setting.get_by_name('device_type')
        device_type.value = form.device_type.data
        db.session.add(device_type)

        set_stage(SETUP_TYPE)

        db.session.commit()

        return redirect(url_for('setup.location'))

    return render_template('setup/type.html', form=form)

@setup.route('/location', methods=['GET', 'POST'])
def location():
    form = DeviceLocationForm()
    if form.validate_on_submit():
        # do stuff
        #

        device_location = Setting.get_by_name('device_location')
        device_location.value = form.device_location.data
        db.session.add(device_location)

        set_stage(SETUP_LOCATION)
        db.session.commit()

        return redirect(url_for('setup.{0}'.format(device_location.value)))

    return render_template('setup/location.html', form=form)

@setup.route('/local', methods=['GET', 'POST'])
def local():
    form = SerialDeviceForm()
    if form.validate_on_submit():
        # do stuff
        #

        device_path = Setting.get_by_name('device_path')
        baudrate = Setting.get_by_name('device_baudrate')

        device_path.value = form.device_path.data
        baudrate.value = form.baudrate.data

        db.session.add(device_path)
        db.session.add(baudrate)

        set_stage(SETUP_LOCAL)
        db.session.commit()

        return redirect(url_for('setup.device'))

    return render_template('setup/local.html', form=form)

@setup.route('/network', methods=['GET', 'POST'])
def network():
    form = NetworkDeviceForm()
    if form.validate_on_submit():
        # do stuff
        #

        device_address = Setting.get_by_name('device_address')
        device_port = Setting.get_by_name('device_port')
        ssl = Setting.get_by_name('use_ssl')

        device_address.value = form.device_address.data
        device_port.value = form.device_port.data
        ssl.value = form.ssl.data

        db.session.add(device_address)
        db.session.add(device_port)
        db.session.add(ssl)

        set_stage(SETUP_NETWORK)
        db.session.commit()

        # if form.ssl.data == True:
        #     return redirect(url_for('setup.ssl'))
        # else:
        return redirect(url_for('setup.test'))

    return render_template('setup/network.html', form=form)

@setup.route('/ssl', methods=['GET', 'POST'])
def ssl():
    form = SSLHostForm()
    if form.validate_on_submit():
        # do stuff
        #

        return redirect(url_for('setup.device'))

    return render_template('setup/ssl.html', form=form)

@setup.route('/device', methods=['GET', 'POST'])
def device():
    form = DeviceForm()
    if form.validate_on_submit():
        device_address = Setting.get_by_name('device_address')
        address_mask = Setting.get_by_name('address_mask')
        lrr_enabled = Setting.get_by_name('lrr_enabled')
        zone_expanders = Setting.get_by_name('emulate_zone_expanders')
        relay_expanders = Setting.get_by_name('emulate_relay_expanders')
        deduplicate = Setting.get_by_name('deduplicate')

        device_address.value = form.device_address.data
        address_mask.value = form.address_mask.data
        lrr_enabled.value = form.lrr_enabled.data
        zone_expanders.value = ''.join(['Y' if str(x) in form.zone_expanders.data else 'N' for x in xrange(1, 6)])
        relay_expanders.value = ''.join(['Y' if str(x) in form.relay_expanders.data else 'N' for x in xrange(1, 5)])
        deduplicate.value = form.deduplicate.data

        db.session.add(device_address)
        db.session.add(address_mask)
        db.session.add(lrr_enabled)
        db.session.add(zone_expanders)
        db.session.add(relay_expanders)
        db.session.add(deduplicate)

        # TODO: configure device itself.

        set_stage(SETUP_COMPLETE)
        db.session.commit()

        return redirect(url_for('setup.test'))

    return render_template('setup/device.html', form=form)

@setup.route('/test', methods=['GET', 'POST'])
def test():
    try:
        decoder.close()
        decoder.open()

        flash('Okay!')
    except Exception:   # FIXME
        pass

    set_stage(SETUP_DEVICE)
    db.session.commit()

    return render_template('setup/test.html', form=None)