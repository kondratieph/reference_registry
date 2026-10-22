from django.urls import path

from reference_registry import views

urlpatterns = [
    path(
        '',
        views.ReferenceBookListView.as_view(),
        name='refbook-list',
    ),
    path(
        '<int:pk>/elements/',
        views.ElementsView.as_view(),
        name='refbook-elements',
    ),
    path(
        '<int:pk>/check_element/',
        views.CheckElementView.as_view(),
        name='refbook-check-element',
    ),
]