try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.permissions.super_admin_only import Super_Admin
from shared.database.input import Input


@routes.route('/api/v1/admin/queue/status',
              methods = ['GET'])
@Super_Admin.is_super(allow_support=True)
def api_admin_queue_status():
    with sessionMaker.session_scope() as session:
        queue_status = serialize_queue_status(session)

        return jsonify(queue_status = queue_status), 200


def serialize_queue_status(session):
    out = {}

    counts = {
        'Count in Remote Queue (Max 100)': get_count_media_items_in_remote_queue(session),
        'Success Last 10 minutes (Max 100)': get_very_recent_success_items(session),
        'Success Last 24 hours (Max 1000)': get_recent_success_items(session),
        'Not Success Last 24 hours (Max 1000)': get_recent_not_success_items(session)
    }
    out['Counts'] = counts
    return out

def get_count_media_items_in_remote_queue(session):
    count = session.query(Input).filter(
            Input.processing_deferred == True,
            Input.archived == False,
            Input.status != 'success',
            or_(Input.mode == None, Input.mode != 'copy_file')
        ).limit(100).count()
    return count


def get_recent_success_items(session):

    one_day_ago = datetime.datetime.utcnow() - \
                        datetime.timedelta(hours = 24)

    count = session.query(Input).filter(
            Input.status == 'success',
            Input.created_time > one_day_ago
        ).limit(1000).count()
    return count


def get_very_recent_success_items(session):

    ten_minutes_ago = datetime.datetime.utcnow() - \
                        datetime.timedelta(minutes = 10)

    count = session.query(Input).filter(
            Input.status == 'success',
            Input.created_time > ten_minutes_ago
        ).limit(100).count()
    return count


def get_recent_not_success_items(session):

    one_day_ago = datetime.datetime.utcnow() - \
                        datetime.timedelta(hours = 24)

    count = session.query(Input).filter(
            Input.processing_deferred == False,
            Input.archived == False,
            Input.status.in_(['failed', 'init']),
            Input.created_time > one_day_ago
        ).limit(1000).count()
    return count

