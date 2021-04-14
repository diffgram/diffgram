# OPENCORE - ADD
from shared.database.common import *
from shared.database.discussion.discussion_member import DiscussionMember
import shared.database.discussion.discussion_relation as discussion_relation_models
from shared.database.annotation.instance import Instance
from shared.shared_logger import get_shared_logger

logger = get_shared_logger()


class Discussion(Base):
    """
    

    """
    __tablename__ = 'discussion'

    id = Column(Integer, primary_key = True)
    created_time = Column(DateTime, default = datetime.datetime.utcnow)
    # todo updating time, updated member
    title = Column(String())

    description = Column(String())

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates = "discussion_list")

    status = Column(String(), default = 'open')

    type = Column(String(), default = 'issue')

    assignees = relationship(DiscussionMember)

    comment_list = relationship("DiscussionComment")


    # In future version we might have polygon, boxes etc...
    marker_type = Column(String(), default = 'point')

    # This can have an x,y coordinate, polygon, circle, box. We leave it as a dict to allow flexibility for future
    # issue visualizations
    marker_data = Column(MutableDict.as_mutable(JSONEncodedDict))

    # For video case, the frame where the marker was placed at.
    marker_frame_number = Column(Integer(), nullable = True)

    # Then do we add an annotation specific activity? what would that look like?

    # Ref to a specific image / group of images?
    # Ref to a specific commit? and how that relates to the above
    # Wouldn't always have issues but...

    def detach_all_instances(self, session):
        issue_relations = session.query(discussion_relation_models.DiscussionRelation).filter(
            discussion_relation_models.DiscussionRelation.instance_id.isnot(None)
        )
        issue_relations.delete()
        return

    def attach_element(self, session: object, element: dict, add_to_session = True, flush_session = True):
        element_id = element.get('id')
        if element_id is None:
            return
        issue_relation = None
        if element_id is None:
            logger.error('Missing ID for element attach to issue {}. Element: '.format(self.id, str(element)))
            return
        if element['type'] == 'instance':
            issue_relation = discussion_relation_models.DiscussionRelation.new(
                session,
                instance_id = element_id,
                type = element['type'],
                discussion_id = self.id
            )
        elif element['type'] == 'file':
            issue_relation = discussion_relation_models.DiscussionRelation.new(
                session,
                file_id = element_id,
                type = element['type'],
                discussion_id = self.id
            )
        elif element['type'] == 'job':
            issue_relation = discussion_relation_models.DiscussionRelation.new(
                session,
                job_id = element_id,
                type = element['type'],
                discussion_id = self.id
            )
        elif element['type'] == 'task':
            issue_relation = discussion_relation_models.DiscussionRelation.new(
                session,
                task_id = element_id,
                type = element['type'],
                discussion_id = self.id
            )
        elif element['type'] == 'project':
            issue_relation = discussion_relation_models.DiscussionRelation.new(
                session,
                project_id = element_id,
                type = element['type'],
                discussion_id = self.id
            )
        else:
            raise Exception('Invalid IssueRelation type')
        if add_to_session:
            session.add(issue_relation)
        if flush_session:
            session.flush()
        return issue_relation

    def update_attached_instances(self,
                                  session: object,
                                  attached_elements: list,
                                  add_to_session = True,
                                  flush_session = True):
        result = []
        for element in attached_elements:
            if element['type'] != 'instance':
                continue
            id = None
            if element['instance_id'] is not None:
                id = element['instance_id']

            updated_element = self.attach_element(session = session,
                                                  element = {
                                                      'type': element['type'],
                                                      'id': id,
                                                  },
                                                  add_to_session = add_to_session,
                                                  flush_session = flush_session)
            result.append(updated_element)
        return result

    @staticmethod
    def update(session,
               discussion_id: int = None,
               description: str = None,
               attached_elements: list = None,
               status: str = None,
               ):

        discussion = Discussion.get_by_id(session, id = discussion_id)
        if description is not None:
            discussion.description = description
        if attached_elements is not None:
            discussion.detach_all_instances(session)
            discussion.update_attached_instances(session = session, attached_elements = attached_elements)
        if status is not None:
            discussion.status = status
        session.add(discussion)
        return discussion

    @staticmethod
    def list(session,
             project_id: int = None,
             task_id: int = None,
             file_id: int = None,
             job_id: int = None,
             status: str = None,
             members_list: list = None,
             ends: str = None,
             starts: str = None,
             type: str = None,
             ):
        if project_id is None:
            return
        query = session.query(Discussion).filter(Discussion.project_id == project_id)

        if task_id or file_id or job_id:
            query = query.join(
                discussion_relation_models.DiscussionRelation,
                discussion_relation_models.DiscussionRelation.discussion_id == Discussion.id
            )
        discussion_filters = []
        if task_id:
            discussion_filters.append(
                discussion_relation_models.DiscussionRelation.task_id == task_id
            )
        if file_id:
            discussion_filters.append(
                discussion_relation_models.DiscussionRelation.file_id == file_id
            )
        if job_id:
            discussion_filters.append(
                discussion_relation_models.DiscussionRelation.job_id == job_id
            )

        query = query.filter(or_(*discussion_filters))
        if status:
            query = query.filter(Discussion.status == status)

        if type:
            query = query.filter(Discussion.type == type)

        if members_list:
            query = query.filter(Discussion.member_created_id.in_(members_list))

        if starts:
            query = query.filter(Discussion.created_time >= starts)

        if ends:
            query = query.filter(Discussion.created_time <= ends)

        query = query.order_by(Discussion.created_time)

        issues_list = query.all()

        return issues_list

    @staticmethod
    def new(session,
            title: str = None,
            description: str = None,
            member_created_id: int = None,
            project_id: int = None,
            status: str = None,
            marker_frame_number: int = None,
            marker_data: dict = None,
            marker_type: str = None,
            type: str = 'issue',
            add_to_session: bool = True,
            flush_session: bool = True):
        discussion = Discussion(
            title = title,
            description = description,
            member_created_id = member_created_id,
            project_id = project_id,
            marker_frame_number = marker_frame_number,
            marker_data = marker_data,
            marker_type = marker_type,
            status = status,
            type = type,
        )
        if add_to_session:
            session.add(discussion)
        if flush_session:
            session.flush()
        # Default relation to project.
        discussion.attach_element(session, {'type': 'project', 'id': project_id})
        return discussion

    @staticmethod
    def get_by_id(session, id: int):
        return session.query(Discussion).filter(Discussion.id == id).first()

    def serialize_attached_elements(self, session: object):
        relations = session.query(discussion_relation_models.DiscussionRelation).filter(
            discussion_relation_models.DiscussionRelation.discussion_id == self.id
        )
        result = []
        for rel in relations:
            result.append(rel.serialize(session))
        return result
        pass

    def serialize(self, session: object):
        attached_elements = self.serialize_attached_elements(session)
        user = None
        if self.member_created and self.member_created.user:
            user = self.member_created.user.serialize_for_activity()
        return {
            'id': self.id,
            'created_time': self.created_time,
            'user': user,
            'marker_type': self.marker_type,
            'marker_frame_number': self.marker_frame_number,
            'marker_data': self.marker_data,
            'title': self.title,
            'type': self.type,
            'description': self.description,
            'member_created_id': self.member_created_id,
            'project_id': self.project_id,
            'status': self.status,
            'attached_elements': attached_elements,

        }

    def serialize_for_list(self):
        user = None
        if self.member_created and self.member_created.user:
            user = self.member_created.user.serialize_for_activity()
        return {
            'id': self.id,
            'created_time': self.created_time,
            'marker_type': self.marker_type,
            'marker_frame_number': self.marker_frame_number,
            'marker_data': self.marker_data,
            'title': self.title,
            'type': self.type,
            'user': user,
            'description': self.description,
            'member_created_id': self.member_created_id,
            'project_id': self.project_id,
            'status': self.status
        }
