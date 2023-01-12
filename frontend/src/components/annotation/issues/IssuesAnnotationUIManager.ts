import {Discussion} from "../../../types/Discussions";
import {MousePosition} from "../../../types/mouse_position";
import axios from '../../../services/customInstance'

export default class IssuesAnnotationUIManager {
  issues_list: Discussion[]
  show_modify_an_issue: boolean
  snackbar_issues: boolean
  issue_mouse_position: MousePosition
  current_issue: Discussion
  issues_expansion_panel: boolean | number

  public constructor() {
    this.snackbar_issues = false
    this.issue_mouse_position = undefined
    this.issues_list = []
    this.show_modify_an_issue = false
    this.issues_expansion_panel = true
    this.current_issue = undefined
  }
  public async get_issues_list(project_string_id: string, file_id: number = undefined, task_id: number = undefined): Promise<Discussion[]>{
    try {
      const response = await axios.post(`/api/v1/project/${project_string_id}/discussions/list`,
        {
          'task_id': file_id,
          'file_id': task_id
        }
      )
      if (response.data && response.data.issues) {
        this.issues_list = response.data.issues as Discussion[];
        return this.issues_list

      }
    } catch (error) {
      console.error(error)
    }
  }
  public update_issue(updated_issue: Discussion){
    this.issues_list = this.issues_list.map(issue =>{
      if(issue.id === updated_issue.id){
        return {
          ...updated_issue
        }
      }
      return issue
    })
  }
  public add_issue_to_list(new_issue: Discussion){
    this.issues_list.push(new_issue)
  }
}
