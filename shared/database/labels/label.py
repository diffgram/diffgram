# OPENCORE - ADD
from shared.database.common import *


class Label(Base):
    __tablename__ = 'label'

    id = Column(Integer, primary_key = True)
    name = Column(String(200))

    default_sequences_to_single_frame = Column(Boolean, default = False)

    # TODO colour is deprecated given storing in file directly now?
    # ie a name may be "universal" but the colour is not?

    # example of colour {"hex": "#194d33", "hsl": {"l": 0.2, "h": 150, "s": 0.5, "a": 1},
    # "rgba": {"a": 1, "g": 77, "r": 25, "b": 51}, "hsv": {"a": 1, "h": 150, "s": 0.66, "v": 0.3}, "a": 1}
    colour = Column(MutableDict.as_mutable(JSONEncodedDict))

    # Remove soft delete?
    soft_delete = Column(Boolean)

    # TODO part of super category or?

    # TODO
    # Label is now part of a file
    # and a source control version
    # Review as neither AI or project realy make sense here

    # project_id = Column(Integer, ForeignKey('project.id'))
    # project = relationship("Project", back_populates="label_list")

    # TODO review on context of source control
    # not sure if this makes sense anymore? And may be part of slowing down thing...
    # instance_list = relationship("Instance", back_populates="label")
    # sequence_list = relationship("Sequence", back_populates="label")

    @staticmethod
    def get_by_name(session, label_name):
        return session.query(Label).filter(
            Label.name == label_name
        ).first()

    @staticmethod
    def new(session,
            add_to_session = True,
            flush_session = True,
            name = None,
            default_sequences_to_single_frame = False):

        label = session.query(Label).filter(
            Label.name == name,
            Label.default_sequences_to_single_frame == default_sequences_to_single_frame
        ).first()

        if not label:
            label = Label(
                name = name,
                default_sequences_to_single_frame = default_sequences_to_single_frame)
            if add_to_session:
                session.add(label)
            if flush_session:
                session.flush()
        return label

    def serialize(self):
        label = {
            'id': self.id,
            'name': self.name,
            'default_sequences_to_single_frame': self.default_sequences_to_single_frame
        }
        return label

    def serialize_PUBLIC(self):
        return {
            'name': self.name
        }
