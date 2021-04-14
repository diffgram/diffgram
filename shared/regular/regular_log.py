# OPENCORE - ADD
def default():
    return default_api_log()


def default_api_log():
    log = {}
    log['error'] = {}
    log['info'] = {}
    log['success'] = False

    return log


def result_has_error(result):
    return 'log' in result and result['log'].get('error') and len(result['log'].get('error').keys()) >= 1


def log_has_error(log):
    print(log)
    return log and log.get('error') and len(log.get('error').keys()) >= 1
