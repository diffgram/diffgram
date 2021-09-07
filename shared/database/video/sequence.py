# OPENCORE - ADD
from shared.database.common import *
from shared.database.annotation.instance import Instance
import bisect

from shared.instance_tools import Instance_tools
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()

from sqlalchemy.schema import Index


class Sequence(Base):
    """
    A sequence of instances. ie in A video
    A sequence has multiple instances
    A label has multiple sequences

    TODO sequence should store a project id

    A video_file_id + label_file_id + number is globally unique

    """

    __tablename__ = 'sequence'

    __table_args__ = (
        Index('index__video_file_id__and__label_file_id',
              "video_file_id", "label_file_id"),
    )

    id = Column(Integer, primary_key = True)

    label_file_id = Column(Integer, ForeignKey('file.id'))
    label_file = relationship("File", foreign_keys = [label_file_id])

    has_changes = Column(Boolean)
    single_frame = Column(Boolean, default = False)

    """
        apparently using this instead of instance_list

        instance_list = Instance.list(		# Using this checks for soft deleted by default
            session = session,
            sequence_id = sequence.id)

        BUT caution we still use this in other places.
            It does work as expected so long as there are sequences there.
    """
    instance_list = relationship("Instance")

    # frame numbers
    # more of a UI thing?
    # keyframe_list['frame_number_list'] to access numbers of keyframes
    # Could maybe put other info here in future too
    keyframe_list = Column(MutableDict.as_mutable(JSONEncodedDict),
                           default = {})

    # Can't attach to video directly,
    # as sequence may change in source control?
    # TODO clarify this is the VIDEO file it's attached to?
    video_file_id = Column(Integer, ForeignKey('file.id'))
    video_file = relationship("File", foreign_keys = [video_file_id])  # back_populates="sequence_list"

    number = Column(Integer, default = -1)

    instance_preview_cache = Column(MutableDict.as_mutable(JSONEncodedDict),
                                    default = {})
    cache_expiry = Column(Integer)
    archived = Column(Boolean, default = False)

    @staticmethod
    def get_by_id(session, sequence_id):
        result = session.query(Sequence).filter(
            Sequence.id == sequence_id
        ).first()
        return result

    def clone_sequence_with_no_instances(
        self,
        session,
        destination_video_parent_file_id = None,
        add_to_session = True,
        flush_session = True):
        """
            Clones all the attributes from the current sequence into a new one with the exception
            of the instances.
        :param session:
        :param video_file: set if you want to replace the video file
        :param add_to_session:
        :param flush_session:
        :return:
        """
        if destination_video_parent_file_id is None:
            destination_video_parent_file_id = self.video_file_id

        new_sequence = Sequence(
            label_file_id = self.label_file_id,
            has_changes = self.has_changes,
            single_frame = self.single_frame,
            keyframe_list = self.keyframe_list,
            video_file_id = destination_video_parent_file_id,
            number = self.number,
            instance_preview_cache = self.instance_preview_cache,
            cache_expiry = self.cache_expiry,
            archived = self.archived
        )
        if add_to_session:
            session.add(new_sequence)
        if flush_session:
            session.flush()
        return new_sequence

    @staticmethod
    def get_by_highest_number(
        session,
        video_file_id: int,
        label_file_id: int,
        archived = False
    ):
        """
        Assumes we don't know the sequence id in question
        And need the highest, ie in the context of adding a new
        sequence from a source that was not previously tracking
        the highest number.
            ie for updating the label file

        """

        query = session.query(Sequence).filter(
            Sequence.video_file_id == video_file_id,
            Sequence.label_file_id == label_file_id,
            Sequence.archived == archived)

        query.order_by(Sequence.number)

        return query.first()

    def serialize(self, session = None):

        return {
            'id': self.id,
            'label': self.label_file.label.serialize(),
            'number': self.number,
            'keyframe_list': self.keyframe_list,
            'single_frame': self.single_frame,
            'instance_preview': self.instance_preview_cache
        }

    # Label id only
    def serialize_for_label_subset(self, session = None):

        return {
            'id': self.id,
            'number': self.number,
            'keyframe_list': self.keyframe_list,
            'single_frame': self.single_frame,
            'label_file_id': self.label_file_id,
            'instance_preview': self.instance_preview_cache
        }

    def serialize_for_export(self):

        return {
            'id': self.id,
            'label_file_id': self.label_file_id,
            'number': self.number,
            'keyframe_list': self.keyframe_list.get('frame_number_list'),
            'single_frame': self.single_frame
        }

    def serialize_for_activity(self):

        return {
            'id': self.id,
            'label': self.label.serialize(),
            'number': self.number
        }

    def build_instance_preview_dict(self, session = None):
        """
        Store cache here as getting instance for each thing is very time
        consuming. In current setup is a DB call for each.
        Probably some way to batch that but less composable.
        Caching reduced time from 20 seconds to 200 ms or so.

        Basic time based cache invalidation.
        This wouldn't work in the exporting context where we set a time in
        advance. See that exporting for it.

        We still need to occasionally regenerate it for the signed URLs if nothing else
        """
        if self.cache_expiry is None or \
            self.cache_expiry <= time.time():

            if session:

                # This needs to be in advance in case no instance
                # Otherwise it will keep rerunning this which is slow

                # caution this needs to match what serialize_for_sequence_preview()
                # creates. a TODO is to pass this to it so it can control it
                instance = self.get_preview_instance(session = session)

                if instance:
                    logger.info("Rebuilding Instance {} Preview".format(instance.id))

                    self.instance_preview_cache = instance.serialize_for_sequence_preview(
                        session = session)
                self.cache_expiry = time.time() + 2591000
                session.add(self)
        return self.instance_preview_cache

    def get_preview_instance(self, session):
        """
        WIP
        Does not yet regenerate if instance is deleted
        (ie it will still reuturn the instance, but doesn't regenerate
        preview)

        Also discussion in design doc, not clear if doing order
        by here is a good idea

        """
        instance = session.query(Instance).filter(
            Instance.sequence_id == self.id,
            Instance.soft_delete == False).order_by(Instance.id)
        instance = instance.first()

        """
        April 8, 2020
            1) We do regenerate here since otherwise always could be risk of instance not matching up.
            2) Issue is that this doesn't directly refresh cache, it just ensures 
            the instance we are getting has a thumbnail.
        """
        if instance:
            logger.info('Regenertaing instance thumb for {}'.format(instance.id))
            self.regenerate_instance_thumb(
                session = session,
                instance = instance)

        return instance

    def frame_list(self,
                   session):
        # Needs file to track sequence id
        raise NotImplementedError

    @staticmethod
    def get_from_video_label_number(
        session,
        video_file_id,
        label_file_id,
        number,
        archived = False
    ):

        """

        For example, in context of creating these in advance
        we don't want skip lock, because we already know it's going to exist.
        """

        sequence = session.query(Sequence).filter(
            Sequence.video_file_id == video_file_id,
            Sequence.label_file_id == label_file_id,
            Sequence.number == number,
            Sequence.archived == archived).first()

        return sequence

    @staticmethod
    def update_single_existing_sequence(
        session,
        instance,
        video_file,
        add_to_session = True):

        sequence = session.query(Sequence).filter(
            Sequence.id == instance.sequence_id,
            Sequence.video_file_id == video_file.id,
            Sequence.label_file_id == instance.label_file_id).first()

        if sequence:
            logger.debug("Update sequence ID {}, number {}".format(sequence.id, sequence.number))
            if add_to_session is True:
                session.add(sequence)

            # Otherwise it doubles up the keyframe list
            sequence.update_frame_number_list(session, instance)
            sequence.has_changes = True

        return sequence

    def update(
        session,
        project,
        video_mode,
        instance,
        video_file):
        """
        Conditions on if an instance exists
        Either creates a new instance or updates existing.

        Arguments:
            shared.database: session object
            keyframe: db object
            video_mode: bool
            new_box: db object
            new_polygon: db object
            new_instance: dictionary object, front end version of instance
            single_frame: bool, if the sequence is restricted to being a single
                frame

        Returns:
            instance: db object
        """

        # TODO [ ] Handling deleting keyframes?
        if video_mode is not True:
            return None

        if instance.frame_number is None:
            return None

        sequence = None  # edge case, we usually expect to return sequence object
        is_new_sequence = False
        # Default case, instance already had a sequence id
        logger.debug('Updating sequence for sequence id {}'.format(instance.sequence_id))
        if instance.sequence_id:
            # Do we even need other checks here?
            # print("instance.sequence_id", instance.sequence_id)
            sequence = Sequence.update_single_existing_sequence(
                session = session,
                instance = instance,
                video_file = video_file
            )

        if not instance.sequence_id:
            logger.debug('No ID checking for number {}'.format(instance.number))
            # Most common case for new instances
            # We have a number from UI but we don't have it mapped
            # To a sequence
            # print("instance number", instance.number)

            if instance.number is not None:
                # in the new context the video file has already been
                # checked too be valid

                sequence = Sequence.get_from_video_label_number(
                    session = session,
                    video_file_id = video_file.id,
                    label_file_id = instance.label_file_id,
                    number = instance.number
                )

                if sequence:
                    # TODO handle removal
                    session.add(sequence)
                    sequence.update_frame_number_list(session, instance)

                if not sequence:
                    sequence = Sequence.new(
                        number = instance.number,
                        video_file_id = video_file.id,
                        label_file = instance.label_file
                    )

                    sequence.keyframe_list['frame_number_list'].append(
                        instance.frame_number)

                    result = sequence.regenerate_instance_thumb(
                        session = session,
                        instance = instance,
                        video = video_file.video)
                    # it needs instance to do things like crop the image
                    is_new_sequence = True
                    session.add(sequence)
                    session.flush()

                sequence.has_changes = True

                instance.sequence_id = sequence.id

                session.add(instance)

        return sequence, is_new_sequence

    @staticmethod
    def new(number,
            video_file_id,
            label_file):
        """
        Does NOT add to session.

        In general this is rarely called directly, see .update() method.

        """

        sequence = Sequence()

        sequence.number = number
        sequence.video_file_id = video_file_id

        sequence.keyframe_list = {}
        sequence.keyframe_list['frame_number_list'] = []

        if label_file:
            sequence.label_file_id = label_file.id
            sequence.single_frame = label_file.label.default_sequences_to_single_frame
        else:
            logger.info(
                "label_file is None, this is unusual. video_file_id was: " + str(video_file_id) + " number was " + str(
                    number))

        return sequence

    @staticmethod
    def list(
        session,
        video_file_id,
        archived = False):

        return session.query(Sequence).filter(
            Sequence.video_file_id == video_file_id,
            Sequence.archived == archived).all()

    @staticmethod
    def update_all_sequences_in_file(
        session,
        video_file_id,
        regenerate_preview_images = False):
        """
        Mostly focused on regenerate_keyframe_list() at the moment
        """

        sequence_list = Sequence.list(
            session = session,
            video_file_id = video_file_id)

        print(len(sequence_list))

        for sequence in sequence_list:
            sequence.regenerate_keyframe_list(session = session)
            if regenerate_preview_images:
                sequence.build_instance_preview_dict(session = session)
            session.add(sequence)
            print(sequence.keyframe_list)

    def regenerate_instance_thumb(
        self,
        session,
        instance,
        video = None
    ):

        if video is None:
            video = self.video_file.video

        result = Instance_tools().new_thumb_image_from_frame(
            session = session,
            video = video,
            instance = instance)

    def regenerate_keyframe_list(
        self,
        session):
        """

        """

        # Not yet tested.
        # does not add to session

        instance_list = Instance.list(  # Using this checks for soft deleted by default
            session = session,
            sequence_id = self.id,
            limit = None)

        # print("len instance_list", len(instance_list))

        for instance in instance_list:
            self.update_frame_number_list(session, instance)

    # print(self.keyframe_list['frame_number_list'])

    def update_frame_number_list(self, session, instance):
        # Use instance for frame number and flag...

        frame_number_list = self.keyframe_list['frame_number_list']
        default_sequences_to_single_frame = instance.label_file.label.default_sequences_to_single_frame
        if instance.soft_delete is False or instance.soft_delete is None:

            # there wasn't a super obvious way to use built in
            # bisect for this test and since we expect this list to
            # generally be < 100 elements just leaving it.

            # this (not in) test is here because it was doubling up
            # keyframes, somethign to do with the way attributes were
            # saving maybe? but it was suprisingly glaring bug
            # on front end

            if instance.frame_number not in frame_number_list:
                # binary search based insertion
                bisect.insort(frame_number_list, instance.frame_number)
        elif instance.soft_delete and not default_sequences_to_single_frame:
            try:
                del frame_number_list[bisect.bisect_left(
                    frame_number_list, instance.frame_number)]
            except:
                pass

        # NOTE we previously had concept of if len(frame_number_list) == 0:
        # Which could then call delete_sequence_shared()
        # This was not fully implmented so leaving for now, but this is the "hook"
        # where we would put it (at least in prior knowledge conextex.)
        elif instance.soft_delete and default_sequences_to_single_frame:
            # Opportunity to have some sort of cache to avoid querying here since this can sometimes be called
            # Inside a for loop.
            """
            1) Future idea. All of this info should be available on 
            `instance_list_kept_serialized`... because, generally speaking
            we have all the instances already so shouldn't have to do a second
            query.
            2) There could be a timing issue here, we seem to do this update
            "opportunistically", eg as each instance completes ... 
            but what if more then one change in the one save event
            """
            count_instances_on_same_frame_and_sequence = Instance.list(
                session = session,
                sequence_id = instance.sequence_id,
                file_id = instance.file_id,
                frame_number = instance.frame_number,
                label_file_id = instance.label_file_id,
                limit = None,
                return_kind = "count"
            )

            # logger.info(count_instances_on_same_frame_and_sequence)

            if count_instances_on_same_frame_and_sequence == 1:
                # Delete frame number list if its the last instance on this keyframe from same seq #.
                try:
                    del frame_number_list[bisect.bisect_left(
                        frame_number_list, instance.frame_number)]
                except:
                    pass

        self.keyframe_list['frame_number_list'] = frame_number_list
