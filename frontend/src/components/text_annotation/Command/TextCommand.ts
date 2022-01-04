import { TextInstanceSnapshot } from "./CreateSnapshot"
import { TextInstance, TextLabelInstanse, TextRelationInstance } from "./Interfaces"

export class TextInterface {
    private instances: TextInstance[];
    private history: any[];
    private currentSnapshotIndex: number;

    constructor() {
        this.instances = []
        this.history = []
        this.currentSnapshotIndex = 0
    }
    
    get(type = null) {
        if (!type) return this.instances;

        const label_instances = [...this.instances].filter(instance => instance.type === type)
        return label_instances
    }

    private makeSnapshot() {
        const snapshot = new TextInstanceSnapshot([...this.instances])
        this.currentSnapshotIndex = this.history.length + 1
        this.history.push(snapshot)
    }
 
    public addLabelInstance(
        x: number, 
        y: number, 
        width: number, 
        sentense_index: number, 
        label: any
        ): void {
        const newTextInstance: TextLabelInstanse = {
            id: this.instances.length + 1,
            type: "label",
            x,
            y,
            width,
            sentense_index,
            label
        }

        this.instances.push(newTextInstance)
        this.makeSnapshot()
    }

    public addRelationInstance(
        M1: number, 
        M2: number, 
        H: number, 
        start_label: number, 
        end_label: number, 
        sentense_index: number, 
        label: any
        ): void {
        const newTextInstance: TextRelationInstance = {
            id: this.instances.length + 1,
            type: "relation",
            M1,
            M2,
            H,
            start_label,
            end_label,
            sentense_index,
            label
        };
        this.instances.push(newTextInstance)
        this.makeSnapshot()
    }

    public deleteInstance (id: number): void {
        console.log(id)
        this.makeSnapshot()
    }

    public updateInstance (id: number): void {
        console.log(id)
        this.makeSnapshot()
    }

    public get_label_by_id(id: number): TextInstance {
        const instance = [...this.instances].find(instance => instance.type === "label" && instance.id === id)
        return instance
    }

    public get_relation_by_id(id: number): TextInstance {
        const instance = [...this.instances].find(instance => instance.type === "relation" && instance.id === id)
        return instance
    }

    public redo() {
        console.log("REDO")
    }

    public undo() {
        if (this.currentSnapshotIndex === 0) return;
        const currentSnapshotIndex = this.currentSnapshotIndex - 1
        const setHistorySnapshot = this.history[currentSnapshotIndex - 1]
        this.currentSnapshotIndex = currentSnapshotIndex
        
        if (setHistorySnapshot) {
            this.instances = setHistorySnapshot.get()
            return
        }
        this.instances = []
    }
}