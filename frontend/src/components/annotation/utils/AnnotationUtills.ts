import stringify  from 'json-stable-stringify';
import { sha256 } from 'js-sha256';

export const hash_string = function(str){
  return sha256(str)
}

export const has_duplicate_instances = function(instance_list){
  if(!instance_list){
    return [false, [], []];
  }
  const hashes = {};
  const dup_ids = [];
  const dup_indexes = [];
  for(let i = 0; i < instance_list.length; i++){
    const inst = instance_list[i];
    if(inst.soft_delete){
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
      points: inst.points ? inst.points.map(point => {return {...point}}) : inst.points,
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

    if(hashes[inst_hash]){
      dup_ids.push(inst.id ? inst.id : 'New Instance')
      dup_ids.push(hashes[inst_hash][0].id ? hashes[inst_hash][0].id : 'New Instance')

      dup_indexes.push(i)
      dup_indexes.push(hashes[inst_hash][1])
      return [true, dup_ids, dup_indexes];

    }
    else{
      hashes[inst_hash] = [inst, i]
    }

  }
  return [false, dup_ids, dup_indexes];
}
