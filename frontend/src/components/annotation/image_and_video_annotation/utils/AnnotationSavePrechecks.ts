import stringify from 'json-stable-stringify';
import { sha256 } from 'js-sha256';

/**
 * Hash a string using the SHA-256 algorithm.
 *
 * @param {string} str - The string to hash.
 * @return {string} The hashed string in hexadecimal format.
 */
export let hash_string = function(str) {
  return sha256(str);
};

/**
 * Check for duplicate instances in a given list based on their data.
 *
 * @param {Array<Object>} instance_list - The list of instances to check for duplicates.
 * @return {Array<boolean, Array<string>, Array<number>>} An array containing a boolean indicating if duplicates were found,
 * and arrays of duplicate instance IDs and their respective indexes in the input list.
 */
export let has_duplicate_instances = function(instance_list) {
  if (!instance_list) {
    return [false, [], []];
  }

  const hashes = {};
  const dup_ids = [];
  const dup_indexes = [];

  for (let i = 0; i < instance_list.length; i++) {
    const inst = instance_list[i];

    // Skip instances with soft delete flag set
    if (inst.soft_delete) {
      continue;
    }

    const inst_data = {
      // ...
    };

    // We want a nested stringify with sorted keys. Builtin JS does not guarantee sort on nested objs.
    const inst_hash_data = stringify(inst_data);
    let inst_hash = hash_string(inst_hash_data);

    if (hashes[inst_hash]) {
      dup_indexes.push(i);
      dup_ids.push(inst.id ? inst.id : 'New Instance');
      dup_ids.push(hashes[inst_hash][0].id ? hashes[inst_hash][0].id : 'New Instance');

      return [true, dup_indexes, dup_ids];
    } else {
      hashes[inst_hash] = [inst, i];
    }
  }

  return [false, dup_ids, dup_indexes];
};

/**
 * Add IDs to new instances and delete old instances in the provided instance list.
 *
 * @param {Object} new_instance_data - The new instance data received from the backend.
 * @param {Object} request_video_data - The video data related to the current request.
 * @param {Array<Object>} instance_list - The list of instances to update.
 * @param {Object} instance_buffer_dict - A dictionary containing instance buffers for each frame.
 * @param {boolean} video_mode - A flag indicating if the function is called in video mode.
 */
export let add_ids_to_new_instances_and_delete_old = function(
  new_instance_data,
  request_video_data,
  instance_list,
  instance_buffer_dict,
  video_mode
) {
  // ...
};

/**
 * Check if there are any pending created instances in the provided instance list.
 *
 * @param {Array<Object>} instance_list - The list of instances to check for pending instances.
 * @return {boolean} A boolean indicating if there are any pending instances.
 */
export let check_if_pending_created_instance = function(instance_list) {
  // ...
};
