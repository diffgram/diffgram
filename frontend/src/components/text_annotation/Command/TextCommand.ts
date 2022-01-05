import { TextInstanceSnapshot } from "./CreateSnapshot"
import { TextInstance, TextLabelInstanse, TextRelationInstance, DrawLabelItem } from "./Interfaces"
import {v4 as uuidv4 } from 'uuid'

export class TextInterface {
    private instances: TextInstance[];
    private history: any[];
    private currentSnapshotIndex: number;
    private resetHead: boolean;

    constructor() {
        this.instances = []
        this.history = []
        this.currentSnapshotIndex = 0
        this.resetHead = false
    }
    
    get(type = null) {
        if (!type) return this.instances;

        const label_instances = [...this.instances].filter(instance => instance.type === type)
        return label_instances
    }

    private resetHistoryHead() {
        const history = [...this.history].splice(0, this.currentSnapshotIndex)
        this.history = history
        this.resetHead = false
    }

    private makeSnapshot() {
        if (this.resetHead) this.resetHistoryHead()
        const snapshot = new TextInstanceSnapshot([...this.instances])
        this.currentSnapshotIndex = this.currentSnapshotIndex + 1
        this.history.push(snapshot)
    }
 
    public addLabelInstance(
        labelItems: DrawLabelItem[], 
        sentense_index: number, 
        label: any
        ): void {
        const newTextInstance: TextLabelInstanse = {
            id: this.instances.length + 1,
            creation_ref_id: uuidv4(),
            type: "label",
            labelItems,
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
            creation_ref_id: uuidv4(),
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
        if (this.currentSnapshotIndex === this.history.length) return this.resetHead = false;
        const setHistorySnapshot = this.history[this.currentSnapshotIndex]
        this.currentSnapshotIndex = this.currentSnapshotIndex + 1
        this.instances = setHistorySnapshot.get()
    }

    public undo() {
        if (this.currentSnapshotIndex === 0) return;
        this.resetHead = true
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