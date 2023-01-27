

export const populate_empty_sequence_ids = (instance_list, sequence_list) => {
  /*
  * This function updates any instances on the give instance list that have no sequence ID
  * and whose sequence ID is available on the sequence_list parameter.
  *
  * This is usually performed after saving a file, to assign the ID's to the newly created sequences
  * that were saved on the file.
  * */
  for(let sequence of sequence_list){
    for(let instance of instance_list){
      if (
        instance &&
        instance.sequence_id == undefined &&
        instance.label_file_id == sequence.label_file_id &&
        instance.number === sequence.number
      ) {
        instance.sequence_id = sequence.id;
      }
    }
  }

}
