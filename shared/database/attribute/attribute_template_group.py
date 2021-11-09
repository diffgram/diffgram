# OPENCORE - ADD
from shared.database.common import *
from shared.database.attribute.attribute_template import Attribute_Template
from shared.database.attribute.attribute_template_group_to_file import Attribute_Template_Group_to_File


class Attribute_Template_Group(Base):
    """



    """

    __tablename__ = 'attribute_template_group'
    id = Column(BIGINT, primary_key = True)

    archived = Column(Boolean, default = False)  # Hide from list

    name = Column(String())
    prompt = Column(String())
    show_prompt = Column(Boolean, default = True)

    is_root = Column(Boolean, default = True)
    is_new = Column(Boolean, default = True)

    parent_id = Column(Integer, ForeignKey('attribute_template.id'))
    root_id = Column(Integer, ForeignKey('attribute_template_group.id'))

    kind = Column(String())  # select_one, check_boxes, ...?

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")

    member_created_id = Column(Integer, ForeignKey('member.id'))
    member_created = relationship("Member", foreign_keys = [member_created_id])

    member_updated_id = Column(Integer, ForeignKey('member.id'))
    member_updated = relationship("Member", foreign_keys = [member_updated_id])

    time_created = Column(DateTime, default = datetime.datetime.utcnow)
    time_updated = Column(DateTime, onupdate = datetime.datetime.utcnow)

    default_value = Column(String())
    default_id = Column(Integer)

    # For slider kind
    min_value = Column(Integer)
    max_value = Column(Integer)

    # External ID's for referencing on integrations like Labelbox, Supervisely, etc.
    default_external_map_id = Column(BIGINT, ForeignKey('external_map.id'))  # TODO: add to production
    default_external_map = relationship("ExternalMap",
                                        uselist = False,
                                        foreign_keys = [default_external_map_id])

    is_global = Column(Boolean, default = False)
    global_type = Column(String(), default = 'file')        # Expansion direction eg for frame, series, etc.


    @staticmethod
    def new(session,
            project,
            member):

        # Singleton ish concept, only ever 1 new() one to return
        # (that hasn't been modified, so seperate drafts are still
        # allowed

        # If we have an existing one
        attribute_template_group = session.query(Attribute_Template_Group).filter(
            Attribute_Template_Group.is_new == True,
            Attribute_Template_Group.archived == False,
            Attribute_Template_Group.member_created == member,
            Attribute_Template_Group.project == project).first()

        if attribute_template_group:
            return attribute_template_group

        # Else create a new one
        attribute_template_group = Attribute_Template_Group(
            project = project,
            member_created = member)

        # Not sure if fan of forcing adding to session here
        # BUT since we potentialy return an existing object it would
        # Be strange to require it after

        session.add(attribute_template_group)
        session.flush()

        return attribute_template_group

    def serialize(self):

        return {
            'id': self.id,
            'kind': "group",
            'is_root': self.is_root,
            'name': self.name,
            'kind': self.kind,
            'prompt': self.prompt,
            'show_prompt': self.show_prompt,
            # wrapping in str() seems to be needed to avoid some strange
            # embedded serialization issues (not with calling it directly, but things
            # like job launch etc.
            'time_updated': str(self.time_updated),
            'default_value': self.default_value,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'default_id': self.default_id,
            'is_global': self.is_global,
            'global_type': self.global_type
        }

    def serialize_for_export(self):
        # don't have a great way to serialize a time stamp
        # and not needed yet, so for now a different for for export

        return {
            'id': self.id,
            'kind': "group",
            'is_root': self.is_root,
            'name': self.name,
            'kind': self.kind,
            'prompt': self.prompt,
            'show_prompt': self.show_prompt,
            'default_value': self.default_value,
            'default_id': self.default_id,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'is_global': self.is_global,
            'global_type': self.global_type
        }

    def serialize_with_attributes_and_labels(self, session):

        data = self.serialize_with_attributes(session)
        rels = Attribute_Template_Group_to_File.get_all_from_group(session = session, group_id = self.id)
        label_file_list = [rel.file for rel in rels]
        data['label_file_list'] = [x.serialize_with_label() for x in label_file_list]
        return data

    def serialize_with_attributes(
        self,
        session):

        attribute_template_list_serialized = []

        attribute_template_list = Attribute_Template.list(
            session = session,
            mode = "from_group",
            group_id = self.id,
            project_id = self.project.id,
            return_kind = "objects"
        )

        for attribute in attribute_template_list:
            attribute_template_list_serialized.append(attribute.serialize())

        group = self.serialize()
        group['attribute_template_list'] = attribute_template_list_serialized

        return group


    @staticmethod
    def get_globals(
            session,
            project_id,
            is_global = True):

        query = session.query(Attribute_Template_Group)

        query = query.filter(Attribute_Template_Group.project_id == project_id)
        query = query.filter(Attribute_Template_Group.is_global == is_global)

        return query.all()


    @staticmethod
    def from_file_attribute_group_list_serialize(
        session,
        file_id):

        # This is concerned about getting from file
        # where as in other cases we may want to get by say
        # project, ie for showing all attribute groups in a project

        # repeating with attribute_template_list a bit here...

        # May not always need to serialize with attributes, ie
        # for selection just the group is enough...

        group_list_serialized = []

        group_list = Attribute_Template_Group.get_group_list(
            session = session,
            file_id = file_id)

        for group in group_list:
            group_list_serialized.append(group.serialize_with_attributes(
                session = session))

        return group_list_serialized

    # TODO clarify this is from file id
    @staticmethod
    def get_group_list(session, file_id):

        sub_query = session.query(Attribute_Template_Group_to_File).filter(
            Attribute_Template_Group_to_File.file_id == file_id).subquery()

        query = session.query(Attribute_Template_Group).filter(
            Attribute_Template_Group.id == sub_query.c.attribute_template_group_id)

        return query.all()

    # General from project or group id
    @staticmethod
    def list(session,
             group_id,
             project_id,
             archived = False,
             recursive = False,
             limit = 100,
             return_kind = "objects",
             is_root = None,
             is_global = None
             ):
        """

        Require project id for security

        """

        query = session.query(Attribute_Template_Group).filter(
                Attribute_Template_Group.project_id == project_id,
                Attribute_Template_Group.archived == archived)

        if group_id:
            query = query.filter(Attribute_Template_Group.id == group_id)

        if is_global:
            query = query.filter(Attribute_Template_Group.is_global == is_global)

        if is_root:
            query = query.filter(Attribute_Template_Group.is_root == is_root)

        # Future
        if recursive == True:

            root_group_list = query.limit(limit).all()

            for group in root_group_list:
                # Caching / have_children? flag on attribute group?
                children = []

                # Children for a root group
                children = Attribute_Template_Group.recurse_graph(
                    session,
                    group,
                    children)

            if return_kind == "serialized":

                serialized = []

                for group in root_group_list:
                    serialized.append(group.serialize())

                return serialized
        ## end future

        if return_kind == "count":
            return query.limit(limit).count()

        if return_kind == "objects":
            return query.limit(limit).all()

    @staticmethod
    def get_by_id(session,
                  id,
                  project_id = None):
        """
        Must include project id for security check

        (This assumes untrusted source)...

        """

        return session.query(Attribute_Template_Group).filter(
            Attribute_Template_Group.id == id,
            Attribute_Template_Group.project_id == project_id).first()

    # WIP

    def recurse_graph(
        session,
        group,
        children = []
    ):

        # Get templates for a group
        attribute_template_list = Attribute_Template.list(
            session = session,
            mode = "from_group",
            group_id = group.id,
            project_id = group.project.id,
            return_kind = "objects"
        )

        if attribute_template_list is None or len(attribute_template_list) is 0:
            return children

        # TODO handle serialzing children
        children.append(new_child)

        group.serialize(children = children)

        children['new_folder'] = []

        # ??
        # children.append(group.serialize())

        for template in attribute_template_list:

            print("Looking a template group")

            # Somehow append group to list.
            # TODO group serialize handles serializeing templates within group

            # TODO not clear how well this will update in the right place
            # ie need to append to children...

            # WIP not clear where we are saving this stuff yet
            # Depth limit.

            if template.kind == "children":
                print("Children, recusing graph")

                child_group_list = Attribute_Template_Group.child_group_list(
                    session = session,
                    template = template)

                for child_group in child_group_list:
                    Attribute_Template_Group.recurse_graph(
                        session,
                        group,
                        children = children)

        return children

    def child_group_list(session, template):
        # cache child list somehow?
        return session.query(Attribute_Template_Group).filter(
            Attribute_Template_Group.parent_id == template.id,
            Attribute_Template_Group.archived == False).all()
