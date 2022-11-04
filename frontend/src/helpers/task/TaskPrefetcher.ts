import { getFollowingTask } from "../../services/tasksServices"

export default class TaskPrefetcher {
  project_string_id: string;

  constructor(project_string_id: string) {
    this.project_string_id = project_string_id
  }

  async prefetch_next_task(task: any) {
    const response = await getFollowingTask(
      this.project_string_id,
      task.job_id,
      task.id,
      'next',
      true
    )

    console.log(response)
  }
} 