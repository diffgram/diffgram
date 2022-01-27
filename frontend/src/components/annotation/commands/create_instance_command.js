export class CreateInstanceCommand {
  _copyInstance(instance) {
    if (instance.initialized != true) {
      // legacy instances
      if (!Array.isArray(instance.points)) return null;
      const newInstance = {
        ...instance,
        points: [...instance.points.map(p => ({ ...p }))]
      };
      if (instance.type === "curve") {
        newInstance.p1 = { ...instance.p1 };
        newInstance.p2 = { ...instance.p2 };
        newInstance.cp = { ...instance.cp };
      }
      if (instance.type === "cuboid") {
        newInstance.rear_face = {
          ...instance.rear_face,
          top_right: { ...instance.rear_face.top_right },
          top_left: { ...instance.rear_face.top_left },
          bot_left: { ...instance.rear_face.bot_left },
          bot_right: { ...instance.rear_face.bot_right }
        };
        newInstance.front_face = {
          ...instance.front_face,
          top_right: { ...instance.front_face.top_right },
          top_left: { ...instance.front_face.top_left },
          bot_left: { ...instance.front_face.bot_left },
          bot_right: { ...instance.front_face.bot_right }
        };
      }
      return newInstance;
    }

    if (instance.type == "keypoints") {
      let newInstance = instance.get_instance_data();

      let initializedInstance = this.ann_core_ctx.initialize_instance(
        newInstance
      );
      return initializedInstance;
    }
  }

  constructor(instance, ann_core_ctx, frame_number = undefined) {
    this.ann_core_ctx = ann_core_ctx;
    this.instance = this._copyInstance(instance);
    this.frame_number = frame_number;
    this.created_instance_index = undefined;
  }

  execute() {
    if (this.instance.id) {
      this.instance.soft_delete = false;
      for (let i = 0; i < this.ann_core_ctx.instance_list.length; i++) {
        const current = this.ann_core_ctx.instance_list[i];
        if (current.id === this.instance.id) {
          this.created_instance_index = i;
          break;
        }
      }
    } else {
      const existing_instance = this.ann_core_ctx.instance_list.filter(
        instance => instance.creation_ref_id === this.instance.creation_ref_id
      );
      if (existing_instance.length === 0) {
        this.instance.soft_delete = false;
        this.ann_core_ctx.add_instance_to_file(
          {
            ...this.instance,
            points: [...this.instance.points.map(p => ({ ...p }))]
          },
          this.frame_number
        );
        this.created_instance_index = this.ann_core_ctx.instance_list.length - 1;
        // Get the pushed instance to have the creation ref ID in future redo's
        this.instance = this._copyInstance(
          this.ann_core_ctx.instance_list[this.created_instance_index]
        );
        const polygon_alert_shown = this.ann_core_ctx.$store.state.user.settings
          .polygon_autoborder_info;
        if (this.instance.type === "polygon" && !polygon_alert_shown) {
          this.ann_core_ctx.canvas_alert_x = this.ann_core_ctx.mouse_position.x;
          this.ann_core_ctx.canvas_alert_y = this.ann_core_ctx.mouse_position.y;
          this.ann_core_ctx.$refs.autoborder_alert.show_alert();
          this.ann_core_ctx.$store.commit("set_user_setting", [
            "polygon_autoborder_info",
            true
          ]);
        }
      } else {
        const existing_instance = this.ann_core_ctx.instance_list.filter(
          instance => instance.creation_ref_id === this.instance.creation_ref_id
        )[0];
        existing_instance.soft_delete = false;
      }
    }
  }

  undo() {
    const instance = this.ann_core_ctx.instance_list[
      this.created_instance_index
    ];

    // We don't want to delete instances that already have an ID on backend, just soft delete them.
    instance.soft_delete = true;
    this.ann_core_ctx.instance_list.splice(
      this.created_instance_index,
      1,
      instance
    );

    this.ann_core_ctx.has_changed = true;
  }
}
