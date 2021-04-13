# OPENCORE - ADD
from shared.database.common import *
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.database.source_control.file import File
from shared.data_tools_core import Data_tools

data_tools = Data_tools().data_tools


class Video(Base):
	"""
	A video has:
		multiple files
		multiple instances
		multiple keyframes

	"""
	__tablename__ = 'video'
	id = Column(Integer, primary_key = True)
	
	# TODO confirm this is deprecated!!!
	keyframe_list = Column(MutableDict.as_mutable(JSONEncodedDict), 
					default = {})	
	# TODO is this deprecated? ###
	label_id_map_to_instance_group_id = Column(MutableDict.as_mutable(JSONEncodedDict), 
					default = {})
	####

	root_blob_path_to_frames = Column(String())

	url_signed_expiry = Column(Integer)
	file_signed_url = Column(String())
	file_blob_path = Column(String())

	preview_image_url_thumb = Column(String())
	preview_image_id = Column(Integer, ForeignKey('image.id'))
	preview_image = relationship("Image")

	width = Column(Integer)
	height = Column(Integer)

	soft_delete = Column(Boolean, default = False)
	filename = Column(String())

	# frame_number is 0 indexed while frame_count is not?
	# ie last frame number == 68 and frame_count == 69 == ok
	frame_count = Column(Integer)
	
	description = Column(String())
	
	created_time = Column(DateTime, default=datetime.datetime.utcnow)
	last_updated_time = Column(DateTime)

	status = Column(String(), default = "init")

	frame_rate = Column(Integer)	# Actual FPS
	original_fps = Column(Integer)
	fps_conversion_ratio = Column(Float, default = 1)

	offset_in_seconds = Column(Integer)
	parent_video_split_duration = Column(Integer())


	def get_by_id(session, id):    
		return session.query(Video).filter(
			Video.id == id).first()


	def regenerate_url(
			self,
			session = None,
			project = None):
		"""
		Assumptions:
			BOTH thumbnail and raw file
			use the same url_signed_expiry

			So when we update the urls we also must update
			1) raw file
			2) thumbnail
			3) the url_signed_expiry
			
			We had an earlier pattern of storing the asset path
			for the file signed url, but the thumbnail follows 
			different pattern...

			There is NO preivew_image in the new frame context
			because we don't create Image objects for frames

			TODO would like to refactor this signed url checking 
			into it's own function

		Passing project
			A Video is nearly always a child of a File
			So since we store Project on File already
			it seems reasonable to pass it to Video when needed
			(instead of Video storing it).


		Jan 28, 2020
			We are subtracting the "offset" to guarantee
			a minimum number of days since generation.
			in context of export generation.

			Another option of course would be to just generate
			a new URL for the export only
			at a specific number of days... 

			As a manual test I looked at some old
			and new expires in exports to see if it returned
			as expected and it did. To mock a test case would 
			want an expiry that was clearly old (ie last month)
			and one that's still "valid" but less then the minimum
			days.
			------------
			
			TODO review how long / we want to generate 
			the new URL for ie

			We could do something like
			new_days = 60
			new_expiry_offset = 86400 * new_days

			BUT we would have to pass this down to get_frame_url() too
			because that has some other generation thing...
			so would need to update a bit more the just what's in this function.
			

			CAUTION with the <= comparison the time to check should be a
			"+" because we are wanting to make sure that it's still valid going into the
			future that number of days (was in context of export).
			Otherwise this can fail.

			TODO some type of testing, ie that a given video with that time stamp works as expected.

			Already tested and for tasks it is providing this stuff as expected.


			We assume that we want to create the URL for a longer duration
			then what is valid. 

			Things I would like to test here
			* It can regenerate as expected
			* It does not regenerate when not needed
			* It regenerates at right time

			One test is to load an old file
			expect it to fire first time, then when reload not fire

			We assume that minimum days should always be lower then
			new_offset_days_valid because
			we don't want to have to keep regenerating if not needed.

			datetime.datetime.fromtimestamp(1581663035)

			Yes there are a lot of things wrong with this code
			but it does appear to work for now so move on.
			Did a manual test and it reloaded task as expected

			(For example would like this to depend on user account...)

			TODO would like to be able to set this per account maybe

		"""
		if session and self.file_blob_path:

			# We assume a significant delta between minimum days 
			# and new offset (ie at least 10 minutes)
			minimum_days_valid = 30 * 12		# this should always be lower then new offset
			new_offset_days_valid = 30 * 14
			time_to_check = time.time() + (86400 * minimum_days_valid)

			if self.url_signed_expiry is None or \
				self.url_signed_expiry <= time_to_check:

				#print("Rebuild URL")
				new_offset_in_seconds = 86400 * new_offset_days_valid

				self.file_signed_url = data_tools.build_secure_url(
									self.file_blob_path, new_offset_in_seconds)				

				# For the preview image we basically
				# assume it's the first frame (ie frame 0)
				self.preview_image_url_thumb = self.get_frame_url(
						frame_number = 0, thumb=True, project=project)

				
				self.url_signed_expiry = time.time() + new_offset_in_seconds
				session.add(self)


	def serialize_list_view(
			self, 
			session = None,
			project = None):

		self.regenerate_url(
			project = project,
			session = session)

		created_time = None
		if self.created_time:
			created_time = self.created_time.isoformat()

		video = {
			'id' : self.id,
			'filename' : self.filename,
			'frame_rate' : self.frame_rate,
			'frame_count' : self.frame_count,
			'created_time' : created_time,
			'status' : self.status,
			'description' : self.description,
			'preview_image_url_thumb' : self.preview_image_url_thumb,
			'file_signed_url': self.file_signed_url,
			'width': self.width,
			'height': self.height,	
			'fps_conversion_ratio' : self.fps_conversion_ratio,
			'offset_in_seconds' : self.offset_in_seconds,
			'parent_video_split_duration': self.parent_video_split_duration
		}
		return video

	# TODO is this deprecated??
	def serialize_detail_view(self):


		return {
			'id' : self.id,
			'filename' : self.filename,
			'frame_rate' : self.frame_rate,
			'frame_count' : self.frame_count,
			'created_time' : self.created_time.isoformat(),
			'status' : self.status,
			'description' : self.description,
			'preview_image_url' : self.preview_image_url,
			'file_signed_url': self.file_signed_url,
			'width': self.width,
			'height': self.height,
			'fps_conversion_ratio' : self.fps_conversion_ratio
		}

	def calculate_global_reference_frame(
			self,
			frame_number: int
			) -> int:
		"""		
		Overall goal is 

		(Starting offset * orginal_fps) + (current_frame * FPS conversion rate)

		"""
		if frame_number is None or self.fps_conversion_ratio is None:
			return None

		frames_offset = 0
		if self.offset_in_seconds and self.original_fps:
			# Case of a video not being split
			# We do not have to have this?
			frames_offset = int(self.offset_in_seconds * self.original_fps)

		current_frame_fps_converted = int(frame_number * 
					self.fps_conversion_ratio)

		return frames_offset + current_frame_fps_converted


	def get_by_frame_and_directory(session, directory_id, video_id, frame_number):

		# We need working dir other wise could be a different version
		working_dir_sub_query = session.query(WorkingDirFileLink).filter(
			WorkingDirFileLink.working_dir_id == directory_id).subquery('working_dir_sub_query')

		# Video id is shared - so we need the File 
		# To get right version
		# And individual image files could change ? hmmmm something not quite right here

		return session.query(File).filter(
					File.video_id == video_id,
					File.id == working_dir_sub_query.c.file_id,
					File.frame_number == frame_number).first()


	@staticmethod
	def new(
			session,
			project,
			filename,
			frame_rate,
			frame_count: int,
			width: int,
			height: int,
			directory_id: int,
			parent_input_id: int = None,	# WIP
			parent_video_split_duration: int = None
		):
		# Does it make sense for this to be here
		# or would it make more sense for this to
		# be in file?
		"""
		TODO Jan 13, 2020
		Note clear if we should be saving parent_id
		or video_parent_file as the relation of a clip to
		the parent...

		Overall doesn't really make sense

		So the thing is we never actually create a file
		for "original" the only thing that exists is the input id
		So not really sure what we would be storing here...
		can do file.input.parent_input ...

		We could log the parent_input_id somewhere
		ie to make it easier to group videos in the future
		directionally that should be ok
		but we should be careful to understand it's the 
		Input class not File class

		"""
		#print(parent_input_id)

		video = Video(
			filename = filename,
			frame_rate = frame_rate,
			frame_count = frame_count,
			width = width,
			height = height,
			parent_video_split_duration = parent_video_split_duration
			)

		# File will want the ID right away
		session.add(video)
		session.flush()
		
		file = File.new(
			session = session,
			project_id = project.id,
			working_dir_id = directory_id,
			file_type = "video",
			video_id = video.id,
			original_filename = filename
			)

		return video, file


	# TODO consider caching...

	def get_frame_url(
			self, 
			frame_number: int, 
			thumb: bool = False,
			project = None) -> str:

		# Temp thing, until we have project saved here or something

		# New default
		if self.root_blob_path_to_frames:
			path = self.root_blob_path_to_frames + str(frame_number)
		# Migration

		# This migration doesn't really make sense
		# since why we are supplying a frame number otherwise here?

		else:
			print("used migration")
			# note just project, not self.
			if self.preview_image and project:
				path = settings.PROJECT_IMAGES_BASE_DIR + \
					str(project.id) + "/" + str(self.preview_image.id)
			else:
				return None

		if thumb is True:
			path += "_thumb"

		return data_tools.build_secure_url(path)
