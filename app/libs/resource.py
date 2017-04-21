from typing import List, Tuple, Optional
from urllib.parse import urljoin

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import BaseQuery, Model

from connexion import NoContent, request, problem

from app.config import API_DEFAULT_LIMIT

from .authorization import get_authorization


READ_ONLY_FIELDS = ('created', 'updated', 'username')


########################################################################################################################
# DEFAULT HANDLER
########################################################################################################################
class ResourceHandler:

    model_fields = ()

    @property
    def authorization(self):
        return get_authorization()

    ####################################################################################################################
    # HANDLERS
    ####################################################################################################################
    @classmethod
    def list(cls, **kwargs) -> dict:
        resource = cls()

        # Get query
        query = resource.get_query(**kwargs)

        # Filter query
        filter_kwargs = resource.get_filter_kwargs(**kwargs)
        if filter_kwargs:
            query = resource.get_filtered_query(query, **filter_kwargs)

        # Limit query
        query = resource.get_limited_query(query, **kwargs)

        # Get objects from DB
        objs = resource.get_objects(query)

        # Transform objects to resources
        resources = [resource.build_resource(obj, **kwargs) for obj in objs]

        # Return list response (mainly add _meta)
        return resource.build_list_response(resources, **kwargs)

    @classmethod
    def get(cls, **kwargs) -> dict:
        resource = cls()

        obj_id = int(kwargs.get('id'))

        # Get objects from DB
        obj = resource.get_object(obj_id, **kwargs)

        # Transform object to resource
        return resource.build_resource(obj, **kwargs)

    @classmethod
    def create(cls, **kwargs) -> Tuple:
        resource = cls()

        resource.validate(**kwargs)

        # Build object from resource payload
        obj = resource.new_object(**kwargs)

        # Should raise Authorization error if needed!
        resource.authorization.create(obj, **kwargs)

        # Persist
        try:
            obj = resource.save_object(obj)
        except IntegrityError:
            return problem(status=400, title='Duplication error', detail='Resource already exist')

        # Transform object to resource
        return resource.build_resource(obj), 201

    @classmethod
    def update(cls, **kwargs) -> dict:
        resource = cls()

        obj_id = int(kwargs.get('id'))

        # Get objects from DB
        obj = resource.get_object(obj_id, **kwargs)

        resource.validate(**kwargs)

        resource.authorization.update(obj, **kwargs)

        # Persist
        try:
            obj = resource.update_object(obj, **kwargs)
        except IntegrityError as e:
            return problem(status=400, title='Duplication error', detail='Resource already exist')

        return resource.build_resource(obj, **kwargs)

    @classmethod
    def delete(cls, **kwargs) -> Tuple:
        resource = cls()

        obj_id = int(kwargs.get('id'))

        # Get objects from DB
        obj = resource.get_object(obj_id, **kwargs)

        resource.authorization.delete(obj, **kwargs)

        resource.delete_object(obj, **kwargs)

        return NoContent, 204

    ####################################################################################################################
    # DEFAULT IMPL
    ####################################################################################################################
    def build_list_response(self, resources: List[dict], **kwargs) -> dict:
        return {
            'data': resources,
            '_meta': {
                'count': len(resources),
                # TODO: paging URIs
            }
        }

    def get_limited_query(self, query: BaseQuery, **kwargs) -> BaseQuery:
        """Apply pagination limits on query"""
        limit = kwargs.get('limit', API_DEFAULT_LIMIT)
        offset = kwargs.get('offset', 0)

        return query.limit(limit).offset(offset)

    def get_filtered_query(self, query: BaseQuery, **kwargs) -> BaseQuery:
        """Filter query using query parameters"""
        return query.filter_by(**kwargs)

    def get_filter_kwargs(self, **kwargs) -> dict:
        return {}

    def build_resource(self, obj: Model, request_path: Optional[str]=None, **kwargs) -> dict:
        resource = {}

        for field in self.model_fields:
            resource[field] = getattr(obj, field)

        if not request_path:
            request_path = request.path

        if not hasattr(obj, 'id'):
            return resource

        uri_path = '{}/{}'.format(request_path, str(obj.id))

        # Adjust path components (list v.s. detail)
        path_components = request_path.lstrip('/').rsplit('/', 1)
        if str(obj.id) == path_components[-1]:
            uri_path = request_path

        resource['uri'] = urljoin(request.base_url, uri_path)

        return resource

    def get_id_from_uri(self, uri: str) -> Optional[int]:
        end = uri.strip('/').rsplit('/', 1)[-1]

        if end.isdigit():
            return int(end)

        return None

    def get_object_fields(self, body: dict, **kwargs) -> dict:
        fields = {}

        for field in self.model_fields:
            if field in READ_ONLY_FIELDS:
                continue
            fields[field] = body.get(field)

        return fields

    ####################################################################################################################
    # NOT IMPL
    ####################################################################################################################
    def validate(self, **kwargs) -> None:
        pass

    def get_query(self, **kwargs) -> BaseQuery:
        raise NotImplemented

    def new_object(self, **kwargs) -> Model:
        raise NotImplemented

    def get_objects(self, query: BaseQuery, **kwargs) -> List[Model]:
        raise NotImplemented

    def get_object(self, obj_id: int, **kwargs) -> Model:
        raise NotImplemented

    def save_object(self, obj: Model, **kwargs) -> Model:
        raise NotImplemented

    def update_object(self, obj: Model, **kwargs) -> Model:
        raise NotImplemented

    def delete_object(self, obj: Model, **kwargs) -> Model:
        raise NotImplemented
