import {v4 as uuidv4} from 'uuid'

export default class DiffgramExportFileIngestor {
  public export_raw_obj: any = null;
  public file: any = null;
  public new_label_map: any = null;
  private export_ingestor_version: string = '1.0' // This is the ingestor for format v1.0
  public metadata_keys: string[] = ['readme', 'label_map', 'export_info', 'attribute_groups_reference']

  public constructor(export_raw_obj, file) {
    this.export_raw_obj = export_raw_obj
    this.file = file
    this.validate_export_obj();
  }

  public get_label_names() {
    const export_obj = this.export_raw_obj;
    const result = [];
    if (!export_obj.label_map) {
      throw new Error('Export data has no key "labels_map". Please provide this key in the JSON file.')
    }
    for (const key of Object.keys(export_obj.label_map)) {
      let label_name = export_obj.label_map[key]
      result.push(label_name)
    }
    return result;
  }

  public get_file_names() {
    const export_obj = this.export_raw_obj;
    const result = [];
    for (const key of Object.keys(export_obj)) {
      if (this.metadata_keys.includes(key)) {
        continue
      }
      let file_data = export_obj[key];
      if (!file_data.file || !file_data.file.original_filename) {
        throw new Error(`File key ${key} has no "file.original_filename". Please check this key exists in the export.`)
      }
      result.push(file_data.original_filename)

    }
    return result;
  }

  public get_blob_list() {
    const export_obj = this.export_raw_obj;
    const result = [];
    for (const key of Object.keys(export_obj)) {
      if (this.metadata_keys.includes(key)) {
        continue
      }
      let file_data = export_obj[key];
      if (!file_data.file || !file_data.file.blob_url) {
        throw new Error(`File key ${key} has no blob. Please check this file has the key "file.blob_url" in the export.`)
      }
      result.push(file_data.file.blob_url)

    }
    return result;
  }

  public check_export_meta_data() {
    // Check existence of metadata fields
    const result = [];
    const export_obj = this.export_raw_obj;
    for (const key of this.metadata_keys) {
      if (!export_obj[key]) {
        throw new Error(`Invalid Export Format: "${key}" key is missing`)
      }
    }
  }

  private validate_export_obj() {
    let result = true;
    const export_obj = this.export_raw_obj;
    this.check_export_meta_data()
    // Check valid file keys
    const file_keys = Object.keys(this.export_raw_obj).filter(key => !this.metadata_keys.includes(key));
    for (const file_key of file_keys) {
      let file_id = parseInt(file_key, 10);
      if (isNaN(file_id)) {
        throw new Error(`Invalid Export Format: "${file_key}" unrecognized key.`)
      }
    }

  }

  private check_points_type_instance(instance) {
    let expected_keys = ['points'];
    let expected_keys_point = ['x', 'y'];
    for (let key of expected_keys) {
      if (!(key in instance)) {
        throw new Error(`${key} is missing in ${instance.type} instance. Data is: ${JSON.stringify(instance)}`)
      }
    }
    for (let key of expected_keys_point) {
      for (let i = 0; i < instance.points.length; i++) {
        if (!(key in instance.points[i])) {
          throw new Error(`${key} is missing in ${instance.type} instance. Data is: ${JSON.stringify(instance)}`)
        }
      }
    }
  }

  private check_instance_spacial_data(instance) {
    if (instance.type === 'box') {
      let expected_keys = ['x_min', 'x_max', 'y_min', 'y_max'];
      for (let key of expected_keys) {
        if (!(key in instance)) {
          throw new Error(`${key} is missing in ${instance.type} instance. Data is: ${JSON.stringify(instance)}`)
        }
      }
    } else if (instance.type === 'point') {
      this.check_points_type_instance(instance);
    } else if (instance.type === 'line') {
      this.check_points_type_instance(instance);
    } else if (instance.type === 'cuboid') {
      let expected_keys_faces = ['front_face', 'rear_face'];
      let expected_per_face_keys = ['top_right', 'top_left', 'bot_right', 'bot_left'];
      let point_keys = ['x', 'y'];
      for (let face_key of expected_keys_faces) {
        if (!(face_key in instance)) {
          throw new Error(`${face_key} is missing in ${instance.type} instance. Data is: ${JSON.stringify(instance)}`)
        }
        for (let position_key of expected_per_face_keys) {
          if (!(position_key in instance[face_key])) {
            throw new Error(`${position_key} is missing in ${instance.type} ${face_key}, instance. Data is: ${JSON.stringify(instance)}`)
          }
          for (let point_key of point_keys) {
            if (!(point_key in instance[face_key][position_key])) {
              throw new Error(`${point_key} is missing in ${instance.type} ${face_key}, ${position_key} instance. Data is: ${JSON.stringify(instance)}`)
            }
          }
        }
      }
    } else if (instance.type === 'polygon') {
      this.check_points_type_instance(instance);
    } else if (instance.type === 'ellipse') {
      let expected_keys = ['center_x', 'center_y', 'width', 'height', 'angle'];
      for (let key of expected_keys) {
        if (!(key in instance)) {
          throw new Error(`${key} is missing in ${instance.type} instance. Data is: ${JSON.stringify(instance)}`)
        }
      }

    }
  }

  private check_instance_sequences(instance) {
    if (!('number' in instance)) {
      throw new Error(`Sequence number missing: "number" key is missing in ${instance.type} instance. Data is: ${JSON.stringify(instance)}`)
    }
    if (isNaN(instance.number)) {
      throw new Error(`Instance sequence number must be a number. Data is: ${JSON.stringify(instance)}`)
    }
  }

  private check_label_is_valid(instance) {
    if (!('label_file_id' in instance)) {
      throw new Error(`Label File ID missing. Provide 'label_file_id'. Data is: ${JSON.stringify(instance)}`)
    }
    let label_name = this.export_raw_obj.label_map[instance.label_file_id];
    if (!label_name) {
      throw new Error(`Invalid label_file_id ${instance.label_file_id}. ID not available in label_map.`)
    }
  }

  private check_image_instances(file_data) {
    let instance_list = file_data.instance_list;
    for (const instance of instance_list) {
      this.check_instance_spacial_data(instance);
      this.check_label_is_valid(instance);
    }
  }

  private check_valid_frames(sequence_list) {
    for (const sequence of sequence_list) {
      for (const instance of sequence.instance_list) {
        if (isNaN(instance.frame_number)) {
          throw new Error(`Invalid frame_number: ${instance.frame_number}`)
        }
      }
    }
  }

  private check_video_instances(file_data) {
    let sequence_list = file_data.sequence_list;
    this.check_valid_frames(sequence_list);
    for (let sequence of sequence_list) {
      for (let instance of sequence.instance_list) {
        this.check_instance_spacial_data(instance);
        this.check_label_is_valid(instance);
        this.check_instance_sequences(instance);
      }
    }
  }

  private check_instances_based_on_type(file_data) {
    if (file_data.file.type === 'image') {
      this.check_image_instances(file_data)
    } else if (file_data.file.type === 'video') {
      this.check_video_instances(file_data);
    } else {
      throw new Error(`Invalid File type: ${file_data.file.type}`)
    }

  }

  public validate_instances() {
    const export_obj = this.export_raw_obj;
    const result = [];
    for (const key of Object.keys(export_obj)) {
      if (this.metadata_keys.includes(key)) {
        continue
      }
      let file_data = export_obj[key];
      this.check_instances_based_on_type(file_data);

    }
    return result;

  }

  private add_to_instance_count_list(file_data, instance) {
    if (instance.type === 'box') {
      file_data.box_instances.push(instance);
    } else if (instance.type === 'point') {
      file_data.point_instances.push(instance)
    } else if (instance.type === 'point') {
      file_data.point_instances.push(instance)
    } else if (instance.type === 'polygon') {
      file_data.polygon_instances.push(instance)
    } else if (instance.type === 'line') {
      file_data.line_instances.push(instance)
    } else if (instance.type === 'cuboid') {
      file_data.cuboid_instances.push(instance)
    } else if (instance.type === 'ellipse') {
      file_data.ellipse_instances.push(instance)
    } else {
      throw new Error(`Invalid instance type ${instance.type}`)
    }

    file_data.instances.push(instance)
  }

  private add_to_label_count_list(file_data, instance) {
    let label_name = this.export_raw_obj.label_map[instance.label_file_id];
    if (!file_data.labels[label_name]) {
      file_data.labels[label_name] = 1
    } else {
      file_data.labels[label_name] += 1
    }
  }

  private build_instance_list_for_input_payload(file) {
    const result = [];
    if(!this.new_label_map){
      throw new Error('new_label_map not set. Please set the value to the current project label_file ids mapping.')
    }
    let instance_list = file.instance_list;
    for(let instance of instance_list){
      let label_name = this.export_raw_obj.label_map[instance.label_file_id];
      let label_file_id_new = this.new_label_map[label_name];
      result.push({
        ...instance,
        name: label_name,
        label_file_id: label_file_id_new,
      })
    }
    return result
  }
  public set_new_label_map(label_map){
    this.new_label_map = label_map;
  }
  private build_frame_packet_map_for_input_payload(file) {
    const result = {};
    if(!this.new_label_map){
      throw new Error('new_label_map not set. Please set the value to the current project label_file ids mapping.')
    }
    for(let sequence of file.sequence_list){
      for(let instance of sequence.instance_list){
        let label_name = this.export_raw_obj.label_map[instance.label_file_id];
        let label_file_id_new = this.new_label_map[label_name]

        if(result[instance.frame_number]){
          result[instance.frame_number].push({
            ...instance,
            label_file_id: label_file_id_new,
            name: label_name
          })
        }
        else{
          result[instance.frame_number] = [{
            ...instance,
            label_file_id: label_file_id_new,
            name: label_name
          }]
        }
      }
    }
    return result
  }

  public get_payload_for_batch_creation() {
    const result = [];
    const export_obj = this.export_raw_obj;
    const file_names = {};
    for (const key of Object.keys(export_obj)) {
      if (this.metadata_keys.includes(key)) {
        continue
      }
      let file = export_obj[key];
      const uuid = uuidv4();
      let file_name = file.file.original_filename;
      if(file_names[file_name]){
        file_names[file_name] += 1
        file_name = `(${file_names[file_name]})${file_name}`
      }
      else{
        file_names[file_name] = 1
      }
      result[uuid] = {
        instance_list: [],
        frame_packet_map: {},
        file_id: file.file_id,
        url: file.file.blob_url,
        type: file.file.type,
        name: file_name
      };
      if (file.file.type === 'image') {
        let instance_list = this.build_instance_list_for_input_payload(file);
        result[uuid].instance_list = instance_list;
      } else if (file.file.type === 'video') {
        let frame_packet_map = this.build_frame_packet_map_for_input_payload(file);
        result[uuid].frame_packet_map = frame_packet_map;
      } else {
        throw new Error(`Invalid file type ${file.file.type}`)
      }
    }
    return result;
  }

  public get_instance_count_per_file() {
    const result = [];
    const export_obj = this.export_raw_obj;
    const file_names = {};
    for (const key of Object.keys(export_obj)) {
      if (this.metadata_keys.includes(key)) {
        continue
      }
      let file = export_obj[key];
      let file_name = file.file.original_filename;
      if(file_names[file_name]){
        file_names[file_name] += 1
        file_name = `(${file_names[file_name]})${file_name}`
      }
      else{
        file_names[file_name] = 1
      }
      let file_data = {
        name: file_name,
        file_id: file_name,
        box_instances: [],
        point_instances: [],
        polygon_instances: [],
        line_instances: [],
        cuboid_instances: [],
        ellipse_instances: [],
        instances: [],
        labels: {},
      }

      if (file.file.type === 'image') {
        for (const instance of file.instance_list) {
          this.add_to_instance_count_list(file_data, instance)
          this.add_to_label_count_list(file_data, instance)
        }
      } else if (file.file.type === 'video') {
        for (let sequence of file.sequence_list) {
          for (let instance of sequence.instance_list) {
            this.add_to_instance_count_list(file_data, instance)
            this.add_to_label_count_list(file_data, instance)
          }
        }
      } else {
        throw new Error(`Invalid File type ${file.type}`)
      }

      result.push(file_data)
    }
    return result;
  }

  public add_batch_to_export_data(batch){
    const export_obj = this.export_raw_obj;
    for (const key of Object.keys(export_obj)) {
      if (this.metadata_keys.includes(key)) {
        continue
      }
      export_obj[key].batch_id = batch.id
    }
  }

}
