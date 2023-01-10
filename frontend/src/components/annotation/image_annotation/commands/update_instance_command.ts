import AnnotationScene3D from "../../../3d_annotation/AnnotationScene3DOrtographicView";
import {Instance} from "../../../vue_canvas/instances/Instance";
import {CanvasMouseCtx} from "../../../../types/mouse_position";
import {duplicate_instance} from "../../../../utils/instance_utils";

const CLASS_INSTANCE_TYPES = [
  'keypoints',
  'cuboid_3d',
  'text_token',
  'relation'
]

interface ComponentWithInstanceList extends Vue, CanvasMouseCtx {
 instance_list: any[]
}

export class UpdateInstanceCommand {
  public ann_core_ctx: ComponentWithInstanceList;
  public scene_controller_3d: AnnotationScene3D;
  public old_instance: Instance;
  public instance: Instance;
  public instance_index: number;

  _copyInstance(instance) {
    let new_instance = duplicate_instance(instance, this.ann_core_ctx, true)
    return new_instance
  }

  constructor(instance: Instance, instance_index: number, old_instance: Instance, ann_core_ctx: ComponentWithInstanceList, scene_controller_3d: AnnotationScene3D = undefined) {
    this.ann_core_ctx = ann_core_ctx;
    this.scene_controller_3d = scene_controller_3d;
    this.old_instance = this._copyInstance(old_instance);
    this.instance = this._copyInstance(instance);
    this.instance_index = instance_index;
  }

  execute() {
    this.ann_core_ctx.instance_list.splice(
      this.instance_index,
      1,
      this._copyInstance(this.instance)
    );
  }

  undo() {
    this.ann_core_ctx.instance_list.splice(
      this.instance_index,
      1,
      this._copyInstance(this.old_instance)
    );
  }
}
