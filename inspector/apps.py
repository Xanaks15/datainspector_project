from django.apps import AppConfig
import os
import shutil
import uuid
from django.conf import settings

class InspectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inspector'

    def ready(self):
        """
        Copia el dataset por defecto a /datasets/
        solo si la carpeta está vacía.
        """
        datasets_dir = settings.MEDIA_ROOT
        default_csv = settings.DEFAULT_DATASET_PATH

        os.makedirs(datasets_dir, exist_ok=True)

        # Si ya hay archivos, no hacemos nada.
        if os.listdir(datasets_dir):
            return

        # Crear ID único
        dataset_id = uuid.uuid4().hex
        dest = os.path.join(datasets_dir, f"{dataset_id}.csv")

        shutil.copy(default_csv, dest)
        print(f"✔ Dataset por defecto copiado a: {dest}")
