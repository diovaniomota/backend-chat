from django.contrib import admin
from attachments.models import FileAttachment, AudioAttachments

# Registrar os modelos no admin
admin.site.register(FileAttachment)
admin.site.register(AudioAttachments)
