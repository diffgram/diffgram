


export class CommandManagerAnnotationCore {

  constructor() {
    this.command_history = [];
    this.command_index = undefined;
  }

  executeCommand(command){
    command.execute();

    if(this.command_history.length === 0){
      this.command_history.push(command);
      this.command_index = 0;
    }
    else{
      if(this.command_index < this.command_history.length - 1){
        this.command_history.length = this.command_index + 1;
      }
      this.command_history.push(command);
      this.command_index = this.command_history.length - 1
    }
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

