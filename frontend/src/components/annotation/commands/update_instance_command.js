export class UpdateInstanceCommand {

  _copyInstance(instance) {
   if (instance.initialized != true) {   // legacy instances
      const newInstance = {
        ...instance,
        points: [...instance.points.map(p => ({...p}))]
      };
      if (instance.type === 'curve') {
        newInstance.p1 = {...instance.p1}
        newInstance.p2 = {...instance.p2}
        newInstance.cp = {...instance.cp}
      }
      if (instance.type === 'cuboid') {
        newInstance.rear_face = {
          ...instance.rear_face,
          top_right: {...instance.rear_face.top_right},
          top_left: {...instance.rear_face.top_left},
          bot_left: {...instance.rear_face.bot_left},
          bot_right: {...instance.rear_face.bot_right},
        }
        newInstance.front_face = {
          ...instance.front_face,
          top_right: {...instance.front_face.top_right},
          top_left: {...instance.front_face.top_left},
          bot_left: {...instance.front_face.bot_left},
          bot_right: {...instance.front_face.bot_right},
        }
      }
      return newInstance
    }
    if (instance.initialized == true) {
      let newInstance = instance.get_instance_data()
      let initializedInstance = this.ann_core_ctx.initialize_instance(newInstance)
      return initializedInstance
    }
    return newInstance
  }

  constructor(instance, instance_index, old_instance, ann_core_ctx) {
    this.ann_core_ctx = ann_core_ctx;
    this.old_instance = this._copyInstance(old_instance)
    this.instance = this._copyInstance(instance)
    this.instance_index = instance_index;
  }

  execute() {
    this.ann_core_ctx.instance_list.splice(this.instance_index, 1, this._copyInstance(this.instance));
  }

  undo() {
    this.ann_core_ctx.instance_list.splice(this.instance_index, 1, this._copyInstance(this.old_instance));
  }
}
