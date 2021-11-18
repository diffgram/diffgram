from diffgram import Project

project = Project(project_string_id = "testing-project-44",
                  client_id = "LIVE__f6ohnamrw1qbrv0o7lww",
                  client_secret = "gmveay9zah07axlda95k9usjmiky5y1xoex19v5rifudj1oxxqe7sxxldcgi")
dir = project.directory.get(name = 'Default')

member_list = project.get_member_list()
print(member_list)
member_list_ids = [x['member_id'] for x in member_list]
job = project.job.new(
    name = "my job test pablo 222",
    instance_type = "box",
    share = "Project",
    sync_directories = [dir],
    members_list_ids = member_list_ids,
    auto_launch = True
)
