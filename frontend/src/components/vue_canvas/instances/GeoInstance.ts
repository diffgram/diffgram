import { Instance } from "./Instance";
import { v4 as uuidv4 } from 'uuid'
import { InstanceInterface } from "../../../helpers/interfaces/InstanceData";

interface Origin {
    lat: number;
    lng: number;
}

export class GeoCircle extends Instance implements InstanceInterface {
    public origin: Origin;
    public radius: number;
    public type: string = "geo_circle";

    constructor() {
        super();
    }

    public create_instance() {}

    public create_frontend_instance(origin: Origin, radius: number, label_file: any, soft_delete: boolean = false): void {
        this.origin = origin;
        this.radius = radius;
        this.soft_delete = soft_delete;
        this.creation_ref_id = uuidv4();
        this.label_file = label_file;
        this.label_file_id = label_file.id;
    }

    public get_instance_data() {
        const payload = {
            id: this.id || this.creation_ref_id,
            type: this.type,
            selected: this.selected,
            label_file: this.label_file,
            label_file_id: this.label_file_id,
            soft_delete: this.soft_delete,
            creation_ref_id: this.creation_ref_id,
            origin: this.origin,
            radius: this.radius
        }
        
        return payload
    }
}

export class GeoPoly extends Instance implements InstanceInterface {
    public bounds: Array<number>;
    public type: string;

    constructor(type: string) {
        super();
        this.type = type;
    }

    public create_instance() {}

    public create_frontend_instance(bounds: Array<number>, label_file: any, soft_delete: boolean = false): void {
        this.bounds = bounds;
        this.soft_delete = soft_delete;
        this.creation_ref_id = uuidv4();
        this.label_file = label_file;
        this.label_file_id = label_file.id;
    }

    public get_instance_data() {
        const payload = {
            id: this.id || this.creation_ref_id,
            type: this.type,
            selected: this.selected,
            label_file: this.label_file,
            label_file_id: this.label_file_id,
            soft_delete: this.soft_delete,
            creation_ref_id: this.creation_ref_id,
            bounds: this.bounds,
        }
        
        return payload
    }
}

class GeoLine extends Instance {}

export class GeoPoint extends Instance implements InstanceInterface {
    public origin: Origin;
    public type: string = "geo_point";

    constructor() {
        super();
    }

    public create_instance() {}

    public create_frontend_instance(origin: Origin, label_file: any, soft_delete: boolean = false): void {
        this.origin = origin;
        this.soft_delete = soft_delete;
        this.creation_ref_id = uuidv4();
        this.label_file = label_file;
        this.label_file_id = label_file.id;
    }

    public get_instance_data() {
        const payload = {
            id: this.id || this.creation_ref_id,
            type: this.type,
            selected: this.selected,
            label_file: this.label_file,
            label_file_id: this.label_file_id,
            soft_delete: this.soft_delete,
            creation_ref_id: this.creation_ref_id,
            origin: this.origin,
        }
        
        return payload
    }
}

class GeoTag extends Instance {}

class GeoPoligon extends Instance {}
