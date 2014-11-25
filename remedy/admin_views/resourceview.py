"""
resourceview.py

Contains administrative views for working with resources.
"""
from admin_helpers import *

from flask import redirect, flash, request, url_for
from flask.ext.login import current_user
from flask.ext.admin import Admin, AdminIndexView, BaseView, expose
from flask.ext.admin.menu import MenuLink
from flask.ext.admin.actions import action
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from sqlalchemy import or_, not_, func

from flask_wtf import Form
from wtforms import TextField, StringField, IntegerField, DecimalField, PasswordField, validators, ValidationError

from remedy.rad.models import Resource, User, Category, Review, db
from remedy.rad.geocoder import Geocoder

class ResourceView(AdminAuthMixin, ModelView):
    """
    An administrative view for working with resources.
    """
    column_list = ('name', 'organization', 
        'address', 'url', 
        'source', 'last_updated')

    column_default_sort = 'name'

    column_searchable_list = ('name','description','organization',)

    column_filters = ('visible','source',)

    form_excluded_columns = ('date_created', 'last_updated', 
        'category_text', 'reviews')

    create_template = 'admin/resource_create.html'

    edit_template = 'admin/resource_edit.html'

    def scaffold_form(self):
        """
        Scaffolds the creation/editing form so that the latitude
        and longitude fields are optional, but can still be set
        by the Google Places API integration.
        """
        form_class = super(ResourceView, self).scaffold_form()

        # Override the latitude/longitude fields to be optional
        form_class.latitude = DecimalField(validators=[validators.Optional()])
        form_class.longitude = DecimalField(validators=[validators.Optional()])

        return form_class    

    @action('togglevisible', 
        'Toggle Visibility', 
        'Are you sure you wish to toggle visibility for the selected resources?')
    def action_togglevisible(self, ids):
        """
        Attempts to toggle visibility for each of the specified resources.

        Args:
            ids: The list of resource IDs, indicating which resources
                should have their visibility toggled.
        """
        # Load all resources by the set of IDs
        target_resources = self.get_query().filter(self.model.id.in_(ids)).all()

        # Build a list of all the results
        results = []

        if len(target_resources) > 0:

            for resource in target_resources:
                # Build a helpful message string to use for messages.
                resource_str =  'resource #' + str(resource.id) + ' (' + resource.name + ')'
                visible_status = ''
                try:
                    if not resource.visible:
                        resource.visible = True
                        visible_status = ' as visible'
                    else:
                        resource.visible = False
                        visible_status = ' as not visible'
                except Exception as ex:
                    results.append('Error changing ' + resource_str + ': ' + str(ex))
                else:
                    results.append('Marked ' + resource_str + visible_status + '.')

            # Save our changes.
            self.session.commit()

        else:
            results.append('No resources were selected.')

        # Flash the results of everything
        flash("\n".join(msg for msg in results))

    @action('assigncategories', 'Assign Categories')
    def action_assigncategories(self, ids):
        """
        Sets up a redirection action for mass-assigning categories
        to the specified resources.

        Args:
            ids: The list of resource IDs that should be updated.
        """
        return redirect(url_for('resourcecategoryassignview.index', ids=ids))

    def __init__(self, session, **kwargs):
        super(ResourceView, self).__init__(Resource, session, **kwargs)


class ResourceRequiringGeocodingView(ResourceView):
    """
    An administrative view for working with resources that need geocoding.
    """
    column_list = ('name', 'organization', 'address', 'source')

    # Disable model creation/deletion
    can_create = False
    can_delete = False

    def get_query(self):
        """
        Returns the query for the model type.

        Returns:
            The query for the model type.
        """
        query = self.session.query(self.model)
        return self.prepare_geocode_query(query)

    def get_count_query(self):
        """
        Returns the count query for the model type.

        Returns:
            The count query for the model type.
        """
        query = self.session.query(func.count('*')).select_from(self.model)
        return self.prepare_geocode_query(query)

    def prepare_geocode_query(self, query):
        """
        Prepares the provided query by ensuring that
        all relevant geocoding-related filters have been applied.

        Args:
            query: The query to update.

        Returns:
            The updated query.
        """
        # Ensure an address is defined
        query = query.filter(self.model.address != None)
        query = query.filter(self.model.address != '')

        # Ensure at least one geocoding field is missing
        query = query.filter(or_(self.model.latitude == None,
            self.model.longitude == None))

        return query

    @action('geocode', 
        'Geocode')
    def action_geocode(self, ids):
        """
        Attempts to geocode each of the specified resources.

        Args:
            ids: The list of resource IDs, indicating which resources
                should be geocoded.
        """
        # Load all resources by the set of IDs
        target_resources = self.get_query().filter(self.model.id.in_(ids)).all()

        # Build a list of all the results
        results = []

        if len(target_resources) > 0:

            # Set up the geocoder, and then try to geocode each resource
            geocoder = Geocoder()

            for resource in target_resources:
                # Build a helpful message string to use for errors.
                resource_str =  'resource #' + str(resource.id) + ' (' + resource.name + ')'
                try:
                    geocoder.geocode(resource)
                except Exception as ex:
                    results.append('Error geocoding ' + resource_str + ': ' + str(ex))
                else:
                    results.append('Geocoded ' + resource_str + '.')

            # Save our changes.
            self.session.commit()

        else:
            results.append('No resources were selected.')

        # Flash the results of everything
        flash("\n".join(msg for msg in results))

    @action('removeaddress', 
        'Remove Address', 
        'Are you sure you wish to remove address information from the selected resources?')
    def action_remove_address(self, ids):
        """
        Attempts to remove address information from each of the specified resources.

        Args:
            ids: The list of resource IDs, indicating which resources
                should have address information stripped.
        """
        # Load all resources by the set of IDs
        target_resources = self.get_query().filter(self.model.id.in_(ids)).all()

        # Build a list of all the results
        results = []

        if len(target_resources) > 0:
            for resource in target_resources:
                # Build a helpful message string to use for errors.
                resource_str =  'resource #' + str(resource.id) + ' (' + resource.name + ')'
                try:
                    resource.address = None
                    resource.latitude = None
                    resource.longitude = None
                except Exception as ex:
                    results.append('Error updating ' + resource_str + ': ' + str(ex))
                else:
                    results.append('Removed address information from ' + resource_str + '.')

            # Save our changes.
            self.session.commit()
        else:
            results.append('No resources were selected.')

        # Flash the results of everything
        flash("\n".join(msg for msg in results))

    def __init__(self, session, **kwargs):
        # Because we're invoking the ResourceView constructor,
        # we don't need to pass in the ResourceModel.
        super(ResourceRequiringGeocodingView, self).__init__(session, **kwargs)


class ResourceRequiringCategoriesView(ResourceView):
    """
    An administrative view for working with resources that need categories.
    """
    column_list = ('name', 'organization', 'address', 'source')

    # Disable model creation/deletion
    can_create = False
    can_delete = False

    def get_query(self):
        """
        Returns the query for the model type.

        Returns:
            The query for the model type.
        """
        query = self.session.query(self.model)
        return self.prepare_category_query(query)

    def get_count_query(self):
        """
        Returns the count query for the model type.

        Returns:
            The count query for the model type.
        """
        query = self.session.query(func.count('*')).select_from(self.model)
        return self.prepare_category_query(query)

    def prepare_category_query(self, query):
        """
        Prepares the provided query by ensuring that
        filtering out resources with categories has been applied.

        Args:
            query: The query to update.

        Returns:
            The updated query.
        """
        # Ensure an address is defined
        query = query.filter(not_(self.model.categories.any()))

        return query

    def __init__(self, session, **kwargs):
        # Because we're invoking the ResourceView constructor,
        # we don't need to pass in the ResourceModel.
        super(ResourceRequiringCategoriesView, self).__init__(session, **kwargs)


class ResourceCategoryAssignView(AdminAuthMixin, BaseView):
    """
    The view for mass-assigning resources to categories.
    """
    # Not visible in the menu.
    def is_visible(self):
        return False

    @expose('/', methods=['GET', 'POST'])
    def index(self):
        """
        A view for mass-assigning resources to categories.
        """
        # Load all resources by the set of IDs
        target_resources = Resource.query.filter(Resource.id.in_(request.args.getlist('ids')))
        target_resources = target_resources.order_by(Resource.name.asc()).all()

        # Make sure we have some, and go back to the resources
        # view (for assigning categories) if we don't.
        if len(target_resources) == 0:
            flash('At least one resource must be selected.')
            return redirect(url_for('category-resourceview.index_view'))
        
        if request.method == 'GET':
            # Get all categories
            available_categories = Category.query.order_by(Category.name.asc())
            available_categories = available_categories.all()

            # Return the view for assigning categories
            return self.render('admin/resource_assign_categories.html',
                ids = request.args.getlist('ids'),
                resources = target_resources,
                categories = available_categories)
        else:
            # Get the selected categories - use request.form,
            # not request.args
            target_categories = Category.query.filter(Category.id.in_(request.form.getlist('categories'))).all()

            if len(target_categories) > 0:
                # Build a list of all the results
                results = []

                for resource in target_resources:
                    # Build a helpful message string to use for resources.
                    resource_str =  'resource #' + str(resource.id) + ' (' + resource.name + ')'

                    try:
                        # Assign all categories
                        for category in target_categories:

                            # Make sure we're not double-adding
                            if not category in resource.categories:
                                resource.categories.append(category)

                    except Exception as ex:
                        results.append('Error updating ' + resource_str + ': ' + str(ex))
                    else:
                        results.append('Updated ' + resource_str + '.')

                # Save our changes.
                self.session.commit()

                # Flash the results of everything
                flash("\n".join(msg for msg in results))                
            else:
                flash('At least one category must be selected.')

            return redirect(url_for('category-resourceview.index_view'))

    def __init__(self, session, **kwargs):
        self.session = session
        super(ResourceCategoryAssignView, self).__init__(**kwargs) 

