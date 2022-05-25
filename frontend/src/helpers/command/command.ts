import { GeoCircle, GeoPoint, GeoPoly } from "../../components/vue_canvas/instances/GeoInstance";
import { TextAnnotationInstance, TextRelationInstance } from "../../components/vue_canvas/instances/TextInstance";
import { AudioAnnotationInstance } from "../../components/vue_canvas/instances/AudioInstance";
import InstanceList from "../instance_list";
import { CommandInterface } from "../interfaces/Command";
import { InstanceInterface } from "../interfaces/InstanceData";

export abstract class Command implements CommandInterface {   
    protected instances: Array<InstanceInterface>;
    protected instance_list: InstanceList;
    protected replacement_indexes: Array<number> = [];

    constructor(received_instances: Array<InstanceInterface>, instance_list: InstanceList) {
        this.instances = received_instances.map(inst => {
            this.replacement_indexes.push(instance_list.get_all().indexOf(inst))
            return this._copyInstance(inst)
        })
        this.instance_list = instance_list
    }

    protected _copyInstance(instance: InstanceInterface): InstanceInterface {
        let initializedInstance;
        let newInstance = instance.get_instance_data();

        if (instance.type === "audio") {
            initializedInstance = new AudioAnnotationInstance()
        }

        if (instance.type === "text_token") {
            initializedInstance = new TextAnnotationInstance()
        }

        if (instance.type === "relation") {
            initializedInstance = new TextRelationInstance()
        }

        if (instance.type === "geo_point") {
            initializedInstance = new GeoPoint()
        }

        if (instance.type === "geo_circle") {
            initializedInstance = new GeoCircle()
        }

        if (instance.type === "geo_polyline" || 
            instance.type === "geo_polygon" || 
            instance.type === "geo_box"
        ) {
            initializedInstance = new GeoPoly(instance.type)
        }

        initializedInstance.populate_from_instance_obj(newInstance)
        return initializedInstance;
    };

    protected get_instances_ids(): Array<string | number> {
        const id_list: Array<string | number> = this.instances.map(instance => instance.get_instance_data().id)
        return id_list
    };

    abstract execute(): void;
    abstract undo(): void;
}
