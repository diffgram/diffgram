import {Interaction} from "./Interaction";

export interface InteractionGenerator{
  generate_interaction(): Interaction
}
