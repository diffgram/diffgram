try:
    from methods.regular.regular_api import *
except:
    from walrus.methods.regular.regular_api import *
from shared.database.event.eventhub import EventHub
from threading import Thread

@routes.route('/api/walrus/eventhub/new', methods = ['POST'])
@limiter.limit("300 per second")
def new_eventhub_web():
    """
        Creates a new eventhub entry on based on the POST params.
    """
    spec_list = [
        {"file_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        },
        {"object_type": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"kind": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"page_name": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"link": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"success": {
            'kind': bool,
            'default': None,
            'required': False
        }
        },
        {"task_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        },
        {"project_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        },

        {"task_template_id": {
            'kind': int,
            'default': None,
            'required': False
        }
        },
        {"error_log": {
            'kind': dict,
            'default': None,
            'required': False
        }
        },
        {"run_time": {
            'kind': dict,
            'default': None,
            'required': False
        }
        },
        {"member_id": {
            'kind': dict,
            'default': None,
            'required': False
        }
        },
        {"input_id": {
            'kind': dict,
            'default': None,
            'required': False
        }
        },
        {"report_template_data": {
            'kind': dict,
            'default': None,
            'required': False
        }
        },
        {"report_data": {
            'kind': dict,
            'default': None,
            'required': False
        }
        },
        {"report_template_id": {
            'kind': dict,
            'default': None,
            'required': False
        }
        },
        {"install_fingerprint": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"diffgram_version": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"storage_backend": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"service_name": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"event_type": {
            'kind': str,
            'default': None,
            'required': False
        }
        },

        {"description": {
            'kind': str,
            'default': None,
            'required': False
        }
        },

        {"previous_version": {
            'kind': str,
            'default': None,
            'required': False
        }
        },

        {"host_os": {
            'kind': str,
            'default': None,
            'required': False
        }
        },

        {"startup_time": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"shut_down_time": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
        {"created_date": {
            'kind': str,
            'default': None,
            'required': False
        }
        },
    ]
    logger.debug('Received Event from Event hub')
    if not settings.ALLOW_EVENTHUB:
        logger.debug('Eventhub disabled, ignoring...')
        return jsonify({"disabled": 'Eventhub disabled'}), 202

    log, input, untrusted_input = regular_input.master(
        request = request,
        spec_list = spec_list)

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    t = Thread(
        target = new_evenhub_threaded,
        args = ((input, log)))
    t.start()

    if len(log["error"].keys()) >= 1:
        return jsonify(log = log), 400

    return jsonify(ok = True), 200


def new_evenhub_threaded(input_data, log):
    eventhub_data, log = new_eventhub_core(
        log = log,
        kind = input_data['kind'],
        member_id = input_data['member_id'],
        success = input_data['success'],
        error_log = input_data['error_log'],
        link = input_data['link'],
        project_id = input_data['project_id'],
        task_id = input_data['task_id'],
        run_time = input_data['run_time'],
        page_name = input_data['page_name'],
        object_type = input_data['object_type'],
        task_template_id = input_data['task_template_id'],
        input_id = input_data['input_id'],
        file_id = input_data['file_id'],
        report_template_id = input_data['report_template_id'],
        report_template_data = input_data['report_template_data'],
        install_fingerprint = input_data['install_fingerprint'],
        diffgram_version = input_data['diffgram_version'],
        storage_backend = input_data['storage_backend'],
        service_name = input_data['service_name'],
        event_type = input_data['event_type'],
        description = input_data['description'],
        previous_version = input_data['previous_version'],
        host_os = input_data['host_os'],
        startup_time = input_data['startup_time'],
        shut_down_time = input_data['shut_down_time'],
    )
    if regular_log.log_has_error(log):
        logger.error(f'Error with eventhub create {log}')

    else:
        logger.debug('EventHub: event processed successfully')
def new_eventhub_core(log = regular_log.default(),
                      kind = None,
                      member_id = None,
                      success = None,
                      error_log = None,
                      description = None,
                      link = None,
                      project_id = None,
                      task_id = None,
                      run_time = None,
                      page_name = None,
                      object_type = None,
                      task_template_id = None,
                      input_id = None,
                      report_data = None,
                      report_template_data = None,
                      report_template_id = None,
                      file_id = None,
                      install_fingerprint = None,
                      diffgram_version = None,
                      storage_backend = None,
                      service_name = None,
                      event_type = None,
                      previous_version = None,
                      host_os = None,
                      startup_time = None,
                      shut_down_time = None,

                      ):
    """
        Returns the created discussion as a python dictionary.
    :param session:
    :param log:
    :param member:
    :param project:
    :param title:
    :param description:
    :param attached_elements:
    :return: created discussion python dict.
    """
    with sessionMaker.session_scope_threaded() as session:
        eventhub = EventHub.new(
            session = session,
            kind = kind,
            member_id = member_id,
            success = success,
            error_log = error_log,
            description = description,
            link = link,
            project_id = project_id,
            task_id = task_id,
            run_time = run_time,
            page_name = page_name,
            object_type = object_type,
            task_template_id = task_template_id,
            input_id = input_id,
            report_template_id = report_template_id,
            report_data = report_data,
            report_template_data = report_template_data,
            file_id = file_id,
            install_fingerprint = install_fingerprint,
            diffgram_version = diffgram_version,
            storage_backend = storage_backend,
            service_name = service_name,
            previous_version = previous_version,
            host_os = host_os,
            startup_time = startup_time,
            shut_down_time = shut_down_time,
            event_type = event_type,
        )

        eventhub_data = eventhub.serialize()
        return eventhub_data, log
