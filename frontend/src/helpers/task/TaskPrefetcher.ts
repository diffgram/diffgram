import { getFollowingTask } from "../../services/tasksServices"

//
// How does this calss should work:

// 1. Constructor called with project_string_id and optionally can be passed prefetch_number_of_tasks
// 2. On teh contructor prfect next and previous tasks, and set ethem to the class
// 3. When the next task is called, insteead if doing immidiate API call, we will check if the next task is on the state
//         a. If it on the state -  we don't do API call, get it from the state and then do a call for cashe more tasks
//         b. if there is nothing on the state (for exmaple switching too fast) - we do an API call
//

export default class TaskPrefetcher {
  current_task: any
  cached_next_tasks: any[] = [];
  cached_previous_tasks: any[] = [];
  
  project_string_id: string;
  prefetch_number_of_tasks: number

  constructor(
    project_string_id: string, 
    prefetch_number_of_tasks: number = 2
  ) {
    this.project_string_id = project_string_id
    this.prefetch_number_of_tasks = prefetch_number_of_tasks
  }

  async update_tasks(task: any) {
    this.current_task = task
    this.prefetch_next_task()
  }

  async prefetch_next_task() {
    const [result, error] = await getFollowingTask(
      this.project_string_id,
      this.current_task.id,
      this.current_task.job_id,
      'next',
      false
    )
  
    this.cached_next_tasks.push(result.task)
  }

  async prefetch_previous_task() {
    const [result, error] = await getFollowingTask(
      this.project_string_id,
      this.current_task.id,
      this.current_task.job_id,
      'previous',
      false
    )

    this.cached_previous_tasks.push(result.task)
  }

  // async change_task(task: any) {
  //   this.current_task = task

  //   for (let i = 0; i < this.prefetch_number_of_tasks; i++) {
  //     if (i === 0) {
  //       await this.prefetch_next_task(task)
  //       await this.prefetch_previous_task(task)
  //     } else {
  //       const most_recent_next_task = this.cached_next_tasks[i - 1]
  //       const most_recent_previous_task = this.cached_previous_tasks[i - 1]
  //       await this.prefetch_next_task(most_recent_next_task)
  //       await this.prefetch_previous_task(most_recent_previous_task)
  //     }
  //   }

  //   console.log(this.cached_next_tasks, this.cached_previous_tasks)
  // }


  async change_task(task: any, direction: string) {
    console.log("here", this.cached_next_tasks)
    if (direction === 'next') {
      return this.cached_next_tasks[0]
    }

    if (direction === 'previous') {
      return this.cached_previous_tasks[0]
    }
  }
} 