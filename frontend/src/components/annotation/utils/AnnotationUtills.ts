import stringify from 'json-stable-stringify';
import {sha256} from 'js-sha256';

export let hash_string = function (str) {
  return sha256(str)
}

export let has_duplicate_instances = function (instance_list) {
  if (!instance_list) {
    return [false, [], []];
  }
  const hashes = {};
  const dup_ids = [];
  const dup_indexes = [];
  for (let i = 0; i < instance_list.length; i++) {
    const inst = instance_list[i];
    if (inst.soft_delete) {
      continue;
    }
    const inst_data = {
      type: inst.type,
      x_min: inst.x_min,
      y_min: inst.y_min,
      y_max: inst.y_max,
      x_max: inst.x_max,
      p1: inst.p1,
      p2: inst.p2,
      cp: inst.cp,
      center_x: inst.center_x,
      center_y: inst.center_y,
      center_z: inst.center_z,
      rotation_euler_angles: inst.rotation_euler_angles,
      position_3d: inst.position_3d,
      angle: inst.angle,
      width: inst.width,
      height: inst.height,
      start_char: inst.start_char,
      end_char: inst.end_char,
      start_token: inst.start_token,
      end_token: inst.end_token,
      start_sentence: inst.start_sentence,
      end_sentence: inst.end_sentence,
      sentence: inst.sentence,
      label_file_id: inst.label_file_id,
      number: inst.number,
      rating: inst.rating,
      points: inst.points ? inst.points.map(point => {
        return {...point}
      }) : inst.points,
      front_face: {...inst.front_face},
      rear_face: {...inst.rear_face},
      soft_delete: inst.soft_delete,
      attribute_groups: {...inst.attribute_groups},
      machine_made: inst.machine_made,
      sequence_id: inst.sequence_id,
      pause_object: inst.pause_object
    }

    // We want a nested stringify with sorted keys. Builtin JS does not guarantee sort on nested objs.
    const inst_hash_data = stringify(inst_data)
    let inst_hash = hash_string(inst_hash_data)

    if (hashes[inst_hash]) {
      dup_ids.push(inst.id ? inst.id : 'New Instance')
      dup_ids.push(hashes[inst_hash][0].id ? hashes[inst_hash][0].id : 'New Instance')

      dup_indexes.push(i)
      dup_indexes.push(hashes[inst_hash][1])
      return [true, dup_ids, dup_indexes];

    } else {
      hashes[inst_hash] = [inst, i]
    }

  }
  return [false, dup_ids, dup_indexes];
}


export let add_ids_to_new_instances_and_delete_old = function (response,
                                                                 request_video_data,
                                                                 instance_list,
                                                                 video_mode) {
    /*
    * This function is used in the context of AnnotationUpdate.
    * The new created/deleted instances are merged without loss of the current
    * frontend data (like selected context for example).
    * This is done by destructuring the new instance (the one received from backend)
    * and then adding the original instance keys on top of the new one.
    * */

  // Add instance ID's to the newly created instances
  const new_added_instances = response.data.added_instances;
  const new_deleted_instances = response.data.deleted_instances;
  if (video_mode) {
    instance_list = this.instance_buffer_dict[request_video_data.current_frame]
  }
  for (let i = 0; i < instance_list.length; i++) {
    const current_instance = instance_list[i]
    if (!current_instance.id) {
      // Case of a new instance added
      const new_instance = new_added_instances.filter(x => x.creation_ref_id === current_instance.creation_ref_id)
      if (new_instance.length > 0) {
        // Now update the instance with the new ID's provided by the API
        current_instance.id = new_instance[0].id;
        current_instance.root_id = new_instance[0].root_id;
        current_instance.version = new_instance[0].version;
        current_instance.sequence_id = new_instance[0].sequence_id;
        current_instance.number = new_instance[0].number;
        instance_list.splice(i, 1, current_instance)

      }
    } else {
      // Case of an instance updated.
      const new_instance = new_added_instances.filter(x => x.previous_id === current_instance.id)
      if (new_instance.length > 0) {
        // Now update the instance with the new ID's provided by the API
        current_instance.id = new_instance[0].id;
        current_instance.root_id = new_instance[0].root_id;
        current_instance.previous_id = new_instance[0].previous_id;
        current_instance.version = new_instance[0].version;
        current_instance.sequence_id = new_instance[0].sequence_id;
        current_instance.number = new_instance[0].number;
        instance_list.splice(i, 1, current_instance)

      }
    }

  }

}


export let check_if_pending_created_instance = function(instance_list){
  // Sets the pending changes flag if there are any instances that have not been saved yet.
  for(let i = 0; i < instance_list.length; i++){
    let instance = instance_list[i];
    if(!instance.id){
      return true
    }
  }
  return false
}
