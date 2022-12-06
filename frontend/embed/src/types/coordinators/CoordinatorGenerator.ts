import {Coordinator} from "./Coordinator";

export interface CoordinatorGenerator {
  generate_coordinator(): Coordinator
}
