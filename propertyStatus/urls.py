from django.urls import path,include
from .views import *
from .filters_views import *


urlpatterns = [
    path('project/', ProjectAPIview.as_view(),name="ProjectAPIview"),
    path('project/<int:pk>/', ProjectAPIview.as_view(),name="ProjectAPIview"),

    path('project-type/', ProjectTypAPIview.as_view(),name="ProjectTypAPIview"),
    path('project-type/<int:pk>/', ProjectTypAPIview.as_view(),name="ProjectTypAPIview"),

    path('unit-number/', UnitNoAPIview.as_view(),name="UnitNoAPIview"),
    path('unit-number/<int:pk>/', UnitNoAPIview.as_view(),name="UnitNoAPIview"),

    path('phase/', PhaseAPIview.as_view(),name="PhaseAPIview"),
    path('phase/<int:pk>/', PhaseAPIview.as_view(),name="PhaseAPIview"),

    path('status/', StatusAPIview.as_view(),name="StatusAPIview"),
    path('status/<int:pk>/', StatusAPIview.as_view(),name="StatusAPIview"),

    path('tax/', TaxTypeAPIview.as_view(),name="TaxTypeAPIview"),
    path('tax/<int:pk>/', TaxTypeAPIview.as_view(),name="TaxTypeAPIview"),

    # urls for the filters apis
    path('project-type-filter/', ProjectTypeListView.as_view(),name="ProjectTypeListView"),
    path('unit-number-filter/', UnitNoListView.as_view(),name="UnitNoListView"),

    path('phase-number-filter/', PhaseFilterData.as_view(),name="PhaseFilterData"),
    path('unit-no-with-available/', UnitNoListunbookedAllViewunitnumber.as_view(),name="UnitNoListunbookedAllViewunitnumber"),
    path('unit-no-non-available/', UnitNoListbookedAllViewunitnumber.as_view(),name="UnitNoListunbookedAllViewunitnumber"),

    path('document-type/', ProjectDocumentTypeAPIview.as_view(),name="ProjectDocumentTypeAPIview"),
    path('document-type/<int:pk>/', ProjectDocumentTypeAPIview.as_view(),name="ProjectDocumentTypeAPIview"),

    path('upload-document/', ProjectDocumentAPIview.as_view(),name="ProjectDocumentAPIview"),
    path('upload-document/<int:pk>/', ProjectDocumentAPIview.as_view(),name="ProjectDocumentAPIview"),

    path('phase-project-filter/<int:project_id>/', PhaseByProjectAPIView.as_view(),name="PhaseByProjectAPIView"),

    path('unit-project-filter/', ProjectUnitFilter.as_view(),name="ProjectUnitFilter"),
]
