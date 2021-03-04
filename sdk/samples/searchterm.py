from diffgram import Project

# TODO replace `Project()` with full credential object - to get started quickly can copy and paste from Share/Developer Auth
project = Project()

first_dir = project.directory.get("Default")

# TODO replace `apples` with desired search term
file_list = first_dir.list_files(
    search_term="apples")

print(file_list)
print("Length", len(file_list))
print(file_list[0].original_filename)


