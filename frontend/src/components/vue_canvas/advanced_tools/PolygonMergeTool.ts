import {Instance} from "../instances/Instance";
import {v4 as uuidv4} from "uuid";
import { store } from '../../../../src/store.js'

export class PolygonMergeTool {
  parent_merge_instance: Instance
  instances_to_merge: Instance[]

  public constructor(inst: Instance) {
    this.parent_merge_instance = inst
    this.instances_to_merge = []
  }
  public is_allowed_instance_to_merge(instance_to_select: Instance): boolean{
    if(!this.parent_merge_instance){
      return
    }
    if(!instance_to_select){
      return
    }
    if (this.parent_merge_instance.id === instance_to_select.id) {
      return false;
    }

    if (this.parent_merge_instance.label_file_id !== instance_to_select.label_file_id) {
      return false;
    }

    if (this.parent_merge_instance.type !== instance_to_select.type) {
      return false;
    }
    return true;
  }
  public update_instances_to_merge(instance: Instance){

    if (!this.instances_to_merge.includes(instance)) {
      this.instances_to_merge.push(instance);
    } else {
      let index = this.instances_to_merge.indexOf(instance);
      if (index > -1) {
        this.instances_to_merge.splice(index, 1);
      }
    }
  }
  public delete_instances_and_add_to_merged_instance(parent_instance: Instance,
                                                     instances_to_merge: Instance[],
                                                     instance_list: Instance[]): number[]{
    // For instance to merge, delete it and add al points to parent instance with a new figure ID.
    let deleted_instance_indexes = []
    for (const instance of instances_to_merge) {
      let figure_id = uuidv4();
      let new_points = parent_instance.points.map((p) => p);
      for (const point of instance.points) {
        let new_figure_id = figure_id;
        if (point.figure_id) {
          new_figure_id = point.figure_id;
        }
        new_points.push({
          ...point,
          figure_id: new_figure_id,
        });
      }

      let instance_to_delete = instance_list.find(inst => inst.id === instance.id);
      let instance_index = instance_list.indexOf(instance_to_delete)
      if (instance_index > -1) {
        instance_to_delete.soft_delete = true
        deleted_instance_indexes.push(instance_index)
      }
      parent_instance.points = new_points;
    }
    return deleted_instance_indexes

  }
  public merge_polygons(instance_list): number[]{
    let parent_instance = this.parent_merge_instance;
    let instances_to_merge = this.instances_to_merge
    if(instances_to_merge.length === 0){
      return []
    }
    let has_multiple_figures = parent_instance.points.filter((p) => p.figure_id != undefined).length > 0;
    let deleted_instance_indexes = []
    if (has_multiple_figures) {
      // For each instance to merge, delete it and add al points to parent instance with a new figure ID.
      deleted_instance_indexes = this.delete_instances_and_add_to_merged_instance(
        parent_instance,
        instances_to_merge,
        instance_list
      );
    } else {
      // Add a figure ID for parent instance points
      let figure_id = uuidv4();
      parent_instance.points = parent_instance.points.map((p) => {
        return {
          ...p,
          figure_id: figure_id,
        };
      });
      // For each instance to merge, delete it and add all points to parent instance with a new figure ID.
      deleted_instance_indexes = this.delete_instances_and_add_to_merged_instance(
        parent_instance,
        instances_to_merge,
        instance_list
      );
    }
    return deleted_instance_indexes
  }
}
