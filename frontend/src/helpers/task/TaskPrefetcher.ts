import { get_instance_list_from_task } from "../../services/instanceServices";
import { getFollowingTask } from "../../services/tasksServices"

export default class TaskPrefetcher {
  no_prev_task: boolean
  no_next_task: boolean
  
  current_task: any
  current_image: any
  current_annotations: any

  cached_next_tasks: any[] = [];
  cached_next_images: any[] = [];
  cached_next_annotations: any[] = [];

  cached_previous_tasks: any[] = [];
  cached_previous_images: any[] = [];
  cached_previous_annotations: any[] = [];
  
  project_string_id: string;
  prefetch_number_of_tasks: number;

  prefetch_next_promise: Promise<any> | null = null;
  prefetch_prev_promise: Promise<any> | null = null;

  constructor(
    project_string_id: string, 
    prefetch_number_of_tasks: number = 1
  ) {
    this.project_string_id = project_string_id
    this.prefetch_number_of_tasks = prefetch_number_of_tasks
  }

  private async prefetch_image(src: string, image_array: Array<any>) {
      const image = new Image()
      image.src = src
      image.onload = () => image_array.push(image)
  }

  private async prefetch_instances(task_id: number, instances_array: Array<any>) {
    const response = await get_instance_list_from_task(this.project_string_id, task_id)
    instances_array.push(response)
  }
  
  private async prefetch_next_task(): Promise<any> {
    const [result, error] = await getFollowingTask(
      this.project_string_id,
      this.current_task.id,
      this.current_task.job_id,
      'next',
      false
    )

    this.cached_next_images = []
    this.cached_next_annotations = []
    this.no_next_task = false

    if (!error && result.task) {
      if (result.task.file.type === 'image') {
        await this.prefetch_image(result.task.file.image.url_signed, this.cached_next_images)
      }
      await this.prefetch_instances(result.task.id, this.cached_next_annotations)
      
      this.cached_next_tasks = [result.task]
    } else {
      this.no_next_task = true
    }
  }

  private async prefetch_previous_task(): Promise<any> {
    const [result, error] = await getFollowingTask(
      this.project_string_id,
      this.current_task.id,
      this.current_task.job_id,
      'previous',
      false
    )

    this.cached_previous_images = []
    this.cached_previous_annotations = []
    this.no_prev_task = false

    if (!error && result.task) {
      if (result.task.file.type === 'image') {
        await this.prefetch_image(result.task.file.image.url_signed, this.cached_previous_images)
      }
      await this.prefetch_instances(result.task.id, this.cached_previous_annotations)
      
      this.cached_previous_tasks = [result.task]
    } else {
      this.no_prev_task = true
    }
  }

  has_next(direction: string) {
    return direction === 'next' ? !this.no_next_task : !this.no_prev_task
  }

  async update_tasks(task: any) {
    this.current_task = task
    this.prefetch_next_promise = this.prefetch_next_task()
    this.prefetch_prev_promise = this.prefetch_previous_task()
  }

  async change_task(direction: string) {
    let new_task: any;
    let new_image: any;
    let new_instances: any;

    if (direction === 'next') {
      if (this.prefetch_next_promise) {
        await this.prefetch_next_promise
        this.prefetch_next_promise = null
      }
      new_task = this.cached_next_tasks.splice(0, 1);
      new_image = this.cached_next_images.splice(0, 1);
      new_instances = this.cached_next_annotations.splice(0, 1);
    }
    
    if (direction === 'previous') {
      if (this.prefetch_prev_promise) {
        await this.prefetch_prev_promise
        this.prefetch_prev_promise = null
      }
      new_task = this.cached_previous_tasks.splice(0, 1);
      new_image = this.cached_previous_images.splice(0, 1);
      new_instances = this.cached_previous_annotations.splice(0, 1);
    }

    this.current_task = new_task[0]
    this.current_image = new_image[0]
    this.current_annotations = new_instances[0]
    
    return {
      task: this.current_task,
      image: this.current_image,
      instances: this.current_annotations
    }
  }
} 