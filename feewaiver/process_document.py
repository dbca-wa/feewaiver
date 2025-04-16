import os
from django.core.files.base import ContentFile
import traceback
from feewaiver.main_models import EmailUser
from feewaiver.models import FeeWaiverUserAction
from django.contrib import auth
from feewaiver.storage import PrivateMediaStorage

private_storage = PrivateMediaStorage()


def process_generic_document(request, instance, document_type=None, *args, **kwargs):
    print("process_generic_document")
    print(request.data)
    try:
        action = request.data.get('action')
        input_name = request.data.get('input_name')
        comms_log_id = request.data.get('comms_log_id')
        comms_instance = None

        if document_type == 'comms_log' and comms_log_id and comms_log_id != 'null':
            comms_instance = instance.comms_logs.get(id=comms_log_id)
        elif document_type == 'comms_log':
            comms_instance = instance.comms_logs.create()

        if action == 'list':
            pass
        elif action == 'delete':
            delete_document(request, instance, comms_instance, document_type, input_name)
        elif action == 'cancel':
            deleted = cancel_document(request, instance, comms_instance, document_type, input_name)
        elif action == 'save':
            save_document(request, instance, comms_instance, document_type, input_name)

        # HTTP Response varies by action and instance type
        if comms_instance and action == 'cancel' and deleted:
            return deleted
        elif comms_instance:
            returned_file_data = [dict(file=d._file.url, id=d.id, name=d.name,) for d in comms_instance.documents.all() if d._file]
            return {'filedata': returned_file_data, 'comms_instance_id': comms_instance.id}
        else:
            returned_file_data = [dict(file=d._file.url, id=d.id, name=d.name, ) for d in instance.documents.all() if d._file]
            return {'filedata': returned_file_data}

    except Exception as e:
        print(traceback.print_exc())
        raise e


def delete_document(request, instance, comms_instance, document_type, input_name=None):
    # comms_log doc store delete
    if comms_instance and 'document_id' in request.data:
        document_id = request.data.get('document_id')
        document = comms_instance.documents.get(id=document_id)

    # default doc store delete
    elif 'document_id' in request.data:
        document_id = request.data.get('document_id')
        document = instance.documents.get(id=document_id)

    if document._file and os.path.isfile(
            document._file.path):
        os.remove(document._file.path)

    if document:
        document.delete()
        # log document action
        request_user = auth.get_user(request)
        if type(request_user) is EmailUser:
            instance.fee_waiver.log_user_action(
                FeeWaiverUserAction.ACTION_DELETE_DOCUMENT.format(
                    instance.fee_waiver.lodgement_number, 
                    document.name, 
                    request.user.get_full_name()),
                request)


def cancel_document(request, instance, comms_instance, document_type, input_name=None):
        if comms_instance:
            document_list = comms_instance.documents.all()
        else:
            document_list = instance.documents.all()

        for document in document_list:
            if document._file and os.path.isfile(document._file.path):
                os.remove(document._file.path)
            document.delete()

        if comms_instance:
            return comms_instance.delete()


def save_document(request, instance, comms_instance, document_type, input_name=None):

    # comms_log doc store save
    if comms_instance and 'filename' in request.data:
        filename = request.data.get('filename')
        _file = request.data.get('_file')

        document = comms_instance.documents.get_or_create(
            name=filename)[0]
        path = private_storage.save(
            '{}/{}/communications/{}/documents/{}'.format(
                instance._meta.model_name, instance.id, comms_instance.id, filename), ContentFile(
                _file.read()))

        document._file = path
        document.save()

    # default doc store save
    elif 'filename' in request.data:
        filename = request.data.get('filename')
        _file = request.data.get('_file')

        document = instance.documents.get_or_create(
            name=filename)[0]
        
        path = private_storage.save(
            '{}/{}/documents/{}'.format(
                instance._meta.model_name, instance.id, filename), ContentFile(
                _file.read()))

        document._file = path
        document.save()

        # log document action
        request_user = auth.get_user(request)
        if type(request_user) is EmailUser:
            try:
                instance.fee_waiver.log_user_action(
                    FeeWaiverUserAction.ACTION_SAVE_DOCUMENT.format(
                        instance.fee_waiver.lodgement_number, 
                        document.name, 
                        request.user.get_full_name()),
                    request)
            except Exception as e:
                print(traceback.print_exc())

# For transferring files from temp doc objs to comms_log objs
def save_comms_log_document_obj(instance, comms_instance, temp_document):
    document = comms_instance.documents.get_or_create(
        name=temp_document.name)[0]
    path = private_storage.save(
        '{}/{}/communications/{}/documents/{}'.format(
            instance._meta.model_name, 
            instance.id, 
            comms_instance.id, 
            temp_document.name
            ), 
            temp_document._file
        )

    document._file = path
    document.save()


# For transferring files from temp doc objs to default doc objs
def save_default_document_obj(instance, temp_document):
    document = instance.documents.get_or_create(
        name=temp_document.name)[0]
    path = private_storage.save(
        '{}/{}/documents/{}'.format(
            instance._meta.model_name, 
            instance.id, 
            temp_document.name
            ), 
            temp_document._file
        )

    document._file = path
    document.save()

