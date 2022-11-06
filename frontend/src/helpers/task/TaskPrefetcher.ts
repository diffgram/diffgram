import { getFollowingTask } from "../../services/tasksServices"

export default class TaskPrefetcher {
  current_task: any
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
      false
    )
  
    this.cached_next_tasks.push(result.task)
  }

  async prefetch_previous_task(task: any) {
    const [result, error] = await getFollowingTask(
      this.project_string_id,
      task.id,
      task.job_id,
      'previous',
      false
    )

    this.cached_previous_tasks.push(result.task)
  }

  async change_task(task: any) {
    this.current_task = task

    for (let i = 0; i < this.prefetch_number_of_tasks; i++) {
      if (i === 0) {
        await this.prefetch_next_task(task)
        await this.prefetch_previous_task(task)
      } else {
        const most_recent_next_task = this.cached_next_tasks[i - 1]
        const most_recent_previous_task = this.cached_previous_tasks[i - 1]
        await this.prefetch_next_task(most_recent_next_task)
        await this.prefetch_previous_task(most_recent_previous_task)
      }
    }

    console.log(this.cached_next_tasks, this.cached_previous_tasks)
  }

  async next_task(task: any) {
    console.log('Next task')
  }
} 