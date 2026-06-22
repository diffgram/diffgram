import { Discussion } from "../../../types/Discussions";
import { MousePosition } from "../../../types/mouse_position";
import axios from "../../../services/customInstance";

export default class IssuesAnnotationUIManager {
  issues_list: Discussion[];
  show_modify_an_issue: boolean;
  snackbar_issues: boolean;
  issue_mouse_position: MousePosition | undefined;
  current_issue: Discussion | undefined;
  issues_expansion_panel: boolean | number;

  public constructor() {
    this.snackbar_issues = false;
    this.issue_mouse_position = undefined;
    this.issues_list = [];
    this.show_modify_an_issue = false;
    this.issues_expansion_panel = true;
    this.current_issue = undefined;
  }

  /**
   * Gets a list of issues for a given project and optional file/task IDs.
   * @param project_string_id The string ID of the project.
   * @param file_id The ID of the file (optional).
   * @param task_id The ID of the task (optional).
   * @returns A promise that resolves to an array of issues.
   */
  public async get_issues_list(
    project_string_id: string,
    file_id?: number,
    task_id?: number
  ): Promise<Discussion[]> {
    try {
      const response = await axios.post(
        `/api/v1/project/${project_string_id}/discussions/list`,
        {
          task_id,
          file_id,
        }
      );
      if (response.data && response.data.issues) {
        this.issues_list = response.data.issues;
        return this.issues_list;
      }
    } catch (error) {
      console.error(error);
      // Handle the error appropriately, e.g. by showing a message to the user.
    }
  }

  /**
   * Updates an issue in the issues list.
   * @param updated_issue The updated issue.
   */
  public update_issue(updated_issue: Discussion): void {
    this.issues_list = this.issues_list.map((issue) =>
      issue.id === updated_issue.id ? { ...updated_issue } : issue
    );
  }

  /**
   * Adds a new issue to the issues list, if it's not already present.
   * @param new_issue The new issue.
   */
  public add_issue_to_list(new_issue: Discussion): void {
    if (!this.issues_list.some((issue) => issue.id === new_issue.id)) {
      this.issues_list.push(new_issue);
    }
  }
}
