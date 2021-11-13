def do_routes_importing():
    from methods.attribute.attribute_template_group import new_attribute_template_group_factory_api
    from methods.attribute.attribute_template_list import api_attribute_template_list
    from methods.attribute.attribute import api_attribute_update_or_new
    from methods.attribute.attribute_template_group_update import api_attribute_template_group_update

    from methods.project.project_update import api_project_update
    from methods.source_control.file.file_update import api_file_update

    from methods.project.project_list import project_list_api

    from methods.user.account.account_password import user_password_set_api
    from methods.user import confirmation_token

    from methods.task.task.task_by_id import task_by_id_api

    from methods.task.task_template.job_pin import job_pin_api
    from methods.task.task_template.job_resync import job_resync_api

    from methods.task.task.task_list import task_list_api
    from methods.task.task.task_update import task_update_api
    from methods.task.task.task_next import task_next
    from methods.task.task.task_next_issue import task_next_issue
    from methods.task.task.task_review import task_review_api
    from methods.task.task.task_complete import api_task_complete

    from methods.task.file.file_attach import add_files_to_job_api
    from methods.task.file.dir_attach import update_dirs_to_job_api
    from methods.source_control.file.file_exists import file_list_exists_api

    from methods.task.stats.stats_leaderboard import stats_leadboard_api
    from methods.task.stats.stats_job import stats_job_api
    from methods.task.stats.stats_task import stats_task_api
    
    from methods.task.task_template.job_cancel import job_cancel_api
    from methods.task.task_template.job_info_builder import job_info_builder_api
    from methods.task.task_template.job_trainer_info import job_trainer_info_api
    from methods.task.task_template.job_launch import task_template_launch_api
    from methods.task.task_template.job_new_or_update import new_web as task_job_new_web
    from methods.task.task_template.job_list import job_list_api
    from methods.task.task_template.job_launch_list import job_launch_list_api

    from methods.task.task.task_annotator_request import task_next_by_job_api

    from methods.task.guide.guide_new import guide_new_api
    from methods.task.guide.guide_edit import guide_edit_api
    from methods.task.guide.guide_list import guide_list_api
    from methods.task.guide.guide_attach_to_job import guide_attach_to_job_api

    from methods.auth.api.auth_api_new import auth_api_credential_new_from_api

    from methods.user.account.account_new import user_new_api
    from methods.user.account.account_verify import redeem_verify_via_email_api
    from methods.user.builder.builder_signup import builder_enable_api
    from methods.user.api_enable import api_enable_user

    from methods.user.edit import user_edit
    from methods.user.login import login
    from methods.user.account.magic_login import start_magic_login_api
    from methods.user.logout import logout
    from methods.user.view import user_view
    from methods.user.one_time_pass import enable_otp_from_web

    from methods.share.share import share_member_project_api

    from methods.annotation.annotation import annotation_update_via_project_api
    from methods.annotation.labels.labels import api_label_new
    from methods.annotation.labels.view import web_build_name_to_file_id_dict
    from methods.annotation.flags import ann_is_complete_toggle

    from methods.project.project_new import project_new_api
    from methods.project.view_project import project_view
    from methods.project.edit import api_project_update_edit

    from methods.source_control.working_dir.new_directory import new_directory_api
    from methods.source_control.working_dir.directory_list import list_directory_api

    from methods.source_control.file.file_browser import view_file_diff

    from methods.source_control.file.remove import remove_file
    from methods.source_control.working_dir.view import view_working_dir_web

    from methods.source_control.working_dir.directory_update import update_directory_api

    from methods.project.star import star_status
    from methods.project.tags import update_tags

    from methods.video.video_view import get_video_single_image
    from methods.video.sequence import get_sequence

    from methods.connection.connection_admin import connection_info_api
    from methods.sync_events import sync_events_list

    from methods.event.event_list import api_event_list
    from methods.share.share_link import share_link

    from methods.discussions.discussion_new import new_discussion_web
    from methods.discussions.discussion_detail import discussion_detail_web
    from methods.discussions.discussion_list import discussion_list_web
    from methods.discussions.discussion_comment_new import new_discussion_comment_web
    from methods.discussions.discussion_comment_list import list_discussion_comment_web
    from methods.discussions.discussion_comment_update import update_discussion_comment_web
    from methods.discussions.discussion_update import update_discussion_web

    from methods.video.instance.next_instance import next_instance

    from methods.event.event_create import api_event_create
    from methods.event.user_visit_history import user_visit_history_api
    from methods.annotation.instance_template_new import new_instance_template_api
    from methods.annotation.instance_template_list import list_instance_template_api
    from methods.annotation.instance_template_update import update_instance_template_api
    from methods.annotation.instance_history import instance_history_api

    from methods.report.report_runner import report_save_api
    from methods.report.report_list import report_list_api
    from methods.userscript.userscript import userscript_new_api

    from methods.batch.batch_new import new_input_batch
    from methods.batch.append_to_batch import append_to_batch_api
    from methods.batch.batch_detail import input_batch_detail_api

    from methods.model.model_run_list import model_run_list_web
    from methods.query_engine.query_suggest import query_suggest_web
    from methods.source_control.file.file_cache_regen import api_file_cache_regen

    from methods.video.sequence_preview_create import api_create_sequence_preview

    from methods.ui_schema.ui_schema import ui_schema_new_api

    from methods.configs.mailgun_is_set import mailgun_is_set
    from methods.task.credential.credential_type_new import new_credential_type_api
    from methods.task.credential.credential_list import credential_list_api
    from methods.task.credential.credential_type_attach_to_job import credential_type_attach_to_job_api
    from methods.task.credential.credential_type_update import update_credential_type_image_api

<<<<<<< HEAD
    from methods.task.stats.fast_stats import job_stat, jon_user_stats
=======


>>>>>>> 1dc2e64262e12b02acbf83032d29e3516f6a15ac
