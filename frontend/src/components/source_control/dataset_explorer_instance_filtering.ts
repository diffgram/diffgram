import {Instance} from '../vue_canvas/instances/Instance'
import {initialize_instance_object} from '../../utils/instance_utils'
import {CanvasMouseCtx, MousePosition} from "../../types/mouse_position";
import {ModelRun} from "../../types/models";

const create_empty_mouse_ctx = (): CanvasMouseCtx => {
  // We initialize empty ctx, since there is no drawing logic for dataset explorer.
  let canvas_ctx: CanvasMouseCtx = {
    mouse_position: {x: 0, y: 0},
    canvas_element_ctx: {},
    instance_context: {},
    trigger_instance_changed: () => {
    },
    instance_selected: () => {
    },
    instance_deselected: () => {
    },
    new_global_instance: () => {
      let new_instance = new Instance();
      new_instance.type = 'global'
      return new_instance
    },
    mouse_down_delta_event: {x: 0, y: 0},
    mouse_down_position: {x: 0, y: 0},
    label_settings: {}
  }
  return canvas_ctx
}
export const filter_from_model_id = (global_instance_list: Array<Instance>, model_run_id: number, model_run_color: string): Array<Instance> => {
  let filtered_instance_list = []
  filtered_instance_list = global_instance_list.filter(inst => {
    return inst.model_run_id === model_run_id;
  })
  let canvas_ctx = create_empty_mouse_ctx()
  filtered_instance_list = filtered_instance_list.map(inst => {
    inst = initialize_instance_object(inst, canvas_ctx)
    inst.override_color = model_run_color
    return inst
  })
  return filtered_instance_list
}

export const filter_from_model_runs = (global_instance_list: Array<Instance>,
                                       filtered_instance_list: Array<Instance>,
                                       compare_to_model_run_list: Array<any>) => {
  let added_ids = filtered_instance_list.map(inst => inst.id);
  let canvas_ctx = create_empty_mouse_ctx()
  for (const model_run of compare_to_model_run_list) {

    let filtered_instances = global_instance_list.filter(inst => {
      return inst.model_run_id === model_run.id;
    })

    filtered_instances = filtered_instances.map(inst => {
      inst = initialize_instance_object(inst, canvas_ctx)
      inst.override_color = model_run.color
      return inst
    })
    for (const instance of filtered_instances) {
      if (!added_ids.includes(instance.id)) {
        let initialized_instance = this.initialize_instance(instance);
        filtered_instance_list.push(initialized_instance);
        added_ids.push(initialized_instance.id)
      }
    }

  }
  return filtered_instance_list
}

export const filter_ground_truth_instances = (
  global_instance_list: Array<Instance>,
  filtered_instance_list: Array<Instance>,
  show_ground_truth: boolean
): Array<Instance> => {
  if (!show_ground_truth){
    return filtered_instance_list
  }
  if(!global_instance_list) {
    return filtered_instance_list
  }
  const ground_truth_instances = global_instance_list.filter(inst => !inst.model_run_id);
  let canvas_ctx = create_empty_mouse_ctx()
  for(const inst of ground_truth_instances){
    let initialized_instance = initialize_instance_object(inst, canvas_ctx)
    filtered_instance_list.push(initialized_instance)
  }
  return filtered_instance_list
}

export const filter_global_instance_list = (filtered_instance_list: Array<Instance>,
                                            global_instance_list: Array<Instance>,
                                            base_model_run: ModelRun,
                                            compare_to_model_run_list: Array<any>,
                                            show_ground_truth: boolean) => {

  if (base_model_run) {
    filtered_instance_list = filter_from_model_id(
      filtered_instance_list,
      base_model_run.id,
      base_model_run.color
    )
  }


  if (compare_to_model_run_list) {
    filtered_instance_list = filter_from_model_runs(
      global_instance_list,
      filtered_instance_list,
      compare_to_model_run_list
    )
  }


  if(show_ground_truth){
    filtered_instance_list = filter_ground_truth_instances(
      global_instance_list,
      filtered_instance_list,
      show_ground_truth
    )
  }
  return filtered_instance_list
}
