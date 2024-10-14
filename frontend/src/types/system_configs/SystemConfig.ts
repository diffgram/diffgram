import { Image } from "../files";

/**
 * The SystemConfig class represents the configuration settings for a system.
 * It includes an image identifier and a logo image.
 */
export class SystemConfig {
  /**
   * The unique identifier for the image.
   */
  image_id: number;

  /**
   * The logo image for the system. This is an instance of the Image class.
   */
  logo: Image;
}
