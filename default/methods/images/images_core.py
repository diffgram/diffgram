
import logging, re, sys, time, json
import tempfile
import shutil

from methods import routes
from shared.helpers import sessionMaker
from shared.database.image import Image
from shared.settings import settings
from shared.permissions.project_permissions import Project_permissions
from shared.data_tools_core import Data_tools
from flask import request
from flask import jsonify

from imageio import imwrite
from imageio import imread
from shared.image_tools import imresize


data_tools = Data_tools().data_tools

gcs = data_tools.gcs
bucket = data_tools.bucket


def get_and_set_width_and_height(
        diffgram_image,
        imageio_read_image):

    diffgram_image.height = imageio_read_image.shape[0]
    diffgram_image.width = imageio_read_image.shape[1]

    return diffgram_image


def process_profile_image(session,
                          user,
                          file,
                          file_name,
                          content_type,
                          extension=".jpg"):
    new_image = Image(original_filename=file_name)
    session.add(new_image)

    try:
        session.commit()
    except:
        session.rollback()
        raise

    user.profile_image = new_image

    user.profile_image_blob = settings.USER_IMAGES_BASE_DIR + \
                              str(user.id) + "/" + str(new_image.id)
    blob = bucket.blob(user.profile_image_blob)

    image = imread(file)
    image = image[:, :, :3]  # remove alpha channel

    if image is None:
        raise IOError("Could not open")

    new_image = get_and_set_width_and_height(new_image, image)

    if new_image.height > 640 or new_image.width > 640:
        ratio = min((640 / new_image.height),
                    (640 / new_image.width))

        shape_x = int(round(new_image.width * ratio))
        shape_y = int(round(new_image.height * ratio))

        image = imresize(image,
                                    (shape_x, shape_y))
        new_image = get_and_set_width_and_height(new_image, image)

    user.profile_image_expiry = int(time.time() + 25920000)  # 10 months

    # Save File
    temp = tempfile.mkdtemp()
    new_temp_filename = temp + "/resized" + str(extension)
    imwrite(new_temp_filename, image)

    blob.upload_from_filename(new_temp_filename,
                              content_type="image/jpg")
    user.profile_image_url = blob.generate_signed_url(expiration=user.profile_image_expiry)

    # Save Thumb
    user.profile_image_thumb_blob = user.profile_image_blob + "_thumb"
    blob = bucket.blob(user.profile_image_thumb_blob)
    thumbnail_image = imresize(image, (80, 80))
    new_temp_filename = temp + "/resized" + str(extension)
    imwrite(new_temp_filename, thumbnail_image)
    blob.upload_from_filename(new_temp_filename,
                              content_type="image/jpg")

    # Build URLS
    user.profile_image_thumb_url = blob.generate_signed_url(
        expiration=user.profile_image_expiry)

    session.add(new_image, user)

    try:
        shutil.rmtree(temp)  # delete directory
    except OSError as exc:
        if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
            raise  # re-raise exception

    return new_image


def process_image_generic(session,
                          file,
                          file_name,
                          content_type,
                          blob_base,
                          extension=".jpg",
                          do_resize_main=True,
                          thumb_size=80):
    """
        session, db session object
        file, python file pointer???
        file_name, string?
        content_type, string??
        blob_base, string, ie "projects/images/" must end with "/" slash
        extension, ?? must include "."?

    """

    # Consider moving this to paramter
    blob_expiry = int(time.time() + 45920000)  # ~20 months

    new_image = Image(original_filename=file_name)
    session.add(new_image)

    try:
        session.commit()
    except:
        session.rollback()
        raise

    image_blob = blob_base + str(new_image.id)
    image_blob_thumb = image_blob + "_thumb"

    blob = bucket.blob(image_blob)

    image = imread(file)
    image = image[:, :, :3]  # remove alpha channel

    if image is None:
        raise IOError("Could not open")
    new_image = get_and_set_width_and_height(new_image, image)

    if do_resize_main is True:
        if new_image.height > 640 or new_image.width > 640:
            ratio = min((640 / new_image.height),
                        (640 / new_image.width))

            shape_x = int(round(new_image.width * ratio))
            shape_y = int(round(new_image.height * ratio))

            image = imresize(image,
                                        (shape_x, shape_y))
            new_image = get_and_set_width_and_height(new_image, image)

    # Save File
    temp = tempfile.mkdtemp()
    new_temp_filename = temp + "/resized" + str(extension)
    imwrite(new_temp_filename, image)

    blob.upload_from_filename(new_temp_filename,
                              content_type="image/jpg")

    signed_url = blob.generate_signed_url(expiration=blob_expiry)

    # Save Thumb
    blob = bucket.blob(image_blob_thumb)
    thumbnail_image = imresize(image, (thumb_size, thumb_size))
    new_temp_filename = temp + "/resized" + str(extension)
    imwrite(new_temp_filename, thumbnail_image)
    blob.upload_from_filename(new_temp_filename,
                              content_type="image/jpg")

    signed_url_thumb = blob.generate_signed_url(expiration=blob_expiry)

    session.add(new_image)

    try:
        shutil.rmtree(temp)  # delete directory
    except OSError as exc:
        if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
            raise  # re-raise exception

    # Two different generations of naming conventions... todo review
    new_image.url_signed = signed_url
    new_image.url_signed_blob_path = image_blob

    new_image.url_signed_thumb = signed_url_thumb
    new_image.url_signed_thumb_blob_path = image_blob_thumb

    new_image.url_signed_expiry = blob_expiry

    return new_image


@routes.route('/api/project/<string:project_string_id>/images/annotation_example_toggle',
              methods=['POST'])
@Project_permissions.user_has_project(["admin"])
def annotation_example_toggle(project_string_id):
    with sessionMaker.session_scope() as s:

        data = request.get_json(force=True)
        reqiest_image = data.get('image', None)
        if reqiest_image is None:
            return json.dumps("image is None"), 400, {'ContentType': 'application/json'}

        request_image_id = reqiest_image.get('id', None)
        if request_image_id is None:
            return json.dumps("image_id is None"), 400, {'ContentType': 'application/json'}

        image = Image.get_by_id(s, request_image_id)
        image.is_annotation_example = not image.is_annotation_example
        s.add(image)

        out = {'success': True}
        return jsonify(out), 200, {'ContentType': 'application/json'}
