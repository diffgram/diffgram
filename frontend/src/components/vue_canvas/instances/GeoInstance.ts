import { Instance } from "./Instance";
import { v4 as uuidv4 } from 'uuid'
import { InstanceInterface } from "../../../helpers/interfaces/InstanceData";

export class GeoCircle extends Instance implements InstanceInterface {
    public type: string = "geo_circle";
    public lonlat: Array<number>;
    public coords: Array<number>;
    public radius: number;
    public ol_id: string;

    constructor() {
        super();
    }

    public create_instance() {}

    public create_frontend_instance(
            lonlat: Array<number>, 
            coords: Array<any>, 
            radius: number, 
            label_file: any, 
            ol_id: string,
            soft_delete: boolean = false
        ): void {
        this.lonlat = lonlat;
        this.coords = coords;
        this.radius = radius;
        this.soft_delete = soft_delete;
        this.creation_ref_id = uuidv4();
        this.label_file = label_file;
        this.label_file_id = label_file.id;
        this.ol_id = ol_id;
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
            lonlat: this.lonlat,
            coords: this.coords,
            radius: this.radius,
            ol_id: this.ol_id
        }
        
        return payload
    }
}

export class GeoPoly extends Instance implements InstanceInterface {
    public bounds: Array<number>;
    public bounds_lonlat: Array<number>;
    public type: string;
    public ol_id: string;

    constructor(type: string) {
        super();
        this.type = type;
    }

    public create_instance() {}

    public create_frontend_instance(
            bounds: Array<number>, 
            bounds_lonlat: Array<number>, 
            label_file: any, 
            ol_id: string,
            soft_delete: boolean = false
        ): void {
        this.bounds = bounds;
        this.bounds_lonlat = bounds_lonlat;
        this.soft_delete = soft_delete;
        this.creation_ref_id = uuidv4();
        this.label_file = label_file;
        this.label_file_id = label_file.id;
        this.ol_id = ol_id;
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
            bounds_lonlat: this.bounds_lonlat,
            ol_id: this.ol_id
        }
        
        return payload
    }
}

export class GeoPoint extends Instance implements InstanceInterface {
    public lonlat: Array<number>;
    public coords: Array<number>;
    public type: string = "geo_point";
    public ol_id: string;

    constructor() {
        super();
    }

    public create_instance() {}

    public create_frontend_instance(
            lonlat: Array<number>,
            coords: Array<number>,
            label_file: any,
            ol_id: string,
            soft_delete: boolean = false
        ): void {
        this.lonlat = lonlat;
        this.coords = coords;
        this.soft_delete = soft_delete;
        this.creation_ref_id = uuidv4();
        this.label_file = label_file;
        this.label_file_id = label_file.id;
        this.ol_id = ol_id;
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
            lonlat: this.lonlat,
            coords: this.coords,
            ol_id: this.ol_id
        }
        
        return payload
    }
}

