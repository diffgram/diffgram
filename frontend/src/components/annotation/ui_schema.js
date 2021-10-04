


export class UI_Schema {

  constructor() {
    this.show_logo = false
  }

  show(value) {
    if (value == undefined){
      return true
    }
    return value
  }

  undo(){
    const command = this.command_history[this.command_index];
    if(!command){return}
    command.undo();
    if(this.command_index != undefined && this.command_index > 0){
      this.command_index -= 1;
    }
    else if(this.command_index != undefined && this.command_index === 0){
      this.command_index = undefined;
    }
    return true
  }

  redo(){
    if(this.command_index == undefined && this.command_history.length > 0){
      this.command_index = 0;
      const command = this.command_history[this.command_index]
      if(!command){return}
      command.execute();
    }
    else if(this.command_index >= 0){
      this.command_index += 1;
      const command = this.command_history[this.command_index]
      if(!command){return}
      command.execute();
    }
    return true
  }

}

