

def rotate_box(instance:dict, width: int, height: int):
    old_x = instance['x_min']
    old_y = instance['y_min']
    instance['x_min'] = width - old_y
    instance['y_min'] = old_x
    width_instance = instance['width']
    height_instance = instance['height']
    instance['width'] = height_instance
    instance['height'] = width_instance
    return instance


def rotate_points_instance(instance: dict, width: int, height: int):
    points = instance['points']
    for p in points:
        old_x = p['x']
        old_y = p['y']
        p['x'] = width - old_y
        p['y'] = old_x
    return instance


def rotate_instance_dict_90_degrees(instance: dict, width: int, height: int):
    """
        Rotates the instance dict data 90 degrees.
        Currently only supports 2D image data instances.
    :param instance: Instance dictionary data
    :param width: the reference with of the image to rotate from
    :param height: the reference height of the image to rotate from
    :return: The modified instance with all coords rotated by 90 degrees.
    """
    if instance['type'] == 'box':
        return rotate_box(instance, width, height)
    elif instance['type'] == 'polygon':
        return rotate_points_instance(instance, width, height)
    elif instance['type'] == 'point':
        return rotate_points_instance(instance, width, height)
    elif instance['type'] == 'line':
        return rotate_points_instance(instance, width, height)
    elif instance['type'] == 'cuboid':
        raise NotImplementedError
    elif instance['type'] == 'ellipse':
        raise NotImplementedError
    elif instance['type'] == 'keypoints':
        raise NotImplementedError

