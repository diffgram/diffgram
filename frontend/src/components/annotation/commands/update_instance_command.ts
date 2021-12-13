import * as instance_utils from '../../../utils/instance_utils';
import AnnotationScene3D from "../../3d_annotation/AnnotationScene3DOrtographicView";
import {Instance} from "../../vue_canvas/instances/Instance";

const CLASS_INSTANCE_TYPES = [
  'keypoints',
  'cuboid_3d'
]

interface ComponentWithInstanceList extends Vue {
 instance_list: any[]
}

export class UpdateInstanceCommand {
  public ann_core_ctx: ComponentWithInstanceList;
  public scene_controller_3d: AnnotationScene3D;
  public old_instance: Instance;
  public instance: Instance;
  public instance_index: number;

  _copyInstance(instance) {
    if (!CLASS_INSTANCE_TYPES.includes(instance.type)) {
      // legacy instances
      let newInstance = {
        ...instance,
        attribute_groups: instance.prev_attribute
          ? {
            [instance.prev_attribute.group]: instance.prev_attribute.value
          }
          : instance.attribute_groups,
        points: [...instance.points.map(p => ({...p}))]
      };
      if (instance.type === "curve") {
        newInstance.p1 = {...instance.p1};
        newInstance.p2 = {...instance.p2};
        newInstance.cp = {...instance.cp};
      }
      if (instance.type === "cuboid") {
        newInstance.rear_face = {
          ...instance.rear_face,
          top_right: {...instance.rear_face.top_right},
          top_left: {...instance.rear_face.top_left},
          bot_left: {...instance.rear_face.bot_left},
          bot_right: {...instance.rear_face.bot_right}
        };
        newInstance.front_face = {
          ...instance.front_face,
          top_right: {...instance.front_face.top_right},
          top_left: {...instance.front_face.top_left},
          bot_left: {...instance.front_face.bot_left},
          bot_right: {...instance.front_face.bot_right}
        };
      }

      return newInstance;
    }
    else if (instance.type === 'keypoints') {
      let newInstance = instance.get_instance_data();
      let initializedInstance = instance_utils.initialize_instance_object(
        newInstance,
        this.ann_core_ctx,
      );
      return initializedInstance;
    }
    else if(instance.type === 'cuboid_3d'){
      let newInstance = instance.get_instance_data();
      console.log('instance to copy mesh', instance, this.ann_core_ctx, this.scene_controller_3d)
      newInstance.mesh = instance.mesh;

      let initializedInstance = instance_utils.initialize_instance_object(
        newInstance,
        this.ann_core_ctx,
        this.scene_controller_3d
      );
      initializedInstance.remove_edges();

      console.log('end inistialized', initializedInstance)
      return initializedInstance;
    }
    else{
      throw Error('Invalid type for update instance command.')
    }
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
