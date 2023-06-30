from dataclasses import dataclass
from dataclasses import field
from typing import Any

@dataclass(order = True)
class PrioritizedItem:
    # https://diffgram.readme.io/docs/prioritizeditem
    priority: int
    input_id: int = field(compare = False, default = None)
    input: int = field(compare = False, default = None)
    file_is_numpy_array: bool = field(compare = False, default = False)
    raw_numpy_image: Any = field(compare = False, default = None)
    video_id: Any = field(compare = False, default = None)
    video_parent_file: Any = field(compare = False, default = None)
    frame_number: Any = field(compare = False, default = None)
    global_frame_number: Any = field(compare = False, default = None)
    frame_completion_controller: Any = None
    total_frames: int = 0
    num_frames_to_update: int = 0
    media_type: str = None
    mode: str = None
