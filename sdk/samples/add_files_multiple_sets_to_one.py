from diffgram import Project

# TODO replace `Project()` with full credential object - to get started quickly can copy and paste from Share/Developer Auth
project = Project()

# Gets target joint directory
# TODO replace string `joint_dir` with desired name
# This is the dir that will house the combination of next two dirs
join_dir = project.directory.get("joint_dir")

# TODO replace string `first` with desired name
first_dir = project.directory.get("first")		# Gets directory object
file_list = first_dir.list_files()		# Gets list of files. can add search_term
print("Length", len(file_list))
result = join_dir.add(file_list)
print(result)

# TODO replace string `second` with desired name
second_dir = project.directory.get("second")
file_list = second_dir.list_files()
print("Length", len(file_list))
result = join_dir.add(file_list)
print(result)

# Can add further datasets here. Or can do this on demand

# Verify results
file_list = join_dir.list_files()
print("Length Joint", len(file_list))
