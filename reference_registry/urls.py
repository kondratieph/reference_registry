from django.urls import path

from reference_registry import views

urlpatterns = [
    path(
        '',
        views.ReferenceBookListView.as_view(),
        name='refbook-list',
    ),
    path(
        '<int:id>/elements/',
        views.ElementsView.as_view(),
        name='refbook-elements',
    ),
    path(
        '<int:id>/check_element/',
        views.CheckElementView.as_view(),
        name='refbook-check-element',
    ),
]