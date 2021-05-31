# OPENCORE - ADD
from shared.database.source_control.file import File
from shared.database.annotation.instance import Instance

from shared.database.source_control.file import build_annotation_hash_list_to_object


def get_annotation_database_objects(hash_list, bravo_hash_to_object):

	out = []
	for hash in hash_list:
		out.append(bravo_hash_to_object[hash])

	return out
	#return session.query(annotation).filter(annotation.id.in_(annotation_id_list)).all()
   

def difference_between_files(
		session, 
		annotation,
		alpha, 
		bravo=None):
	"""
	1. Compares differences between hashes


	Arguments
		alpha, bravo : lists to compare

	Returns
		changes : dict
			{'unchanged', 'added', 'deleted'}

	There may be only additions... hmmm
	"""

	# can't we merge hashes for the sake of this comparison? ??? ***
	# we could also compare database objects but that feels like 
	# missing the point of all the hashing lol

	changes = {}

	if bravo:
		annotation_list_bravo = bravo.instance_list
		bravo_hash_list, bravo_hash_to_object = build_annotation_hash_list_to_object(
			annotation_list_bravo)

	annotation_list_alpha = alpha.instance_list
	alpha_hash_list, alpha_hash_to_object = build_annotation_hash_list_to_object(
		annotation_list_alpha)

	# Could maybe compare hash_to_object directly? would have to test...
	if bravo:

		set_alpha = set(alpha_hash_list)
		set_bravo = set(bravo_hash_list)

		unchanged = set_alpha.intersection(set_bravo)
		added = set_alpha.difference(set_bravo)
		deleted = set_bravo.difference(set_alpha)

		changes['unchanged'] = get_annotation_database_objects(unchanged,
															   alpha_hash_to_object)
		changes['added'] = get_annotation_database_objects(added,
														   alpha_hash_to_object)
		changes['deleted'] = get_annotation_database_objects(deleted, 
															 bravo_hash_to_object)
	
	# Handle only init case?
	else:
		changes['added'] = get_annotation_database_objects(alpha_hash_list,
														   alpha_hash_to_object)

	return changes


def file_difference(
		session, 
		file_id_alpha, 
		file_id_bravo=None):
	"""
	Compare two annotation files

	If second file is not provided compares to first files
	parent_id

	Arguments:
		alpha,bravo  file ids

	Returns:
		result, True == success, False, == fail
		changes annotations, dict

	"""

	# TODO be more clear on the output of annotations dict

	alpha = session.query(File).filter(File.id == file_id_alpha).first()

	bravo = None
	if not file_id_bravo:
		if alpha.state == "changed":
			file_id_bravo = alpha.parent_id
			
	bravo = session.query(File).filter(File.id == file_id_bravo).first()

	instance_list = difference_between_files(session, Instance,
												alpha, bravo)

	return True, instance_list


def add_change_type_flags_into_one_list(annotation_list, change_type_list):
	# this looks like (O) n^2
	# But really it's n, as annotation_list[change_type] * 3 == original annotation list size
	new_list_with_flags = []
	for change_type in change_type_list:   # n = 3, if only added n = 1
		change_list = annotation_list.get(change_type, None)
		if change_list:
			for annotation in change_list:  # n = orignal boxes n
				annotation_serialized = annotation.serialize_for_source_control()
				annotation_serialized['change_type'] = change_type
				new_list_with_flags.append(annotation_serialized)
	return new_list_with_flags


def file_difference_and_serialize_for_web(session, file_id_alpha, file_id_bravo=None):
	"""
	Serialize differences for web output
	Could this also be web end point

	Convert lists into flags

	"""


	result, instance_list = file_difference(session, file_id_alpha, file_id_bravo)

	if result == True:
		change_type_list = ['unchanged', 'added', 'deleted']
		instance_list = add_change_type_flags_into_one_list(instance_list, change_type_list)

		return True, instance_list

	else:
		return False, None




## How we want to handle if we want to use a hash instead