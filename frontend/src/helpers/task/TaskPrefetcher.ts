import { getFollowingTask } from "../../services/tasksServices"

export default class TaskPrefetcher {
  cached_next_tasks: any[] = [];
  cached_previous_tasks: any[] = [];
  
  project_string_id: string;
  prefetch_number_of_tasks: number

  constructor(project_string_id: string, prefetch_number_of_tasks: number = 2) {
    this.project_string_id = project_string_id
    this.prefetch_number_of_tasks = prefetch_number_of_tasks
  }

  async prefetch_next_task(task: any) {
    const [result, error] = await getFollowingTask(
      this.project_string_id,
      task.id,
      task.job_id,
      'next',
      true
    )
  
    this.cached_next_tasks.push(result.task)
  }

  async prefetch_previous_task(task: any) {
    const [result, error] = await getFollowingTask(
      this.project_string_id,
      task.id,
      task.job_id,
      'previous',
      true
    )

    this.cached_previous_tasks.push(result.task)
  }

  async change_task(task: any) {
    for (let i = 0; i < this.prefetch_number_of_tasks; i++) {
      await this.prefetch_next_task(task)
      await this.prefetch_previous_task(task)
    } 

    console.log(this.cached_next_tasks, this.cached_previous_tasks)
  }
} 