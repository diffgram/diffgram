import {KeypointInstance} from "../components/vue_canvas/instances/KeypointInstance";
import Cuboid3DInstance from "../components/vue_canvas/instances/Cuboid3DInstance";
import CuboidDrawerTool from "../components/3d_annotation/CuboidDrawerTool";

export const duplicate_instance = function(instance_to_copy, component_ctx){
  let points = [];
  let nodes = [];
  let edges = [];
  if (instance_to_copy.points) {
    points = [...instance_to_copy.points.map((p) => ({ ...p }))];
  }
  if (instance_to_copy.nodes) {
    nodes = [...instance_to_copy.nodes.map((node) => ({ ...node }))];
  }
  if (instance_to_copy.edges) {
    edges = [...instance_to_copy.edges.map((edge) => ({ ...edge }))];
  }
  let result = {
    ...instance_to_copy,
    id: undefined,
    initialized: false,
    points: points,
    nodes: nodes,
    edges: edges,
    version: undefined,
    root_id: undefined,
    previous_id: undefined,
    action_type: undefined,
    next_id: undefined,
    creation_ref_id: undefined,
    attribute_groups: instance_to_copy.attribute_groups
      ? { ...instance_to_copy.attribute_groups }
      : null,
  };

  if (result.type === "cuboid") {
    result.rear_face = {
      ...instance_to_copy.rear_face,
      top_right: { ...instance_to_copy.rear_face.top_right },
      top_left: { ...instance_to_copy.rear_face.top_left },
      bot_left: { ...instance_to_copy.rear_face.bot_left },
      bot_right: { ...instance_to_copy.rear_face.bot_right },
    };

    result.front_face = {
      ...instance_to_copy.front_face,
      top_right: { ...instance_to_copy.front_face.top_right },
      top_left: { ...instance_to_copy.front_face.top_left },
      bot_left: { ...instance_to_copy.front_face.bot_left },
      bot_right: { ...instance_to_copy.front_face.bot_right },
    };
  }

  result = initialize_instance_object(result, component_ctx);
  return result;
}

export const initialize_instance_object = function(instance, component_ctx, scene_controller_3d = undefined){
  let initialized_instance;
  if(instance.type === 'keypoints' && !instance.initialized){
    initialized_instance = new KeypointInstance(
      component_ctx.mouse_position,
      component_ctx.canvas_element_ctx,
      component_ctx.instance_context,
      component_ctx.trigger_instance_changed,
      component_ctx.instance_selected,
      component_ctx.instance_deselected,
      component_ctx.mouse_down_delta_event,
      component_ctx.mouse_down_position,
      component_ctx.label_settings
    );
    initialized_instance.populate_from_instance_obj(instance);
    return initialized_instance
  }
  else if(instance.type === 'cuboid_3d' && !instance.initialized){
    if(!instance.mesh){
      let cuboid_drawer_tools = new CuboidDrawerTool(scene_controller_3d);
      let cuboid_mesh = cuboid_drawer_tools.create_mesh_from_instance_data(instance)
      initialized_instance = new Cuboid3DInstance(
        scene_controller_3d,
        cuboid_mesh
      );
      initialized_instance.populate_from_instance_obj(instance);
    }
    else{
      initialized_instance = new Cuboid3DInstance(
        scene_controller_3d,
        instance.mesh
      );
      initialized_instance.populate_from_instance_obj(instance);
    }
    return initialized_instance
  }
  else if (instance.type === 'global') {
    let new_global_instance = component_ctx.new_global_instance();
    new_global_instance.populate_from_instance_obj(instance)
    return new_global_instance
  }
  else{
    return instance
  }
}


export const create_instance_list_with_class_types = function(instance_list, component_ctx, scene_controller_3d = undefined){
  const result = []
  if (!instance_list) { return result }
  for(let i = 0; i < instance_list.length; i++){
    let current_instance = instance_list[i];

    // Note that this variable may now be one of any of the classes on vue_canvas/instances folder.
    // Or (for now) it could also be a vanilla JS object (for those types) that haven't been refactored.
    let initialized_instance = initialize_instance_object(current_instance, component_ctx, scene_controller_3d)
    result.push(initialized_instance);
  }
  return result;
}

export const duplicate_instance_template = function(instance_template, component_ctx){
  let result = {...instance_template}
  result.instance_list = instance_template.instance_list.map(inst => {
    return duplicate_instance(inst, component_ctx);
  })
  return result;
}
