import {KeypointInstance} from "../components/vue_canvas/instances/KeypointInstance";
import Cuboid3DInstance from "../components/vue_canvas/instances/Cuboid3DInstance";
import CuboidDrawerTool from "../components/annotation/3d_annotation/CuboidDrawerTool";
import {CanvasMouseCtx} from "../types/mouse_position"
import {BoxInstance} from "../components/vue_canvas/instances/BoxInstance";
import {TextAnnotationInstance, TextRelationInstance} from "../components/vue_canvas/instances/TextInstance";
import {Instance, SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES} from "../components/vue_canvas/instances/Instance";
import {LabelColourMap} from "../types/label_colour_map";
import {ImageLabelSettings} from "../types/image_label_settings";
import {InstanceImage2D} from "../components/vue_canvas/instances/InstanceImage2D";
import {ImageCanvasTransform} from "../types/CanvasTransform";
import {LabelFileMap} from "../types/label";
import {v4 as uuidv4} from 'uuid';
import {PolygonInstance} from "../components/vue_canvas/instances/PolygonInstance";
import {CanvasMouseTools} from "../components/vue_canvas/CanvasMouseTools";
import {GlobalInstance} from "../components/vue_canvas/instances/GlobalInstance";

export const to_serializable_instance_list =  function (inst_list){
  // Removes any references to objects preventing the instance to be serialzed as a JSON.
  const copy = [...inst_list]
  const res = copy.map(inst => {

    return {...inst, canvas_mouse_tools: undefined}
  })
  return res
}
export const duplicate_for_undo = function() {
  let duplicate_instance = new BoxInstance(
    this.ctx,
    this.on_instance_updated,
    this.on_instance_selected,
    this.on_instance_deselected,
    this.mouse_down_delta_event,
    this.mouse_down_position,
    this.image_label_settings,
  );
  let instance_data_to_keep = {
    ...this,
  };
  duplicate_instance.populate_from_instance_obj(instance_data_to_keep);
  return duplicate_instance
}
export const duplicate_instance = function (instance_to_copy, component_ctx: CanvasMouseCtx, with_ids = false) {
  let points = [];
  let nodes = [];
  let edges = [];
  let result;
  if (instance_to_copy.points) {
    points = [...instance_to_copy.points.map((p) => ({...p}))];
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
        ? {...instance_to_copy.attribute_groups}
        : null,
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
        : null,
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

  result = initialize_instance_object(result, component_ctx);
  return result;
}

export const initialize_instance_object = function (instance, component_ctx: CanvasMouseCtx, scene_controller_3d = undefined): Instance {
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
  } else if (instance.type === 'polygon' && !instance.initialized) {
    initialized_instance = new PolygonInstance(
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
    let new_global_instance = new GlobalInstance()
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
                                            unhovered_callback: Function,
                                            canvas_mouse_tool: CanvasMouseTools) {
  if (!instance) {
    return
  }
  let colour_map = {} as LabelColourMap
  for (let key of Object.keys(label_file_map)) {
    colour_map[key] = label_file_map[key].colour
  }
  if (instance.label_file && instance.label_file_id) {
    label_file_map[instance.label_file_id] = instance.label_file
    colour_map[instance.label_file_id] = instance.label_file.colour
  }
  instance.label_file_colour_map = colour_map
  let label_file = label_file_map[instance.label_file_id]
  if (!instance.label_file) {
    instance.label_file = label_file
  }
  if(instance.creation_ref_id == undefined){
    instance.creation_ref_id = uuidv4()
  }
  if (SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES.includes(instance.type)) {
    let inst = instance as InstanceImage2D
    inst.set_label_file_colour_map(colour_map)
    inst.set_color_from_label()
    inst.set_canvas(canvas_elm)
    inst.set_image_label_settings(label_settings)
    inst.set_canvas_transform(canvas_transform)
    inst.set_label_file(label_file)
    inst.set_canvas_mouse_tools(canvas_mouse_tool)



    inst.on('hover_in', hover_callback)
    inst.on('hover_out', unhovered_callback)
    return inst
  }
  return instance
}
