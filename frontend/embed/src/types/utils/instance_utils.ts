import {Edge, KeypointInstance} from "../instances/KeypointInstance";
import Cuboid3DInstance from "../instances/Cuboid3DInstance";
import CuboidDrawerTool from "../../../../src/components/3d_annotation/CuboidDrawerTool";
import {CanvasMouseCtx, Point} from "../annotation/image/MousePosition"
import {BoxInstance} from "../instances/BoxInstance";
import {TextAnnotationInstance, TextRelationInstance} from "../instances/TextInstance";
import {Instance, SUPPORTED_CLASS_INSTANCE_TYPES} from "../instances/Instance";
import {LabelColourMap} from "../labels/LabelColourMap";
import {ImageLabelSettings} from "../annotation/image/ImageLabelSettings";
import {InstanceImage2D} from "../instances/InstanceImage2D";
import {ImageCanvasTransform} from "../annotation/image/CanvasTransform";
import {LabelFileMap} from "../labels/Label";
import {v4 as uuidv4} from 'uuid';
import {PolygonPoint} from "../../../../src/components/vue_canvas/instances/PolygonInstance";
export const duplicate_instance = function (instance_to_copy: Instance, component_ctx: CanvasMouseCtx, with_ids: boolean = false) {
  let points: PolygonPoint[] = [];
  let nodes: Point[] = [];
  let edges: Edge[] = [];
  let result;
  if (instance_to_copy.points) {
    points = [...instance_to_copy.points.map((p) => ({...p} as PolygonPoint))];
  }
  if (instance_to_copy.nodes) {
    nodes = [...instance_to_copy.nodes.map((node) => ({...node}))];
  }
  if (instance_to_copy.edges) {
    edges = [...instance_to_copy.edges.map((edge) => ({...edge}))];
  }

  if (!with_ids) {
    result = {
      ...instance_to_copy,
      action_type: undefined,
      attribute_groups: instance_to_copy.attribute_groups
        ? {...instance_to_copy.attribute_groups}
        : undefined,
      creation_ref_id: undefined,
      edges: edges,
      id: undefined,
      initialized: false,
      next_id: undefined,
      nodes: nodes,
      points: points,
      previous_id: undefined,
      root_id: undefined,
      version: undefined,
    };
  } else {
    result = {
      ...instance_to_copy,
      initialized: false,
      points: points,
      nodes: nodes,
      edges: edges,
      attribute_groups: instance_to_copy.attribute_groups
        ? {...instance_to_copy.attribute_groups}
        : undefined,
    };
  }


  if (result.type === "cuboid") {
    result.rear_face = {
      ...instance_to_copy.rear_face,
      top_right: {...instance_to_copy.rear_face.top_right},
      top_left: {...instance_to_copy.rear_face.top_left},
      bot_left: {...instance_to_copy.rear_face.bot_left},
      bot_right: {...instance_to_copy.rear_face.bot_right},
    };

    result.front_face = {
      ...instance_to_copy.front_face,
      top_right: {...instance_to_copy.front_face.top_right},
      top_left: {...instance_to_copy.front_face.top_left},
      bot_left: {...instance_to_copy.front_face.bot_left},
      bot_right: {...instance_to_copy.front_face.bot_right},
    };
  } else if (instance_to_copy.type === 'text_token') {
    const {id, start_token, end_token, label_file, creation_ref_id, soft_delete} = instance_to_copy.get_instance_data()
    const newInstance = new TextAnnotationInstance()
    if (typeof id === "number") {
      newInstance.create_instance(id, start_token, end_token, label_file, soft_delete)
    } else {
      newInstance.create_frontend_instance(start_token, end_token, label_file, soft_delete)
    }
    newInstance.initialized = true
    newInstance.creation_ref_id = creation_ref_id
    return newInstance
  } else if (instance_to_copy.type === 'relation') {
    const {
      id,
      from_instance_id,
      to_instance_id,
      label_file,
      creation_ref_id,
      soft_delete
    } = instance_to_copy.get_instance_data()
    const newInstance = new TextRelationInstance()
    if (typeof id === "number") {
      newInstance.create_instance(id, from_instance_id, to_instance_id, label_file, soft_delete)
    } else {
      newInstance.create_frontend_instance(from_instance_id, to_instance_id, label_file, soft_delete)
    }
    newInstance.initialized = true
    newInstance.creation_ref_id = creation_ref_id
    return newInstance
  }

  result = initialize_instance_object(result as Instance, component_ctx);
  return result;
}

export const initialize_instance_object = function (instance: Instance, component_ctx: CanvasMouseCtx, scene_controller_3d = undefined): Instance {
  let initialized_instance;
  if (instance.type === 'keypoints' && !instance.initialized) {
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
  } else if (instance.type === 'box' && !instance.initialized) {
    initialized_instance = new BoxInstance(
      component_ctx.mouse_position,
      component_ctx.canvas_element_ctx,
      component_ctx.trigger_instance_changed,
      component_ctx.instance_selected,
      component_ctx.instance_deselected,
      component_ctx.mouse_down_delta_event,
      component_ctx.mouse_down_position,
      component_ctx.canvas_transform,
      component_ctx.label_settings
    )
    initialized_instance.populate_from_instance_obj(instance);
    return initialized_instance
  } else if (instance.type === 'cuboid_3d' && !instance.initialized) {
    if (!instance.mesh) {
      let cuboid_drawer_tools = new CuboidDrawerTool(scene_controller_3d);
      let cuboid_mesh = cuboid_drawer_tools.create_mesh_from_instance_data(instance)
      initialized_instance = new Cuboid3DInstance(
        scene_controller_3d,
        cuboid_mesh
      );
      initialized_instance.populate_from_instance_obj(instance);
    } else {
      initialized_instance = new Cuboid3DInstance(
        scene_controller_3d,
        instance.mesh
      );
      initialized_instance.populate_from_instance_obj(instance);
    }
    return initialized_instance
  } else if (instance.type === 'global') {
    let new_global_instance = component_ctx.new_global_instance();
    new_global_instance.populate_from_instance_obj(instance)
    return new_global_instance
  } else {
    return instance
  }
}


export const create_instance_list_with_class_types = function (instance_list, component_ctx: CanvasMouseCtx, scene_controller_3d = undefined) {
  const result = []
  if (!instance_list) {
    return result
  }
  for (let i = 0; i < instance_list.length; i++) {
    let current_instance = instance_list[i];

    // Note that this variable may now be one of any of the classes on vue_canvas/instances folder.
    // Or (for now) it could also be a vanilla JS object (for those types) that haven't been refactored.
    let initialized_instance = initialize_instance_object(current_instance, component_ctx, scene_controller_3d)
    result.push(initialized_instance);
  }
  return result;
}

export const duplicate_instance_template = function (instance_template, component_ctx) {
  let result = {...instance_template}
  result.instance_list = instance_template.instance_list.map(inst => {
    return duplicate_instance(inst, component_ctx);
  })
  return result;
}

export const post_init_instance = function (instance: Instance,
                                            label_file_map: LabelFileMap,
                                            canvas_elm: HTMLCanvasElement,
                                            label_settings: ImageLabelSettings,
                                            canvas_transform: ImageCanvasTransform,
                                            hover_callback: Function,
                                            unhovered_callback: Function) {
  if (!instance) {
    return
  }
  let colour_map = {} as LabelColourMap
  for (let key of Object.keys(label_file_map)){
    colour_map[key] = label_file_map[key].colour
  }
  if(instance.label_file && instance.label_file_id){
    label_file_map[instance.label_file_id] = instance.label_file
    colour_map[instance.label_file_id] = instance.label_file.colour
  }
  instance.label_file_colour_map = colour_map
  let label_file = label_file_map[instance.label_file_id]
  if(!instance.label_file){
    instance.label_file = label_file
  }
  if(instance.creation_ref_id == undefined){
    instance.creation_ref_id = uuidv4()
  }
  if (SUPPORTED_CLASS_INSTANCE_TYPES.includes(instance.type)) {
    let inst = instance as InstanceImage2D
    inst.set_label_file_colour_map(colour_map)
    inst.set_color_from_label()
    inst.set_canvas(canvas_elm)
    inst.set_image_label_settings(label_settings)
    inst.set_canvas_transform(canvas_transform)
    inst.on('hover_in', hover_callback)
    inst.on('hover_out', unhovered_callback)
    return inst
  }
  return instance
}
