
export class APICredentials {
  project_string_id: string;
  api_key: string;
  api_secret: string;

  constructor(project_string_id: string, api_key: string, api_secret: string) {
    this.project_string_id = project_string_id
    this.api_key = api_key
    this.api_secret = api_secret
  }

  public buildAuthHeaderValue(){
    let value = `${this.api_key}:${this.api_secret}`
    return btoa(value)
  }

}
