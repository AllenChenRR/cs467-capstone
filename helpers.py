import os
def get_image_url(app, id):
    return os.path.join(
        app.config['STORAGE_URL'],
        app.config['BUCKET'],
        id
    )

                        