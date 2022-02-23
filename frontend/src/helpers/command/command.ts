import { Instance } from "../../components/vue_canvas/instances/Instance"

export default abstract class Command {    
    constructor(instances: Array<Instance>) {
        this._copyInstance(instances[0])
    }

    private _copyInstance(instance: Instance): Instance {
        return instance
    }

    undo() {}

    abstract execute()
}