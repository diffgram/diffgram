import { Instance } from "./Instance";
import { v4 as uuidv4 } from 'uuid'

export class GeoCircle extends Instance {
    public lat: number;
    public lon: number;
    public radius: number;
}

class GeoBox extends Instance {}

class GeoLine extends Instance {}

class GeoPoint extends Instance {}

class GeoTag extends Instance {}

class GeoPoligon extends Instance {}
